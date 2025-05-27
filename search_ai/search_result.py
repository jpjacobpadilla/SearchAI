from typing import Any

from .proxy import Proxy
from .utils import extract_metadata, generate_markdown, valid_type
from .extractor import get_page_sync, get_page

from pydantic import BaseModel, HttpUrl


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
        parts = [f'**Title:** {self.title}', f'**Link:** {self.link}']
        if self.description:
            parts.append(f'**Description:** {self.description}')
        return '\n'.join(parts)

    def _extended_markdown(
        self,
        page_source: str,
        content_length: int,
        only_page_content: bool = False,
        ignore_links: bool = False,
        ignore_images: bool = True,
    ) -> str:
        markdown = generate_markdown(page_source, ignore_links, ignore_images)

        if only_page_content:
            return markdown[:content_length]

        metadata = extract_metadata(page_source)

        parts = [f'**Title:** {metadata.get("title") or self.title}', f'**Link:** {self.link}']

        if metadata.get('description'):
            parts.append(f'**Description:** {metadata["description"]}')
        elif self.description:
            parts.append(f'**Description:** {self.description}')

        if metadata.get('author'):
            parts.append(f'**Author:** {metadata["author"]}')
        if metadata.get('twitter'):
            parts.append(f'**Twitter:** {metadata["twitter"]}')

        if markdown:
            parts.append('')  # Extra break between metadata and page data
            parts.append('## Page Preview:\n')
            parts.append(markdown[:content_length].strip())

        return '\n'.join(parts)

    def _extended_json(
        self, page_source: str, content_length: int, ignore_links: bool = False, ignore_images: bool = True
    ) -> dict:
        metadata = extract_metadata(page_source)
        markdown = generate_markdown(page_source, ignore_links, ignore_images)

        combined_data = {'title': metadata.get('title') or self.title, 'link': str(self.link)}

        if metadata.get('description'):
            combined_data['description'] = metadata['description']
        elif self.description:
            combined_data['description'] = self.description

        if metadata.get('author'):
            combined_data['author'] = metadata['author']
        if metadata.get('twitter'):
            combined_data['twitter'] = metadata['twitter']

        if markdown:
            combined_data['page_preview'] = markdown[:content_length]

        return combined_data


class SearchResult(BaseSearchResult):
    def markdown(
        self,
        extend: bool = False,
        content_length: int = 1_000,
        ignore_links: bool = False,
        ignore_images: bool = True,
        only_page_content: bool = False,
    ) -> str:
        if not extend or not valid_type(str(self.link)):
            return self._basic_markdown()

        page_source = get_page_sync(str(self.link), self._proxy)
        return self._extended_markdown(page_source, content_length, only_page_content, ignore_links, ignore_images)

    def json(
        self,
        extend: bool = False,
        content_length: int = 1_000,
        ignore_links: bool = False,
        ignore_images: bool = True,
        **kwargs: Any,
    ) -> dict:
        if not extend or not valid_type(str(self.link)):
            return super().model_dump(**kwargs)

        page_source = get_page_sync(str(self.link), self._proxy)
        return self._extended_json(page_source, content_length, ignore_links, ignore_images)


class AsyncSearchResult(BaseSearchResult):
    async def markdown(
        self,
        extend: bool = False,
        content_length: int = 1_000,
        ignore_links: bool = False,
        ignore_images: bool = True,
        only_page_content: bool = False,
    ) -> str:
        if not extend or not valid_type(str(self.link)):
            return self._basic_markdown()

        page_source = await get_page(str(self.link), self._proxy)
        return self._extended_markdown(page_source, content_length, only_page_content, ignore_links, ignore_images)

    async def json(
        self,
        extend: bool = False,
        content_length: int = 1_000,
        ignore_links: bool = False,
        ignore_images: bool = True,
        **kwargs: Any,
    ) -> dict:
        if not extend or not valid_type(str(self.link)):
            return super().model_dump(**kwargs)

        page_source = await get_page(str(self.link), self._proxy)
        return self._extended_json(page_source, content_length, ignore_links, ignore_images)


class SearchResults(list):
    def __init__(self, results: list[SearchResult], _proxy: Proxy | None = None):
        super().__init__(results)
        self._proxy = _proxy

    def markdown(self, extend: bool = False, content_length: int = 1_000, **kwargs) -> str:
        if not self:  # Edge case for no search results
            return ''

        if not extend:
            content = [result._basic_markdown() for result in self]

        else:
            page_sources = get_page_sync([str(result.link) for result in self], self._proxy)
            content = [
                result._extended_markdown(page_source=page_source, content_length=content_length, **kwargs)
                for result, page_source in zip(self, page_sources)
            ]

        return '# Search Results\n\n' + '\n----------\n'.join(content)

    def json(self, extend: bool = False, content_length: int = 1_000, **kwargs) -> list[dict]:
        if not extend:
            return [result.model_dump() for result in self]

        page_sources = get_page_sync([str(result.link) for result in self], self._proxy)
        return [
            result._extended_json(page_source=page_source, content_length=content_length, **kwargs)
            for result, page_source in zip(self, page_sources)
        ]


class AsyncSearchResults(list):
    def __init__(self, results: list[AsyncSearchResult], _proxy: Proxy | None = None):
        super().__init__(results)
        self._proxy = _proxy

    async def markdown(self, extend: bool = False, content_length: int = 1_000, **kwargs) -> str:
        if not extend:
            content = [result._basic_markdown() for result in self]

        else:
            page_sources = await get_page([str(result.link) for result in self], self._proxy)
            content = [
                result._extended_markdown(page_source=page_source, content_length=content_length, **kwargs)
                for result, page_source in zip(self, page_sources)
            ]

        return '# Search Results\n\n' + '\n----------\n'.join(content)

    async def json(self, extend: bool = False, content_length: int = 1_000, **kwargs) -> list[dict]:
        if not extend:
            return [result.model_dump() for result in self]

        page_sources = await get_page([str(result.link) for result in self], self._proxy)
        return [
            result._extended_json(page_source=page_source, content_length=content_length, **kwargs)
            for result, page_source in zip(self, page_sources)
        ]
