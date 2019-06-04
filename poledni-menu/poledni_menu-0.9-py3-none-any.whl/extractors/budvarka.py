import string
import urllib.request

import lxml.html


def get_name():
    return "Budvarka"


def get_url():
    return "https://dejvice.pivnice-budvarka.cz/"


def get_menu():
    # They don't have HTTP-EQUIV meta tag with encoding
    parser = lxml.html.HTMLParser(encoding="utf-8")
    doc = lxml.html.parse(urllib.request.urlopen(get_url()), parser)
    menus = doc.xpath('//div[@id="menu-daily"]//dl/dt[@class="menu-item"]')
    for dt in menus:
        name = dt.find('span[@class="name"]').text
        name = name.strip(" " + string.punctuation)
        price = ""
        desc = ""
        dd = dt.getnext()
        while dd is not None and dd.tag == "dd":
            if dd.get("class") == "price":
                price = dd.text
            elif dd.get("class") == "description":
                desc = dd.text.strip()
            dd = dd.getnext()
        yield (" ".join([name, desc]), price)
