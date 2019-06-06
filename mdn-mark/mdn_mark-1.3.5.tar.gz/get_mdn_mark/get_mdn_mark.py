"""
request the mdn marks or labels from baidu.com, so.com, sogou.com
auth: chenzhongrun
mail: chenzhongrun@bonc.com
com: bonc
release data: 2019-0529

Usage:

$ mdn-mark
    -s --360                采集360
    -b --baidu              采集百度
    -g --sogou              采集搜狗
    -a --sogou-api          采集搜狗API

    --file xx.csv           指定要采集的号码列表文件，无此参数则以对话方式请求列表文件

    -i                      打开对话框请求打开代理IP文件
    --ip-file xx.txt        指定代理IP文件

    --check-ip              筛选代理IP文件中的可用IP(同$ screen-ips)

$ screen-ips                筛选代理IP文件中的可用IP

"""


import logging; logging.basicConfig(level=logging.INFO)
import time
import json
import csv
import sys
import os
import re
# import getopt
from typing import Callable
from threading import Thread
# from multiprocessing import Process

import requests_html
from zoran_tools.csv_tools import write_csv_row
from zoran_tools.path_tools import ask_file
from zoran_tools.zoran_tools import WithProgressBar
from zoran_tools.json_tools import jsonp_to_json
from zoran_tools.log import Logger

try:
    from .proxies import random_proxy, proxies, screen_alive_proxies
except:
    from proxies import random_proxy, proxies, screen_alive_proxies


# constant val
SOURCES = {
    'baidu': {
        'name': '百度手机卫士',
        'url_pat': 'https://m.baidu.com/s?ie=UTF-8&wd={mdn}',
        'unsuccessful': ['采集失败', 'null', 'null', '百度手机卫士'],
    },
    '360': {
        'name': '360手机卫士',
        'url_pat': 'https://m.so.com/s?q={mdn}',
        'unsuccessful': ['采集失败', 'null', '360手机卫士'],
    },
    'sogou': {
        'name': '搜狗号码通',
        'url_pat': 'https://www.sogou.com/tx?query={mdn}',
        'unsuccessful': ['采集失败', '搜狗号码通'],
    },
    'sogou_api': {
        'name': '搜狗号码通',
        'url_pat': 'https://www.sogou.com/reventondc/inner/vrapi?number={mdn}&type=json&callback=show&isSogoDomain=1',
        'unsuccessful': ['采集失败', '搜狗号码通API'],
    }
}


# init val
start_time = time.strftime('%Y%m%d_%H%M%S')
failed = []
IPs = []
USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Mobile Safari/537.36'
USE_PROXY = False


def generate_to_filename(from_filename: str, source: str='result') -> str:
    # generate a new file name for writing data by from file name
    prefix, suffix = os.path.splitext(from_filename)
    return '{prefix}.{source}.{time}{suffix}'.format(prefix=prefix, time=start_time, suffix=suffix, source=source)


def open_csv_utils(from_filename: str) -> list:
    # a utils function to open a csv file
    with open(from_filename, mode='r', encoding='utf8') as f:
        fr_csv = csv.reader(f)
        return list(fr_csv)


def down(url: str, retry_times: int=3) -> (requests_html.HTMLResponse, bool):
    # request the url for downloading response
    ip_proxies = USE_PROXY
    try:
        ss = requests_html.HTMLSession()
        ss.headers['User-Agent'] = USER_AGENT

        # use the local ip to request at the last time
        if retry_times == 0:
            ip_proxies = False
        if ip_proxies:
            ss.proxies = random_proxy(ips=IPs)
        r = ss.get(url, timeout=10)
        if r.status_code == 200:
            return r, True
        if retry_times > 0:
            return down(url, retry_times - 1)
        return None, False
    except BaseException:
        if retry_times:
            return down(url, retry_times - 1)
        return None, False


