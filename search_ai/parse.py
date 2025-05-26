from lxml import html
from urllib.parse import urlparse, parse_qs


RESULTS_XPATH = './/div[@class="ezO2md"][descendant::*[contains(@class, "fuLhoc")]]'
TITLE_XPATH = './/*[contains(@class, "fuLhoc")]'
SUB_TITLE_XPATH = './span[1]'
LINK_XPATH = './/a'
DESCRIPTION_XPATH = './/span[contains(@class, "FrIlee")]//span[@class="fYyStc" and normalize-space()]'


def parse_search(data):
    result_set = []

    tree = html.fromstring(data)
    results = tree.xpath(RESULTS_XPATH)

    for result in results:
        title_elem = result.xpath(TITLE_XPATH)
        if not title_elem:
            continue

        title_elem = title_elem[0]
        if title := title_elem.xpath(SUB_TITLE_XPATH):
            extracted_title = title[0].text
        else:
            extracted_title = title_elem.text

        link_elem = result.xpath(LINK_XPATH)[0].attrib['href']
        link = parse_qs(urlparse(link_elem).query).get('q')
        if not link:
            continue

        extracted_link = link[0].strip()

        description_elem = result.xpath(DESCRIPTION_XPATH)
        if description_elem:
            extracted_description = description_elem[0].text_content().strip()
        else:
            extracted_description = None

        result_set.append({'title': extracted_title, 'link': extracted_link, 'description': extracted_description})

    return result_set
