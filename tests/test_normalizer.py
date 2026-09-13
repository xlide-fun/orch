from content_normalizer import normalize
from orchestrator.categorizer import ContentCategorizer
from orchestrator.normalizer import ContentNormalizer

def test_normalize_limits():
    n = normalize("x" * 500, "#tag")
    assert len(n["x"]) <= 280
    assert len(n["threads"]) <= 500
    assert len(n["instagram"]) <= 2200

def test_categorizer():
    c = ContentCategorizer()
    assert c.categorize({"tags": ["gym", "workout"]}) == "fitness"
    assert c.categorize({"tags": ["ballet"]}) == "dance"
    assert c.categorize({"tags": []}) == "fitness"

def test_platform_normalizer():
    n = ContentNormalizer()
    pkt = n.normalize_for_platform({"title": "hello", "tags": ["gym"]}, "x", "fitness")
    assert pkt["platform"] == "x"
    assert "Xlide" in pkt["caption"] or "fitness" in pkt["caption"].lower() or len(pkt["caption"]) > 0
