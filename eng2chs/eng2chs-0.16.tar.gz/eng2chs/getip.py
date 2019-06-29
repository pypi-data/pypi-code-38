from bs4 import BeautifulSoup
import requests
import random
import socket
import urllib.request

def get_ip():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }
    url = 'http://www.xicidaili.com/nn/'
    web_data = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        ip_list.append(tds[1].text + ':' + tds[2].text)

    proxy_list = []
    for ip in ip_list:
        proxy_list.append('http://' + ip)
    proxies = []
    i = 0
    for ip in proxy_list:
        proxies.append([i, ip])
        i = i + 1
    # proxies = dict(proxies)
    text = ''
    for ip in proxies:
        text = text + ip[1] +'\n'
    f = open('ip.txt', 'w')
    f.write(text)
    f.close()
    return proxies






