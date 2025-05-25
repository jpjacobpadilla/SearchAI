from typing import  Any

from .utils import extract_metadata, generate_markdown, valid_type
from .proxy import Proxy

from pydantic import BaseModel, HttpUrl
from playwright.sync_api import Browser, sync_playwright
from playwright.async_api import async_playwright, Browser as AsyncBrowser


PLAYWRIGHT_CONFIG = {
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'viewport': {'width': 1280, 'height': 720},
    'locale': 'en-US'
}


class BaseSearchResult(BaseModel):
    title: str
    link: HttpUrl
    description: str | None = None
    _proxy: Proxy | None = None

    def __str__(self):
        """
        This is here to hide _proxy, which is more of an implementation detail.
        """
        return f'{self.__class__.__name__}(title="{self.title}", link="{self.link}", description="{self.description}")'

    def __repr__(self):
        return self.__str__()

    def _basic_markdown(self) -> str:
        parts = [f"**Title:** {self.title}", f"**Link:** {self.link}"]
        if self.description:
            parts.append(f"**Description:** {self.description}")
        return "\n".join(parts)

    def _extended_markdown(
        self,
        page_source: str,
        only_page_content: bool,
        content_length: int,
        ignore_links: bool,
        ignore_images: bool,
    ) -> str:
        markdown = generate_markdown(page_source, ignore_links, ignore_images)

        if only_page_content:
            return markdown[:content_length]

        metadata = extract_metadata(page_source)

        parts = [
            f"**Title:** {metadata['title'] or self.title}",
            f"**Link:** {self.link}",
        ]

        if metadata["description"]:
            parts.append(f"**Description:** {metadata['description']}")
        elif self.description:
            parts.append(f"**Description:** {self.description}")

        if metadata["author"]:
            parts.append(f"**Author:** {metadata['author']}")
        if metadata["twitter"]:
            parts.append(f"**Twitter:** {metadata['twitter']}")

        parts.append("")  # Extra break between metadata and page data
        parts.append("## Page Preview:\n")
        parts.append(markdown[:content_length].strip())

        return "\n".join(parts)

    def _extended_json(
        self,
        page_source: str,
        content_length: int,
        ignore_links: bool,
        ignore_images: bool,
    ) -> dict:
        metadata = extract_metadata(page_source)
        markdown = generate_markdown(page_source, ignore_links, ignore_images)

        combined_data = {
            "title": metadata["title"] or self.title,
            "link": str(self.link),
        }

        if metadata["description"]:
            combined_data["description"] = metadata["description"]
        elif self.description:
            combined_data["description"] = self.description

        if metadata["author"]:
            combined_data["author"] = metadata["author"]
        if metadata["twitter"]:
            combined_data["twitter"] = metadata["twitter"]

        combined_data["page_preview"] = markdown[:content_length]

        return combined_data


class SearchResult(BaseSearchResult):
    def markdown(
        self,
        extend: bool = True,
        content_length: int = 1_000,
        ignore_links: bool = False,
        ignore_images: bool = True,
        only_page_content: bool = False,
        browser: Browser | None = None,
    ) -> str:
        if not extend or not valid_type(str(self.link)):
            return self._basic_markdown()

        page_source = self._get_page_source(browser)
        return self._extended_markdown(
            page_source, only_page_content, content_length, ignore_links, ignore_images
        )

    def json(
        self,
        extend: bool = True,
        content_length: int = 1_000,
        browser: Browser | None = None,
        ignore_links: bool = False,
        ignore_images: bool = True,
        **kwargs: Any,
    ) -> dict:
        if not extend or not valid_type(str(self.link)):
            return super().model_dump(**kwargs)

        page_source = self._get_page_source(browser)
        return self._extended_json(
            page_source, content_length, ignore_links, ignore_images
        )

    def _get_page_source(self, browser: Browser) -> str:
        if browser:
            return self._use_playwright(browser)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                proxy=self._proxy.to_playwright_proxy() if self._proxy else None
            )
            return self._use_playwright(browser)

    def _use_playwright(self, browser: Browser) -> str:
        context = browser.new_context(**PLAYWRIGHT_CONFIG)
        page = context.new_page()

        page.goto(str(self.link), wait_until="load")
        page_source = page.content()
        page.close()
        context.close()
        return page_source


