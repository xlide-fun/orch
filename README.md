# orch

5-Platform Social Distribution Bot (X · Reddit · Instagram · TikTok · Threads)

## Stack
- Playwright stealth sessions
- FastAPI `/distribute`
- SQLite job queue
- aiogram Telegram trigger
- Per-platform managers inheriting BaseManager

## Run
```bash
pip install -r requirements.txt
playwright install chromium
export TELEGRAM_BOT_TOKEN=...
python api_router.py &          # :8000
python queue_worker.py &        # consumer
python telegram_bot.py          # trigger
```

## Flow
Telegram video + caption → POST /distribute → queue → staggered post with human delays + screenshots on fail.

Sessions: `./sessions/{platform}_{handle}.json`
User data: `./user_data/...` (persistent profiles)

Selectors will break — fallbacks + screenshots included.

https://github.com/xlide-fun/orch
