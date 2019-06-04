from ..utils import parsed_html_doc


def get_name(place_id=None):
    return "Potrefená husa"


def get_url(place_id=None):
    return "https://www.potrefene-husy.cz/cz/dejvice-poledni-menu"


def _get_menu_url(place_id):
    if place_id is None:
        place_id = "restaurace-praha-dejvice"
    return "https://www.staropramen.cz/hospody/" + place_id


def get_menu(place_id=None):
    doc = parsed_html_doc(_get_menu_url(place_id))
    for meal in doc.xpath(
        '//dt[@class="is-open"]/following-sibling::dd[1]'
        '/ul[@class="menu-list"]/li',
    ):
        name, price = (x.text_content().strip() for x in meal.findall('div'))
        if (name is not None) and (price is not None):
            yield (name, price)
