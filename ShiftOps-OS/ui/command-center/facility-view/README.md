# Elkhart Dock Command Center

A predictive outbound dashboard for bakery warehouse operations.

## Features
- **Predictive ETA:** Calculates load readiness based on Bakery UPH and pick sequence.
- **Dock Board:** Real-time visualization of door status and active loads.
- **Production Timeline:** 12-hour horizon showing the queue status.
- **Health Monitoring:** Automatically flags loads at risk of missing their "drop-dead" window.
- **CSV Engine:** Uses `PapaParse` to process WMS exports directly in the browser (no server required).

## How to Use
1. Open `index.html` in any modern web browser.
2. Adjust "Production Controls" (UPH, Trays/Stack) to match current shift conditions.
3. Upload CSV exports from your WMS in the "Data Command Center" section.
4. The dashboard will automatically recalculate and update every minute.

## Tech Stack
- **Frontend:** HTML5, Tailwind CSS, Chart.js.
- **Data Parsing:** PapaParse (CSV).
- **Deployment:** Single-file "Serverless" architecture. Can be run locally or hosted on any static file server.

## Future Recommendations
- **Automated Data Sync:** Use a Python script to monitor a folder for new WMS exports and automatically update a `data.json` file that this dashboard can consume.
- **TV Mode:** Add a "Fullscreen" toggle for warehouse floor displays.
