import time
import random
from typing import Literal

import httpx

from .filters import Filters


BASE_URL = 'https://www.google.com/search'


def search(
        query: str,
        mode: Literal['news'] | Literal['search'] = 'search',
        filters: Filters | None = None,
        length: int = 5,
        offset: int = 0,
        unique: bool = False,
        safe: bool = True,
        lang: str = 'en',
        region: str | None = None,
        proxy: str | None = None,
        sleep_time: int = 1
):
    assert mode in ('news', 'search'), '"mode" must be "news" or "search"'

    filters = filters.compile_filters() if filters else ''
    compiled_query = f'{query}{" " if filters else ""}{filters}'

    results = []
    result_set = set()

    while len(results) < length:
        response = _request(compiled_query, mode, length + 1, lang, offset, safe, region, proxy)
        response.raise_for_status()

        from .utils import parse_search
        new_results = parse_search(response.text)

        for new_result in new_results:
            if unique:
                if new_result.link in result_set:
                    continue
                else:
                    result_set.add(new_result.link)

            results.append(new_result)
            if len(results) == length:
                return results

        twenty_percent = sleep_time * .20
        time.sleep(random.uniform(sleep_time - twenty_percent, sleep_time + twenty_percent))

    return results

def _request(
        query: str,
        mode: Literal['news'] | Literal['search'],
        number: int,
        lang: str,
        offset: int,
        safe: bool,
        region: str | None,
        proxy: str | None
) -> httpx.Response:
    params = {
        'q': query,
        'num': number,
        'start': offset,
        'safe': safe,
        'hl': lang,
        'gl': region
    }

    if mode == 'news':
        params['tbm'] = 'nws'

    cookies = {
        'CONSENT': 'PENDING+987',
        'SOCS': 'CAESHAgBEhIaAB'
    }

    headers = {
        'Accept': 'text/html, text/plain, text/sgml, text/css, */*;q=0.01',
        'Accept-Encoding': 'gzip, compress, bzip2',
        'Accept-Language': 'en',
        'User-Agent': generate_useragent()
    }

    resp = httpx.get(BASE_URL, params=params, headers=headers, cookies=cookies, proxy=proxy)
    return resp


def generate_useragent():
    # Lynx: 2.8.5–2.9.2 or 3.0.0–3.2.0
    major = random.choice([2, 3])
    if major == 2:
        minor = random.randint(8, 9)
        patch = random.randint(0, 2)
    else:
        minor = random.randint(0, 2)
        patch = 0
    lynx_version = f"Lynx/{major}.{minor}.{patch}"

    # libwww-FM: realistically 2.14 ± small variance
    libwww_version = f"libwww-FM/{random.choice([13,14,15])}"

    # SSL-MM: pin around 1.4.x
    ssl_mm_version = f"SSL-MM/1.{random.randint(4,5)}.{random.randint(0,9)}"

    # OpenSSL: legacy 1.1.x or modern 3.x (3.4–3.5)
    openssl_major = random.choice([1, 3])
    if openssl_major == 1:
        openssl_minor = random.randint(0, 1)
    else:
        openssl_minor = random.randint(4, 5)
    openssl_patch = random.randint(0, 9)
    openssl_version = f"OpenSSL/{openssl_major}.{openssl_minor}.{openssl_patch}"

    return f"{lynx_version} {libwww_version} {ssl_mm_version} {openssl_version}"






