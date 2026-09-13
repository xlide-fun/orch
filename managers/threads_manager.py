from managers.base_manager import BaseManager
from utils.stealth import launch_stealth_context, human_delay
from utils.screenshot import capture_failure
from playwright.async_api import async_playwright
from pathlib import Path

class ThreadsManager(BaseManager):
    def __init__(self, handle: str, credentials: dict = None):
        super().__init__("threads", handle)
        self.credentials = credentials or {}

    async def is_logged_in(self) -> bool:
        if not self.page:
            return False
        try:
            await self.page.goto("https://www.threads.net/", timeout=15000)
            return "login" not in self.page.url.lower()
        except Exception:
            return False

    async def login(self) -> bool:
        async with async_playwright() as p:
            user_dir = f"./user_data/threads_{self.handle}"
            Path(user_dir).mkdir(parents=True, exist_ok=True)
            self.context = await launch_stealth_context(p, "threads", user_data_dir=user_dir, headless=False)
            self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
            if await self.is_logged_in():
                await self.context.storage_state(path=self.get_session_path())
                return True
            await self.page.goto("https://www.threads.net/login")
            await human_delay(2, 4)
            # Often redirects through Instagram auth; rely on shared session
            if await self.is_logged_in():
                await self.context.storage_state(path=self.get_session_path())
                return True
            return False

    async def post(self, video_path: str, caption: str) -> str:
        try:
            if not self.page:
                ok = await self.login()
                if not ok:
                    raise RuntimeError("Threads login failed")
            await self.page.goto("https://www.threads.net/")
            await human_delay(2, 3)
            await self.page.click('div[role="button"]:has-text("New thread")')
            await human_delay(1, 2)
            await self.page.fill('div[role="textbox"]', caption)
            if video_path:
                file_input = self.page.locator('input[type="file"]').first
                await file_input.set_input_files(video_path)
                await human_delay(4, 8)
            await self.page.click('div[role="button"]:has-text("Post")')
            await human_delay(3, 6)
            return self.page.url
        except Exception:
            if self.page:
                await capture_failure(self.page, "threads", "post")
            raise
