from typing import Dict, List

CATEGORY_TAGS = {
    "fitness": ["workout", "gym", "yoga", "flexibility", "exercise", "fitness"],
    "sports": ["sports", "athlete", "training", "performance"],
    "dance": ["dance", "choreography", "hiphop", "ballet", "contemporary"],
    "art": ["art", "painting", "sculpture", "creative", "drawing"],
    "adventure": ["adventure", "nature", "exploration", "outdoors", "travel"],
}

class ContentCategorizer:
    def __init__(self):
        self.tag_map = {}
        for cat, tags in CATEGORY_TAGS.items():
            for t in tags:
                self.tag_map[t.lower()] = cat

    def categorize(self, content: Dict) -> str:
        tags = [t.lower() for t in content.get("tags", [])]
        scores = {}
        for t in tags:
            cat = self.tag_map.get(t)
            if cat:
                scores[cat] = scores.get(cat, 0) + 1
        if not scores:
            return "fitness"  # default
        return max(scores, key=scores.get)
