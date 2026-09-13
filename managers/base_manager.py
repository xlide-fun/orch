from abc import ABC, abstractmethod
from pathlib import Path

class BaseManager(ABC):
    def __init__(self, platform: str, handle: str, session_dir: str = "./sessions"):
        self.platform = platform
        self.handle = handle
        self.session_path = Path(session_dir) / f"{platform}_{handle}.json"
        self.context = None
        self.page = None

    def get_session_path(self) -> str:
        return str(self.session_path)

    @abstractmethod
    async def login(self) -> bool:
        pass

    @abstractmethod
    async def is_logged_in(self) -> bool:
        pass

    @abstractmethod
    async def post(self, video_path: str, caption: str) -> str:
        """Returns post_url or raises"""
        pass

    async def close(self):
        if self.context:
            await self.context.close()
