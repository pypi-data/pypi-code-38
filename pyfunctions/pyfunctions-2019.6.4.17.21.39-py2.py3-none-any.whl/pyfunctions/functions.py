import os
import datetime
import time
import random
import glob
import shutil
import json
import chardet
import requests
import html2text
import w3lib.url  # import w3lib 报错
import w3lib.encoding
import fake_useragent
from lxml.html import etree
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def make_useragent():
    """获取useragents并保存到本地，返回UserAgent对象"""
    version = fake_useragent.VERSION
    resp = requests.get("https://fake-useragent.herokuapp.com/browsers/" + version)
    useragent_filename = "fake_useragent.json"
    if not os.path.exists(useragent_filename):
        with open(useragent_filename, "w") as f:
            json.dump(resp.json(), f)
    return fake_useragent.UserAgent(path=useragent_filename)


ua = make_useragent()


def query_param(url, param):
    """查找url中的某个参数的值"""
    value = w3lib.url.url_query_parameter(url, param)
    return value or ""


def generate_url(url, key, value):
    """通过修改url参数生成url, 常用于生成页数"""
    return w3lib.url.add_or_replace_parameter(url, key, value)


def generate_urls(url, key, start, end):
    """生成一系列页面链接, start为开始page no, end为结束page no"""
    return [generate_url(url, key, value) for value in range(start, end + 1)]


def random_sleep(max_sleep_time):
    """随机sleep"""
    time.sleep(random.random() * max_sleep_time)


def html2tree(html):
    """将html转为tree"""
    try:
        return etree.HTML(html)
    except:
        return


def resp2html(response):
    """获取response的html 自动处理了encoding"""
    content_type = response.headers.get("content-type")
    auto_detect_fun = lambda x: chardet.detect(x).get("encoding")
    _, html = w3lib.encoding.html_to_unicode(
        content_type, response.content, auto_detect_fun=auto_detect_fun
    )
    return html


def resp2json(resp):
    """获取response的数据"""
    try:
        return resp.json()
    except:
        return {}


def get_url(url, timeout=5, **kwargs):
    """requests get封装"""
    try:
        if "headers" in kwargs:
            kwargs["headers"].update({"User-Agent": ua.random})
        return requests.get(url, timeout=timeout, **kwargs)
    except:
        return


def post_data(url, data, **kwargs):
    """requests post封装"""
    try:
        if "headers" in kwargs:
            kwargs["headers"].update({"User-Agent": ua.random})
        return requests.post(url, json=data, **kwargs)
    except:
        return


def url2tree(url, **kwargs):
    """请求url到转化为etree的全部过程封装"""
    resp = get_url(url, **kwargs)
    html = resp2html(resp)
    return html2tree(html)


def url2text(url, **kwargs):
    """访问url，并返回经过html2text处理过的text"""
    resp = get_url(url, **kwargs)
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    return h.handle(resp2html(resp))


def load_cookies(filename):
    """从文件中加载cookie"""
    cookies = {}
    with open(filename, "r") as f:
        for item in json.loads(f.read()):
            cookies.update({item["name"]: item["value"]})
    return cookies


def make_driver(driver="chrome", load_img=False):
    """只支持chrome和phantomjs"""
    driver = driver.lower()
    if driver == "phantomjs":
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
        dcap["phantomjs.page.settings.loadImages"] = load_img
        d = webdriver.PhantomJS(desired_capabilities=dcap)
    elif driver == "chrome":
        # 创建chrome并配置
        ops = webdriver.ChromeOptions()
        ops.add_argument("--headless")
        ops.add_argument("--no-sandbox")
        ops.add_argument("--disable-gpu")
        ops.add_argument("--start-maximized")
        # ops.add_argument('--incognito')
        ops.add_argument("lang=zh_CN")
        if load_img is False:
            prefs = {"profile.managed_default_content_settings.images": 2}
            ops.add_experimental_option("prefs", prefs)
        # 解决window.navigator.webdriver=True的问题
        # https://wwwhttps://www.cnblogs.com/presleyren/p/10771000.html.cnblogs.com/presleyren/p/10771000.html
        ops.add_experimental_option("excludeSwitches", ["enable-automation"])
        ops.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"')
        try:
            # selenium兼容问题
            d = webdriver.Chrome(options=ops)
        except:
            d = webdriver.Chrome(chrome_options=ops)
    else:
        raise ValueError(
            "Unknown argument %s. Support chrome and phantomjs only." % driver
        )
    d.set_window_size(1024, 786)
    return d


def generate_cookies_dir():
    """生成cookies文件"""
    today = datetime.date.today()
    today_cookies_dir = "cookies-" + str(today)
    # 匹配文件夹
    old_cookies_dirs = glob.glob("cookies-*")
    # 如果不存在今天的，就新建今天的文件夹
    if today_cookies_dir in old_cookies_dirs:
        old_cookies_dirs.remove(today_cookies_dir)
    else:
        os.mkdir(today_cookies_dir)
    # 删除过期cookies
    # 使用os.removedirs报错
    for old_cookies in old_cookies_dirs:
        shutil.rmtree(old_cookies)

    return today_cookies_dir


def save_response_content(response, output_file):
    """save response as a png file"""
    with open(output_file, "wb") as f:
        f.write(response._content)