def parse_baidu(r: requests_html.HTMLResponse) -> [str] * 4:
    # parse label from baidu.com
    # label = r.html.xpath('//span[contains(@class, "op_fraudphone_label")]/text()')
    # label = re.sub('\s', '', ''.join(label))
    # cnt = r.html.xpath('//div[@class="op_fraudphone_word"]/text()')
    # cnt = ''.join(cnt)
    # cnt = re.findall('(\d+)', cnt)
    # cnt = cnt[0] if cnt else '0'
    # source = r.html.xpath('//div[@class="op_fraudphone_word"]/a/text()')
    # source = re.sub('\s', '', ''.join(source))
    # child = r.html.xpath('//div[@class="op_fraudphone_word"]/strong/text()')
    # child = re.sub('"|\s', '', ''.join(child))
    #
    # if label:
    #     return [label, child, cnt, source]
    # else:
    #     return ['未标记', '-', '0', '百度手机卫士']

    label: list = r.html.xpath('//div[@class="c-container"]//i/text()')
    if not label:
        return ['未标记', '-', '0', '百度手机卫士']
    label: str = ''.join(label)
    label = re.sub('\s', '', label)

    info: list = r.html.xpath('//div[@class="c-container"]//p[@class="c-color-gray"]//text()')
    info: str = ''.join(info)
    pat = re.compile('被(?P<cnt>\d+)个(?P<source>.*)用户标记为"(?P<mark>.*)"')
    info: list = pat.findall(info)
    if info:
        cnt, source, child = info[0]
    else:
        cnt, source, child = ('0', '百度手机卫士', '-')
    return [label, child, cnt, source]


def parse_360(r: requests_html.HTMLResponse) -> [str] * 3:
    # parse label from 360.com
    # mark = r.html.xpath('//span[@class="mohe-ph-mark"]/text()')
    # cnt = r.html.xpath('//span[./a[@class="mohe-sjws"]]/b/text()')
    # mark = re.sub('\s', '', ''.join(mark))
    # cnt = re.sub('\s', '', ''.join(cnt))
    # if mark:
    #     return [mark, cnt, '306手机卫士']
    # else:
    #     return ['未标记', '0', '306手机卫士']

    title = ''.join(r.html.xpath('//title/text()'))
    if '异常' in title:
        logging.error('访问异常出错： {}'.format(title))
        return sys.exit(1)

    mark = r.html.xpath('//div[@class="mh-tel-mark"]/text()')
    mark = ''.join(mark)
    mark = re.sub('\s', '', mark)
    if not mark:
        return ['未标记', '0', '306手机卫士']
    cnt_info: list = r.html.xpath('//div[contains(@class, "g-flex-item")]//text()')
    cnt_info: str = ''.join(cnt_info)
    pat = re.compile('.*此号码近期被(\\d+)位360手机卫士用户标记.*')
    cnt: list = pat.findall(cnt_info)
    if cnt:
        cnt: str = next(e for e in cnt if e)
    else:
        cnt = '0'
    return [mark, cnt, '306手机卫士']


def parse_sogou(r: requests_html.HTMLResponse) -> [str] * 2:
    # parse label from sogou.com
    label = re.findall('号码通用户数据：(.*)：', r.html.text)
    label = re.sub('\s', '', ''.join(label))
    if label:
        return [label, '搜狗号码通']
    else:
        return ['未标记', '搜狗号码通']


def parse_sogou_api(r: requests_html.HTMLResponse) -> [str] * 2:
    s = jsonp_to_json(r.html.text)
    try:
        j: dict = json.loads(s)
        info = j.get('NumInfo')
        mark = re.match('^号码通用户数据：(.*)：.*', info)
        if mark:
            mark = mark.groups()[0]
            return [mark, '搜狗号码通API']
        else:
            return ['未标记', '搜狗号码通API']
    except Exception:
        return ['采集失败', '搜狗号码通']


def crawl_from(mdn: str, parser: Callable[[requests_html.HTMLResponse], list],
               source: dict) -> [str]:
    # to download and parse info from some platform
    url = source.get('url_pat').format(mdn=mdn)
    r, ok = down(url)
    if ok:
        return parser(r)
    else:
        return source.get('unsuccessful')


def crawl_from_baidu(mdn: str) -> [str]:
    # a shortcut for crawling from baidu
    return crawl_from(mdn=mdn, parser=parse_baidu, source=SOURCES.get('baidu'))


def crawl_from_360(mdn: str) -> [str]:
    # a shortcut for crawling from 360
    return crawl_from(mdn=mdn, parser=parse_360, source=SOURCES.get('360'))


def crawl_from_sogou(mdn: str) -> [str]:
    # a shortcut for crawling from sogou
    return crawl_from(mdn=mdn, parser=parse_sogou, source=SOURCES.get('sogou'))


def crawl_from_sogou_api(mdn: str) -> [str]:
    # a shortcut for crawling from sogou
    return crawl_from(mdn=mdn, parser=parse_sogou_api, source=SOURCES.get('sogou_api'))


