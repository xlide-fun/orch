from managers.base_manager import BaseManager
from utils.stealth import launch_stealth_context, human_delay, human_type
from utils.screenshot import capture_failure
from playwright.async_api import async_playwright
from pathlib import Path

class RedditManager(BaseManager):
    def __init__(self, username: str, credentials: dict = None, subreddit: str = "fitness"):
        super().__init__("reddit", username)
        self.credentials = credentials or {}
        self.subreddit = subreddit
        self._pw = None

    async def _ensure_context(self):
        if self.context:
            return
        self._pw = await async_playwright().start()
        user_dir = f"./user_data/reddit_{self.handle}"
        Path(user_dir).mkdir(parents=True, exist_ok=True)
        self.context = await launch_stealth_context(self._pw, "reddit", user_data_dir=user_dir, headless=True)
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()

    async def is_logged_in(self) -> bool:
        await self._ensure_context()
        try:
            await self.page.goto("https://old.reddit.com", timeout=15000)
            return bool(await self.page.locator("#header-bottom-right .user a").count())
        except Exception:
            return False

    async def login(self) -> bool:
        await self._ensure_context()
        if await self.is_logged_in():
            await self.context.storage_state(path=self.get_session_path())
            return True
        await self.page.goto("https://old.reddit.com/login")
        await human_delay(1, 2)
        await self.page.fill('input[name="user"]', self.credentials.get("username", ""))
        await self.page.fill('input[name="passwd"]', self.credentials.get("password", ""))
        await self.page.click('button[type="submit"]')
        await human_delay(2, 4)
        if await self.is_logged_in():
            Path(self.get_session_path()).parent.mkdir(parents=True, exist_ok=True)
            await self.context.storage_state(path=self.get_session_path())
            return True
        return False

    async def post(self, video_path: str, caption: str, title: str = None) -> str:
        try:
            if not await self.is_logged_in():
                if not await self.login():
                    raise RuntimeError("Reddit login failed")
            title = (title or caption.split(".")[0] or caption)[:300]
            body = caption
            await self.page.goto(f"https://old.reddit.com/r/{self.subreddit}/submit")
            await human_delay(1, 2)
            await self.page.fill('textarea[name="title"]', title)
            await self.page.fill('textarea[name="text"]', body)
            await self.page.click('button[name="submit"]')
            await human_delay(3, 6)
            return self.page.url
        except Exception:
            if self.page:
                await capture_failure(self.page, "reddit", "post")
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
