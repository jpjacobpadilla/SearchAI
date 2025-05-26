import random
import mimetypes

import html2text
from lxml import html, etree


def extract_metadata(page_source: str) -> dict:
    try:
        tree = html.fromstring(page_source)
    except Exception:
        return {}

    page_title = tree.xpath('//head/title/text()')
    page_description = tree.xpath('//head/meta[@name="description"]/@content')
    author = tree.xpath('//head/meta[@name="author"]/@content')
    twitter_handle = tree.xpath('//head/meta[@name="twitter:site"]/@content')

    result = {}

    if page_title:
        result['title'] = page_title[0]
    if page_description and valid_description_metadata(page_description[0]):
        result['description'] = page_description[0]
    if author:
        result['author'] = author[0]
    if twitter_handle:
        result['twitter'] = twitter_handle[0]

    return result


def valid_description_metadata(desc: str) -> bool:
    try:
        etree.fromstring(desc)
        return False
    except etree.XMLSyntaxError:
        return True


def generate_markdown(page_source: str, ignore_links: bool, ignore_images: bool) -> str:
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = ignore_links
    text_maker.ignore_images = ignore_images
    text_maker.body_width = 0  # Prevent automatic wrapping
    return text_maker.handle(page_source).strip()


def valid_type(url: str) -> bool:
    """
    Currently, only text / html pages are supported for extended data retrival.
    """
    mime, _ = mimetypes.guess_type(url)
    return mime in ('text/html', 'text/plain', 'application/xhtml+xml', None)


def generate_useragent() -> str:
    """
    Returns a Lynx browser User Agent string.

    The idea to use the Lynx browser User Agent was from
    the following GitHub project: https://github.com/Nv7-GitHub/googlesearch

    Returns:
        str: A User Agent string for the Lynx browser.
    """

    # Lynx: 2.8.5–2.9.2 or 3.0.0–3.2.0
    major = random.choice([2, 3])
    if major == 2:
        minor = random.randint(8, 9)
        patch = random.randint(0, 2)
    else:
        minor = random.randint(0, 2)
        patch = 0
    lynx_version = f'Lynx/{major}.{minor}.{patch}'

    # libwww-FM: realistically 2.14 ± small variance
    libwww_version = f'libwww-FM/{random.choice([13, 14, 15])}'

    # SSL-MM: pin around 1.4.x
    ssl_mm_version = f'SSL-MM/1.{random.randint(4, 5)}.{random.randint(0, 9)}'

    # OpenSSL: legacy 1.1.x or modern 3.x (3.4–3.5)
    openssl_major = random.choice([1, 3])
    if openssl_major == 1:
        openssl_minor = random.randint(0, 1)
    else:
        openssl_minor = random.randint(4, 5)
    openssl_patch = random.randint(0, 9)
    openssl_version = f'OpenSSL/{openssl_major}.{openssl_minor}.{openssl_patch}'

    return f'{lynx_version} {libwww_version} {ssl_mm_version} {openssl_version}'
