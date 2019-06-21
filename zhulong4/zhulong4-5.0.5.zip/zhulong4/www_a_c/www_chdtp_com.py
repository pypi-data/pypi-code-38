import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json



from zhulong4.util.etl import est_tbs, est_meta, est_html, add_info, est_meta_large

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fqztb.com/Home/tenderList?index=3&type=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)



_name_ = 'www_chdtp_com'


def f1(driver, num):
    locator=(By.XPATH,"//iframe[contains(@id,'iframepage')]")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    mark_url=driver.current_url
    iframe_ = driver.find_element_by_xpath("//iframe[contains(@id,'iframepage')]")
    driver.switch_to.frame(iframe_)
    locator = (By.XPATH, '//table[@class="wwFormTable"]//tr[2]//a[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//span[@class="page"]').text
    cnum = re.findall('第(.+?)/', cnum)[0].strip()

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//table[@class="wwFormTable"]//tr[2]//a[1]').get_attribute('href')[-30:-7]

        select = Select(driver.find_element_by_xpath('//select[@id="jump"]'))
        select.select_by_value(str(num))

        locator = (By.XPATH, '//table[@class="wwFormTable"]//tr[2]//a[1][not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='wwFormTable')
    trs = div.find_all('tr', style=None)
    for tr in trs:
        name = tr.find('a')['title']
        href = tr.find('a')['href']

        ggstart_time = tr.find_all('td')[-1].get_text().strip().strip(']').strip('[')

        if 'zhaobiaoList' in mark_url:
            href = re.findall("javascript:.+?\('(.+?)'\)", href)[0]
            href = 'https://www.chdtp.com/staticPage/' + href
        else:
            mark_str=re.findall("javascript:.+?\('(.+?)','(.+?)'\)", href)[0]
            href='https://www.chdtp.com/webs/detailNewZbhxrgsZxzxAction.action?chkedId={}&cminid={}'.format(mark_str[0],mark_str[1])

        tmp = [name, ggstart_time, href]

        data.append(tmp)

    df = pd.DataFrame(data=data)
    df["info"] = None
    driver.switch_to.parent_frame()

    return df

def f4(driver,num):

    locator = (By.XPATH, '//table[@class="wwFormTable"]//tr[2]//a[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//span[@class="page"]').text
    cnum = re.findall('第(.+?)/', cnum)[0].strip()

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//table[@class="wwFormTable"]//tr[2]//a[1]').get_attribute('href')[-30:-7]
        driver.execute_script("document.getElementById('jump').value=%d" % num)
        driver.find_element_by_tag_name('label').click()
        driver.execute_script(
            "document.getElementById('Currentpage').form.action='/webs/displayNewsCgxxAction.action';document.getElementById('Currentpage').form.submit();")

        locator = (By.XPATH, '//table[@class="wwFormTable"]//tr[2]//a[1][not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='wwFormTable')
    trs = div.find_all('tr')[1:]
    for tr in trs:
        name = tr.find('a').get_text()
        href = tr.find('a')['href']
        company = tr.find_all('a')[1].get_text()
        ggstart_time = tr.find_all('td')[1].get_text().strip().strip(']').strip('[')

        href = re.findall("javascript:.+?\('(.+?)'\)", href)[0]

        href = 'https://www.chdtp.com/staticPage/' + href

        info={'company':company}
        info=json.dumps(info,ensure_ascii=False)

        tmp = [name, ggstart_time, href, info]

        data.append(tmp)


    df = pd.DataFrame(data=data)


    driver.switch_to.parent_frame()

    return df



def chang_type(f,num):
    def inner(*args):
        driver=args[0]
        locator = (By.XPATH, '//div[@class="main_top"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        ctext=driver.find_element_by_xpath('//td[@class="kjywtdnow1"]//a').text
        if num == 1:
            driver.switch_to.frame('iframepage1')
        elif ctext == '询价公告' and num == 2:
            driver.switch_to.frame('iframepage1')
            val = driver.find_element_by_xpath('//table[@class="wwFormTable"]//tr[2]//a[1]').get_attribute('href')[-30:-7]
            driver.switch_to.parent_frame()
            driver.execute_script('showywtdT(2);ShowFLTT(2)')
            driver.switch_to.frame('iframepage0')
            locator = (By.XPATH, '//table[@class="wwFormTable"]//tr[2]//a[1][not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        else:
            driver.switch_to.frame('iframepage0')

        return f(*args)
    return inner


def f5(driver):
    locator = (By.XPATH, '//table[@class="wwFormTable"]//tr[2]//a[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//span[@class="page"]').text
    total = re.findall('/(.+?)页', total)[0].strip()

    total = int(total)

    driver.quit()

    return total



def f2(driver):
    locator = (By.XPATH, '//div[@class="main_top"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    iframe_=driver.find_element_by_xpath("//iframe[contains(@id,'iframepage')]")

    driver.switch_to.frame(iframe_)

    locator = (By.XPATH, '//table[@class="wwFormTable"]//tr[2]//a[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//span[@class="page"]').text
    total = re.findall('/(.+?)页', total)[0].strip()

    total = int(total)

    driver.quit()

    return total



def f3(driver, url):

    driver.get(url)

    locator = (By.XPATH, '//div[@class="main_top main_top_CG"][string-length()>10]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))


    time.sleep(0.1)
    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 10: break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    div = soup.find('div',class_="main_top main_top_CG")

    return div


data = [
    ["qy_zhaobiao_gg", "https://www.chdtp.com/pages/wzglS/zbgg/zhaobiaoList.jsp",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongbiaohx_gg", "https://www.chdtp.com/pages/wzglS/zbhxrgs/zbhxrgs.jsp",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhaobiao_xunjia_gg", "https://www.chdtp.com/pages/wzglS/cgxx/caigou.jsp",["name", "ggstart_time", "href", "info"], add_info(chang_type(f4,1),{'zbfs':'询价'}), chang_type(f5,1)],
    ["qy_zhaobiao_tanpan_gg", "https://www.chdtp.com/pages/wzglS/cgxx/caigou.jsp",["name", "ggstart_time", "href", "info"], add_info(chang_type(f4,2),{'zbfs':'竞争性谈判'}), chang_type(f5,2)],

]

def work(conp, **args):
    est_meta_large(conp, data=data, diqu="华电集团", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch3", "www_chdtp_com"],headless=False,num=1)
    pass