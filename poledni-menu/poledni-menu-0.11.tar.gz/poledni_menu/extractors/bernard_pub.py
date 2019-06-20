import datetime

from ..utils import parsed_html_doc


def get_url(place_id=None):
    return "https://www.bernardpub.cz/pub/" + (place_id or "andel")


def get_name(place_id=None):
    doc = parsed_html_doc(get_url(place_id))
    title = doc.find('/head/title')
    if title is not None:
        return title.text_content()
    else:
        return "Neznámý Bernard Pub"


def get_menu(place_id=None):
    doc = parsed_html_doc(get_url(place_id))
    tabs = doc.xpath(
        '//section[@class="daily-menu"]'
        '//ul[@class="day-selection"]/li'
        '/span[text()="{0.day}. {0.month}."]/..'.format(
            datetime.date.today(),
        ),
    )
    if len(tabs) < 1:
        raise ValueError("Na dnešek není vystaveno menu")

    dm = doc.findall('//div[@id="{}"]//div[@class="single-food"]'.format(
        tabs[0].get('data-tab-target'),
    ))
    for meal in dm:
        name = meal.find('strong')
        price = meal.find('span[@class="food-price"]')
        if (name is not None) and (price is not None):
            mealname = name.text_content().strip().capitalize()
            if mealname:
                yield (mealname, price.text_content().strip())
