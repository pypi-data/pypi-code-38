import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info
import urllib

_name_ = "shaoyang"


# driver=webdriver.Chrome()

# url="""http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xtype=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD"""

# driver.get(url)


def f1(driver, num):
    locator = (By.ID, "list")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = int(driver.find_element_by_xpath("//span[@class='cPageNum']").text)
    if cnum != num:
        # val=driver.find_element_by_xpath("//ul[@id='list']//li[2]//a").get_attribute("href")[-20:]
        driver.execute_script("pageNav.go(%d)" % num)
        time.sleep(0.2)
        locator = (By.CLASS_NAME, "h-load")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located(locator))
        # locator=(By.XPATH,"//ul[@id='list']//li[2]//a[not(contains(@href,'%s'))]"%val)
        # WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    ul = soup.find("ul", id="list")
    lis = ul.find_all("li", recursive=False)[1:]
    data = []
    for li in lis:
        a = li.find("a")
        span = li.find("span")
        name = a["title"]
        name = re.sub("【.*】", "", name)
        href = "http://ggzy.shaoyang.gov.cn" + a["href"]
        ggstart_time = span.text.strip()
        tmp = [name, href, ggstart_time]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.ID, "pageNav")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    try:
        total = int(re.findall('共([0-9]*)页', driver.find_element_by_id("pageNav").get_attribute("title"))[0])
    except StaleElementReferenceException:
        total = int(re.findall('共([0-9]*)页', driver.find_element_by_id("pageNav").get_attribute("title"))[0])
    total = int(total)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//iframe[@class='ugly']")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    page1 = driver.page_source

    soup1 = BeautifulSoup(page1, 'html.parser')
    div = str(soup1.find('div',id='timeBanner'))

    for i in driver.find_elements_by_xpath("//iframe[@class='ugly']"):
        driver.switch_to.frame(i)
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

        div2 = soup.find('div',class_='content')
        div += str(div2)
        driver.switch_to_default_content()
    return div


def switch_to(driver, xmtype, ggtype):
    locator = (By.ID, "list")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cxmtype = driver.find_element_by_xpath("//div[@class='newsType on']").text
    if xmtype != cxmtype:
        driver.find_element_by_xpath("//div[@class='newsType'][contains(string(), '%s')]" % xmtype).click()
        time.sleep(0.2)
        locator = (By.CLASS_NAME, "h-load")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located(locator))

    cggtype = driver.find_element_by_xpath("//div[@class='site-bar']//button[@class='btn-site on']").text
    if ggtype != cggtype:
        driver.find_element_by_xpath("//div[@class='site-bar']//button[contains(string(), '%s')]" % ggtype).click()
        time.sleep(0.2)
        locator = (By.CLASS_NAME, "h-load")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located(locator))


def gcjs(f, ggtype):
    def wrap(*krg):
        driver = krg[0]
        switch_to(driver, "工程建设", ggtype)
        if f == f1:
            df = f(*krg)
            if '\u2003' in ggtype:
                types = ggtype.replace('\u2003', '')
            else:
                types = ggtype
            a = {"yuan_ggtype": types}
            a = json.dumps(a, ensure_ascii=False)
            df["info"] = a
            return df
        else:
            return f(*krg)

    return wrap


def zfcg(f, ggtype):
    def wrap(*krg):
        driver = krg[0]
        switch_to(driver, "政府采购", ggtype)
        if f == f1:
            df = f(*krg)
            if '\u2003' in ggtype:
                types = ggtype.replace('\u2003', '')
            else:
                types = ggtype
            a = {"yuan_ggtype": types}
            a = json.dumps(a, ensure_ascii=False)
            df["info"] = a
            return df
        else:
            return f(*krg)

    return wrap


data = [

    ["gcjs_zhaobiao_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xtype=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "招标公告"), gcjs(f2, "招标公告")],

    ["gcjs_gqita_bian_bu_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xtype=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "补充通知"), gcjs(f2, "补充通知")],

    ["gcjs_gqita_bian_da_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xtype=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "答 疑"), gcjs(f2, "答 疑")],

    ["gcjs_zhongbiaohx_sjg_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xtype=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "入围公示"), gcjs(f2, "入围公示")],

    ["gcjs_zhongbiaohx_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xtype=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "中标候选人公示"), gcjs(f2, "中标候选人公示")],
    # 政府采购

    ["zfcg_zhaobiao_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&ext=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD"
        , ["name", "href", "ggstart_time", "info"], zfcg(f1, "采购公告"), zfcg(f2, "采购公告")],

    ["zfcg_gqita_bian_bu_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&ext=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD"
        , ["name", "href", "ggstart_time", "info"], zfcg(f1, "补充通知"), zfcg(f2, "补充通知")],

    ["zfcg_gqita_bian_da_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&ext=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD"
        , ["name", "href", "ggstart_time", "info"], zfcg(f1, "答 疑"), zfcg(f2, "答 疑")],

    ["zfcg_zhongbiao_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&ext=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD"
        , ["name", "href", "ggstart_time", "info"], zfcg(f1, "中标公示"), zfcg(f2, "中标公示")],

    ["zfcg_hetong_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&ext=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD"
        , ["name", "href", "ggstart_time", "info"], zfcg(f1, "合同公示"), zfcg(f2, "合同公示")],

]


def work(conp, **args):
    est_meta(conp, data, diqu="湖南省邵阳市", **args)
    est_html(conp, f3, **args)


# work(conp=["postgres","since2015","127.0.0.1","hunan","shaoyang"])
if __name__ == '__main__':
    # work(conp=["postgres", "since2015", "192.168.3.171", "hunan", "shaoyang"])
    # driver=webdriver.Chrome()
    # url = "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&ext=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD"
    # driver.get(url)
    # df = zfcg(f2,"合同公示")(driver)
    # print(df)
    driver=webdriver.Chrome()
    # url = "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&ext=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD"
    # driver.get(url)
    # for i in range(3,5):
    #     df=zfcg(f1,"合同公示")(driver, i)
    #     print(df.values)
    #     for i in df[1].values:
    #         print(i)
    # # i = 'http://ggzy.shaoyang.gov.cn/%E6%96%B0%E6%B5%81%E7%A8%8B/%E6%8B%9B%E6%8A%95%E6%A0%87%E4%BF%A1%E6%81%AF/jyxx_x.aspx?iq=x&type=%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A&tpid=5c81c8eef04806607ced240c#title_%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A'
    f = f3(driver, 'http://ggzy.shaoyang.gov.cn/%E6%96%B0%E6%B5%81%E7%A8%8B/%E6%8B%9B%E6%8A%95%E6%A0%87%E4%BF%A1%E6%81%AF/jyxx_x.aspx?iq=x&type=%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A&tpid=5a1fa9a8f04806c5cca57b6e#title_%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A')
    print(f)
