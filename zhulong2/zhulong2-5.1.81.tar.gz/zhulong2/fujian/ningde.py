import json
import time

import pandas as pd
import re

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from zhulong2.util.etl import est_html, est_meta, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hefei.gov.cn/jyxx/002001/002001002/moreinfo_jyxx.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'fujian_ningde'


def f1(driver, num):
    locator = (By.XPATH, '//tr[@class="gradeX"][1]/td[4]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    cnum = re.findall('\?page=(\d+?)&', url)[0]

    if int(cnum) != num:
        s='?page=%d&'%num
        val = driver.find_element_by_xpath('//tr[@class="gradeX"][1]/td[4]/a').get_attribute('href')[-30:]

        url = re.sub('\?page=(\d+?)&',s,url)

        driver.get(url)

        locator = (By.XPATH, '//tr[@class="gradeX"][1]/td[4]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find_all('tr', class_='gradeX')

    for tr in trs:
        tds=tr.find_all('td')
        address=tds[0].get_text()
        cg_type=tds[1].get_text()
        cg_dw=tds[2].get_text()
        href=tds[3].a['href']
        name=tds[3].a.get_text()
        ggstart_time=tds[4].get_text()

        if 'http' in href:
            href = href
        else:
            href = "http://zfcg.czj.ningde.gov.cn" + href
        info={'diqu':address,'cg_type':cg_type,'cg_dw':cg_dw}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)


    return df


def f2(driver):
    locator = (By.XPATH, '//tr[@class="gradeX"][1]/td[4]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//div[@class="pageGroup"]/button[last()]').get_attribute('onclick')

    page = re.findall('page=(\d+?)&', page)[0]
    total=int(page)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="print-content"][string-length()>10]')

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

    div = soup.find('div',class_="notice-cont")

    return div


data = [

    ["zfcg_zhaobiao_gg", "http://zfcg.czj.ningde.gov.cn/350900/noticelist/d03180adb4de41acbb063875889f9af1/?page=1&notice_type=463fa57862ea4cc79232158f5ed02d03", ['name', 'ggstart_time', 'href','info'],f1, f2],
    ["zfcg_biangeng_gg", "http://zfcg.czj.ningde.gov.cn/350900/noticelist/d03180adb4de41acbb063875889f9af1/?page=1&notice_type=7dc00df822464bedbf9e59d02702b714", ['name', 'ggstart_time', 'href','info'],f1, f2],
    ["zfcg_zhongbiao_gg", "http://zfcg.czj.ningde.gov.cn/350900/noticelist/d03180adb4de41acbb063875889f9af1/?page=1&notice_type=b716da75fe8d4e4387f5a8c72ac2a937", ['name', 'ggstart_time', 'href','info'],f1, f2],
    ["zfcg_gqita_bian_gg", "http://zfcg.czj.ningde.gov.cn/350900/noticelist/d03180adb4de41acbb063875889f9af1/?page=1&notice_type=d812e46569204c7fbd24cbe9866d0651", ['name', 'ggstart_time', 'href','info'],f1, f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://zfcg.czj.ningde.gov.cn/350900/noticelist/d03180adb4de41acbb063875889f9af1/?page=1&notice_type=255e087cf55a42139a1f1b176b244ebb", ['name', 'ggstart_time', 'href','info'],add_info(f1,{'zbfs':"单一来源"}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="福建省宁德市", **args)
    est_html(conp, f=f3, **args)

if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "lch", "fujian_ningde"]

    work(conp=conp,num=1)