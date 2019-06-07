"""
Program's aim is to get tables from a given html
Pure functional.
"""
import urllib.parse
from bs4 import BeautifulSoup

def _get_soup(html, elem):
    """
    Soup html element
    :param html:
    :param elem:
    :return:
    """
    soup = BeautifulSoup(html)
    tables = soup.findAll(elem)
    return tables


def _get_fixed_soup(html):
    """
    Fix the soup
    :param html:
    :return:
    """
    tables = _get_soup(html, 'table')
    if tables is not None and len(tables) > 0:
        return tables
    # Sometime we get just tr td, in a small html snippet.
    trs = _get_soup(html, 'tr')
    if trs is not None:
        return _get_soup("<table>" + html + "</table>", 'table')
    return None


def _get_header_cells(soup):
    all_th = []
    th = soup('th')
    for i in th:
        all_th.append(i.text)
    return all_th


def _get_caption_cells(soup):
    all_th = []
    th = soup('caption')
    for i in th:
        all_th.append(i.text)
    return all_th


def get_table(html):
    """
    :param html: html of a page.
    :return: (number of tables found, {'header' : top_row, 'data' : other_rows})
    """
    all_tables = []
    soup = _get_fixed_soup(html)
    if not soup:
        return 0, None

    count = 0
    if type(soup) == list:
        for s in soup:
            rows = [[cell.text for cell in row("td")]
                         for row in s("tr")]
            count = count + 1
            first_row = _get_header_cells(s)
            caption = _get_caption_cells(s)
            all_tables.append({'header' : first_row, 'data': rows, 'title': caption})
    else:
        rows = [[cell.text for cell in row("td")]
                         for row in soup("tr")]
        count = count + 1
        first_row = _get_header_cells(soup)
        caption = _get_caption_cells(soup)
        all_tables.append({'header' : first_row, 'data': rows, 'title': caption})
    return count, all_tables


def get_table_with_links(html, base_url):
    """
    Fetch all tables in the html that contain links,
    returns a list of dictionaries with {header : [], data : [[]], num_links : 4}
    :param html:
    :return:
    """
    all_tables = []
    soup = _get_fixed_soup(html)
    if not soup:
        return 0, None

    count = 0
    if type(soup) == list:
        for s in soup:
            rows = [[cell.text for cell in row("td")]
                    for row in s("tr")]
            links = [[_fix_url(cell, base_url) for cell in row("td")]
                    for row in s("tr")]
            count = count + 1
            first_row = _get_header_cells(s)
            caption = _get_caption_cells(s)
            all_tables.append({'header': first_row, 'data': rows, 'title': caption, 'links': links})
    else:
        rows = [[cell.text for cell in row("td")]
                for row in soup("tr")]

        links = [[cell.findAll('a') for cell in row("td")]
                 for row in soup("tr")]
        count = count + 1
        first_row = _get_header_cells(soup)
        caption = _get_caption_cells(soup)
        all_tables.append({'header': first_row, 'data': rows, 'title': caption, 'links' : links})
    return count, all_tables


def _fix_url(soup, base_url):
    # extract url from url_raw
    aa = soup.findAll("a")
    a_href = None
    for a in aa:
        try:
            a_href_rel = a['href']
            a_href = urllib.parse.urljoin(base_url, a_href_rel)
        except Exception as e:
            continue
    return a_href

if __name__ == "__main__":
    import requests
    base_url = "http://www.jreda.com/tenders/tenders.htm"
    r = requests.get(base_url)
    num, tables = get_table_with_links(r.content, base_url)
    print(num)
    for table in tables:
        for link in table["links"]:
            print(link)