def crawl_task(from_file: str, crawling_rows: list, source: str, crawler: Callable[[str], list]):
    # a task for threading to crawl from some source
    to_file = generate_to_filename(from_file, source)
    logger = Logger(source)
    logger.time(). \
        info('正在从 {source} 下载号码标注. 采集结果将会实时写入 {file}'.
             format(source=source, file=to_file))

    for row in WithProgressBar(crawling_rows):
        mdn = row[0]
        res = crawler(mdn)
        write_csv_row(to_file, row + res)

    logger.time().info('任务完成. 结果写入了文件：{}'.format(to_file))


def threading_main(argv=sys.argv[1:]):
    # with multi threading
    # print(argv)
    ip_file = None
    to_crawl_baidu = False
    to_crawl_360 = False
    to_crawl_sogou = False
    to_crawl_sogou_api = False

    from_file = None

    global USE_PROXY
    global IPs

    # 检查传入参数
    if isinstance(argv, (list, tuple)):

        if '-h' in argv or '--help' in argv:
            print(__doc__)
            sys.exit(0)

        # 筛选可用IP，而不是进行采集
        if '--check-ip' in argv:
            return screen_alive_proxies()

        # 检查是否指定文件名
        if '--file' in argv:
            try:
                from_file = argv[argv.index('--file') + 1]
                assert re.match('.*\.csv', from_file) is not None
            except IndexError:
                logging.error('没有正确指定文件')
            except AssertionError:
                logging.warning('指定的文件不是CSV文件')

        # 检查是否要使用IP代理，
        # -i表示以对话框形式请求用打开一个包含IP列表的文件，
        # --ip-file表示在命令行中设定参数指定IP列表文件
        if '-i' in argv:
            print('请打开一个IP文件')
            ip_file = ask_file()
            if not ip_file:
                sys.exit(1)
            USE_PROXY = True
        elif '--ip-file' in argv:
            try:
                ip_file = argv[argv.index('--ip-file') + 1]
                USE_PROXY = True
            except IndexError:
                logging.error('没有正确指定文件')

        # 检查要采集的源，
        # -b：百度，
        # -s：360（so.com）
        # -g：搜狗
        # -a：搜狗API
        if '-b' in argv or '--baidu' in argv:
            to_crawl_baidu = True
        if '-s' in argv or '--360' in argv:
            to_crawl_360 = True
        if '-g' in argv or '--sogou' in argv:
            to_crawl_sogou = True
        if '-a' in argv or '--sogou-api' in argv:
            to_crawl_sogou_api = True

    # 如果不指定采集源，则都进行采集
    if len(argv) == 0:
        to_crawl_baidu = True
        to_crawl_360 = True

    # 修改IP代理中的IP，应当传入合法的路径
    if ip_file:
        IPs = proxies(ip_file)  # global var

    # 如果此前没有获取电话号码列表文件，则以交互方式请求用户打开一个文件
    if not from_file:
        logging.info('请打开要采集的号码CSV文件')
        from_file = ask_file()

    logging.info('正在读取文件 {}'.format(from_file))
    rows = open_csv_utils(from_file)
    logging.info('文件中有 {} 行待采集.'.format(len(rows)))
    if not rows:
        logging.warning('文件中不存在行, 程序退出!')
        sys.exit(1)

    # multi processing or multi threading ?
    tasks = []
    if to_crawl_baidu:
        task_baidu = Thread(target=crawl_task, args=(from_file, rows, 'baidu', crawl_from_baidu))
        tasks.append(task_baidu)
    if to_crawl_360:
        task_360 = Thread(target=crawl_task, args=(from_file, rows, '360', crawl_from_360))
        tasks.append(task_360)
    if to_crawl_sogou:
        task_sogou = Thread(target=crawl_task, args=(from_file, rows, 'sogou', crawl_from_sogou))
        tasks.append(task_sogou)
    if to_crawl_sogou_api:
        task_sogou_api = Thread(target=crawl_task, args=(from_file, rows, 'sogou_api', crawl_from_sogou_api))
        tasks.append(to_crawl_sogou_api)

    # task_baidu = Process(target=crawl_task, args=(from_file, rows, 'baidu', crawl_from_baidu))
    # task_360 = Process(target=crawl_task, args=(from_file, rows, '360', crawl_from_360))
    # task_sogou = Process(target=crawl_task, args=(from_file, rows, 'sogou', crawl_from_sogou))
    # task_sogou_api = Process(target=crawl_task, args=(from_file, rows, 'sogou_api', crawl_from_sogou_api))
    for task in tasks:
        time.sleep(2)
        task.start()
    for task in tasks:
        task.join()


if __name__ == '__main__':
    # main()
    threading_main(sys.argv[1:])
