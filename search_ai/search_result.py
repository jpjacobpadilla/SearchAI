from typing import Generator, Any, AsyncGenerator

from .utils import extract_metadata, generate_markdown

from pydantic import BaseModel, HttpUrl
from playwright.sync_api import Browser, sync_playwright
from playwright.async_api import async_playwright


class BaseSearchResult:
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
            ignore_images: bool
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
            ignore_images: bool
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

class SearchResult(BaseModel, BaseSearchResult):
    title: str
    link: HttpUrl
    description: str | None = None

    def markdown(
        self,
        extend: bool = True,
        content_length: int = 1_000,
        ignore_links: bool = False,
        ignore_images: bool = True,
        only_page_content: bool = False,
        browser: Browser | None = None,
    ) -> str:
        if not extend:
            return self._basic_markdown()

        page_source = self._get_page_source(browser)
        return self._extended_markdown(page_source, only_page_content, content_length, ignore_links, ignore_images)

    def json(
        self,
        extend: bool = False,
        content_length: int = 1_000,
        browser: Browser | None = None,
        ignore_links: bool = False,
        ignore_images: bool = True,
        **kwargs: Any,
    ) -> dict:
        if not extend:
            return super().model_dump(**kwargs)

        page_source = self._get_page_source(browser)
        return self._extended_json(page_source, content_length, ignore_links, ignore_images)

    def _get_page_source(self, browser: Browser) -> str:
        if browser:
            return self._use_playwright(browser)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            return self._use_playwright(browser)

    def _use_playwright(self, browser: Browser) -> str:
        page = browser.new_page()
        page.goto(str(self.link), wait_until="load")
        page_source = page.content()
        page.close()
        return page_source


class AsyncSearchResult(BaseModel):
    title: str
    link: HttpUrl
    description: str | None = None

    async def markdown(
            self,
            extend: bool = True,
            content_length: int = 1_000,
            ignore_links: bool = False,
            ignore_images: bool = True,
            only_page_content: bool = False,
            browser: Browser | None = None,
    ) -> str:
        if not extend:
            return self._basic_markdown()

        page_source = await self._get_page_source(browser)
        return self._extended_markdown(page_source, only_page_content, content_length, ignore_links, ignore_images)

    async def json(
            self,
            extend: bool = False,
            content_length: int = 1_000,
            browser: Browser | None = None,
            ignore_links: bool = False,
            ignore_images: bool = True,
            **kwargs: Any,
    ) -> dict:
        if not extend:
            return super().model_dump(**kwargs)

        page_source = await self._get_page_source(browser)
        return self._extended_json(page_source, content_length, ignore_links, ignore_images)

    async def _get_page_source(self, browser: Browser | None = None) -> str:
        if browser:
            return await self._use_playwright(browser)

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            return await self._use_playwright(browser)

    async def _use_playwright(self, browser: Browser) -> str:
        page = await browser.new_page()
        await page.goto(str(self.link), wait_until="load")
        page_source = await page.content()
        page.close()
        return page_source


class SearchResults:
    def __init__(self, results: list[SearchResult], proxy: str = ""):
        self.results = results
        self.proxy = proxy

    def __iter__(self) -> Generator[SearchResult, None, None]:
        for result in self.results:
            yield result

    def markdown(self, extend: bool = False, content_length: int = 400, **kwargs) -> str:
        content = ['# Search Results:']

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)

            for result in self.results:
                content.append(result.markdown(extend=extend, content_length=content_length, browser=browser, **kwargs))

        return '\n\n'.join(content)

    def json(self, extend: bool = False, content_length: int = 400, **kwargs) -> list[dict]:
        data = []

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)

            for result in self.results:
                data.append(result.json(extend=extend, content_length=content_length, browser=browser, **kwargs))

        return data


class AsyncSearchResults:
    def __init__(self, results: list[AsyncSearchResult], proxy: str = ""):
        self.results = results
        self.proxy = proxy

    async def __aiter__(self) -> AsyncGenerator[AsyncSearchResult, None]:
        for result in self.results:
            yield result

    async def markdown(self, extend: bool = False, content_length: int = 400, **kwargs) -> str:
        content = ['# Search Results:']

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)

            for result in self.results:
                content.append(await result.markdown(extend=extend, content_length=content_length, browser=browser, **kwargs))

        return '\n\n'.join(content)

    async def json(self, extend: bool = False, content_length: int = 400, **kwargs) -> list[dict]:
        data = []

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)

            for result in self.results:
                data.append(await result.json(extend=extend, content_length=content_length, browser=browser, **kwargs))

        return data
