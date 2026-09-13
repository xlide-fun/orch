from managers.base_manager import BaseManager
from utils.stealth import launch_stealth_context, human_delay, human_type
from utils.screenshot import capture_failure
from playwright.async_api import async_playwright
import json
from pathlib import Path

class XManager(BaseManager):
    def __init__(self, handle: str, credentials: dict = None):
        super().__init__("x", handle)
        self.credentials = credentials or {}

    async def is_logged_in(self) -> bool:
        if not self.page:
            return False
        try:
            await self.page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=15000)
            return "login" not in self.page.url.lower()
        except Exception:
            return False

    async def login(self) -> bool:
        async with async_playwright() as p:
            user_dir = f"./user_data/x_{self.handle}"
            Path(user_dir).mkdir(parents=True, exist_ok=True)
            self.context = await launch_stealth_context(p, "x", user_data_dir=user_dir, headless=False)
            self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
            if await self.is_logged_in():
                await self.context.storage_state(path=self.get_session_path())
                return True
            await self.page.goto("https://x.com/i/flow/login")
            await human_delay(2, 4)
            # Username
            await self.page.fill('input[autocomplete="username"]', self.credentials.get("username", ""))
            await self.page.keyboard.press("Enter")
            await human_delay(1, 3)
            # Password
            await self.page.fill('input[name="password"]', self.credentials.get("password", ""))
            await self.page.keyboard.press("Enter")
            await human_delay(3, 6)
            if await self.is_logged_in():
                await self.context.storage_state(path=self.get_session_path())
                return True
            return False

    async def post(self, video_path: str, caption: str) -> str:
        try:
            if not self.page:
                ok = await self.login()
                if not ok:
                    raise RuntimeError("X login failed")
            await self.page.goto("https://x.com/compose/post")
            await human_delay(2, 4)
            # Media upload
            file_input = self.page.locator('input[type="file"]').first
            await file_input.set_input_files(video_path)
            await human_delay(3, 6)
            # Caption
            editor = self.page.locator('[data-testid="tweetTextarea_0"]')
            await editor.click()
            await human_type(self.page, '[data-testid="tweetTextarea_0"]', caption)
            await human_delay(1, 2)
            # Post
            await self.page.locator('[data-testid="tweetButton"]').click()
            await human_delay(4, 8)
            # Extract URL (best effort)
            url = self.page.url
            if "/status/" in url:
                return url
            return f"https://x.com/{self.handle}/status/unknown"
        except Exception as e:
            if self.page:
                await capture_failure(self.page, "x", "post")
            raise
