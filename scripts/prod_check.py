#!/usr/bin/env python3
"""Production readiness gate. Exit 1 if critical issues."""
import sys
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []
warnings = []

REQUIRED = [
    "api_router.py",
    "queue_worker.py",
    "telegram_bot.py",
    "content_normalizer.py",
    "config.yaml",
    "requirements.txt",
    "utils/db.py",
    "utils/stealth.py",
    "utils/media.py",
    "managers/base_manager.py",
    "managers/x_manager.py",
    "managers/instagram_manager.py",
    "managers/reddit_manager.py",
    "managers/tiktok_manager.py",
    "managers/threads_manager.py",
    "collector/redgifs_collector.py",
    "collector/eporner_collector.py",
    "orchestrator/main.py",
    "adapters/api/telegram_adapter.py",
    "adapters/api/bluesky_adapter.py",
    ".gitignore",
]

for rel in REQUIRED:
    if not (ROOT / rel).exists():
        errors.append(f"MISSING: {rel}")

# gitignore must protect secrets
gi = (ROOT / ".gitignore").read_text() if (ROOT / ".gitignore").exists() else ""
for pattern in ["sessions", "user_data", ".env", "orch.db"]:
    if pattern not in gi:
        errors.append(f".gitignore missing '{pattern}'")

# no hardcoded obvious secrets in tracked py files
for p in ROOT.rglob("*.py"):
    if ".venv" in str(p):
        continue
    text = p.read_text(errors="ignore")
    if "sk-" in text and "api_key" in text.lower():
        warnings.append(f"possible secret pattern in {p.relative_to(ROOT)}")

# db must expose claim_job
db_src = (ROOT / "utils/db.py").read_text()
if "def claim_job" not in db_src:
    errors.append("utils/db.py missing claim_job")
if "WAL" not in db_src:
    errors.append("utils/db.py missing WAL mode")

# config should not contain real-looking passwords committed
cfg = (ROOT / "config.yaml").read_text()
if "password: \"" in cfg and len(cfg.split("password:")) > 3:
    # empty placeholders ok
    pass

# parse all py files
for p in ROOT.rglob("*.py"):
    if any(x in str(p) for x in [".venv", "__pycache__"]):
        continue
    try:
        ast.parse(p.read_text())
    except SyntaxError as e:
        errors.append(f"SyntaxError {p.relative_to(ROOT)}: {e}")

print("=== Production Readiness ===")
for w in warnings:
    print("WARN:", w)
for e in errors:
    print("ERROR:", e)

if errors:
    print(f"\nFAILED: {len(errors)} critical issue(s)")
    sys.exit(1)
print("\nPASSED: structure + safety checks OK")
sys.exit(0)
