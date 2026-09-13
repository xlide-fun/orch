#!/usr/bin/env python3
from content_normalizer import normalize
from orchestrator.categorizer import ContentCategorizer
from orchestrator.normalizer import ContentNormalizer
from utils.db import init_db, enqueue_job, claim_job, mark_posted, mark_failed
from utils.rate_limiter import RateLimiter
from utils.proxy import parse_proxy
from utils.selectors import first_match, X_COMPOSE
from utils.config_loader import load_config
from adapters.api.base_adapter import BaseApiAdapter
from adapters.api.telegram_adapter import TelegramAdapter
from adapters.api.bluesky_adapter import BlueskyAdapter

assert normalize("hi", "#t")["x"]
print("core imports ok")
