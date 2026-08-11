from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DEFAULT_INPUT = Path("workout_links.txt")
DEFAULT_OUTPUT = Path("workouts.json")


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def read_urls(input_path: Path) -> list[str]:
    text = input_path.read_text(encoding="utf-8")
    urls = re.findall(r"https?://[^\s'\"\],]+", text)
    return urls


def create_session() -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_page(url: str, session: requests.Session) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue

    raise RuntimeError(f"Failed to fetch {url}: {last_error}") from last_error


def extract_workout(url: str, session: requests.Session) -> dict[str, Any]:
    response_text = fetch_page(url, session)
    soup = BeautifulSoup(response_text, "html.parser")

    title_tag = soup.select_one(".reset.ffGothamBlack.exTtl")
    title = normalize_text(title_tag.get_text(" ", strip=True) if title_tag else None) or "No title found"

    main_image_tag = soup.select_one(".imgWrp.exWrp.hasAnim img")
    if main_image_tag:
        main_image_url = (
            main_image_tag.get("data-url_male")
            or main_image_tag.get("src")
            or main_image_tag.get("data-url_female")
            or "No main image found"
        )
    else:
        main_image_url = "No main image found"

    primary_muscles: list[str] = []
    secondary_muscles: list[str] = []
    equipment: list[str] = []

    for block in soup.select(".left.metaWrp .metaBlock"):
        key_tag = block.select_one(".metaKey")
        key = normalize_text(key_tag.get_text(" ", strip=True) if key_tag else None)
        if not key:
            continue

        values = [normalize_text(a.get_text(" ", strip=True)) for a in block.select(".metaVal a") if normalize_text(a.get_text(" ", strip=True))]
        if not values:
            continue

        key_lower = key.lower()
        if "equipment" in key_lower:
            equipment.extend(values)
        elif "primary" in key_lower:
            primary_muscles.extend(values)
        elif "secondary" in key_lower:
            secondary_muscles.extend(values)

    description_block = soup.select_one(".right.ffGothamBook.cntWrp")
    description = normalize_text(description_block.get_text(" ", strip=True)) if description_block else "No description found"

    return {
        "title": title,
        "main_image": main_image_url,
        "equipment_required": equipment,
        "muscles_worked_primary": primary_muscles,
        "muscles_worked_secondary": secondary_muscles,
        "description": description,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape workout pages from a URL list and save them as JSON.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to the file containing workout URLs.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to save the JSON output.")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit on the number of workout URLs to scrape.")
    args = parser.parse_args()

    urls = read_urls(args.input)
    if args.limit > 0:
        urls = urls[: args.limit]

    workouts: list[dict[str, Any]] = []
    if args.output.exists():
        try:
            existing = json.loads(args.output.read_text(encoding="utf-8"))
            if isinstance(existing, list):
                workouts = existing
        except Exception:
            workouts = []

    session = create_session()
    for index, url in enumerate(urls, start=1):
        try:
            workout = extract_workout(url, session)
            workouts.append(workout)
            print(f"[{index}/{len(urls)}] Saved: {workout['title']}")
        except Exception as exc:
            print(f"[{index}/{len(urls)}] Failed: {url} -> {exc}")

        if index % 25 == 0 or index == len(urls):
            args.output.write_text(json.dumps(workouts, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"Saved progress: {len(workouts)} records")

    args.output.write_text(json.dumps(workouts, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {len(workouts)} records to {args.output}")


if __name__ == "__main__":
    main()
