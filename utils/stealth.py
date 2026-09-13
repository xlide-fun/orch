import random
from playwright.async_api import async_playwright, BrowserContext

STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
window.chrome = {runtime: {}};
"""

async def launch_stealth_context(playwright, platform: str, user_data_dir: str = None, proxy: str = None, headless: bool = False) -> BrowserContext:
    args = ["--disable-blink-features=AutomationControlled"]
    launch_opts = {
        "headless": headless,
        "args": args,
        "viewport": {"width": 1280, "height": 720},
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "locale": "en-US",
        "timezone_id": "America/New_York",
    }
    if proxy:
        launch_opts["proxy"] = {"server": proxy}
    if user_data_dir:
        context = await playwright.chromium.launch_persistent_context(user_data_dir, **launch_opts)
    else:
        browser = await playwright.chromium.launch(**launch_opts)
        context = await browser.new_context()
    await context.add_init_script(STEALTH_JS)
    return context

async def human_delay(min_s=1.0, max_s=5.0):
    import asyncio
    await asyncio.sleep(random.uniform(min_s, max_s))

async def human_type(page, selector, text, delay_ms=(50, 150)):
    await page.click(selector)
    for ch in text:
        await page.keyboard.type(ch, delay=random.randint(*delay_ms))
