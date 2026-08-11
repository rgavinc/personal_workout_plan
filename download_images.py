from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parent
SOURCE_JSON_PATH = ROOT / "workouts.json"
PUBLISHED_JSON_PATH = ROOT / "docs" / "workouts.json"
IMAGE_DIR = ROOT / "docs" / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def normalize_name(title: str) -> str:
    title = title.lower().strip()
    title = re.sub(r"[^a-z0-9]+", "-", title)
    title = re.sub(r"-+", "-", title).strip("-")
    return title or "workout"


def download_image(url: str, out_path: Path) -> bool:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Referer": "https://workoutlabs.com/",
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "image/" in content_type or response.text.lstrip().startswith("<svg"):
            out_path.write_bytes(response.content)
            return True
    except Exception:
        return False
    return False


def main() -> None:
    if not SOURCE_JSON_PATH.exists():
        raise FileNotFoundError(f"Missing source JSON file: {SOURCE_JSON_PATH}")

    workouts: list[dict[str, Any]] = json.loads(SOURCE_JSON_PATH.read_text(encoding="utf-8"))

    for index, workout in enumerate(workouts, start=1):
        image_url = workout.get("main_image") or ""
        if not image_url or image_url.startswith("./images/"):
            continue

        title = workout.get("title") or f"workout-{index}"
        filename = f"{normalize_name(title)}.svg"
        output_path = IMAGE_DIR / filename

        if output_path.exists():
            workout["main_image"] = f"./images/{filename}"
            continue

        downloaded = download_image(image_url, output_path)
        if downloaded:
            workout["main_image"] = f"./images/{filename}"
            print(f"[{index}/{len(workouts)}] Downloaded: {filename}")
        else:
            print(f"[{index}/{len(workouts)}] Failed: {image_url}")

    PUBLISHED_JSON_PATH.write_text(json.dumps(workouts, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Finished. Files saved in {IMAGE_DIR}")


if __name__ == "__main__":
    main()
