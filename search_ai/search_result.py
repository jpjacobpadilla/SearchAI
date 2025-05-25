from typing import Generator, Any

import html2text
from lxml import html
from pydantic import BaseModel, HttpUrl
from playwright.sync_api import Browser, sync_playwright


def extract_metadata(page_source: str) -> dict:
    tree = html.fromstring(page_source)

    page_title = tree.xpath("//head/title/text()")
    page_description = tree.xpath('//head/meta[@name="description"]/@content')
    author = tree.xpath('//head/meta[@name="author"]/@content')
    twitter_handle = tree.xpath('//head/meta[@name="twitter:site"]/@content')

    result = {}

    if page_title:
        result["title"] = page_title[0]
    if page_description:
        result["description"] = page_description[0]
    if author:
        result["author"] = author[0]
    if twitter_handle:
        result["twitter"] = twitter_handle[0]

    return result


class SearchResult(BaseModel):
    title: str
    link: HttpUrl
    description: str | None = None

    def _get_page_source(self, browser: Browser) -> str:
        page_source = ""

        if browser:
            page_source = self._use_playwright(browser)
        else:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page_source = self._use_playwright(browser)

        return page_source

    @staticmethod
    def _generate_markdown(
        page_source: str, ignore_links: bool, ignore_images: bool
    ) -> str:
        text_maker = html2text.HTML2Text()
        text_maker.ignore_links = ignore_links
        text_maker.ignore_images = ignore_images
        text_maker.body_width = 0  # Prevent automatic wrapping
        return text_maker.handle(page_source)

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
            parts = [f"**Title:** {self.title}", f"**Link:** {self.link}"]
            if self.description:
                parts.append(f"**Description:** {self.description}")
            return "\n".join(parts)

        page_source = self._get_page_source(browser)
        markdown = self._generate_markdown(page_source, ignore_links, ignore_images)

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

    def _use_playwright(self, browser: Browser) -> str:
        page = browser.new_page()
        page.goto(str(self.link), wait_until="load")
        page_source = page.content()
        page.close()
        return page_source

    def json(
        self,
        extend: bool = False,
        content_length: int = 400,
        browser: Browser | None = None,
        ignore_links: bool = False,
        ignore_images: bool = True,
        **kwargs: Any,
    ) -> dict:
        if not extend:
            return super().model_dump(**kwargs)

        page_source = self._get_page_source(browser)
        metadata = extract_metadata(page_source)
        markdown = self._generate_markdown(page_source, ignore_links, ignore_images)

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


class SearchResults:
    def __init__(self, results: list[SearchResult], proxy: str = ""):
        self.results = results
        self.proxy = proxy

    def __iter__(self) -> Generator[SearchResult, None, None]:
        for result in self.results:
            yield result

    def markdown(self, extend: bool = False, content_length: int = 400) -> str:
        content = "# Search Results:\n\n"
        browser = None

        for result in self.results:
            content += (
                result.markdown(
                    extend=extend,
                    content_length=content_length,
                    browser_context=browser,
                )
                + "\n\n"
            )

        return content

    def json(self, extend: bool = False, content_length: int = 400) -> list[dict]:
        data = []
        browser = None

        for result in self.results:
            data.append(
                result.json(
                    extend=extend,
                    content_length=content_length,
                    browser_context=browser,
                )
            )

        return data
