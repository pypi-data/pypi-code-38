import time
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
import json
from zhulong.util.etl import est_tables, gg_meta, gg_html, est_meta, est_html, add_info

_name_='jinan'

def f1(driver, num):
    """
    进行翻页，并获取数据
    :param driver: 已经访问了url
    :param num: 返回的是从第一页一直到最后一页
    :return:
    """
    locator = (By.XPATH, '//*[@id="content"]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//*[@id="pag"]').text

    # val = driver.find_element_by_xpath("//ul[@class='ewb-info-list']//li[1]//a").text
    if num != int(cnum):
        val = driver.find_element_by_xpath("//*[@id='content']/ul/li[1]/a").text.strip()
        # driver.find_element_by_xpath('//*[@id="toPageNum"]').clear()
        # driver.find_element_by_xpath('//*[@id="toPageNum"]').send_keys(num)
        # driver.find_element_by_xpath('//*[@id="part4"]/span[8]').click()
        driver.execute_script("search1({});".format(num))

        locator = (By.XPATH, "//*[@id='content']/ul/li[1]/a[not(contains(string(), '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find("div", id="content")
    lis = ul.find_all("li")
    data = []
    for li in lis:
        info = {}
        a = li.find("a")
        title = a["title"]
        try:
            a_nunm = a["onclick"]
            a_num = re.findall('\((.*)\)', a_nunm)[0]
            link = "http://jnggzy.jinan.gov.cn/jnggzyztb/front/showNotice.do?iid={}&xuanxiang=".format(a_num)
        except:
            link = "http://jnggzy.jinan.gov.cn" + a["href"]

        span1 = li.find("span", class_="span1")
        span2 = li.find("span", class_="span2")
        if span1:
            diqu = span1.text.strip()
            if re.findall(r'\[(\w+)\]', diqu):
                diqu = re.findall(r'\[(\w+)\]', diqu)[0]
                info['diqu'] = diqu
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [title.strip(), span2.text.strip(), link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    """
    返回总页数
    :param driver:
    :return:
    """
    locator = (By.XPATH, '//*[@id="content"]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//*[@id="apagesum"]')
    page = WebDriverWait(driver, 1).until(EC.presence_of_element_located(locator)).text

    driver.quit()
    return int(page)



def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//div[@class='list'][string-length()>15]")
    WebDriverWait(driver,20).until(EC.presence_of_all_elements_located(locator))
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
    div=soup.find('div',class_='list')
    return div


data = [
        ["gcjs_zhaobiao_gg",
         "http://jnggzy.jinan.gov.cn/jnggzyztb/front/noticelist.do?type=0&xuanxiang=1&area=",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_zhongbiao_gg",
         "http://jnggzy.jinan.gov.cn/jnggzyztb/front/noticelist.do?type=0&xuanxiang=2&area=",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_zhaobiao_gg",
         "http://jnggzy.jinan.gov.cn/jnggzyztb/front/noticelist.do?type=1&xuanxiang=1&area=",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_zhongbiao_gg",
         "http://jnggzy.jinan.gov.cn/jnggzyztb/front/noticelist.do?type=1&xuanxiang=2&area=",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_biangeng_gg",
         "http://jnggzy.jinan.gov.cn/jnggzyztb/front/noticelist.do?type=1&xuanxiang=3&area=",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_liubiao_gg",
         "http://jnggzy.jinan.gov.cn/jnggzyztb/front/noticelist.do?type=1&xuanxiang=4&area=",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["qsy_zhaobiao_gg",
         "http://jnggzy.jinan.gov.cn/jnggzyztb/front/noticelist.do?type=7&xuanxiang=1&area=",
         ["name", "ggstart_time", "href","info"],add_info(f1, {'jylx':'其他交易'}),f2],

        ["qsy_zhongbiao_gg",
         "http://jnggzy.jinan.gov.cn/jnggzyztb/front/noticelist.do?type=7&xuanxiang=2&area=",
         ["name", "ggstart_time", "href","info"],add_info(f1, {'jylx':'其他交易'}),f2],

        ["gcjs_zhaobiao_shuili_gg",
         "http://jnggzy.jinan.gov.cn/jnggzyztb/front/noticelist.do?type=4&xuanxiang=1&area=",
         [ "name", "ggstart_time", "href","info"],add_info(f1,{"gctype":"水利"}),f2],

        ["gcjs_zhongbiao_shuili_gg",
         "http://jnggzy.jinan.gov.cn/jnggzyztb/front/noticelist.do?type=4&xuanxiang=2&area=",
         [ "name", "ggstart_time", "href","info"],add_info(f1,{"gctype":"水利"}),f2],

        ["gcjs_zhaobiao_tielu_gg",
         "http://jnggzy.jinan.gov.cn/jnggzyztb/front/noticelist.do?type=5&xuanxiang=1&area=",
         [ "name", "ggstart_time", "href","info"],add_info(f1,{"gctype":"铁路"}),f2],

        ["gcjs_zhongbiao_tielu_gg",
         "http://jnggzy.jinan.gov.cn/jnggzyztb/front/noticelist.do?type=5&xuanxiang=2&area=",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"gctype":"铁路"}),f2],

        ["gcjs_zhongbiaohx_tielu_gg",
         "http://jnggzy.jinan.gov.cn/jnggzyztb/front/noticelist.do?type=5&xuanxiang=5&area=",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"gctype":"铁路"}),f2],

        ["gcjs_zhaobiao_jiaotong_gg",
         "http://jnggzy.jinan.gov.cn/jnggzyztb/front/noticelist.do?type=6&xuanxiang=1&area=",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"gctype":"交通"}),f2],

        ["gcjs_zhongbiao_jiaotong_gg",
         "http://jnggzy.jinan.gov.cn/jnggzyztb/front/noticelist.do?type=6&xuanxiang=2&area=",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"gctype":"交通"}),f2],

    ]



def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省济南市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","jinan"])

