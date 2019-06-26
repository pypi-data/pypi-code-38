import urllib.parse
import urllib.request

import lxml.html

_PLACES = {
    "Pod Juliskou": "https://www.podjuliskou.cz/menu/",
}


def get_name(place_id=None):
    return place_id or "Pod Juliskou"


def get_url(place_id=None):
    return _PLACES.get(get_name(place_id), "")


def get_menu(place_id=None):
    """Menu podle Obědáře"""

    url = "http://obedar.fit.cvut.cz/restaurants/{}".format(
        urllib.parse.quote(get_name(place_id)),
    )
    parser = lxml.html.HTMLParser(encoding="utf-8")
    doc = lxml.html.parse(urllib.request.urlopen(url), parser)
    for meal in doc.findall('//table/tr'):
        name = meal.find('td')
        price = meal.find('td[@class="price"]')
        if name is None or price is None:
            continue
        name, price = (el.text_content() for el in (name, price))
        yield (name, price)
