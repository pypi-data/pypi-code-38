# coding: utf-8
from bs4 import BeautifulSoup
import requests
from googlesearch import search
from urllib.parse import urlparse

BASE_URL = 'www.animelyrics.com'

def search(query):
    def __init__(self, query):
        results = search('site:{} {}'.format(BASE_URL, query), stop=10)
        if not results:
            return "No lyrics found"
        else:
            return results