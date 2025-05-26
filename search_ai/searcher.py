import time
import random
import asyncio
from typing import Literal
from functools import partial

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from .proxy import Proxy
from .filters import Filters
from .parse import parse_search
from .utils import generate_useragent
from .search_result import SearchResult, SearchResults, AsyncSearchResult, AsyncSearchResults

BASE_URL = 'https://www.google.com/search'

retry_httpx = partial(
    retry,
    stop=stop_after_attempt(2),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(httpx.HTTPError),
    reraise=True,
)


def search(
    query: str = '',
    filters: Filters | None = None,
    mode: Literal['news'] | Literal['search'] = 'search',
    count: int = 10,
    offset: int = 0,
    unique: bool = False,
    safe: bool = True,
    region: str | None = None,
    proxy: Proxy | None = None,
    sleep_time: int = 0.5,
):
    assert mode in ('news', 'search'), '"mode" must be "news" or "search"'

    filters = filters.compile_filters() if filters else ''
    compiled_query = f'{query}{" " if filters else ""}{filters}'

    results = SearchResults(results=[], _proxy=proxy)
    result_set = set()

    while len(results) < count:
        adjusted_count = (count - len(results)) + 2  # Plus 2 because not all the results are links
        response = _request(compiled_query, mode, adjusted_count, offset, safe, region, proxy)

        new_results = parse_search(response)

        if not new_results:
            return results

        for new_result in new_results:
            if unique:
                if new_result['link'] in result_set:
                    continue
                else:
                    result_set.add(new_result['link'])

            results.append(SearchResult(**new_result, _proxy=proxy))
            if len(results) == count:
                return results

        offset += len(new_results)

        twenty_percent = sleep_time * 0.10
        time.sleep(random.uniform(sleep_time - twenty_percent, sleep_time + twenty_percent))

    return results


async def async_search(
    query: str = '',
    filters: Filters | None = None,
    mode: Literal['news'] | Literal['search'] = 'search',
    count: int = 10,
    offset: int = 0,
    unique: bool = False,
    safe: bool = True,
    region: str | None = None,
    proxy: Proxy | None = None,
    sleep_time: int = 0.5,
):
    assert mode in ('news', 'search'), '"mode" must be "news" or "search"'

    filters = filters.compile_filters() if filters else ''
    compiled_query = f'{query}{" " if filters else ""}{filters}'

    results = AsyncSearchResults(results=[], _proxy=proxy)
    result_set = set()

    while len(results) < count:
        adjusted_count = (count - len(results)) + 2  # Plus 2 because not all the results are links
        response = await _async_request(compiled_query, mode, adjusted_count, offset, safe, region, proxy)

        new_results = parse_search(response)

        if not new_results:
            return results

        for new_result in new_results:
            if unique:
                if new_result['link'] in result_set:
                    continue
                else:
                    result_set.add(new_result['link'])

            results.append(AsyncSearchResult(**new_result, _proxy=proxy))
            if len(results) == count:
                return results

        offset += len(new_results)

        twenty_percent = sleep_time * 0.10
        await asyncio.sleep(random.uniform(sleep_time - twenty_percent, sleep_time + twenty_percent))

    return results


def generate_request_params(
    query: str,
    mode: Literal['news'] | Literal['search'],
    number: int,
    offset: int,
    safe: bool,
    region: str | None,
    proxy: Proxy | None,
) -> tuple[dict, dict, dict, str | None]:
    params = {
        'q': query,
        'num': number,
        'start': offset,
        'safe': 'active' if safe else 'off',
    }

    if region:
        params['gl'] = region
    if mode == 'news':
        params['tbm'] = 'nws'

    cookies = {'CONSENT': 'PENDING+987', 'SOCS': 'CAESHAgBEhIaAB'}

    headers = {
        'Accept': 'text/html, text/plain, text/sgml, text/css, */*;q=0.01',
        'Accept-Encoding': 'gzip, compress, bzip2',
        'Accept-Language': 'en',
        'User-Agent': generate_useragent(),
    }

    httpx_proxy = proxy.to_httpx_proxy_url() if proxy else None

    return params, cookies, headers, httpx_proxy


@retry_httpx()
def _request(
    query: str,
    mode: Literal['news'] | Literal['search'],
    number: int,
    offset: int,
    safe: bool,
    region: str | None,
    proxy: Proxy | None,
) -> str:
    params, cookies, headers, httpx_proxy = generate_request_params(query, mode, number, offset, safe, region, proxy)
    with httpx.Client(proxy=httpx_proxy, headers=headers, cookies=cookies) as client:
        resp = client.get(BASE_URL, params=params)
        resp.raise_for_status()
        return resp.text


@retry_httpx()
async def _async_request(
    query: str,
    mode: Literal['news'] | Literal['search'],
    number: int,
    offset: int,
    safe: bool,
    region: str | None,
    proxy: Proxy | None,
) -> str:
    params, cookies, headers, httpx_proxy = generate_request_params(query, mode, number, offset, safe, region, proxy)
    async with httpx.AsyncClient(proxy=httpx_proxy, headers=headers, cookies=cookies) as client:
        resp = await client.get(BASE_URL, params=params)
        resp.raise_for_status()
        return resp.text
