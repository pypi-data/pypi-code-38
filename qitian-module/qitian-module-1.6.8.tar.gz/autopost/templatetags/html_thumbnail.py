from django import template
from bs4 import BeautifulSoup

register = template.Library()


@register.filter
def html_first(value):
    soup = BeautifulSoup(value, 'lxml')
    first_img = soup.find('img')
    if not first_img:
        return None
    return first_img['src']
