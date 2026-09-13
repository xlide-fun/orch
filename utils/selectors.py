"""Multi-fallback selector helper for brittle UIs."""
from typing import List, Optional
from playwright.async_api import Page, Locator

async def first_match(page: Page, selectors: List[str], timeout: int = 8000) -> Optional[Locator]:
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            await loc.wait_for(state="visible", timeout=timeout)
            return loc
        except Exception:
            continue
    return None

async def click_first(page: Page, selectors: List[str], timeout: int = 8000) -> bool:
    loc = await first_match(page, selectors, timeout)
    if not loc:
        return False
    await loc.click()
    return True

async def fill_first(page: Page, selectors: List[str], text: str, timeout: int = 8000) -> bool:
    loc = await first_match(page, selectors, timeout)
    if not loc:
        return False
    await loc.fill(text)
    return True

# Platform-specific common sets
X_COMPOSE = ['[data-testid="tweetTextarea_0"]', 'div[role="textbox"]', '[contenteditable="true"]']
X_POST_BTN = ['[data-testid="tweetButton"]', '[data-testid="tweetButtonInline"]', 'button:has-text("Post")']
IG_CAPTION = ['textarea[aria-label="Write a caption..."]', 'textarea[placeholder*="caption"]', 'div[aria-label*="caption"]']
IG_SHARE = ['div[role="button"]:has-text("Share")', 'button:has-text("Share")']
