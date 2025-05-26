import asyncio
import subprocess
from typing import overload

from .proxy import Proxy
from .utils import valid_type

from playwright.async_api import async_playwright, Browser as AsyncBrowser, Error as PlaywrightError


PLAYWRIGHT_CONFIG = {
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'viewport': {'width': 1280, 'height': 720},
    'locale': 'en-US',
}


@overload
def get_page_sync(url: str, proxy: Proxy | None) -> str: ...
@overload
def get_page_sync(url: list[str], proxy: Proxy | None) -> list[str]: ...
@overload
async def get_page(url: str, proxy: Proxy | None) -> str: ...
@overload
async def get_page(url: list[str], proxy: Proxy | None) -> list[str]: ...


def get_page_sync(url: str | list[str], proxy: Proxy | None) -> str | list[str]:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio

            nest_asyncio.apply()
            return asyncio.run(get_page(url, proxy))
        else:
            return loop.run_until_complete(get_page(url, proxy))
    except RuntimeError:
        return asyncio.run(get_page(url, proxy))


async def get_page(url: str | list[str], proxy: Proxy | None) -> str | list[str]:
    semaphore = asyncio.Semaphore(8)
    url_list = url if isinstance(url, list) else [url]

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True, proxy=proxy.to_playwright_proxy() if proxy else None
            )

            tasks = [_get_page_source(url, semaphore, browser) for url in url_list]
            results = await asyncio.gather(*tasks)
            await browser.close()

            return results[0] if isinstance(url, str) else results

    except PlaywrightError:
        print("Playwright browser not found. Running 'playwright install'...")
        subprocess.run(['playwright', 'install', 'chromium'], check=True)
        return await get_page(url, proxy)


async def _get_page_source(url: str, semaphore: asyncio.Semaphore, browser: AsyncBrowser) -> str:
    if not valid_type(url):
        return ''

    async with semaphore:
        context = await browser.new_context(**PLAYWRIGHT_CONFIG)
        page = await context.new_page()

        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=6000)
            await page.wait_for_timeout(2000)  # Wait an extra 2s for JS to populate content
        except Exception:
            page_source = ''
        else:
            page_source = await page.content()

        await page.close()
        await context.close()
        return page_source
