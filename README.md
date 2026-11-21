# Marketing Insights — Custom Flask Dashboard

A responsive marketing dashboard recreation for a technical assessment, using **synthetic marketing data**. Developed in Python (pandas/NumPy), Flask, HTML, CSS, JavaScript and Chart.js.

## Run locally (Visual Studio Community or PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python generate_data.py
python app.py
```

Visit http://127.0.0.1:5000

## Features

- Eight KPI cards with sparklines and true calendar-aligned year-over-year comparisons
- Filters: date range, channel, data source and campaign
- Channel, data-source and campaign performance tables
- Channel impression time-series line chart
- Chart datasets and table metrics reflect filters
- Deterministic synthetic data, clearly identified as such
- Responsive UI

## KPI definitions

- **CTR** = clicks / impressions × 100
- **CPM** = paid spend / all impressions × 1000 (organic impressions included; this mixed metric is for screenshot recreation only; for professional paid CPM filter to paid channels)
- **CPC** = paid spend / all clicks (same mixed-channel caveat)
- **Conversion Rate** = conversions / clicks × 100
- **YoY %** = (current / previous-calendar-year − 1) × 100; undefined previous baselines appear as em dash
- Organic traffic has spend = 0; estimated revenue is synthetic for illustration.

## Important interpretation

The source reference screenshot contains several metrics that cannot all be reproduced consistently from a standard marketing fact table; this project prioritizes internally consistent metric calculations rather than copying those numbers exactly. In particular, CTR is computed from clicks and impressions rather than assigned directly as a dashboard output.

## Deployment with Render

1. Push this folder's contents to a public GitHub repository.
2. In Render create a **Web Service** and connect your repo.
3. Runtime: **Python**. Build command: `pip install -r requirements.txt && python generate_data.py`.
4. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`.
5. Use the resulting HTTPS service URL in your submission. Hosting plan availability, pricing and spin-down conditions may change.

## Technical notes

For larger datasets, replace the CSV with a database and persist pre-aggregated data. The current generator creates ~26k rows (36 daily campaign/source combinations × 730 days). Flask loads CSV once on startup. For production, add caching, pagination, monitoring, tests and security hardening.

## Assessment attribution

Independently created interpretation of the screenshot from [Marketing Analytics Assignments / TCS Assignment](https://github.com/ej29-r3d/Marketing-Analytics-Assignments/tree/main/tcs-assignment). No affiliation with Improvado. All data are simulated.
