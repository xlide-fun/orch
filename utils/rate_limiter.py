import time
from collections import defaultdict

class TokenBucket:
    def __init__(self, rate: float, capacity: float):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last = time.monotonic()

    def consume(self, n=1) -> bool:
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= n:
            self.tokens -= n
            return True
        return False

class RateLimiter:
    def __init__(self):
        self.buckets = defaultdict(lambda: TokenBucket(1, 5))

    def allow(self, key: str) -> bool:
        return self.buckets[key].consume()
