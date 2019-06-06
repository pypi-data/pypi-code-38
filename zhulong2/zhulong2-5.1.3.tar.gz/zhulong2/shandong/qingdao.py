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


from zhulong2.util.etl import est_tbs, est_meta, est_html, gg_existed, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hefei.gov.cn/jyxx/002001/002001002/moreinfo_jyxx.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_='shandong_qingdao'



def f1(driver,num):

    locator = (By.XPATH, '(//div[@style="display: block;" or (@id="tagContent0" and not (@style))]//a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    if num != 1:
        val = driver.find_element_by_xpath(
            '(//div[@style="display: block;" or (@id="tagContent0" and not (@style))]//a)[1]').get_attribute('href')[-25:-5]
        driver.execute_script('pageClick("%s")' % num)

        locator = (By.XPATH,
                   '(//div[@style="display: block;" or (@id="tagContent0" and not (@style))]//a)[1][not(contains(@href,"{val}"))]'.format(
                       val=val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find('div', attrs={'class':re.compile('tagContent hangc.*'),'style':'display: block;'})
    if not divs:
        divs = soup.find('div', attrs={'id':"tagContent0",'style':''}).find_all('div',class_='neitzbox')
    else:
        divs=divs.find_all('div',class_='neitzbox')

    for div in divs:

        href=div.find('div',class_='neinewli').a['href']
        name=div.find('div',class_='neinewli').a['title']
        name1=div.find('div',class_='neinewli').a.get_text().strip()
        diqu=re.findall('^\[(.+?)\]',name1)

        if diqu:
            info={'diqu':diqu[0]}
            info=json.dumps(info,ensure_ascii=False)
        else:
            info=None
        ggstart_time=div.find('div',class_='neitime').get_text()
        if 'http' in href:
            href=href
        else:
            href="http://www.ccgp-qingdao.gov.cn/sdgp2014/site/"+href

        tmp = [name, ggstart_time,href,info]

        data.append(tmp)

    df=pd.DataFrame(data=data)

    return df


def f2(driver):
    interval_page = 100
    lower = 0
    hight = interval_page

    while (hight - lower) > 1:

        total = (hight - lower) // 2 + lower

        val = driver.find_element_by_xpath(
            '(//div[@style="display: block;" or (@id="tagContent0" and not (@style))]//a)[1]').get_attribute('href')[-25:-5]
        driver.execute_script('pageClick("%s")' % (total))

        try:
            locator = (By.XPATH,
            '(//div[@style="display: block;" or (@id="tagContent0" and not (@style))]//a)[1][not(contains(@href,"{val}"))]'.format(val=val))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH,
                       '(//div[@style="display: block;" or (@id="tagContent0" and not (@style))]//a)[1][not(contains(@href,"#"))]')
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))
            hight += interval_page
            lower = total

        except:
            try:
                alert = driver.switch_to.alert
                alert.accept()
            except:
                if '没有查询到信息' in driver.page_source:
                    break
                else:
                    raise ValueError
            hight = total
            interval_page = interval_page // 2

    total=total-1
    driver.quit()
    return total





def chang(f,mark_i):
    def inner(*args):
        driver=args[0]
        locator = (By.XPATH, '(//div[@style="display: block;" or (@id="tagContent0" and not (@style))]//a)[1]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        cur_text=driver.find_element_by_xpath('//li[@class="selectTag"]/a').text
        the_text=driver.find_element_by_xpath('//ul[@id="tags"]/li[{mark_i}]/a'.format(mark_i=mark_i+1)).text

        if cur_text != the_text:
            val=driver.find_element_by_xpath('(//div[@id="tagContent0"]//a)[1]').get_attribute('href')[-25:-5]
            driver.find_element_by_xpath('//ul[@id="tags"]/li[{mark_i}]/a'.format(mark_i=mark_i+1)).click()
            locator=(By.XPATH,'(//div[@id="tagContent{mark_i}"]//a)[1][not(contains(@href,"{val}"))]'.format(mark_i=mark_i,val=val))
            WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        return f(*args)
    return inner





def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="cont"][string-length()>10]')

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


    div1 = soup.find('div',class_="cont")
    div1.find_all('table')[-1].extract()
    div2=div1.find_next_sibling('div',align="left")
    div=BeautifulSoup(str(div1)+str(div2),'html.parser')

    if div == None:
        raise ValueError

    return div

data=[
        #
    ["zfcg_zhaobiao_diqu1_gg", "http://www.ccgp-qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0401&flag=0401",['name', 'ggstart_time', 'href', 'info'], add_info(chang(f1,0),{"diqu":"市本级"}), chang(f2,0)],
    ["zfcg_zhaobiao_diqu2_gg", "http://www.ccgp-qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0501&flag=0501",['name', 'ggstart_time', 'href', 'info'], chang(f1,0), chang(f2,0)],

    ["zfcg_zhongbiao_diqu1_gg", "http://www.ccgp-qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0401&flag=0401",['name', 'ggstart_time', 'href', 'info'], add_info(chang(f1,1),{"diqu":"市本级"}), chang(f2,1)],
    ["zfcg_zhongbiao_diqu2_gg", "http://www.ccgp-qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0501&flag=0501",['name', 'ggstart_time', 'href', 'info'], chang(f1,1), chang(f2,1)],

    ["zfcg_biangeng_diqu1_gg", "http://www.ccgp-qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0401&flag=0401",['name', 'ggstart_time', 'href', 'info'], add_info(chang(f1,2),{"diqu":"市本级"}), chang(f2,2)],
    ["zfcg_biangeng_diqu2_gg", "http://www.ccgp-qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0501&flag=0501",['name', 'ggstart_time', 'href', 'info'], chang(f1,2), chang(f2,2)],

    ["zfcg_liubiao_diqu1_gg", "http://www.ccgp-qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0401&flag=0401",['name', 'ggstart_time', 'href', 'info'], add_info(chang(f1,3),{"diqu":"市本级"}), chang(f2,3)],
    ["zfcg_liubiao_diqu2_gg", "http://www.ccgp-qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0501&flag=0501",['name', 'ggstart_time', 'href', 'info'], chang(f1,3), chang(f2,3)],

    ["zfcg_zhaobiao_danyilaiyuan_diqu1_gg", "http://www.ccgp-qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0401&flag=0401",['name', 'ggstart_time', 'href', 'info'], add_info(chang(f1,4),{"diqu":"市本级","zbfs":"单一来源"}), chang(f2,4)],
    ["zfcg_zhaobiao_danyilaiyuan_diqu2_gg", "http://www.ccgp-qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0501&flag=0501",['name', 'ggstart_time', 'href', 'info'], chang(f1,4), chang(f2,4)],

    ["zfcg_gqita_diqu2_gg", "http://www.ccgp-qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0501&flag=0501",['name', 'ggstart_time', 'href', 'info'], chang(f1,5), chang(f2,5)],

]

###区县的地区可从f1获取,不用add_info

def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省青岛市",**args)
    est_html(conp,f=f3,**args)
if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","shandong_qingdao"]

    # work(conp=conp,headless=False,num=1,cdc_total=2)

    driver=webdriver.Chrome()
    url="http://www.ccgp-qingdao.gov.cn/sdgp2014/site/read370200.jsp?id=1578&flag=0501"
    # driver.get(url)
    f3(driver,url)