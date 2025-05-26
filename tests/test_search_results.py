import pytest
from pydantic import HttpUrl
from search_ai.search_result import (
    SearchResult,
    AsyncSearchResult,
    SearchResults,
    AsyncSearchResults,
)


@pytest.fixture
def sample_data():
    return {'title': 'Example Title', 'link': 'https://example.com', 'description': 'An example description.'}


def test_search_result(sample_data):
    result = SearchResult(**sample_data)

    assert result.title == sample_data['title']
    assert result.link == HttpUrl(sample_data['link'])
    assert result.description == sample_data['description']

    markdown = result.markdown()
    assert '**Title:**' in markdown
    assert '**Link:**' in markdown
    assert '**Description:**' in markdown

    json_data = result.json()
    for key, val in sample_data.items():
        if key == 'link':
            assert json_data[key] == HttpUrl(val)
        else:
            assert json_data[key] == val

    assert set(json_data.keys()) == set(sample_data.keys())


@pytest.mark.asyncio
async def test_async_search_result(sample_data):
    result = AsyncSearchResult(**sample_data)
    assert result.title == sample_data['title']
    assert result.link == HttpUrl(sample_data['link'])
    assert result.description == sample_data['description']

    markdown = await result.markdown()
    assert '**Title:**' in markdown
    assert '**Link:**' in markdown
    assert '**Description:**' in markdown

    json_data = await result.json()
    for key, val in sample_data.items():
        if key == 'link':
            assert json_data[key] == HttpUrl(val)
        else:
            assert json_data[key] == val

    assert set(json_data.keys()) == set(sample_data.keys())


def test_search_results(sample_data):
    r1 = SearchResult(**sample_data)
    r2 = SearchResult(**sample_data)
    results = SearchResults(results=[r1, r2])

    markdown = results.markdown()
    assert markdown.count('**Title:**') == 2
    assert markdown.startswith('# Search Results')

    json_data = results.json()
    assert isinstance(json_data, list)
    assert len(json_data) == 2


@pytest.mark.asyncio
async def test_async_search_results(sample_data):
    r1 = AsyncSearchResult(**sample_data)
    r2 = AsyncSearchResult(**sample_data)
    results = AsyncSearchResults(results=[r1, r2])

    markdown = await results.markdown()
    assert markdown.count('**Title:**') == 2
    assert markdown.startswith('# Search Results')

    json_data = await results.json()
    assert isinstance(json_data, list)
    assert len(json_data) == 2
