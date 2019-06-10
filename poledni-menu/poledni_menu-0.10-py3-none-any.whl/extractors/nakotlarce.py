import datetime
import locale

from ..utils import parsed_html_doc


def get_url():
    return "https://nakotlarce.cz/poledni-menu/"


def get_name():
    return "Bernard Pub Na Kotlářce"


def get_menu():
    doc = parsed_html_doc(get_url())
    locale.setlocale(locale.LC_TIME, 'cs_CZ.UTF8')
    dayname = datetime.date.today().strftime("%A")
    daylink = doc.xpath('//h4[text() = "{}"]/parent::a/@href'.format(dayname),)
    if len(daylink) < 1:
        raise ValueError("Jídelní lístek nenalezen")
    daylink = daylink[0][1:]
    meals = doc.findall('//*[@id="{}"]//tr'.format(daylink))
    for meal in meals:
        if len(meal) != 2:
            continue
        name, price = [x.text_content().strip() for x in meal.getchildren()]
        if not price.endswith("Kč"):
            continue
        yield (name, price)
