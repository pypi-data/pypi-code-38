import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zlshenpi.util.etl import add_info, est_meta, est_html, est_tbs, add_info, est_meta_large
import sys
import time
import json

_name_ = "guangdongsheng"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='per95']/table/tbody/tr[child::td][1]/td[1]")
    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    locator = (By.XPATH, "//span[@class='current']")

    cnum = int(WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text)

    if num != int(cnum):
        driver.execute_script('javascript:jumpPage(%s)' % num)
        locator = (By.XPATH, "//div[@class='per95']/table/tbody/tr[child::td][1]/td[1][not(contains(string(), '%s'))]" % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    contents = body.xpath("//div[@class='per95']/table/tbody/tr[child::td]")
    data = []
    for content in contents:
        if 'searchMore2' in driver.current_url or "searchMore4" in driver.current_url:
            name = content.xpath('./td[2]/div/text()')[0].strip()
            xm_code = content.xpath("./td[1]/text()")[0].strip()
            manage_apartment = content.xpath('./td[3]/div/text()')[0].strip()
            ggstart_time = content.xpath('./td[4]/div/text()')[0].split('至')[0].strip()
            end_time = content.xpath('./td[4]/div/text()')[0].split('至')[1].strip()
            href = 'http://www.gdtz.gov.cn' + content.xpath('./td/a/@href')[0].strip()
            info_tmp = {'公示结束时间': end_time, "manage_apartment": manage_apartment, 'xm_code': xm_code}
        else:

            name = content.xpath('./td/div/a/text()')[0].strip()
            href = 'http://www.gdtz.gov.cn' + content.xpath('./td/div/a/@href')[0].strip()
            xm_code = content.xpath("./td[1]/text()")[0].strip()
            process = content.xpath('./td[3]/div/text()')[0].strip()
            status = content.xpath('./td[4]/text()')[0].strip()
            ggstart_time = content.xpath('./td[last()]/div/text()')[0].strip()
            info_tmp = {'xm_code': xm_code, "process": process, 'status': status}

        if href == 'None' or href is None:
            info_tmp.update({'hreftype': '不可抓网页'})

        info = json.dumps(info_tmp, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)

    df = pd.DataFrame(data)
    return df


def f2(driver):
    if "searchMore4.action" not in driver.current_url:
        locator = (By.XPATH, "//div[@class='badoo']/a[last()]")
        txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')
        total_page = int(re.findall('\d+', txt)[0])
    else:
        try:
            locator = (By.XPATH, "//div[@class='badoo']/a[last()]")
            txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')
            total_page = int(re.findall('\d+', txt)[0])
        except:total_page = 1
    driver.quit()
    return total_page


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='per95']|//div[@class='tab-content']")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_="per95")
    if not div:
        div = soup.find('div',class_="tab-content")
    return div


data = [
    ["xm_beian_gg",
     "http://www.gdtz.gov.cn/tybm/apply3!searchMore3.action",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["xm_hezhun_gg",
     "http://www.gdtz.gov.cn/approval!list.action?param.state=1,2,3,4,7,8",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["xm_hzqgs_gg",
     "http://www.gdtz.gov.cn/tybm/apply3!searchMore4.action",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="广东省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlshenpi", "guangdongsheng"])
    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get('http://www.gdtz.gov.cn/tybm/apply3!searchMore4.action')
    # print(d[1])
    # print(f3(driver, "http://www.gdtz.gov.cn/approval!view.action?id=ff808081670c81e3016714e4ab0e4762"))
