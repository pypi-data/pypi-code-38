import json
import requests

from django import template
from django.conf import settings

register = template.Library()


@register.filter()
def google_short_url(long_url):
    try:
        api_key = settings.GOOGLE_API_KEY
        url = 'https://www.googleapis.com/urlshortener/v1/url?key=%s' % api_key
        headers = {'Content-Type': 'application/json'}
        payload = {"longUrl": long_url}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        return r.json().get('id', '')
    except Exception as e:
        return ''
