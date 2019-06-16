# -*- coding: utf-8 -*-


from aparnik.settings import Setting

from . import humanize
from .num2words import num2word_FA


def format_price(price, price_format=None):
    formatted_price = ''
    price_value = price
    input_currency = {'%ic=r': 'r', '%ic=t': 't'}  # default system currency
    currency = {'%cu=r': 'ریال', '%cu=t': 'تومان', '%cu=': ''}  # desire currency
    seperator = {'%se=,': ',', '%se=/': '/', '%se=': ''}  # number seperator
    grouping = {'%gr=3': 3, '%gr=0': 0}  ##TODO: Custome number grouping for future
    precision = {'%pr=1': 1, "%pr=2": 2, '%pr=3': 3}  ##TODO: future feature
    translate = {'%tr=True': True, '%tr=False': False}  # 1200 -> ۱هزار و دویست
    abbriviation = {'%abbr=True': True, '%abbr=False': False}  # ۱۰۰۰۰۰۰۰-> ۱۰ میلیون تومان
    translate_str = {'%StrTr=True': True, '%StrTr=False': False}

    # check if function called with a price format parameter otherwise look in setting for price format
    if not price_format:
        try:
            price_format = Setting.objects.get(key='PRICE_FORMAT').get_value()
        except:
            price_format = str('%ic=t:%se=,:%cu=t:%gr=3:%tr=True:%abbr=True')

    price_format = list((str(x)) for x in price_format.split(':') if x)

    if get_parameter('%ic', price_format):
        if input_currency[get_parameter('%ic=', price_format)] == 'r' and get_parameter('%cu=',
                                                                                        price_format) == '%cu=t':
            price_value = price / 10

    if get_parameter('%cu', price_format):
        if get_parameter('%ic=', price_format) == '%ic=t' and get_parameter('%cu=',
                                                                            price_format) == '%cu=r':
            price_value = price * 10
        currency = currency[get_parameter('%cu=', price_format)]

    if get_parameter('%tr', price_format):
        if translate[get_parameter('%tr', price_format)]:
            # For value under 1000 algorithm returns jumbled words, need to fix
            if price_value >= 1000:
                formatted_price = num2word_FA.to_card(price_value)
                price = ''

    if get_parameter('%StrTr', price_format):
        if translate_str[get_parameter('%StrTr', price_format)]:
            formatted_price = num2word_FA.to_card_str(price_value)
            price = ''

    if get_parameter('%abbr', price_format):
        if abbriviation[(get_parameter('%abbr=', price_format))]:
            humanize.i18n.activate('fa_FA')
            formatted_price = str(humanize.intword(price_value, '%.3f'))
            price = ''

    if get_parameter('%gr', price_format):
        if get_parameter('%se', price_format):
            seperator = seperator[get_parameter('%se=', price_format)]
            humanize.i18n.activate('fa_FA')
            formatted_price = humanize.intcomma(price_value, seperator)
            price = ''

    if get_parameter('%price_str_abbriviation', price_format):
        formatted_price = num2word_FA.to_ord(price_value)

    return formatted_price + str(price) + ' ' + currency


# getting desired format parameter
def get_parameter(parameter, price_format):
    for word in price_format:
        if parameter in word:
            return word
    return False
