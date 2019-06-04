import datetime

from ..utils import parsed_html_doc


def get_name():
    return "Avantgardino"


def get_url():
    return "https://www.avantgardino.cz/"


def get_menu():
    doc = parsed_html_doc(get_url())
    rows = doc.xpath(
        '//div[@class="dennimenu"]'
        '/h3[contains(text(), "{0.day}. {0.month}")]'
        '/../table/tbody/tr'.format(
            datetime.date.today(),
        ),
    )
    for meal in rows:
        cols = meal.findall("td")
        if len(cols) == 3:
            weight, name, price = cols
        else:
            continue
        if (name is not None) and (price is not None):
            mealname = name.text_content().strip().capitalize()
            if mealname:
                yield (mealname, price.text_content().strip())