class AsyncSearchResult(BaseSearchResult):
    async def markdown(
        self,
        extend: bool = True,
        content_length: int = 1_000,
        ignore_links: bool = False,
        ignore_images: bool = True,
        only_page_content: bool = False,
        browser: AsyncBrowser | None = None,
    ) -> str:
        if not extend or not valid_type(str(self.link)):
            return self._basic_markdown()

        page_source = await self._get_page_source(browser)
        return self._extended_markdown(
            page_source, only_page_content, content_length, ignore_links, ignore_images
        )

    async def json(
        self,
        extend: bool = True,
        content_length: int = 1_000,
        browser: AsyncBrowser | None = None,
        ignore_links: bool = False,
        ignore_images: bool = True,
        **kwargs: Any,
    ) -> dict:
        if not extend or not valid_type(str(self.link)):
            return super().model_dump(**kwargs)

        page_source = await self._get_page_source(browser)
        return self._extended_json(
            page_source, content_length, ignore_links, ignore_images
        )

    async def _get_page_source(self, browser: AsyncBrowser | None = None) -> str:
        if browser:
            return await self._use_playwright(browser)

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True,
                proxy=self._proxy.to_playwright_proxy() if self._proxy else None
            )
            return await self._use_playwright(browser)

    async def _use_playwright(self, browser: AsyncBrowser) -> str:
        context = await browser.new_context(**PLAYWRIGHT_CONFIG)
        page = await context.new_page()

        await page.goto(str(self.link), wait_until="load")
        page_source = await page.content()
        await page.close()
        await context.close()
        return page_source


class SearchResults(list):
    def __init__(self, results: list[SearchResult], _proxy: Proxy | None):
        super().__init__(results)
        self._proxy = _proxy

    def markdown(
        self, extend: bool = True, content_length: int = 400, **kwargs
    ) -> str:
        content = ["# Search Results:"]

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                proxy=self._proxy.to_playwright_proxy() if self._proxy else None
            )

            for result in self:
                content.append(
                    result.markdown(
                        extend=extend,
                        content_length=content_length,
                        browser=browser,
                        **kwargs,
                    )
                )

        return "\n\n".join(content)

    def json(
        self, extend: bool = True, content_length: int = 400, **kwargs
    ) -> list[dict]:
        data = []

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                proxy=self._proxy.to_playwright_proxy() if self._proxy else None
            )

            for result in self:
                data.append(
                    result.json(
                        extend=extend,
                        content_length=content_length,
                        browser=browser,
                        **kwargs,
                    )
                )

        return data


class AsyncSearchResults(list):
    def __init__(self, results: list[AsyncSearchResult], _proxy: Proxy| None):
        super().__init__(results)
        self._proxy = _proxy

    async def markdown(
        self, extend: bool = True, content_length: int = 400, **kwargs
    ) -> str:
        content = ["# Search Results:"]

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True,
                proxy=self._proxy.to_playwright_proxy() if self._proxy else None
            )

            for result in self:
                content.append(
                    await result.markdown(
                        extend=extend,
                        content_length=content_length,
                        browser=browser,
                        **kwargs,
                    )
                )

        return "\n\n".join(content)

    async def json(
        self, extend: bool = True, content_length: int = 400, **kwargs
    ) -> list[dict]:
        data = []

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True,
                proxy=self._proxy.to_playwright_proxy() if self._proxy else None
            )

            for result in self:
                data.append(
                    await result.json(
                        extend=extend,
                        content_length=content_length,
                        browser=browser,
                        **kwargs,
                    )
                )

        return data
