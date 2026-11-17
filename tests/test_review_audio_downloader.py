import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.review_audio_downloader import download_unique


class ReviewAudioDownloaderTests(unittest.TestCase):
    def test_deduplicates_and_keeps_review_only_state(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            candidates = [
                {"title": "Rain", "creator": "A", "source_url": "https://example/rain", "download_url": "https://example/rain.mp3", "duration_seconds": 180},
                {"title": "Blue", "creator": "B", "source_url": "https://example/blue", "file_url": "https://example/blue.mp3", "duration_seconds": 200},
            ]
            with patch("scripts.review_audio_downloader.urllib.request.urlopen") as opener:
                response = opener.return_value.__enter__.return_value
                response.headers = {"Content-Type": "audio/mpeg"}
                response.read.side_effect = [b"ID3-test-audio", b""]
                report = download_unique([candidates[0]], candidates, output)
            self.assertEqual(report["dedup"]["duplicate_count"], 1)
            self.assertEqual(report["downloaded_count"], 1)
            self.assertFalse(report["approval_mutated"])
            self.assertFalse(report["rights_verified"])
            self.assertEqual(report["publication"], "DISABLED")
            self.assertTrue(json.loads((output / "review-download-manifest.json").read_text())["downloaded"])


if __name__ == "__main__":
    unittest.main()
