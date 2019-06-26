import datetime
import locale

from ..utils import parsed_html_doc


def get_name():
    return "Blox"


def get_url():
    return "http://www.blox-restaurant.cz/#!/page_obedy"


def get_menu():
    doc = parsed_html_doc(get_url())
    locale.setlocale(locale.LC_TIME, 'cs_CZ.UTF8')
    dayname = datetime.date.today().strftime("%A")
    rows = doc.xpath(
        '//*[@id="page_obedy"]//*[text() = "{}"]'
        '/ancestor::tr/following-sibling::tr'.format(dayname),
    )
    for meal in rows:
        cols = meal.findall("td")
        if len(cols) == 4:
            num, name, alergens, price = cols
        else:
            continue
        if num.text_content().strip() == "":
            return
        if (name is not None) and (price is not None):
            mealname = name.text_content().strip()
            if mealname:
                yield (mealname, price.text_content().strip())
