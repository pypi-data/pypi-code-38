import re
import time

from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_meta_large, est_html

_name_ = "hezhou"


def f1(driver, num):
    driver.set_page_load_timeout(60)
    locator = (By.XPATH, "//input[@type='submit']")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//*[@id="Main_unitList_lstMain_lnk_fEntityName_0"]').text
    cnum = driver.find_element_by_xpath(
        "//input[@class='pager-content-selected' and @style='width:20px;cursor:hand;']").get_attribute("value")
    if int(cnum) > int(num):
        driver.get(driver.current_url)
        cnum = 1
    if int(cnum) != int(num):  # 翻页
        if num <= 10 and int(cnum) <= 10:
            locator = (By.ID, "Main_unitList_unitPager_lstMain_btnPage_%s" % (int(num) - 1))
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
            driver.find_element_by_id("Main_unitList_unitPager_lstMain_btnPage_%s" % (int(num) - 1)).click()
            locator = (By.XPATH, '//*[@id="Main_unitList_lstMain_lnk_fEntityName_0"][not(contains(string(),"%s"))]' % val)
            WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located(locator))
        else:
            d = int(num) - int(cnum)
            # print('num',num,'cnum',cnum,'d',d)
            time = d // 10
            if time:
                for i in range(time):
                    if i == 0:
                        if int(cnum) < 11:
                            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "Main_unitList_unitPager_lstMain_btnPage_10"))).click()
                        else:
                            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "Main_unitList_unitPager_lstMain_btnPage_11"))).click()
                    else:
                        locator = (By.ID, "Main_unitList_unitPager_lstMain_btnPage_11")
                        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
                        driver.find_element_by_id("Main_unitList_unitPager_lstMain_btnPage_11").click()
                    locator = (By.XPATH, '//*[@id="Main_unitList_lstMain_lnk_fEntityName_0"][not(contains(string(),"%s"))]' % val)
                    WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located(locator))

            # 10 ,20 ,30为起始页，目标页少10
            if int(cnum) % 10 == 0 and num-int(cnum) > 1:
                if int(cnum) <= 11:
                    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "Main_unitList_unitPager_lstMain_btnPage_10"))).click()
                else:
                    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "Main_unitList_unitPager_lstMain_btnPage_11"))).click()
                locator = (By.XPATH,'//*[@id="Main_unitList_lstMain_lnk_fEntityName_0"][not(contains(string(),"%s"))]' % val)
                WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located(locator))

            d = d - 10 * time
            j_len = int(str(cnum)[-1:]) + d
            locator = (By.XPATH, "//input[@type='submit']")
            WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located(locator))
            btns = driver.find_elements_by_xpath("//input[@type='submit']")
            if int(cnum) <= 10:
                if j_len == 1 and len(btns) > 13:
                    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "Main_unitList_unitPager_lstMain_btnPage_10"))).click()
            else:
                if j_len == 1 and len(btns) > 13:
                    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "Main_unitList_unitPager_lstMain_btnPage_11"))).click()

            t = j_len // 10
            for i in range(t):
                cnum_2 = driver.find_element_by_xpath(
                    "//input[@class='pager-content-selected' and @style='width:20px;cursor:hand;']").get_attribute(
                    "value")
                val = driver.find_element_by_xpath('//*[@id="Main_unitList_lstMain_lnk_fEntityName_0"]').text

                if int(cnum_2) <= 10:
                    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "Main_unitList_unitPager_lstMain_btnPage_10"))).click()
                else:
                    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "Main_unitList_unitPager_lstMain_btnPage_11"))).click()
                j_len -= 10
                locator = (By.XPATH,'//*[@id="Main_unitList_lstMain_lnk_fEntityName_0"][not(contains(string(),"%s"))]' % val)
                WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located(locator))

            locator = (By.ID, "Main_unitList_unitPager_lstMain_btnPage_%s" % j_len)
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
            driver.find_element_by_id("Main_unitList_unitPager_lstMain_btnPage_%s" % j_len).click()

    page = driver.page_source
    body = etree.HTML(page)
    data = []

    content_list = body.xpath("//tr[@class='grid-item' or @class='grid-item-alternate']")
    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        if name == "":
            name = content.xpath("./td[2]/a")[0].xpath("string(.)").strip()
        ggstart_time = content.xpath("./td[@class='grid-item-sorted']/span/text()")[0][:-1].strip().replace("月", '-')
        url = "http://www.hzzfcg.com" + re.findall('\"(.+)\"', content.xpath("./td/a/@onclick")[0])[0][2:]
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.ID, "Main_unitList_unitPager_lstMain_btnLast")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    total_page = driver.find_element_by_xpath("//input[@id='Main_unitList_unitPager_lstMain_btnLast']").get_attribute(
        "value")
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "info_main")
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
    table = soup.find('table', class_='info_main')
    table2 = table.find("table")
    table3 = table2.find("table")
    table4 = table3.find("table")
    return table4


data = [

    ["gcjs_zhaobiao_gg",
     "http://www.hzzfcg.com/page__gp_portal/list_article.aspx?id=9ba20408-67c2-4f11-bc77-13d0dd4c8748",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg",
     "http://www.hzzfcg.com/page__gp_portal/list_article.aspx?id=a99892ee-ed5c-4c0f-aa5d-94fd46fb72c4",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_yucai_gg",
     "http://www.hzzfcg.com/page__gp_portal/list_article.aspx?id=f220428e-dad6-4c31-bc38-f7fefc163cbb",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://www.hzzfcg.com/page__gp_portal/list_article.aspx?id=083422fb-432a-426d-bd0d-58625a9ce035",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta_large(conp, data=data, diqu="广西省贺州市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == "__main__":

    conp = ["postgres", "since2015", "192.168.3.171", "guangxi", "hezhou"]
    work(conp,num=4)
