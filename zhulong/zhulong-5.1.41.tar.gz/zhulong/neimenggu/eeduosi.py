import json
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
from zhulong.util.etl import est_meta, est_html, add_info

_name_ = "eeduosi"


def f1(driver, num):

    locator = (By.XPATH, "//tr[@height='30']/td/a|//*[@id='DataGrid1']/tbody/tr/td/a")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//tr[@height='30'][1]/td/a|//*[@id='DataGrid1']/tbody/tr[1]/td/a").get_attribute("href")[-50:]
    cnum = driver.find_element_by_xpath("//td[@class='yahei redfont']|//font[@color='red']/b").text
    if int(cnum) != int(num):
        for _ in range(3):
            try:
                if "zfcg" in driver.current_url:
                    url = re.sub('Paging=\d+','Paging='+str(num),driver.current_url)
                    driver.get(url)
                else:driver.execute_script("javascript:__doPostBack('Pager','%s')" % num)
                locator = (By.XPATH, "//tr[@height='30'][1]/td/a[not(contains(@href,'%s'))]|//*[@id='DataGrid1']/tbody/tr[1]/td/a[not(contains(@href,'%s'))]" % (val,val))
                WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
                break
            except:
                driver.refresh()
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//tr[@height='30']|//table[@id='DataGrid1']//tr")
    for content in content_list:
        # name = content.xpath("./td/a")[0].xpath("string(.)").strip()
        # if '...' in name:
        name = content.xpath("./td/a/@title")[0].strip()
        ggstart_time = content.xpath("./td[last()]/text()")[0].strip()
        try:
            area = content.xpath('./td//span/text()')[0].strip().strip('[').strip(']')
        except:area='None'
        info = json.dumps({'area': area}, ensure_ascii=False)
        url = "http://www.ordosggzyjy.org.cn" + content.xpath("./td/a/@href")[0].strip()

        temp = [name, ggstart_time, url,info]
        data.append(temp)
        # print(temp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):

    if "zfcg" in driver.current_url:
        total_page = re.findall("\/(\d+)",driver.find_element_by_xpath('//td[@class="huifont"]').text)[0]
    else:

        locator = (By.XPATH, '//*[@id="Pager"]/div/font[2]/b')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        total_page = driver.find_element_by_xpath('//*[@id="Pager"]/div/font[2]/b').text

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//table[@id='tblInfo']")
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
    div = soup.find('table', id='tblInfo')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/showinfo/MoreListSqhb.aspx?CategoryNum=009001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/showinfo/MoreListSqhb.aspx?CategoryNum=009002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/showinfo/MoreListSqhb.aspx?CategoryNum=009003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_zhongbiaohxbian_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/showinfo/MoreListSqhb.aspx?CategoryNum=009007",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'中标候选人变更'}), f2],
    ["gcjs_zhongbiao_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/showinfo/MoreListSqhb.aspx?CategoryNum=009004",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_zhongbiaobiangeng_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/showinfo/MoreListSqhb.aspx?CategoryNum=009006",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'中标变更'}), f2],
    ["gcjs_liubiao_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/showinfo/MoreListSqhb.aspx?CategoryNum=009005",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_liubiao_zhongzhi_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/showinfo/MoreListSqhb.aspx?CategoryNum=009008",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/zfcg/010001/?categorynum=010001&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_yanshou_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/zfcg/010011/?categorynum=010011&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_yucai_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/zfcg/010009/?categorynum=010009&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zgys_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/zfcg/010012/?categorynum=010012&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/zfcg/010002/?categorynum=010002&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/zfcg/010003/?categorynum=010003&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_zhongbiaobiangeng_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/zfcg/010004/?categorynum=010004&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'中标变更'}), f2],
    ["zfcg_liubiao_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/zfcg/010005/?categorynum=010005&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_dyly_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/zfcg/010006/?categorynum=010006&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"单一来源"}), f2],

    ["zfcg_zhaobiao_xj_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/zfcg/010008/010008001/?categorynum=010008001&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"询价"}), f2],
    ["zfcg_zhongbiao_xj_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/zfcg/010008/010008002/?categorynum=010008002&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"询价"}), f2],
    ["zfcg_biangeng_xj_gg",
     "http://www.ordosggzyjy.org.cn/TPFront/zfcg/010008/010008004/?categorynum=010008004&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"询价"}), f2],


]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="内蒙古自治区鄂尔多斯市", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":

    work(conp=["postgres", "since2015", "192.168.3.171", "neimenggu", "eeduosi"],pageloadtimeout=60,pageloadstragegy='none')
