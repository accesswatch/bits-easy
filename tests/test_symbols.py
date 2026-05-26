import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime.symbols import SymbolAssistant


class SymbolAssistantTests(unittest.TestCase):
    def test_insert_search_recent(self):
        symbols = SymbolAssistant()

        ins = symbols.insert_by_code("169")
        self.assertTrue(ins.ok)
        self.assertEqual(ins.payload["symbol"], "©")

        search = symbols.search("trade")
        self.assertTrue(search.ok)
        self.assertGreaterEqual(search.payload["count"], 1)

        recent = symbols.recent()
        self.assertTrue(recent.ok)
        self.assertEqual(recent.payload["code"], "169")


if __name__ == "__main__":
    unittest.main()

