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

_name_ = "bayannaoer"

month_dict ={"sep": "9", "oct": "10", "nov": "11", "dec": "12", "jan": "1", "feb": "2",
                "aug": "8", "jul": "7", "jun": "6", "may": "5", "apr": "4", "mar": "3"}



def f1(driver, num):
    locator = (By.XPATH, "//div[@class='list_content']//li/a")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//div[@class='list_content']//li[1]/a").get_attribute("href")[-35:]
    if "a7ecd0e50016" not in driver.current_url:
        locator = (By.XPATH, "//span[@class='laypage_curr']")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        cnum = driver.find_element_by_xpath("//span[@class='laypage_curr']").text
    else:
        try:
            locator = (By.XPATH, "//span[@class='laypage_curr']")
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
            cnum = driver.find_element_by_xpath("//span[@class='laypage_curr']").text
        except:
            cnum = 1

    if int(cnum) != int(num):
        url = "=".join(driver.current_url.split("=")[:-1]) + "=" + str(num)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='list_content']//li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='list_content']//li")
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        time_temp = content.xpath("./a/span/text()")[0].strip()

        t_tmp = re.findall('\w{1,4}', time_temp)

        ggstart_time = '%s-%s-%s %s:%s:%s'%(t_tmp[2],month_dict[t_tmp[0].lower()],t_tmp[1],str(int(t_tmp[3])+12) if 'PM' == t_tmp[-1] and t_tmp[3] <'12' else t_tmp[3],t_tmp[4],t_tmp[5])
        # print(time_temp,'----------',ggstart_time)
        url = content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    if "a7ecd0e50016" not in driver.current_url:
        locator = (By.ID, "laypage_0")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        total_page = driver.find_element_by_xpath('//*[@id="laypage_0"]/a[contains(string(),"尾页")]').get_attribute("data-page")

    else:
        try:
            locator = (By.ID, "laypage_0")
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
            total_page = driver.find_element_by_xpath('//*[@id="laypage_0"]/a[contains(string(),"尾页")]').get_attribute("data-page")

        except:
            total_page = 1
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='item_detail news_list clearfix']")
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
    div = soup.find('div', class_='item_detail news_list clearfix')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://zwzx.bynr.gov.cn/sunshineGov/list.shtml?columnId=402883f365a786900165a7eba6630013&siteId=1&newsType=ggzyjy&pageNumber=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_bian_bu_gg",
     "http://zwzx.bynr.gov.cn/sunshineGov/list.shtml?columnId=402883f365a786900165a7ec52430015&siteId=1&newsType=ggzyjy&pageNumber=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_zhong_zhonghx_gg",
     "http://zwzx.bynr.gov.cn/sunshineGov/list.shtml?columnId=402883f365a786900165a7ebf8760014&siteId=1&newsType=ggzyjy&pageNumber=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_liubiao_gg",
     "http://zwzx.bynr.gov.cn/sunshineGov/list.shtml?columnId=402883f365a786900165a7ecd0e50016&siteId=1&newsType=ggzyjy&pageNumber=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://zwzx.bynr.gov.cn/sunshineGov/list.shtml?columnId=402883f365a786900165a7e9f2c0000f&siteId=1&newsType=ggzyjy&pageNumber=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://zwzx.bynr.gov.cn/sunshineGov/list.shtml?columnId=402893f365a786900165a7eabc9c0012&siteId=1&newsType=ggzyjy&pageNumber=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://zwzx.bynr.gov.cn/sunshineGov/list.shtml?columnId=402883f365a786900165a7ea2b9f0010&siteId=1&newsType=ggzyjy&pageNumber=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg",
     "http://zwzx.bynr.gov.cn/sunshineGov/list.shtml?columnId=402883f365a786900165a7ea6f700011&siteId=1&newsType=ggzyjy&pageNumber=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="内蒙古自治区巴彦淖尔市", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":
#     url = "http://zwzx.bynr.gov.cn/sunshineGov/list.shtml?columnId=402883f365a786900165a7eba6630013&siteId=1&newsType=ggzyjy&pageNumber=1"
#     driver = webdriver.Chrome()
#     driver.get(url)
    # print(f2(driver))
    # url = "http://zwzx.bynr.gov.cn/sunshineGov/list.shtml?columnId=402883f365a786900165a7ea6f700011&siteId=1&newsType=ggzyjy&pageNumber=1"
    # driver = webdriver.Chrome()
    # driver.get(url)
    # print(f2(driver))
    # for i in range(1, 100):
    # f1(driver, 1)

    work(conp=["postgres", "since2015", "192.168.3.171", "neimenggu", "bayannaoer"])
