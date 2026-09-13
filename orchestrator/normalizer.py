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
        caption = content.get("caption") or content.get("title") or ""
        tags = " ".join(f"#{t}" for t in content.get("tags", [])[:5])
        conv = CONVERSION.get(category, "Find your tribe on Xlide.fun")
        full = f"{caption}\n{tags}\n{conv}".strip()
        norms = base_normalize(full)
        return {
            "platform": platform,
            "category": category,
            "caption": norms.get(platform) if isinstance(norms.get(platform), str) else full[:500],
            "media_url": content.get("url") or content.get("embed_url"),
            "media_path": content.get("media_path"),
        }
