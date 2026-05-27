import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime.emoji_assistant import EmojiAssistant


EMOJI_TEST_SAMPLE = """
# group: Smileys & Emotion
# subgroup: face-smiling
1F600                                                  ; fully-qualified     # 😀 E1.0 grinning face
1F642                                                  ; fully-qualified     # 🙂 E1.0 slightly smiling face
# group: Objects
# subgroup: light & video
1F4A1                                                  ; fully-qualified     # 💡 E0.6 light bulb
""".strip()

EN_XML_SAMPLE = """
<?xml version=\"1.0\" encoding=\"UTF-8\" ?>
<ldml>
  <annotations>
    <annotation cp=\"😀\" type=\"tts\">grinning face</annotation>
    <annotation cp=\"😀\">face | grinning</annotation>
    <annotation cp=\"🙂\" type=\"tts\">slightly smiling face</annotation>
    <annotation cp=\"🙂\">face | smile</annotation>
    <annotation cp=\"💡\" type=\"tts\">light bulb</annotation>
    <annotation cp=\"💡\">idea | light</annotation>
  </annotations>
</ldml>
""".strip()

ES_XML_SAMPLE = """
<?xml version=\"1.0\" encoding=\"UTF-8\" ?>
<ldml>
  <annotations>
    <annotation cp=\"😀\" type=\"tts\">cara sonriendo</annotation>
    <annotation cp=\"😀\">cara | sonreir</annotation>
    <annotation cp=\"💡\" type=\"tts\">bombilla</annotation>
    <annotation cp=\"💡\">idea | luz</annotation>
  </annotations>
</ldml>
""".strip()


class EmojiAssistantTests(unittest.TestCase):
    def _fetcher(self, mapping):
        def _read(url: str, timeout: float) -> str:
            _ = timeout
            if url not in mapping:
                raise RuntimeError(f"unexpected URL: {url}")
            return mapping[url]

        return _read

    def test_dynamic_catalog_uses_unicode_groups_and_localized_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "emoji-cache.json"
            mapping = {
                "https://unicode.org/Public/emoji/latest/emoji-test.txt": EMOJI_TEST_SAMPLE,
                "https://raw.githubusercontent.com/unicode-org/cldr/main/common/annotations/en.xml": EN_XML_SAMPLE,
                "https://raw.githubusercontent.com/unicode-org/cldr/main/common/annotations/es.xml": ES_XML_SAMPLE,
            }

            assistant = EmojiAssistant(
                cache_path=cache_path,
                locale="es",
                fetch_text=self._fetcher(mapping),
            )

            listed = assistant.list_items(limit=20)
            self.assertTrue(listed.ok)
            self.assertEqual(3, listed.payload["count"])

            people = assistant.list_items(category="people", limit=20)
            self.assertEqual(2, people.payload["count"])

            localized = assistant.list_items(query="sonriendo", limit=20)
            self.assertEqual(1, localized.payload["count"])
            self.assertEqual("😀", localized.payload["items"][0]["emoji"])
            self.assertEqual("cara sonriendo", localized.payload["items"][0]["label"])

            inserted = assistant.insert(alias="grinning-face")
            self.assertTrue(inserted.ok)
            self.assertEqual("😀", inserted.payload["insertText"])
            self.assertTrue(cache_path.exists())

    def test_cache_used_when_remote_sources_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "emoji-cache.json"
            good_mapping = {
                "https://unicode.org/Public/emoji/latest/emoji-test.txt": EMOJI_TEST_SAMPLE,
                "https://raw.githubusercontent.com/unicode-org/cldr/main/common/annotations/en.xml": EN_XML_SAMPLE,
            }
            seeded = EmojiAssistant(cache_path=cache_path, locale="en", fetch_text=self._fetcher(good_mapping))
            seeded.list_items(limit=10)
            self.assertTrue(cache_path.exists())

            def always_fail(url: str, timeout: float) -> str:
                _ = (url, timeout)
                raise RuntimeError("offline")

            offline = EmojiAssistant(cache_path=cache_path, locale="en", fetch_text=always_fail)
            listed = offline.list_items(limit=10)
            self.assertTrue(listed.ok)
            self.assertGreaterEqual(listed.payload["count"], 1)
            self.assertTrue(any(row.get("alias") == "grinning-face" for row in listed.payload["items"]))


if __name__ == "__main__":
    unittest.main()
