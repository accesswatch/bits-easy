from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from typing import Optional


class SecretStore(ABC):
    @abstractmethod
    def diagnostics(self) -> dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def set_secret(self, namespace: str, name: str, value: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_secret(self, namespace: str, name: str) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def delete_secret(self, namespace: str, name: str) -> bool:
        raise NotImplementedError


class InMemorySecretStore(SecretStore):
    def __init__(self) -> None:
        self._secrets: dict[str, str] = {}

    @staticmethod
    def _target(namespace: str, name: str) -> str:
        return f"{namespace}:{name}"

    def set_secret(self, namespace: str, name: str, value: str) -> bool:
        self._secrets[self._target(namespace, name)] = value
        return True

    def get_secret(self, namespace: str, name: str) -> Optional[str]:
        return self._secrets.get(self._target(namespace, name))

    def delete_secret(self, namespace: str, name: str) -> bool:
        self._secrets.pop(self._target(namespace, name), None)
        return True

    def diagnostics(self) -> dict[str, object]:
        return {
            "backend": "in-memory",
            "secure": False,
            "persistent": False,
        }


class WindowsCredentialStore(SecretStore):
    def __init__(self) -> None:
        import win32cred  # type: ignore

        self._win32cred = win32cred

    @staticmethod
    def _target(namespace: str, name: str) -> str:
        return f"{namespace}:{name}"

    def set_secret(self, namespace: str, name: str, value: str) -> bool:
        target = self._target(namespace, name)
        try:
            self._win32cred.CredWrite(
                {
                    "Type": self._win32cred.CRED_TYPE_GENERIC,
                    "TargetName": target,
                    "CredentialBlob": value,
                    "Persist": self._win32cred.CRED_PERSIST_LOCAL_MACHINE,
                    "UserName": "bits_easy",
                },
                0,
            )
            return True
        except Exception:
            return False

    def get_secret(self, namespace: str, name: str) -> Optional[str]:
        target = self._target(namespace, name)
        try:
            cred = self._win32cred.CredRead(target, self._win32cred.CRED_TYPE_GENERIC, 0)
        except Exception:
            return None
        blob = cred.get("CredentialBlob", b"")
        if isinstance(blob, bytes):
            try:
                return blob.decode("utf-16-le")
            except Exception:
                return blob.decode("utf-8", errors="ignore")
        return str(blob)

    def delete_secret(self, namespace: str, name: str) -> bool:
        target = self._target(namespace, name)
        try:
            self._win32cred.CredDelete(target, self._win32cred.CRED_TYPE_GENERIC, 0)
            return True
        except Exception:
            return True

    def diagnostics(self) -> dict[str, object]:
        return {
            "backend": "windows-credential-manager",
            "secure": True,
            "persistent": True,
        }


def create_default_secret_store() -> SecretStore:
    if sys.platform.startswith("win"):
        try:
            store = WindowsCredentialStore()
            # Probe once so failures degrade gracefully.
            if store.set_secret("bits_easy.ai.probe", "health", "ok"):
                store.delete_secret("bits_easy.ai.probe", "health")
                return store
            return InMemorySecretStore()
        except Exception:
            return InMemorySecretStore()
    return InMemorySecretStore()

