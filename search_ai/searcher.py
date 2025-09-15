import time
import random
import asyncio
from typing import Literal, Any
from functools import partial

import curl_cffi as curl
from curl_cffi.requests.exceptions import HTTPError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from .proxy import Proxy
from .filters import Filters
from .parse import parse_search
from .search_result import SearchResult, SearchResults, AsyncSearchResult, AsyncSearchResults


BASE_URL = 'https://lite.duckduckgo.com/lite/'
SLEEP_TIME = 0.25

HEADERS = {'origin': 'https://lite.duckduckgo.com', 'referer': 'https://lite.duckduckgo.com/'}

retry_curl = partial(
    retry,
    stop=stop_after_attempt(2),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(HTTPError),
    reraise=True,
)


def search(
    query: str = '',
    filters: Filters | None = None,
    count: int = 10,
    offset: int = 0,
    proxy: Proxy | None = None,
) -> SearchResults:
    results = SearchResults(results=[], _proxy=proxy)

    while len(results) < count:
        response = _request(query, filters, offset, proxy)
        new_results = parse_search(response)

        if not new_results:
            return results

        for new_result in new_results:
            results.append(SearchResult(**new_result, _proxy=proxy))
            if len(results) == count:
                return results

        offset += len(new_results)

        twenty_percent = SLEEP_TIME * 0.10
        time.sleep(random.uniform(SLEEP_TIME - twenty_percent, SLEEP_TIME + twenty_percent))

    return results


async def async_search(
    query: str = '',
    filters: Filters | None = None,
    count: int = 10,
    offset: int = 0,
    proxy: Proxy | None = None,
) -> AsyncSearchResults:
    results = AsyncSearchResults(results=[], _proxy=proxy)

    while len(results) < count:
        response = await _async_request(query, filters, offset, proxy)
        new_results = parse_search(response)

        if not new_results:
            return results

        for new_result in new_results:
            results.append(AsyncSearchResult(**new_result, _proxy=proxy))
            if len(results) == count:
                return results

        offset += len(new_results)

        twenty_percent = SLEEP_TIME * 0.10
        await asyncio.sleep(random.uniform(SLEEP_TIME - twenty_percent, SLEEP_TIME + twenty_percent))

    return results


@retry_curl()
def _request(
    query: str,
    filters: Filters | None,
    offset: int,
    proxy: Proxy | None,
) -> str:
    data: dict[str, Any] = {'q': f'{query} {filters.compile_filters() if filters else ""}'}

    if offset:
        data['s'] = offset - 1
        data['dc'] = offset

    if filters:
        if filters.time_span:
            data['df'] = filters.time_span.value
        if filters.region:
            data['kl'] = filters.region.value

    with curl.Session(proxy=proxy.to_httpx_proxy_url() if proxy else None) as session:
        resp = session.post(BASE_URL, data=data, headers=HEADERS)
        resp.raise_for_status()
        return resp.text


@retry_curl()
async def _async_request(
    query: str,
    filters: Filters | None,
    offset: int,
    proxy: Proxy | None,
) -> str:
    data: dict[str, Any] = {'q': f'{query} {filters.compile_filters() if filters else ""}'}

    if offset:
        data['s'] = offset - 1
        data['dc'] = offset

    if filters:
        if filters.time_span:
            data['df'] = filters.time_span.value
        if filters.region:
            data['kl'] = filters.region.value

    async with curl.AsyncSession(proxy=proxy.to_httpx_proxy_url() if proxy else None) as session:
        resp = await session.post(BASE_URL, data=data, headers=HEADERS)
        resp.raise_for_status()
        return resp.text
