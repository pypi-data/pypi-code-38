from ..utils import killwhitespace, parsed_html_doc

_BASE_URL = "https://agata.suz.cvut.cz/jidelnicky/index.php?clPodsystem={}"


def get_url(place_id=None):
    return _BASE_URL.format(place_id or "5")


def get_name(place_id=None):
    doc = parsed_html_doc(get_url(place_id))
    h3 = doc.find('//h3')
    if h3 is not None:
        return h3.text_content()
    else:
        return "Neznámá menza"


def get_menu(place_id=None):
    doc = parsed_html_doc(get_url(place_id))
    for meal in doc.findall(
        '//div[@id="jidelnicek"]/div[@class="data"]'
        '/table//tr',
    ):
        tds = meal.findall('td')
        if len(tds) == 0:
            continue
        name = tds[2].text
        price = tds[6].text
        place = tds[7].text_content()
        name, price, place = (killwhitespace(s) for s in (name, price, place))
        if name is "" or name is ".":
            continue
        if place:
            name = "{} ({})".format(name, place)
        yield (name, price)
