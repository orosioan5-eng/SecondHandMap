"""Second Hand Map - data collector.

Queries Google Places API for second hand stores in a configurable city,
fetches detailed info for each place, and writes a static locations.json
that the frontend reads.

Designed to run weekly on GitHub Actions. Reads GOOGLE_API_KEY from env.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
OUTPUT_PATH = ROOT / "locations.json"

TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

DETAILS_FIELDS = ",".join([
    "place_id",
    "name",
    "formatted_address",
    "geometry/location",
    "rating",
    "user_ratings_total",
    "formatted_phone_number",
    "international_phone_number",
    "website",
    "url",
    "opening_hours/weekday_text",
    "opening_hours/open_now",
    "business_status",
    "types",
])


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_api_key() -> str:
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        print("ERROR: GOOGLE_API_KEY not set in environment.", file=sys.stderr)
        sys.exit(1)
    return key


def text_search(
    query: str,
    language: str,
    api_key: str,
    center: dict | None = None,
    radius: int | None = None,
) -> list[dict]:
    """Run a Text Search and walk all next_page_token pages (max 60 results)."""
    results: list[dict] = []
    params: dict = {"query": query, "language": language, "key": api_key}
    if center and radius:
        params["location"] = f"{center['lat']},{center['lng']}"
        params["radius"] = str(radius)
    while True:
        resp = requests.get(TEXT_SEARCH_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status")
        if status not in ("OK", "ZERO_RESULTS"):
            print(f"Text Search status={status} error={data.get('error_message')}", file=sys.stderr)
            break
        results.extend(data.get("results", []))
        token = data.get("next_page_token")
        if not token or len(results) >= 60:
            break
        # Google requires a short delay before next_page_token becomes valid.
        time.sleep(2)
        params = {"pagetoken": token, "key": api_key}
    return results


def fetch_details(place_id: str, language: str, api_key: str) -> dict | None:
    params = {
        "place_id": place_id,
        "language": language,
        "fields": DETAILS_FIELDS,
        "key": api_key,
    }
    resp = requests.get(DETAILS_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "OK":
        print(
            f"Details status={data.get('status')} place_id={place_id} error={data.get('error_message')}",
            file=sys.stderr,
        )
        return None
    return data.get("result")


def normalize(detail: dict) -> dict | None:
    geometry = detail.get("geometry") or {}
    location = geometry.get("location") or {}
    lat = location.get("lat")
    lng = location.get("lng")
    if lat is None or lng is None:
        return None
    opening = detail.get("opening_hours") or {}
    return {
        "place_id": detail.get("place_id"),
        "name": detail.get("name"),
        "address": detail.get("formatted_address"),
        "lat": lat,
        "lng": lng,
        "rating": detail.get("rating"),
        "total_ratings": detail.get("user_ratings_total"),
        "phone": detail.get("formatted_phone_number") or detail.get("international_phone_number"),
        "website": detail.get("website"),
        "google_maps_url": detail.get("url"),
        "hours": opening.get("weekday_text") or [],
        "open_now": opening.get("open_now"),
        "business_status": detail.get("business_status"),
        "types": detail.get("types") or [],
    }


def main() -> int:
    config = load_config()
    queries = config.get("queries") or [config.get("query", "second hand Bucuresti")]
    language = config.get("language", "ro")
    min_rating = config.get("min_rating")
    center = config.get("center")
    radius = config.get("radius", 15000)

    api_key = get_api_key()

    seen: dict[str, dict] = {}
    for query in queries:
        print(f"Searching: {query}")
        for hit in text_search(query, language, api_key, center, radius):
            pid = hit.get("place_id")
            if not pid or pid in seen:
                continue
            detail = fetch_details(pid, language, api_key)
            if not detail:
                continue
            entry = normalize(detail)
            if not entry:
                continue
            if min_rating is not None and (entry.get("rating") or 0) < min_rating:
                continue
            if entry.get("business_status") == "CLOSED_PERMANENTLY":
                continue
            seen[pid] = entry

    locations = sorted(seen.values(), key=lambda x: (-(x.get("rating") or 0), x.get("name") or ""))

    payload = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "city": config.get("city"),
        "center": config.get("center"),
        "count": len(locations),
        "locations": locations,
    }

    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved {len(locations)} locations to {OUTPUT_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
