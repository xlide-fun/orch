from abc import ABC, abstractmethod
from typing import List, Dict

class BaseCollector(ABC):
    @abstractmethod
    async def fetch_trending(self, limit: int = 20) -> List[Dict]:
        pass

    @abstractmethod
    async def fetch_recent(self, limit: int = 20) -> List[Dict]:
        pass

    def filter_sfw(self, items: List[Dict]) -> List[Dict]:
        return items
