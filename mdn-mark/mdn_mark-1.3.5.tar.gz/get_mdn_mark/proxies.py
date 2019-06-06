import random
import json
import requests_html

from zoran_tools.zoran_tools import WithProgressBar
from zoran_tools.path_tools import ask_file


def random_proxy(ips) -> dict:
    ip = random.choice(ips)
    return {'https': 'https://' + ip, 'http': 'http://' + ip}


def choose_alive_proxy(ips):
    alive = []
    to_file = 'alive_ips.txt'
    for ip in WithProgressBar(ips):
        proxy = {'https': 'https://' + ip, 'http': 'http://' + ip}
        # url = 'https://www.sogou.com/reventondc/inner/vrapi?number={mdn}&type=json&callback=show&isSogoDomain=1'. \
        #     format(mdn='057486855016')
        url = 'https://m.so.com/s?q=18158450529'
        try:
            r = requests_html.HTMLSession().get(url, proxies=proxy, timeout=10)
            if r.status_code == 200:
                alive.append(ip)
        except:
            continue
    with open(to_file, mode='w') as f:
        f.write('\n'.join(alive))
    print('可用IP写入了{}'.format(to_file))


def proxies(file):
    with open(file, mode='r') as f:
        lines = f.readlines()
        return [line.strip('\n') for line in lines]


def open_proxy_file():
    ip_file = ask_file()
    with open(ip_file, mode='r') as f:
        lines = f.readlines()
        return [line.strip('\n') for line in lines]


def screen_alive_proxies():
    choose_alive_proxy(open_proxy_file())


if __name__ == '__main__':
    choose_alive_proxy()
