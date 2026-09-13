from content_normalizer import normalize as base_normalize

CONVERSION = {
    "fitness": "Transform your body. Find fitness partners on Xlide.fun",
    "sports": "Play sports with real people. Join Xlide.fun",
    "dance": "Find your dance partner on Xlide.fun",
    "art": "Create art together. Connect on Xlide.fun",
    "adventure": "Find adventure partners on Xlide.fun",
}

class ContentNormalizer:
    def normalize_for_platform(self, content: dict, platform: str, category: str) -> dict:
        base = content.get("title") or content.get("caption") or ""
        tags = " ".join(f"#{t}" for t in content.get("tags", [])[:5])
        conv = CONVERSION.get(category, "Find your tribe on Xlide.fun")
        full = f"{base}\n{tags}\n{conv}".strip()
        norms = base_normalize(full)
        text = norms.get(platform, full)
        if isinstance(text, dict):  # reddit
            text["body"] = f"{text.get('body', '')}\n{conv}"
            return {"title": text["title"], "body": text["body"], "media_url": content.get("url")}
        return {"caption": text, "media_url": content.get("url") or content.get("embed_url")}
