import time
from pprint import pprint

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs
from collections import OrderedDict

_name_='linqing'



def f1(driver, num):
    locator = (By.XPATH, "//div[@class='content']//tr[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    nume = driver.find_element_by_xpath('//td[@class="huifont"]').text
    cnum = re.findall(r'(\d+)/', nume)[0]
    if num != int(cnum):
        if "?Paging" not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url = url + s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        val = driver.find_element_by_xpath('//div[@class="content"]//tr[1]//a').get_attribute('href')[-35:]
        driver.get(url)
        locator = (By.XPATH, "//div[@class='content']//tr[1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    html_data = driver.page_source
    soup = BeautifulSoup(html_data, 'html.parser')
    ul = soup.find("div", class_="content")
    tb = ul.find_all("div", recursive=False)[0]
    lis = tb.find_all("tr")
    data = []
    for li in lis:
        a = li.find("a")
        title = a["title"]
        link = "http://ggzy.linqing.gov.cn" + a["href"]
        span = li.find("font")
        tmp = [title.strip(), span.text.strip(), link]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df


def f2(driver):
    """
    返回总页数
    :param driver:
    :return:
    """
    if ('本栏目暂时没有内容' in driver.page_source) or ('404' in driver.title):
        return 0
    locator = (By.XPATH, "//div[@class='content']//tr[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    text=driver.find_element_by_xpath("//td[@class='huifont']").text.split("/")[1]
    total=int(text)
    driver.quit()
    return total


def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH, "//div[@class='detail-content'][string-length()>15]")
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
    before=len(driver.page_source)
    time.sleep(0.1)
    after=len(driver.page_source)
    i=0
    while before!=after:
        before=len(driver.page_source)
        time.sleep(0.1)
        after=len(driver.page_source)
        i+=1
        if i>5:break
    page=driver.page_source
    soup=BeautifulSoup(page,'html.parser')
    div=soup.find('div',class_='detail-content')
    #div=div.find_all('div',class_='ewb-article')[0]
    return div


def get_data():
    data = []
    # 工程建设
    ggtype1 = OrderedDict([("zhaobiao", "001"), ("biangeng", "002"), ("zhongbiao", "003"), ("yucai", "004")])
    gctype = OrderedDict([("勘察设计", "001"), ("施工", "002"), ("监理", "003"), ("专业工程", "004")])
    for w1 in ggtype1.keys():
        for w2 in gctype.keys():
            p1 = "079001%s" % (ggtype1[w1])
            p2 = "079001%s%s" % (ggtype1[w1], gctype[w2])
            href = "http://ggzy.linqing.gov.cn/lqweb/jyxx/079001/%s/%s/" % (p1, p2)
            tmp = ["gcjs_%s_gctype%s_gg" % (w1, gctype[w2]), href, ["name", "ggstart_time", "href", "info"],
                   add_info(f1, {"gctype": w2}), f2]
            data.append(tmp)

    # 政府采购
    zbfs = OrderedDict([("公开招标", "001"), ("邀请招标", "002"), ("竞争性磋商", "003"), ("竞争性谈判", "004"), ("询价", "005"), ("单一来源公示", "006")])
    ggtype2 = OrderedDict(
        [("zhaobiao", "001"), ("biangeng", "002"), ("zhongbiao", "003"), ("liubiao", "004")])

    for w1 in ggtype2.keys():
        for w2 in zbfs.keys():
            p1 = "079002%s" % (ggtype2[w1])
            p2 = "079002%s%s" % (ggtype2[w1], zbfs[w2])
            href = "http://ggzy.linqing.gov.cn/lqweb/jyxx/079002/%s/%s/" % (p1, p2)
            tmp = ["zfcg_%s_zbfs%s_gg" % (w1, zbfs[w2]), href, ["name", "ggstart_time", "href", "info"],
                   add_info(f1, {"zbfs": w2}), f2]
            data.append(tmp)
    tmps = [["zfcg_yucai_gg", "http://ggzy.linqing.gov.cn/lqweb/jyxx/079002/079002006/079002006001/",
            ["name", "ggstart_time", "href", "info"],f1, f2],

           ["zfcg_hetong_gg", "http://ggzy.linqing.gov.cn/lqweb/jyxx/079002/079002006/079002006002/",
            ["name", "ggstart_time", "href", "info"], f1, f2],

           ["zfcg_yanshou_gg", "http://ggzy.linqing.gov.cn/lqweb/jyxx/079002/079002006/079002006003/",
            ["name", "ggstart_time", "href", "info"], f1, f2],

           ["zfcg_gqita_ppp_gg", "http://ggzy.linqing.gov.cn/lqweb/jyxx/079002/079002006/079002006005/",
            ["name", "ggstart_time", "href", "info"], add_info(f1, {"jylx": 'PPP项目公示'}), f2],

            ["zfcg_gqita_zhao_yu_danyilaiyuan_gg", "http://ggzy.linqing.gov.cn/lqweb/jyxx/079002/079002006/079002006006/",
             ["name", "ggstart_time", "href", "info"], add_info(f1, {"zbfs": '单一来源'}), f2],
           ]
    data.extend(tmps)

    # 医疗采购
    ggtype3 = OrderedDict([("zhaobiao", "001"), ("biangeng", "002"), ("zhongbiao", "003")])
    for w1 in ggtype3.keys():
        p1 = "079005%s" % (ggtype3[w1])

        href = "http://ggzy.linqing.gov.cn/lqweb/jyxx/079005/%s/" % p1
        tmp = ["yiliao_%s_gg" % (w1), href, ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'医用采购'}), f2]
        data.append(tmp)

    # 其他采购
    ggtype4 = OrderedDict(
        [("zhaobiao", "001"), ("biangeng", "002"), ("zhongbiao", "003"), ("liubiao", "004"), ("yucai", "005")])
    for w1 in ggtype4.keys():
        p1 = "079006%s" % (ggtype4[w1])
        href = "http://ggzy.linqing.gov.cn/lqweb/jyxx/079006/%s/" % p1
        tmp = ["qsy_%s_gg" % (w1), href, ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'其他采购'}), f2]
        data.append(tmp)
    remove_arr = ["gcjs_biangeng_gctype001_gg", "gcjs_biangeng_gctype004_gg", "gcjs_yucai_gctype004_gg",
                  "gcjs_yucai_gctype003_gg"
        , "zfcg_zhaobiao_zbfs002_gg", "zfcg_biangeng_zbfs002_gg", "zfcg_biangeng_zbfs006_gg",
                  "zfcg_liaobiao_zbfs006_gg", "zfcg_liubiao_zbfs002_gg", "zfcg_liubiao_zbfs005_gg",
                  "zfcg_liubiao_zbfs006_gg"
        , "zfcg_yucai_zbfs003_gg", "zfcg_yucai_zbfs004_gg"]
    data1 = data.copy()
    for w in data:
        if w[0] in remove_arr: data1.remove(w)
    return data1

data=get_data()


def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省临清市")
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","linqing"])




