from lxml import html


LINK_TITLE_XPATH = '//a[@class="result-link" and not(ancestor::tr[@class="result-sponsored"])]'
DESCRIPTION_XPATH = '//td[@class="result-snippet" and not(ancestor::tr[@class="result-sponsored"])]'


def parse_search(data):
    results = []

    tree = html.fromstring(data)

    title_results = tree.xpath(LINK_TITLE_XPATH)
    desc_results = tree.xpath(DESCRIPTION_XPATH)

    assert len(title_results) == len(desc_results), 'Error parsing search results'

    for title, desc in zip(title_results, desc_results):
        results.append(
            {
                'title': title.text_content().strip(),
                'link': title.get('href'),
                'description': desc.text_content().strip(),
            }
        )

    return results
