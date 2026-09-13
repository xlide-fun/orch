# orch

Cross-platform content distribution + arbitrage pipeline.

## Browser tier (Playwright)
X · Reddit · Instagram · TikTok · Threads

## API tier (stubs ready)
Telegram · Discord · Mastodon · Bluesky · LinkedIn · Tumblr

## Pipeline
1. Collectors (RedGIFs / Eporner) → SFW filter
2. Categorizer (fitness/sports/dance/art/adventure)
3. Normalizer + conversion CTAs
4. Queue → browser or API workers

## Run
```bash
pip install -r requirements.txt && playwright install chromium
export TELEGRAM_BOT_TOKEN=... REDGIFS_API_KEY=... EPORNER_API_KEY=...
python api_router.py &
python queue_worker.py &
python orchestrator/main.py &
python telegram_bot.py
```

Sessions persist in `./sessions` and `./user_data`.
Screenshots on failure → `./screenshots`.

https://github.com/xlide-fun/orch
