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

_name_ = "gansusheng"


def f1(driver, num):
    locator = (By.XPATH, "//table[@id='materialtab']/tbody/tr[last()]/td[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='pageFlip']/a[@class='cur']")
    try:
        txt = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(txt)
    except:cnum=1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@id='materialtab']/tbody/tr[last()]/td[last()]/a").get_attribute('onclick')
        val = re.findall(r'\(\'(.*)\'\)', val)[0].split("'")[0]
        ss = """
        function goToPage(pageNo){
        condition = $('#condition').val();
        query(condition,pageNo);  
        };
        goToPage(%s);
        """%num
        driver.execute_script(ss)
        locator = (By.XPATH, "//table[@id='materialtab']/tbody/tr[last()]/td[last()]/a[not(contains(@onclick, '%s'))]" % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find('table', id='materialtab').tbody
    trs = table.find_all('tr')
    data = []

    for tr in trs:
        info = {}
        a = tr.find('a')

        name = tr.find_all('td')[1].text.strip()
        xm_code = re.findall(r'[-\d]+', name)[-1]
        ggstart_time = 'None'
        info['xm_code']=xm_code
        deal_code = re.findall(r'\(\'(.*)\'\)', a['onclick'])[0].split("'")[0]
        pppId = re.findall(r'\(\'(.*)\'\)', a['onclick'])[0].rsplit("'")[-1]
        href = 'http://tzxm.gszwfw.gov.cn:8090/tzxmspweb/tzxmweb/pages/portal/publicinformation/pppProjectInfoDetail.jsp?deal_code='+deal_code+"&ppp_uuid="+pppId+"&from_type=0"
        zuhefangshi = tr.find_all('td')[2].text.strip()
        info['zuhefangshi']=zuhefangshi
        xm_zongtouzi = tr.find_all('td')[3].text.strip()
        info['xm_zongtouzi']=xm_zongtouzi
        xingzhengquhua = tr.find_all('td')[4].text.strip()
        info['xingzhengquhua']=xingzhengquhua
        xm_jieduan = tr.find_all('td')[5].text.strip()
        info['xm_jieduan']=xm_jieduan
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [name,  ggstart_time,href,info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='pageNum']/span[1]/strong")
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    total_page = int(txt)
    driver.quit()
    return total_page


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='box_main'][string-length()>40]")
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
    div = soup.find('div', class_="box_main")
    return div


data = [

    ["xm_shenpi_ppp_gg",
     "http://tzxm.gszwfw.gov.cn:8090/tzxmspweb/portalopenPublicInformation.do?method=goPPPProjectPublicPage",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'PPP项目公示'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="甘肃省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres","since2015","192.168.3.171","zlshenpi","gansusheng"],pageloadtimeout=120)

    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     # df = f2(driver)
    #     # print(df)
    #     driver.maximize_window()
    #     df = f1(driver,4)
    #     print(df.values)
    #     for j in df[2].values:
    #         df = f3(driver, j)
    #         print(df)
