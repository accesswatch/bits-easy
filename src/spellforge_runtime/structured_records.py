from __future__ import annotations

from dataclasses import dataclass
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .diagnostics import get_logger
from .engine import RuntimeResult

_logger = get_logger("spellforge.structured_records")


@dataclass
class FieldDef:
    name: str
    field_type: str = "text"
    required: bool = False
    help_text: str = ""
    validator: str = ""
    choices: List[str] | None = None


class StructuredRecordService:
    def __init__(self, storage_path: Path | str | None = None):
        self._storage_path = Path(storage_path) if storage_path else None
        self._databases: Dict[str, Dict[str, Any]] = {}
        self._deleted_snapshots: Dict[str, Dict[str, Any]] = {}
        self._current_db = ""
        self._entry_counter = 0
        self._launch_bookmark: Dict[str, str] | None = None
        self._load()

    def _save(self) -> None:
        if self._storage_path is None:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "databases": self._databases,
            "deleted": self._deleted_snapshots,
            "current": self._current_db,
            "entryCounter": self._entry_counter,
            "launchBookmark": self._launch_bookmark,
        }
        self._storage_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if self._storage_path is None or not self._storage_path.exists():
            return
        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except Exception:
            _logger.exception("Spellforge: loading structured records at %s failed", self._storage_path)
            return
        self._databases = payload.get("databases", {}) if isinstance(payload.get("databases", {}), dict) else {}
        self._deleted_snapshots = payload.get("deleted", {}) if isinstance(payload.get("deleted", {}), dict) else {}
        self._current_db = str(payload.get("current", ""))
        self._entry_counter = int(payload.get("entryCounter", 0))
        launch = payload.get("launchBookmark")
        self._launch_bookmark = launch if isinstance(launch, dict) else None

    def _active(self) -> tuple[Optional[str], Optional[Dict[str, Any]], Optional[RuntimeResult]]:
        if not self._current_db:
            return None, None, RuntimeResult(ok=False, message="No database is selected.")
        db = self._databases.get(self._current_db)
        if db is None:
            return None, None, RuntimeResult(ok=False, message="Selected database was not found.")
        return self._current_db, db, None

    @staticmethod
    def _normalize_name(name: str) -> str:
        return name.strip().lower()

    def create_database(self, name: str) -> RuntimeResult:
        db_name = self._normalize_name(name)
        if not db_name:
            return RuntimeResult(ok=False, message="Database name is required.")
        if db_name in self._databases:
            return RuntimeResult(ok=False, message="Database name must be unique.")
        self._databases[db_name] = {"schema": {}, "entries": []}
        self._current_db = db_name
        self._save()
        return RuntimeResult(ok=True, message="Database created.", payload={"database": db_name})

    def select_database(self, name: str) -> RuntimeResult:
        db_name = self._normalize_name(name)
        if db_name not in self._databases:
            return RuntimeResult(ok=False, message="Database was not found.")
        self._current_db = db_name
        self._save()
        return RuntimeResult(ok=True, message="Database selected.", payload={"database": db_name})

    def delete_database(self, name: str, *, confirm: bool) -> RuntimeResult:
        db_name = self._normalize_name(name)
        if db_name not in self._databases:
            return RuntimeResult(ok=False, message="Database was not found.")
        if not confirm:
            return RuntimeResult(ok=False, message="Delete requires confirmation.")
        self._deleted_snapshots[db_name] = self._databases[db_name]
        del self._databases[db_name]
        if self._current_db == db_name:
            self._current_db = ""
        self._save()
        return RuntimeResult(ok=True, message="Database deleted with restore point.", payload={"database": db_name})

    def restore_database(self, name: str) -> RuntimeResult:
        db_name = self._normalize_name(name)
        snap = self._deleted_snapshots.get(db_name)
        if snap is None:
            return RuntimeResult(ok=False, message="Restore point was not found.")
        self._databases[db_name] = snap
        self._current_db = db_name
        self._save()
        return RuntimeResult(ok=True, message="Database restored.", payload={"database": db_name})

    def define_field(
        self,
        field_name: str,
        *,
        field_type: str = "text",
        required: bool = False,
        help_text: str = "",
        validator: str = "",
        choices: Optional[List[str]] = None,
    ) -> RuntimeResult:
        _, db, err = self._active()
        if err:
            return err
        fname = field_name.strip()
        if not fname:
            return RuntimeResult(ok=False, message="Field name is required.")
        ftype = field_type.strip().lower()
        if ftype not in ("text", "number", "bool", "date", "choice"):
            return RuntimeResult(ok=False, message="Field type must be text, number, bool, date, or choice.")
        db["schema"][fname] = {
            "name": fname,
            "type": ftype,
            "required": bool(required),
            "helpText": help_text.strip(),
            "validator": validator.strip(),
            "choices": [str(x) for x in (choices or [])],
        }
        self._save()
        return RuntimeResult(ok=True, message="Field defined.", payload={"field": fname, "type": ftype})

    def _validate_value(self, field: Dict[str, Any], value: Any) -> Optional[str]:
        ftype = str(field.get("type", "text"))
        raw = "" if value is None else str(value)
        if field.get("required", False) and not raw.strip():
            return f"Field {field.get('name','')} is required."
        if not raw.strip():
            return None

        if ftype == "number":
            try:
                float(raw)
            except Exception:
                return f"Field {field.get('name','')} must be numeric."
        elif ftype == "bool":
            if raw.strip().lower() not in ("true", "false", "1", "0", "yes", "no"):
                return f"Field {field.get('name','')} must be boolean."
        elif ftype == "date":
            from datetime import datetime

            try:
                datetime.fromisoformat(raw)
            except Exception:
                return f"Field {field.get('name','')} must be ISO date/datetime."
        elif ftype == "choice":
            choices = [str(x) for x in field.get("choices", [])]
            if choices and raw not in choices:
                return f"Field {field.get('name','')} must match allowed choices."

        validator = str(field.get("validator", "")).strip().lower()
        if validator == "email" and "@" not in raw:
            return f"Field {field.get('name','')} must be a valid email."
        return None

    def _validate_entry(self, schema: Dict[str, Any], values: Dict[str, Any]) -> List[str]:
        errors = []
        for field_name, field in schema.items():
            err = self._validate_value(field, values.get(field_name))
            if err:
                errors.append(err)
        return errors

    def add_entry(self, values: Dict[str, Any]) -> RuntimeResult:
        _, db, err = self._active()
        if err:
            return err
        schema = db.get("schema", {})
        if not schema:
            return RuntimeResult(ok=False, message="Define at least one field before adding entries.")

        errors = self._validate_entry(schema, values)
        if errors:
            return RuntimeResult(ok=False, message="Entry validation failed.", payload={"errors": errors})

        self._entry_counter += 1
        eid = f"rec-{self._entry_counter:05d}"
        row = {"entryId": eid, "values": {k: values.get(k) for k in schema.keys()}}
        db["entries"].append(row)
        self._save()
        return RuntimeResult(ok=True, message="Entry added.", payload={"entryId": eid})

    def edit_entry(self, entry_id: str, values: Dict[str, Any]) -> RuntimeResult:
        _, db, err = self._active()
        if err:
            return err
        schema = db.get("schema", {})
        entry = next((x for x in db.get("entries", []) if str(x.get("entryId", "")) == entry_id.strip()), None)
        if entry is None:
            return RuntimeResult(ok=False, message="Entry not found.")

        merged = dict(entry.get("values", {}))
        merged.update(values)
        errors = self._validate_entry(schema, merged)
        if errors:
            return RuntimeResult(ok=False, message="Entry validation failed.", payload={"errors": errors})

        entry["values"] = {k: merged.get(k) for k in schema.keys()}
        self._save()
        return RuntimeResult(ok=True, message="Entry updated.", payload={"entryId": entry_id.strip()})

    def delete_entry(self, entry_id: str, *, confirm: bool) -> RuntimeResult:
        _, db, err = self._active()
        if err:
            return err
        if not confirm:
            return RuntimeResult(ok=False, message="Delete requires confirmation.")

        target = entry_id.strip()
        before = len(db.get("entries", []))
        db["entries"] = [x for x in db.get("entries", []) if str(x.get("entryId", "")) != target]
        if len(db["entries"]) == before:
            return RuntimeResult(ok=False, message="Entry not found.")
        self._save()
        return RuntimeResult(ok=True, message="Entry deleted.", payload={"entryId": target})

    def list_entries(self, columns: Optional[List[str]] = None) -> RuntimeResult:
        _, db, err = self._active()
        if err:
            return err
        schema = db.get("schema", {})
        chosen = [str(x) for x in (columns or list(schema.keys()))]
        rows = []
        for e in db.get("entries", []):
            vals = e.get("values", {})
            row = {"entryId": e.get("entryId", "")}
            for col in chosen:
                row[col] = vals.get(col)
            rows.append(row)
        return RuntimeResult(ok=True, message="Entries ready.", payload={"columns": chosen, "items": rows, "count": len(rows)})

    def entry_detail(self, entry_id: str) -> RuntimeResult:
        _, db, err = self._active()
        if err:
            return err
        entry = next((x for x in db.get("entries", []) if str(x.get("entryId", "")) == entry_id.strip()), None)
        if entry is None:
            return RuntimeResult(ok=False, message="Entry not found.")
        return RuntimeResult(ok=True, message="Entry detail ready.", payload={"entry": entry})

    def search_entries(self, field: str, query: str) -> RuntimeResult:
        _, db, err = self._active()
        if err:
            return err
        key = field.strip()
        q = query.strip().lower()
        rows = []
        for e in db.get("entries", []):
            value = str(e.get("values", {}).get(key, ""))
            if q and q not in value.lower():
                continue
            rows.append(e)
        return RuntimeResult(ok=True, message="Search results ready.", payload={"items": rows, "count": len(rows), "field": key})

    def sort_entries(self, field: str, descending: bool = False) -> RuntimeResult:
        _, db, err = self._active()
        if err:
            return err
        key = field.strip()
        rows = list(db.get("entries", []))
        rows.sort(key=lambda x: str(x.get("values", {}).get(key, "")), reverse=bool(descending))
        return RuntimeResult(ok=True, message="Sorted entries ready.", payload={"items": rows, "count": len(rows), "field": key, "descending": bool(descending)})

    def export_csv(self, out_path: Path | str) -> RuntimeResult:
        _, db, err = self._active()
        if err:
            return err
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        schema = list(db.get("schema", {}).keys())
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["entryId"] + schema)
            for e in db.get("entries", []):
                vals = e.get("values", {})
                writer.writerow([e.get("entryId", "")] + [vals.get(c, "") for c in schema])
        return RuntimeResult(ok=True, message="CSV export complete.", payload={"path": str(path)})

    def export_text(self, out_path: Path | str) -> RuntimeResult:
        _, db, err = self._active()
        if err:
            return err
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        for e in db.get("entries", []):
            lines.append(f"[{e.get('entryId','')}]")
            for k, v in e.get("values", {}).items():
                lines.append(f"{k}: {v}")
            lines.append("")
        path.write_text("\n".join(lines), encoding="utf-8")
        return RuntimeResult(ok=True, message="Text export complete.", payload={"path": str(path)})

    def jamal_export(self, out_path: Path | str) -> RuntimeResult:
        db_name, db, err = self._active()
        if err:
            return err
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "jamalVersion": 1,
            "database": db_name,
            "schema": db.get("schema", {}),
            "entries": db.get("entries", []),
        }
        path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
        return RuntimeResult(ok=True, message="Jamal export complete.", payload={"path": str(path), "database": db_name})

    def jamal_import(self, in_path: Path | str, *, database_name: str = "") -> RuntimeResult:
        path = Path(in_path)
        if not path.exists():
            return RuntimeResult(ok=False, message="Jamal import file not found.")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            return RuntimeResult(ok=False, message=f"Jamal import failed: {exc}")

        schema = payload.get("schema", {})
        entries = payload.get("entries", [])
        if not isinstance(schema, dict) or not isinstance(entries, list):
            return RuntimeResult(ok=False, message="Jamal import data is invalid.")

        target = self._normalize_name(database_name or str(payload.get("database", "jamal-import")))
        if not target:
            target = "jamal-import"
        self._databases[target] = {"schema": schema, "entries": entries}
        self._current_db = target

        for e in entries:
            eid = str(e.get("entryId", ""))
            if eid.startswith("rec-"):
                try:
                    n = int(eid.replace("rec-", ""))
                    self._entry_counter = max(self._entry_counter, n)
                except Exception:
                    pass

        self._save()
        return RuntimeResult(ok=True, message="Jamal import complete.", payload={"database": target, "count": len(entries)})

    def jamal_launch(self, dataset_path: Path | str) -> RuntimeResult:
        db_name, _, err = self._active()
        if err:
            return err
        path = Path(dataset_path)
        self._launch_bookmark = {"database": db_name or "", "datasetPath": str(path)}
        self._save()
        return RuntimeResult(ok=True, message="Jamal launch bridge ready.", payload={"datasetPath": str(path), "bookmark": self._launch_bookmark})

    def jamal_return(self) -> RuntimeResult:
        if self._launch_bookmark is None:
            return RuntimeResult(ok=False, message="No Jamal launch bookmark found.")
        target = str(self._launch_bookmark.get("database", ""))
        if target and target in self._databases:
            self._current_db = target
            self._save()
            return RuntimeResult(ok=True, message="Returned from Jamal launch bookmark.", payload={"database": target})
        return RuntimeResult(ok=False, message="Launch bookmark database was not found.")

    def jamal_sync(self, incoming_entries: List[Dict[str, Any]], *, apply: bool = False) -> RuntimeResult:
        _, db, err = self._active()
        if err:
            return err

        current = {str(e.get("entryId", "")): e for e in db.get("entries", [])}
        incoming = {str(e.get("entryId", "")): e for e in incoming_entries}

        conflicts = []
        for eid, inc in incoming.items():
            cur = current.get(eid)
            if cur is None:
                continue
            if cur.get("values", {}) != inc.get("values", {}):
                conflicts.append({"entryId": eid, "current": cur.get("values", {}), "incoming": inc.get("values", {})})

        if not apply:
            return RuntimeResult(ok=True, message="Jamal sync dry-run complete.", payload={"conflicts": conflicts, "conflictCount": len(conflicts), "wouldApply": True})

        # Apply mode: merge incoming values, keep restore snapshot.
        db_name = self._current_db
        if db_name:
            self._deleted_snapshots[f"sync-snapshot-{db_name}"] = {
                "schema": dict(db.get("schema", {})),
                "entries": list(db.get("entries", [])),
            }

        merged = dict(current)
        for eid, inc in incoming.items():
            merged[eid] = inc
        db["entries"] = list(merged.values())
        self._save()
        return RuntimeResult(ok=True, message="Jamal sync applied with snapshot.", payload={"conflictCount": len(conflicts), "mergedCount": len(db['entries'])})
