# BellaBell

Self-hosted price monitoring with a clean web UI. Add an item URL, tell it how to find the price, choose how often to check, and get alerted when the price moves.

## Current build status

This repository now includes an **initial backend API scaffold** for the MVP:

- FastAPI service with SQLite persistence
- Item CRUD basics (`create`, `list`)
- Manual check endpoint to fetch + extract + store price observation
- Extraction preview endpoint for CSS selector validation
- Basic history endpoint for an item

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API docs.

## Implemented API endpoints

- `GET /health`
- `POST /items`
- `GET /items`
- `GET /items/{item_id}/history`
- `POST /items/{item_id}/check`
- `POST /extract/preview`

## Next steps

- Add authentication + user ownership on items
- Add scheduler/worker split for automated checks
- Add notification channels (SMTP + Telegram)
- Add UI for dashboard, item creation, and history graphs
