import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import pandas as pd
from zhulong.util.etl import est_meta, est_html

_name_ = "wuhai"


def f1(driver, num):
    page = num * 15 - 15
    # url = driver.current_url.split("?")[0]
    url = driver.current_url
    # form_data = {'serch': '', 'startIndex': page, 'resourceCode': 'cgzbgg', 'article.title': ''}
    form_data = {'serch': '', 'startIndex': page, 'article.title': ''}
    response = requests.post(url, data=form_data).text
    data = []
    soup = BeautifulSoup(response, "lxml")
    table = soup.find("table", class_="in_ullist")
    content_list = table.find_all("tr")
    for content in content_list:
        a = content.find("a")
        name = re.sub(r"\s", "", a.text)
        ggstart_time = content.find("span").text.strip()
        url = "http://www.whggzy.com/" + a["href"]
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='page']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    driver.find_element_by_xpath("//div[@class='page']/a[contains(string(),'尾页')]").click()
    total_page = driver.find_element_by_xpath("//option[@selected='true']").text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@class='sub_content']")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('td', class_='sub_content')

    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.whggzy.com/articleWeb!list.action?resourceCode=jszbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg",
     "http://www.whggzy.com/articleWeb!list.action?resourceCode=jsxmdyby",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_zhong_zhonghx_gg",
     "http://www.whggzy.com/articleWeb!list.action?resourceCode=jszbgs",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.whggzy.com/articleWeb!list.action?resourceCode=cgzbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.whggzy.com/articleWeb!list.action?resourceCode=cgxmdyby",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.whggzy.com/articleWeb!list.action?resourceCode=cgzbgs",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="内蒙古自治区乌海市", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "neimenggu", "wuhai"])
    # driver = webdriver.Chrome()
    # driver.get("http://www.whggzy.com/articleWeb!list.action?resourceCode=cgxmdyby")
    # for i in range(1,15):
    #     f1(driver,i)
    # print(f2(driver))
