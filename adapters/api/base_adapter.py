from abc import ABC, abstractmethod
from typing import Optional

class BaseApiAdapter(ABC):
    @abstractmethod
    async def post(self, channel_id: str, text: str, media_path: Optional[str] = None) -> str:
        pass

    async def health_check(self) -> bool:
        return True
