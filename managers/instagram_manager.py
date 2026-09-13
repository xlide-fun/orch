from managers.base_manager import BaseManager
from utils.stealth import launch_stealth_context, human_delay
from utils.screenshot import capture_failure
from utils.selectors import first_match, click_first, fill_first, IG_CAPTION, IG_SHARE
from playwright.async_api import async_playwright
from pathlib import Path

class InstagramManager(BaseManager):
    def __init__(self, handle: str, credentials: dict = None):
        super().__init__("instagram", handle)
        self.credentials = credentials or {}
        self._pw = None

    async def _ensure_context(self):
        if self.context:
            return
        self._pw = await async_playwright().start()
        user_dir = f"./user_data/instagram_{self.handle}"
        Path(user_dir).mkdir(parents=True, exist_ok=True)
        self.context = await launch_stealth_context(self._pw, "instagram", user_data_dir=user_dir, headless=False)
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()

    async def is_logged_in(self) -> bool:
        await self._ensure_context()
        try:
            await self.page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=20000)
            await human_delay(1, 2)
            return "login" not in self.page.url.lower() and "/accounts/login" not in self.page.url
        except Exception:
            return False

    async def login(self) -> bool:
        await self._ensure_context()
        if await self.is_logged_in():
            await self.context.storage_state(path=self.get_session_path())
            return True
        await self.page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")
        await human_delay(2, 4)
        user = self.credentials.get("username") or ""
        pw = self.credentials.get("password") or ""
        u = await first_match(self.page, ['input[name="username"]', 'input[aria-label*="username" i]', 'input[type="text"]'])
        p = await first_match(self.page, ['input[name="password"]', 'input[type="password"]'])
        if not u or not p:
            raise RuntimeError("IG login fields missing")
        await u.fill(user)
        await p.fill(pw)
        await click_first(self.page, ['button[type="submit"]', 'button:has-text("Log in")'])
        await human_delay(4, 8)
        for sel in ['button:has-text("Save Info")', 'button:has-text("Not Now")']:
            try:
                await self.page.click(sel, timeout=2500)
                await human_delay(1, 2)
            except Exception:
                pass
        if await self.is_logged_in():
            Path(self.get_session_path()).parent.mkdir(parents=True, exist_ok=True)
            await self.context.storage_state(path=self.get_session_path())
            return True
        return False

    async def post(self, video_path: str, caption: str) -> str:
        try:
            if not await self.is_logged_in():
                if not await self.login():
                    raise RuntimeError("Instagram login failed")
            await self.page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            await human_delay(2, 3)
            if not await click_first(self.page, [
                'svg[aria-label="New post"]',
                'svg[aria-label="New Post"]',
                '[aria-label="New post"]',
            ]):
                raise RuntimeError("IG New post control not found")
            await human_delay(1, 2)
            fi = self.page.locator('input[type="file"]').first
            await fi.set_input_files(video_path)
            await human_delay(6, 12)
            for _ in range(4):
                if not await click_first(self.page, ['div[role="button"]:has-text("Next")', 'button:has-text("Next")'], timeout=3000):
                    break
                await human_delay(1, 2)
            await fill_first(self.page, IG_CAPTION, caption[:2200])
            await human_delay(1, 2)
            if not await click_first(self.page, IG_SHARE):
                raise RuntimeError("IG Share not found")
            await human_delay(6, 12)
            return self.page.url
        except Exception:
            if self.page:
                await capture_failure(self.page, "instagram", "post")
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
