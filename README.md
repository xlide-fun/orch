# orch

Cross-platform content distribution + arbitrage pipeline.

## Layers
1. **Collectors** – RedGIFs / Eporner (SFW filter)
2. **Orchestrator** – categorize → normalize → enqueue
3. **Browser tier** – Playwright managers (X, Reddit, IG, TikTok, Threads)
4. **API tier** – Telegram, Discord, Mastodon, Bluesky, LinkedIn, Tumblr
5. **Trigger** – Telegram bot → FastAPI `/distribute` → SQLite queue → workers

## Quick start
```bash
pip install -r requirements.txt && playwright install chromium
cp config.yaml.example config.yaml   # edit credentials
export TELEGRAM_BOT_TOKEN=... REDGIFS_API_KEY=... EPORNER_API_KEY=...
python api_router.py &
python queue_worker.py &
python telegram_bot.py
# optional: python -m orchestrator.main   # content cycle
```

## Structure
```
managers/          # Playwright platform managers
adapters/api/      # Official API adapters
collector/         # Content sources
orchestrator/      # Pipeline
utils/             # stealth, db, proxy, screenshot
```

Sessions persist in `./sessions/`. Screenshots on failure in `./screenshots/`.

https://github.com/xlide-fun/orch
