def normalize(caption: str, hashtags: str = "") -> dict:
    full = f"{caption} {hashtags}".strip()
    return {
        "x": full[:280],
        "reddit": {
            "title": (caption.split(".")[0] or caption)[:300],
            "body": full,
        },
        "instagram": full[:2200],
        "tiktok": full[:2200],
        "threads": full[:500],
    }
