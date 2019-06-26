import requests
from bs4 import BeautifulSoup
import re
import string
from datetime import datetime
from time import mktime
import pandas as pd
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from yahoo_fin import stock_info as si

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def getSETSymbols(sector = 'ALL'):
    if sector == 'ALL':
        symbols = []
        url = 'https://www.set.or.th/set/commonslookup.do?language=th&country=TH&prefix={{key}}'
        key = ['NUMBER']
        key.extend(list(string.ascii_uppercase))
        for k in key:
            r = requests.get(url.replace('{{key}}',k), verify=False)
            soup = BeautifulSoup(r.content, "html.parser")
            for i in soup.findAll('a', href=re.compile('.*companyprofile.*')):
                symbols.append(i.text)
        return symbols

    symbols = []
    url = 'https://marketdata.set.or.th/mkt/sectorquotation.do?sector=SET100&language=th&country=TH'
    if sector != 'SET100':
        url = url.replace('SET100', sector)
    r = requests.get(url, verify=False)
    soup = BeautifulSoup(r.content, "html.parser")
    for i in soup.findAll('a', href=re.compile('.*symbol.*')):
        symbols.append(i.text.strip())
    return symbols

def getSET100Price():
    url = 'https://marketdata.set.or.th/mkt/sectorquotation.do?sector=SET100&language=th&country=TH'
    r = requests.get(url, verify=False)
    soup = BeautifulSoup(r.content, "html.parser")
    for i in soup.findAll('caption'):
        timestamp = i.text
        timestamp = timestamp[timestamp.find('ข้อมูลล่าสุด'):].split()
        temp = timestamp[1].split('/')
        temp = temp[0] + '-' + temp[1] + '-' + str(int(temp[2]) - 543)
        timestamp = datetime.strptime(temp + ' ' + timestamp[2], '%d-%m-%Y %H:%M:%S')

    data = []
    for i in soup.findAll('a', href=re.compile('.*symbol.*')):
        children = i.parent.parent.findChildren("td", recursive=False)
        symbol = i.text.strip()
        price = float(children[9].text)
        data.append((symbol, price))

    return data, timestamp

def _get_crumbs_and_cookies(stock):
    url = 'https://finance.yahoo.com/quote/{}/history'.format(stock)
    with requests.session():
        header = {'Connection': 'keep-alive',
                  'Expires': '-1',
                  'Upgrade-Insecure-Requests': '1',
                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
                   AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
                  }

        website = requests.get(url, headers=header, verify=False)
        soup = BeautifulSoup(website.text, 'lxml')
        crumb = re.findall('"CrumbStore":{"crumb":"(.+?)"}', str(soup))

        return (header, crumb[0], website.cookies)


def convert_to_unix(date):
    datum = datetime.strptime(date, '%d-%m-%Y')
    return int(mktime(datum.timetuple()))


def getHistStock(stock, interval='1d', day_begin='01-03-2018', day_end='28-03-2018'):
    day_begin_unix = convert_to_unix(day_begin)
    day_end_unix = convert_to_unix(day_end)
    col = [1]
    while len(col)==1:
        header, crumb, cookies = _get_crumbs_and_cookies(stock)
        with requests.session():
            url = 'https://query1.finance.yahoo.com/v7/finance/download/' \
                  '{stock}?period1={day_begin}&period2={day_end}&interval={interval}&events=history&crumb={crumb}' \
                .format(stock=stock, day_begin=day_begin_unix, day_end=day_end_unix, interval=interval, crumb=crumb)
            website = requests.get(url, headers=header, cookies=cookies, verify=False)
            data = website.text.split('\n')[:-1]
            data = [d.split(',') for d in data]
            col = data[0]
            #print(col)
    data = pd.DataFrame(data[1:])
    data.columns = col
    data.set_index('Date', inplace=True)
    return data.apply(pd.to_numeric, downcast='float', errors='coerce')

def getLivePrice(stock):
    return si.get_live_price(stock)
