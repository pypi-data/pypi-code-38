#!/usr/bin/env python3.5
"""Torrentmirror python interface."""
import warnings
import logging
from collections import defaultdict
from delver import Crawler

warnings.filterwarnings("ignore")

DEFAULT_NAMES = ('rarbg', 'kickass-torrents')


def get_links(craw, url, filter_offline):
    """Extract links."""
    craw.open(url)
    for link in craw.css('.proxy-name>a'):
        status = link.getparent().getparent().cssselect(
            'img[class!=loading-link]')
        if status and status[0].attrib.get('class'):
            status = status[0].attrib['class'].replace('-link', '')
            if not filter_offline or status == 'online':
                yield link.attrib['href'], status


def get_proxies(url="https://www.torrentmirror.net", filter_offline=True):
    """Manage complete search for specified pages."""
    p_url = f'{url}/proxy/'
    craw = Crawler()
    craw.open(url)
    names = [
        name.attrib['href'].replace(p_url, '')
        for name in craw.css('a.proxy-item')
    ]
    return {n: get_links(craw, f'{p_url}{n}', filter_offline) for n in names}


def get_proxies_for(url="https://www.torrentmirror.net",
                    filter_offline=True,
                    names=DEFAULT_NAMES):
    """Manage complete search for specified pages."""
    p_url = f'{url}/proxy/'
    craw = Crawler()
    return {n: get_links(craw, f'{p_url}{n}', filter_offline) for n in names}


def main():
    """Entry point."""
    for name, links in get_proxies().items():
        print(f"Links for {name}")
        for link, status in links:
            print(f'{link} | {status}')
