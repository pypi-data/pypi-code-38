import json
import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from zhulong.util.etl import est_tbs,est_meta,est_html

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://www.lushan.gov.cn/public/column/4443193?type=4&catId=5337461&action=list"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='lushan'

def f1(driver,num):
    driver.maximize_window()
    locator = (By.XPATH, "//div[@class='xxgk_navli'][1]/ul/li[3]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum=driver.find_element_by_xpath("//span[@class='current']").text
    url = driver.current_url
    catid = re.findall('catId=(\d+)&', url)[0]

    if int(cnum) != num:
        val=driver.find_element_by_xpath('//div[@class="xxgk_navli"][1]/ul/li[3]/a').get_attribute(
            "href")[- 30:-5]
        driver.execute_script('''
                (function(pageIndex){Ls.ajax({
                            dataType: "html",
                            url: "/site/label/165919",
                            data : {
                                siteId : "4443205",
                                pageSize : "16",
                                pageIndex: pageIndex,
                                action : "list",
                                isDate : "true",
                                dateFormat : "yyyy-MM-dd",
                                length : "47",
                                organId: "4443193",
                                type: "4",
                                catId: "%s",
                                cId : "",
                                result : "暂无相关信息"
                            }
                        }).done(function(html) {
                            $("#xxgk_lmcon").html(html);
                        });
                                })(%s);
                '''%(catid,num))
        locator = (By.XPATH, '//div[@class="xxgk_navli"][1]/ul/li[3]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    data=[]
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all('div', class_='xxgk_navli')
    for div in divs:
        lis = div.find_all('li')
        index = lis[1].get_text()
        href = lis[2].a['href']
        name = lis[2].a.get_text().strip()
        ggstart_time = lis[3].get_text()

        info={"index_num":index}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    
    return df


def f2(driver):
    driver.maximize_window()

    locator = (By.XPATH, "//div[@class='xxgk_navli'][1]/ul/li[3]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//*[@id="page_public_info"]/a[last()]').get_attribute('paged')
    total=int(total)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="contentxxgk"][string-length()>10]')

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
    div = soup.find('div',class_='contentxxgk')
    return div

data=[
    #
    ["gcjs_gqita_zhao_zhong_gg","http://www.lushan.gov.cn/public/column/4443193?type=4&catId=5337461&action=list",["name","ggstart_time","href",'info'],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://www.lushan.gov.cn/public/column/4443193?type=4&catId=5337475&action=list",["name","ggstart_time","href",'info'],f1,f2],

    ["zfcg_gqita_zhao_zhong_gg","http://www.lushan.gov.cn/public/column/4443193?type=4&catId=5336732&action=list",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_gqita_zhong_zhonghx_gg","http://www.lushan.gov.cn/public/column/4443193?type=4&catId=5337407&action=list",["name","ggstart_time","href",'info'],f1,f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="江西省庐山市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","jiangxi","lushan"]

    work(conp=conp,headless=False,num=1)