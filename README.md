# Second Hand Map

A personal app that auto-collects second hand stores in a city via Google Places API and shows them on an interactive, mobile-friendly map. Hosted free on GitHub Pages.

## Stack

- **Scraper**: Python 3 + `requests` → writes `locations.json`
- **Scheduler**: GitHub Actions (weekly cron, Mondays 07:00 UTC)
- **Frontend**: HTML + Leaflet.js + OpenStreetMap tiles
- **Hosting**: GitHub Pages

## Setup

### 1. Get a Google Places API key

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project, enable **Places API** under *APIs & Services*
3. Generate an API key under *Credentials*, restrict it to *Places API*
4. Enable billing (free tier: $200/month — well above this project's usage)

### 2. Configure the repo

1. Edit `config.json` to set your city, map center, and search queries.
2. Add your API key as a repo secret: *Settings → Secrets and variables → Actions → New repository secret*, name `GOOGLE_API_KEY`.
3. Trigger the workflow manually once: *Actions → Scrape locations → Run workflow*. This generates `locations.json`.
4. Enable GitHub Pages: *Settings → Pages → Source: branch `main`, folder `/ (root)`*.

### 3. Local testing

```bash
pip install -r requirements.txt
export GOOGLE_API_KEY=your-key-here
python scraper.py
```

To preview the frontend locally:

```bash
python -m http.server 8000
# open http://localhost:8000
```

## Files

| File | Purpose |
|------|---------|
| `scraper.py` | Collects locations from Google Places API |
| `config.json` | City, map center, search queries, language |
| `locations.json` | Generated data, read by the frontend |
| `index.html` | Map UI (Leaflet, vanilla JS, mobile-first) |
| `.github/workflows/scrape.yml` | Weekly auto-scrape + commit |
| `requirements.txt` | Python deps |

## Cost

~$1.10 per scrape × 4 scrapes/month = ~$4.40, fully covered by Google's $200/month free tier. Set a $5 budget alert in Google Cloud Console as a safety net.
