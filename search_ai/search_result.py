from typing import Generator, Any

import html2text
from lxml import html
from pydantic import BaseModel, HttpUrl
from playwright.sync_api import Browser, sync_playwright


def extract_metadata(page_source: str) -> dict:
    tree = html.fromstring(page_source)

    page_title = tree.xpath('//head/title/text()')
    page_description = tree.xpath('//head/meta[@name="description"]/@content')
    author = tree.xpath('//head/meta[@name="author"]/@content')
    twitter_handle = tree.xpath('//head/meta[@name="twitter:site"]/@content')

    result = {}

    if page_title:
        result['title'] = page_title[0]
    if page_description:
        result['description'] = page_description[0]
    if author:
        result['author'] = author[0]
    if twitter_handle:
        result['twitter'] = twitter_handle[0]

    return result


class SearchResult(BaseModel):
    title: str
    link: HttpUrl
    description: str | None

    def markdown(
        self,
        extend: bool = True,
        content_length: int = 1_000,
        ignore_links: bool = False,
        ignore_images: bool = True,
        browser: Browser | None = None
    ) -> str:
        if not extend:
            return f'**Title:** {self.title}\n' + \
                   f'**Link:** {self.link}\n' + \
                   f'**Description:** {self.description}' if self.description else ''

        page_source = ''

        if browser:
            page_source = self._get_page_source(browser)
        else:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page_source = self._get_page_source(browser)

        text_maker = html2text.HTML2Text()
        text_maker.ignore_links = ignore_links
        text_maker.ignore_images = ignore_images
        text_maker.body_width = 0  # Prevent automatic wrapping

        markdown = text_maker.handle(page_source)

        metadata = extract_metadata(page_source)

        parts = [
            f"**Title:** {metadata['title'] if metadata['title'] else self.title}",
            f"**Link:** {self.link}",
        ]

        if metadata['description']:
            parts.append(f"**Description:** {metadata['description']}")
        elif self.description:
            parts.append(f"**Description:** {self.description}")

        if metadata['author']:
            parts.append(f"**Author:** {metadata['author']}")
        if metadata['twitter']:
            parts.append(f"**Twitter:** {metadata['twitter']}")

        parts.append('')  # Extra break between metadata and page data
        parts.append("## Page Preview:\n")
        parts.append(markdown[:content_length].strip())

        return "\n".join(parts)

    def _get_page_source(self, browser: Browser) -> str:
        page = browser.new_page()
        page.goto(str(self.link), wait_until="load")
        page_source = page.content()
        page.close()
        return page_source

    def json(self, extend: bool = False, content_length: int = 400, browser_context: Browser | None = None, **kwargs: Any) -> dict:
        pass


class SearchResults:
    def __init__(self, results: list[SearchResult], proxy: str = ''):
        self.results = results
        self.proxy = proxy

    def __iter__(self) -> Generator[SearchResult, None, None]:
        for result in self.results:
            yield result

    def markdown(self, extend: bool = False, content_length: int = 400) -> str:
        content = '# Search Results:\n\n'
        browser = None

        for result in self.results:
            content += result.markdown(extend=extend, content_length=content_length, browser_context=browser) + '\n\n'

        return content

    def json(self, extend: bool = False, content_length: int = 400) -> list[dict]:
        data = []
        browser = None

        for result in self.results:
            data.append(result.json(extend=extend, content_length=content_length, browser_context=browser))

        return data
