# Backtest to Live Slippage Detector

This project reconciles live trading data against backtest strategy data to detect leakage, mismatches, and execution gaps.

## What it does

- loads backtest trades and live trades,
- normalizes both into a common format,
- matches trades by symbol, side, and price tolerance,
- summarizes missing, extra, and matched trades,
- exposes the workflow through a FastAPI backend and a lightweight demo UI.

## Demo mode

The project defaults to a demo mode so it can run without a real MongoDB connection. In demo mode it uses local JSON files under the data/demo folder instead of production collections.

To run locally:

1. Open a terminal in the project folder.
2. Activate the virtual environment.
3. Start the app:

   python -m uvicorn main:app --host 127.0.0.1 --port 9000

4. Open the browser at:

   http://127.0.0.1:9000/

## Production mode

If you want the original MongoDB-backed workflow, set the environment variables in a .env file or use the sample values in .env.example and set APP_MODE=production.

## API example

POST /api/leak

Example payload:

{
"live_algo": "MA_CROSS",
"backtest_algo": "MA_CROSS",
"start_date": "2025-01-03",
"end_date": "2025-01-05",
"price_tolerance": 2.5,
"clientId": "C_101",
"check_qnt": false
}

## Project structure

- main.py: FastAPI app entry point
- dependency.py: selects demo or production repositories
- repositeries: data access layer
- services: normalization, matching, and mismatch detection
- data/demo: mock trade files for demo mode
- templates/demo.html: simple portfolio-ready UI

## Notes

This project is intentionally designed so it can be demonstrated on a CV or portfolio without exposing private market data or production credentials.
