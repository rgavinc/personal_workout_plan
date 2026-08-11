import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import download_images
import scrape_workouts_to_json as scraper


class OutputPathTests(unittest.TestCase):
    def test_scraper_defaults_to_docs_workouts_json(self) -> None:
        self.assertEqual(scraper.DEFAULT_OUTPUT, ROOT / "docs" / "workouts.json")

    def test_downloader_reads_docs_workouts_json(self) -> None:
        self.assertEqual(download_images.SOURCE_JSON_PATH, ROOT / "docs" / "workouts.json")


if __name__ == "__main__":
    unittest.main()
