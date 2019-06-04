import datetime
import locale

from ..utils import parsed_html_doc


def get_name():
    return "Kulaťák"


def get_url():
    return "https://www.kulatak.cz/"


def get_menu():
    doc = parsed_html_doc(get_url())
    locale.setlocale(locale.LC_TIME, 'cs_CZ.UTF8')
    dayname = datetime.date.today().strftime("%A")
    for meal in doc.xpath('//div[@id="daily_menu"]/table/tbody/tr/td'
                          '/strong[contains(.,"{}")]/../..'
                          '/../*'.format(dayname)):
        cells = meal.findall('td')
        if len(cells) != 3:
            continue
        x, name, price = cells
        if (name is not None) and (price is not None):
            yield (
                name.text_content().strip().capitalize(),
                price.text_content().strip(),
            )
