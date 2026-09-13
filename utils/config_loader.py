import os
from pathlib import Path
import yaml

def load_config(path: str = "config.yaml") -> dict:
    cfg = {}
    if Path(path).exists():
        with open(path) as f:
            cfg = yaml.safe_load(f) or {}
    # Env overrides for secrets (never commit real values)
    acc = cfg.setdefault("accounts", {})
    for platform, mapping in {
        "x": [("username", "X_USERNAME"), ("password", "X_PASSWORD"), ("handle", "X_HANDLE")],
        "instagram": [("username", "INSTAGRAM_USERNAME"), ("password", "INSTAGRAM_PASSWORD"), ("handle", "INSTAGRAM_HANDLE")],
        "reddit": [("username", "REDDIT_USERNAME"), ("password", "REDDIT_PASSWORD")],
        "tiktok": [("handle", "TIKTOK_HANDLE")],
        "threads": [("handle", "THREADS_HANDLE")],
    }.items():
        p = acc.setdefault(platform, {})
        for key, envk in mapping:
            if os.getenv(envk):
                p[key] = os.getenv(envk)
    api = cfg.setdefault("api", {})
    if os.getenv("TELEGRAM_BOT_TOKEN"):
        api["telegram_bot_token"] = os.getenv("TELEGRAM_BOT_TOKEN")
    if os.getenv("DISCORD_WEBHOOK"):
        api["discord_webhook"] = os.getenv("DISCORD_WEBHOOK")
    if os.getenv("BLUESKY_HANDLE"):
        api.setdefault("bluesky", {})["handle"] = os.getenv("BLUESKY_HANDLE")
    if os.getenv("BLUESKY_APP_PASSWORD"):
        api.setdefault("bluesky", {})["app_password"] = os.getenv("BLUESKY_APP_PASSWORD")
    if os.getenv("MASTODON_INSTANCE"):
        api.setdefault("mastodon", {})["instance"] = os.getenv("MASTODON_INSTANCE")
    if os.getenv("MASTODON_TOKEN"):
        api.setdefault("mastodon", {})["access_token"] = os.getenv("MASTODON_TOKEN")
    return cfg
