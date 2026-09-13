from managers.base_manager import BaseManager
from utils.stealth import launch_stealth_context, human_delay, human_type
from utils.screenshot import capture_failure
from playwright.async_api import async_playwright
from pathlib import Path
import os

class XManager(BaseManager):
    def __init__(self, handle: str, credentials: dict = None):
        super().__init__("x", handle)
        self.credentials = credentials or {}
        self._pw = None

    async def _ensure_context(self):
        if self.context:
            return
        self._pw = await async_playwright().start()
        user_dir = f"./user_data/x_{self.handle}"
        Path(user_dir).mkdir(parents=True, exist_ok=True)
        storage = self.get_session_path() if Path(self.get_session_path()).exists() else None
        self.context = await launch_stealth_context(
            self._pw, "x", user_data_dir=user_dir, headless=False
        )
        if storage and Path(storage).exists():
            # persistent context already loads profile; also try storage_state if needed
            pass
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()

    async def is_logged_in(self) -> bool:
        await self._ensure_context()
        try:
            await self.page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=20000)
            await human_delay(1, 2)
            return "login" not in self.page.url.lower() and "/i/flow/login" not in self.page.url
        except Exception:
            return False

    async def login(self) -> bool:
        await self._ensure_context()
        if await self.is_logged_in():
            await self.context.storage_state(path=self.get_session_path())
            return True
        await self.page.goto("https://x.com/i/flow/login", wait_until="domcontentloaded")
        await human_delay(2, 4)
        user = self.credentials.get("username") or self.credentials.get("email") or ""
        pw = self.credentials.get("password") or ""
        if not user or not pw:
            raise RuntimeError("X credentials missing")
        # username
        await self.page.wait_for_selector('input[autocomplete="username"]', timeout=15000)
        await human_type(self.page, 'input[autocomplete="username"]', user)
        await self.page.keyboard.press("Enter")
        await human_delay(2, 4)
        # possible unusual activity / phone intermediate
        try:
            unusual = self.page.locator('input[data-testid="ocfEnterTextTextInput"]')
            if await unusual.count():
                # leave for manual / skip
                pass
        except Exception:
            pass
        # password
        await self.page.wait_for_selector('input[name="password"]', timeout=15000)
        await human_type(self.page, 'input[name="password"]', pw)
        await self.page.keyboard.press("Enter")
        await human_delay(4, 8)
        if await self.is_logged_in():
            Path(self.get_session_path()).parent.mkdir(parents=True, exist_ok=True)
            await self.context.storage_state(path=self.get_session_path())
            return True
        return False

    async def post(self, video_path: str, caption: str) -> str:
        try:
            if not await self.is_logged_in():
                ok = await self.login()
                if not ok:
                    raise RuntimeError("X login failed")
            await self.page.goto("https://x.com/compose/post", wait_until="domcontentloaded")
            await human_delay(2, 4)
            file_input = self.page.locator('input[type="file"]').first
            await file_input.set_input_files(video_path)
            await human_delay(4, 8)
            editor = self.page.locator('[data-testid="tweetTextarea_0"]')
            await editor.click()
            await human_type(self.page, '[data-testid="tweetTextarea_0"]', caption[:280])
            await human_delay(1, 2)
            btn = self.page.locator('[data-testid="tweetButton"]')
            await btn.click()
            await human_delay(5, 10)
            url = self.page.url
            if "/status/" in url:
                return url
            # try extract from toast / timeline
            return f"https://x.com/{self.handle}"
        except Exception as e:
            if self.page:
                await capture_failure(self.page, "x", "post")
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
        self.context = None
        self.page = None
