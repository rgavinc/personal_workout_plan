# Workout Scraper Project

This workspace contains a small Python scraper that reads workout URLs from `workout_links.txt` and exports structured workout data to `workouts.json`.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run the scraper

```powershell
python scrape_workouts_to_json.py
```

## Output

The scraper writes a JSON array to `workouts.json` with fields including:

- `title`
- `main_image`
- `equipment_required`
- `muscles_worked_primary`
- `muscles_worked_secondary`
- `description`
