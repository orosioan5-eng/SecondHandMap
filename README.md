# Second Hand Map

Interactive map of second hand stores in Bucharest, auto-collected from Google Maps and displayed with photos, ratings, hours, and directions.

## What it does

- Scrapes second hand stores in Bucharest via Google Places API
- Filters out non-relevant results (barbers, cafes, pawn shops, places outside the city)
- Downloads up to 3 photos per location
- Saves everything as static JSON + images in the repo
- Renders an interactive Leaflet map with mobile-first UI

## Stack

| Part | Tech |
|------|------|
| Data collection | Python + `requests`, Google Places API |
| Storage | Static `locations.json` + `photos/` in repo |
| Frontend | HTML + Leaflet.js + OpenStreetMap tiles |
| Hosting | GitHub Pages |
| Scheduling | GitHub Actions (manual trigger) |

## Live site

https://orosioan5-eng.github.io/SecondHandMap/

## Files

| File | Purpose |
|------|---------|
| `scraper.py` | Pulls data from Google Places, filters, downloads photos |
| `config.json` | City center, search queries, sector tiles, filter thresholds |
| `locations.json` | Generated dataset read by the frontend |
| `photos/` | Generated location photos |
| `index.html` | Map UI (vanilla JS, Leaflet, mobile-first) |
| `.github/workflows/scrape.yml` | Manual-trigger workflow that runs the scraper |
