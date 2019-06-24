import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import pandas as pd
from zhulong.util.etl import est_meta, est_html

_name_ = "wulanchabu"


def f1(driver, num):

    locator = (By.XPATH, "//ul[@class='wb-data-item']/li/div/a")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//ul[@class='wb-data-item']/li[1]/div/a").get_attribute("href")
    try:
        locator = (By.XPATH, "//span[@class='laypage_curr']")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        cnum = driver.find_element_by_xpath("//li[@class='wb-page-li wb-page-item current']").text.strip()
    except:
        cnum = 1
    # return
    if int(cnum) != int(num):
        url = "/".join(driver.current_url.split('/')[:-1])+'/'+str(num)+".html"
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='wb-data-item']/li[1]/div/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
        # val = driver.find_element_by_xpath("//ul[@class='wb-data-item']/li/div/a").text
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='wb-data-item']/li")
    for content in content_list:
        name = content.xpath("./div/a")[0].xpath("string(.)").strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://www.wlcbggzyjy.org.cn" + content.xpath("./div/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//li[@class='wb-page-li wb-page-item wb-page-next wb-page-family wb-page-fs12']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    # print(driver.find_element_by_xpath('//li[@class="wb-page-li wb-page-item wb-page-next wb-page-family wb-page-fs12"]/a[contains(string(),"末页")]').text)
    total_page = re.findall(r"/(\d+)\.",driver.find_element_by_xpath('//li[@class="wb-page-li wb-page-item wb-page-next wb-page-family wb-page-fs12"]/a[contains(string(),"末页")]').get_attribute('href'))[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='article-block']")
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
    div = soup.find('div', class_='article-block')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.wlcbggzyjy.org.cn/005/005001/005001001/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg",
     "http://www.wlcbggzyjy.org.cn/005/005001/005001002/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_zhong_zhonghx_gg",
     "http://www.wlcbggzyjy.org.cn/005/005001/005001003/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_liubiao_gg",
     "http://www.wlcbggzyjy.org.cn/005/005001/005001004/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.wlcbggzyjy.org.cn/005/005002/005002001/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zgys_gg",
     "http://www.wlcbggzyjy.org.cn/005/005002/005002002/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.wlcbggzyjy.org.cn/005/005002/005002003/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_zhong_zhonghx_gg",
     "http://www.wlcbggzyjy.org.cn/005/005002/005002004/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg",
     "http://www.wlcbggzyjy.org.cn/005/005002/005002005/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="内蒙古自治区乌兰察布市", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "neimenggu", "wulanchabu"])
    # driver = webdriver.Chrome()
    # driver.get("http://www.wlcbggzyjy.org.cn/005/005002/005002004/about.html")
    #
    # print(f2(driver))