from managers.base_manager import BaseManager
from utils.stealth import launch_stealth_context, human_delay
from utils.screenshot import capture_failure
from playwright.async_api import async_playwright
from pathlib import Path

class TikTokManager(BaseManager):
    def __init__(self, handle: str, credentials: dict = None):
        super().__init__("tiktok", handle)
        self.credentials = credentials or {}
        self._pw = None

    async def _ensure_context(self):
        if self.context:
            return
        self._pw = await async_playwright().start()
        user_dir = f"./user_data/tiktok_{self.handle}"
        Path(user_dir).mkdir(parents=True, exist_ok=True)
        self.context = await launch_stealth_context(self._pw, "tiktok", user_data_dir=user_dir, headless=False)
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()

    async def is_logged_in(self) -> bool:
        await self._ensure_context()
        try:
            await self.page.goto("https://www.tiktok.com/", timeout=20000)
            await human_delay(1, 2)
            return "login" not in self.page.url.lower()
        except Exception:
            return False

    async def login(self) -> bool:
        await self._ensure_context()
        if await self.is_logged_in():
            await self.context.storage_state(path=self.get_session_path())
            return True
        # Prefer pre-warmed persistent profile / storage_state
        await self.page.goto("https://www.tiktok.com/login")
        await human_delay(3, 6)
        if await self.is_logged_in():
            Path(self.get_session_path()).parent.mkdir(parents=True, exist_ok=True)
            await self.context.storage_state(path=self.get_session_path())
            return True
        return False

    async def post(self, video_path: str, caption: str) -> str:
        try:
            if not await self.is_logged_in():
                if not await self.login():
                    raise RuntimeError("TikTok login failed — warm account first")
            await self.page.goto("https://www.tiktok.com/upload", wait_until="domcontentloaded")
            await human_delay(3, 6)
            file_input = self.page.locator('input[type="file"]').first
            await file_input.set_input_files(video_path)
            await human_delay(10, 20)
            try:
                await self.page.fill('div[contenteditable="true"]', caption[:2200])
            except Exception:
                pass
            await human_delay(1, 2)
            await self.page.click('button:has-text("Post")')
            await human_delay(6, 12)
            return self.page.url
        except Exception:
            if self.page:
                await capture_failure(self.page, "tiktok", "post")
            raise

    async def close(self):
        if self.context:
            try:
                await self.context.storage_state(path=self.get_session_path())
            except Exception:
                pass
            await self.context.close()
        if self._pw:
            await self._pw.stop()
        self.context = self.page = None
