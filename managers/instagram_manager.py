from managers.base_manager import BaseManager
from utils.stealth import launch_stealth_context, human_delay, human_type
from utils.screenshot import capture_failure
from playwright.async_api import async_playwright
from pathlib import Path

class InstagramManager(BaseManager):
    def __init__(self, handle: str, credentials: dict = None):
        super().__init__("instagram", handle)
        self.credentials = credentials or {}

    async def is_logged_in(self) -> bool:
        if not self.page:
            return False
        try:
            await self.page.goto("https://www.instagram.com/", timeout=15000)
            return "login" not in self.page.url.lower()
        except Exception:
            return False

    async def login(self) -> bool:
        async with async_playwright() as p:
            user_dir = f"./user_data/instagram_{self.handle}"
            Path(user_dir).mkdir(parents=True, exist_ok=True)
            self.context = await launch_stealth_context(p, "instagram", user_data_dir=user_dir, headless=False)
            self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
            if await self.is_logged_in():
                await self.context.storage_state(path=self.get_session_path())
                return True
            await self.page.goto("https://www.instagram.com/accounts/login/")
            await human_delay(2, 4)
            await self.page.fill('input[name="username"]', self.credentials.get("username", ""))
            await self.page.fill('input[name="password"]', self.credentials.get("password", ""))
            await self.page.click('button[type="submit"]')
            await human_delay(4, 7)
            # Save info if prompted
            try:
                await self.page.click('button:has-text("Save Info")', timeout=3000)
            except Exception:
                pass
            if await self.is_logged_in():
                await self.context.storage_state(path=self.get_session_path())
                return True
            return False

    async def post(self, video_path: str, caption: str) -> str:
        try:
            if not self.page:
                ok = await self.login()
                if not ok:
                    raise RuntimeError("Instagram login failed")
            await self.page.goto("https://www.instagram.com/")
            await human_delay(2, 3)
            # Create button
            await self.page.click('svg[aria-label="New post"]', timeout=10000)
            await human_delay(1, 2)
            file_input = self.page.locator('input[type="file"]').first
            await file_input.set_input_files(video_path)
            await human_delay(5, 10)  # processing
            # Next / Share flow (selectors change often)
            for _ in range(3):
                try:
                    await self.page.click('div[role="button"]:has-text("Next")', timeout=3000)
                    await human_delay(1, 2)
                except Exception:
                    break
            # Caption
            try:
                await self.page.fill('textarea[aria-label="Write a caption..."]', caption)
            except Exception:
                pass
            await human_delay(1, 2)
            await self.page.click('div[role="button"]:has-text("Share")')
            await human_delay(5, 10)
            return self.page.url
        except Exception:
            if self.page:
                await capture_failure(self.page, "instagram", "post")
            raise
