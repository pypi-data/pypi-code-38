import random
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zhulong.util.etl import est_meta,est_html,add_info
from zhulong.util.fake_useragent import UserAgent

_name_="cixi"


columnid = None
unitid = None

def f1(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s'% proxy}
    except:
        proxies = ''
    num = num*3
    start_url = 'http://www.cixi.gov.cn/module/web/jpage/dataproxy.jsp?startrecord=%s&endrecord=%s&perpage=15'%((num*15-44),(num*15))
    payloadData = {
        "col": 1,
        "appid": 1,
        "webid": 152,
        "path": "/",
        "columnid": columnid,
        "sourceContentType": 1,
        "unitid": unitid,
        "webname": "慈溪市人民政府",
        "permissiontype": 0,
    }
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    if proxies:
        res = requests.post(url=start_url, headers=headers, data=payloadData, proxies=proxies)
    else:
        res = requests.post(url=start_url, headers=headers, data=payloadData)
    # 需要判断是否为登录后的页面
    data_list = []
    time.sleep(1)
    if res.status_code == 200:
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')
        lis = soup.find_all('record')
        for li in lis:
            li = BeautifulSoup(str(li.text.strip()), 'html.parser')
            a = li.find("a")
            try:
                title = a['title'].strip()
            except:
                title = a.text.strip()
            try:
                link = a["href"]
            except:
                link = '-'
            td = li.find("span").text.strip()
            tmp = [title, td, "http://www.cixi.gov.cn" + link.strip()]
            data_list.append(tmp)
    df = pd.DataFrame(data_list)
    df['info'] = None
    return df


def f2(driver):
    global columnid,unitid
    columnid = None
    unitid = None
    url = driver.current_url
    columnid = re.findall(r'/col(\d+)/', url)[0]
    unitid = re.findall(r'uid=(\d+)', url)[0]
    try:
        locator = (By.XPATH, "//div[@class='default_pgContainer']/li[1]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    except:
        driver.refresh()
        locator = (By.XPATH, "//div[@class='default_pgContainer']/li[1]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@class='default_pgTotalPage']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(st)
        if num/3 != int(num/3):
            num = int(num / 3) + 1
        else:
            num = int(num / 3)
    except:
        num = 1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='article'][string-length()>40]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5: break
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('table', id="article")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.cixi.gov.cn/col/col139786/index.html?uid=348556&pageNum=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_yuzhaobiao_gg",
     "http://www.cixi.gov.cn/col/col139787/index.html?uid=348556&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'工程建设招标文件预公示'}), f2],
    #
    ["gcjs_gqita_bian_bu_gg",
     "http://www.cixi.gov.cn/col/col139788/index.html?uid=348556&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.cixi.gov.cn/col/col139789/index.html?uid=348556&pageNum=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gg",
     "http://www.cixi.gov.cn/col/col139791/index.html?uid=348556&pageNum=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://www.cixi.gov.cn/col/col139792/index.html?uid=348556&pageNum=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://www.cixi.gov.cn/col/col139793/index.html?uid=348556&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'单一来源'}),f2],

    ["zfcg_yucai_gg",
     "http://www.cixi.gov.cn/col/col139794/index.html?uid=348556&pageNum=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["qsy_gqita_zhao_bian_gg",
     "http://www.cixi.gov.cn/col/col139806/index.html?uid=348556&pageNum=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'其他公共资源(国企)'}), f2],

    ["qsy_gqita_zhong_liu_gg",
     "http://www.cixi.gov.cn/col/col139807/index.html?uid=348556&pageNum=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'其他公共资源(国企)'}), f2],


    ["jqita_gqita_zhao_bian_gg",
     "http://www.cixi.gov.cn/col/col139808/index.html?uid=348556&pageNum=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'镇级平台(农交所)公告'}), f2],

    ["jqita_gqita_zhong_liu_gg",
     "http://www.cixi.gov.cn/col/col139809/index.html?uid=348556&pageNum=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'镇级平台(农交所)公告'}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省慈溪市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.4.175","zhejiang","cixi"],pageloadtimeout=60)

    # driver=webdriver.Chrome()
    # url="http://www.cixi.gov.cn/col/col139788/index.html?uid=348556&pageNum=1"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver = webdriver.Chrome()
    # url = "http://www.cixi.gov.cn/col/col139788/index.html?uid=348556&pageNum=1"
    # driver.get(url)
    # for i in range(1, 5):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)