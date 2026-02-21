# BellaBell

Self-hosted price monitoring with a clean web UI. Add an item URL, tell it how to find the price, choose how often to check, and get alerted (Email / Telegram) when the price moves.

> Goal: “One simple place to track stuff I care about, without 47 browser extensions and vibes-based notifications.”

---

## What it does
- ✅ Web UI to add/manage monitored items
- ✅ Scheduled checks (per-item interval)
- ✅ Detects **price changes** (increase and/or decrease)
- ✅ Alerts via:
  - Email (SMTP)
  - Telegram (Bot)
- ✅ History view (price over time, last checked, last change)
- ✅ Optional: multiple “price extraction” methods for different sites

---

## Core concept
Price monitoring is harder than it sounds because sites:
- render prices with JavaScript
- format prices differently per region
- hide values in scripts / JSON blobs
- block bots if you hammer them

So the app supports multiple extraction strategies:

### Price extraction strategies (planned)
1. **CSS Selector** (simple HTML sites)
   - Example: `.product-price`
2. **XPath** (when CSS gets annoying)
3. **Regex** (search the HTML text)
4. **JSON path** (for embedded structured data: `application/ld+json`)
5. **Headless browser mode** (Playwright) for JS-rendered pages

Each monitored item stores:
- URL
- Extraction strategy + config (selector/xpath/regex/etc)
- Currency handling (optional)
- Check interval
- Alert rules (any change / only drops / only increases / threshold)

---

## Screenshots
_(Coming soon)_

---

## Quick start (Docker Compose)
### 1) Clone and configure
```bash
git clone <your-repo-url> pricesentry
cd pricesentry
cp .env.example .env
2) Start it
docker compose up -d
3) Open the UI

Web UI: http://localhost:8080

Docker Compose (example)

This is a reference layout. You can adjust ports, volumes, and container names to match your stack.

services:
  web:
    image: ghcr.io/yourorg/pricesentry-web:latest
    environment:
      - APP_URL=http://localhost:8080
      - DATABASE_URL=postgresql://pricesentry:pricesentry@db:5432/pricesentry
      - REDIS_URL=redis://redis:6379/0
      - TZ=Pacific/Auckland
      # Email alerts
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASS=${SMTP_PASS}
      - SMTP_FROM=${SMTP_FROM}
      # Telegram alerts
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_DEFAULT_CHAT_ID=${TELEGRAM_DEFAULT_CHAT_ID}
    ports:
      - "8080:8080"
    depends_on:
      - db
      - redis

  worker:
    image: ghcr.io/yourorg/pricesentry-worker:latest
    environment:
      - DATABASE_URL=postgresql://pricesentry:pricesentry@db:5432/pricesentry
      - REDIS_URL=redis://redis:6379/0
      - TZ=Pacific/Auckland
      # same alert env vars as web
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASS=${SMTP_PASS}
      - SMTP_FROM=${SMTP_FROM}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_DEFAULT_CHAT_ID=${TELEGRAM_DEFAULT_CHAT_ID}
    depends_on:
      - db
      - redis

  scheduler:
    image: ghcr.io/yourorg/pricesentry-scheduler:latest
    environment:
      - DATABASE_URL=postgresql://pricesentry:pricesentry@db:5432/pricesentry
      - REDIS_URL=redis://redis:6379/0
      - TZ=Pacific/Auckland
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=pricesentry
      - POSTGRES_USER=pricesentry
      - POSTGRES_PASSWORD=pricesentry
    volumes:
      - pricesentry_pg:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - pricesentry_redis:/data

volumes:
  pricesentry_pg:
  pricesentry_redis:
Environment variables

Create a .env file (example below).

# Email (SMTP)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=alerts@example.com
SMTP_PASS=supersecret
SMTP_FROM="PriceSentry <alerts@example.com>"

# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCDEF_your_bot_token
TELEGRAM_DEFAULT_CHAT_ID=123456789
How alerts work

When a check runs:

Fetch page content (simple HTTP or headless browser)

Extract the price using the configured strategy

Normalize price (strip symbols, commas, whitespace, convert to decimal)

Compare to last known price

If changed, store the event + send notifications

Alert rule options (planned)

Any change (up or down)

Only drops

Only increases

Threshold (% or absolute), e.g. “alert only if price drops by 10%”

Quiet hours (don’t notify between 10pm–7am)

Digest mode (daily summary)

Roadmap
MVP

 Add item (URL + name)

 Choose extraction method (CSS selector first)

 Set check interval (e.g., 15m / 1h / 6h / daily)

 See last price + last checked + last change

 Email + Telegram alerts

 Basic auth / local login

Next

 Headless mode (Playwright) for JS-heavy stores

 Price history chart

 Multiple users / teams

 Import/export items (JSON)

 “Test extraction” button in UI (shows what price it found)

 Proxy support + user-agent rotation (optional)

 Per-site templates (“this site’s selector is usually X”)

Notes & gotchas (aka: the part where websites fight back)

Some sites block scraping or require JS rendering.

Some prices are personalized by region/account.

Don’t check too frequently. Being polite keeps you off blocklists.

Respect website Terms of Service.
