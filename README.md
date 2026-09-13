# Multi-Platform Social Distribution Bot

5-platform Playwright automation (X, Reddit, Instagram, TikTok, Threads) + content arbitrage pipeline.

## Quick Start
1. `pip install -r requirements.txt`
2. `playwright install`
3. Configure `config.yaml`
4. Run Telegram bot + FastAPI + worker

## Architecture
- Telegram bot → FastAPI /distribute → SQLite queue → platform managers
- Stealth Playwright sessions
- SFW content collectors (RedGIFs, Eporner)

Repo: https://github.com/xlide-fun/multi-platform-social-distribution