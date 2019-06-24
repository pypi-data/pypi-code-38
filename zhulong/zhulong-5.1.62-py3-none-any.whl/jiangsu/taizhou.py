import re
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_meta, est_html, add_info
import time
_name_='taizhou'
global URLS
URLS = [
    "http://58.222.225.18/ggzy/jyxx/004003/004003002/004003002001/MoreInfo.aspx?CategoryNum=004003002001",
    "http://58.222.225.18/ggzy/jyxx/004003/004003002/004003002003/MoreInfo.aspx?CategoryNum=004003002003",
    "http://58.222.225.18/ggzy/jyxx/004003/004003002/004003002004/MoreInfo.aspx?CategoryNum=004003002004",
    "http://58.222.225.18/ggzy/jyxx/004003/004003002/004003002005/MoreInfo.aspx?CategoryNum=004003002005",
    "http://58.222.225.18/ggzy/jyxx/004003/004003002/004003002006/MoreInfo.aspx?CategoryNum=004003002006",
]


def f3(driver, url):
    driver.get(url)
    locator = (By.ID, "tblInfo")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))

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


def f1(driver, num):
    locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    val = driver.find_element_by_xpath('//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a').get_attribute("href")[-50:]

    try:
        cnum = driver.find_element_by_xpath('//font[@color="red"]/b').text
    except:

        page_list = driver.find_elements_by_xpath('//font/img')
        cnum_temp = []
        for p in page_list:
            if 'first' in p.get_attribute('src') or 'prev' in p.get_attribute('src') or 'next' in p.get_attribute('src') or 'last' in p.get_attribute('src'):continue
            cnum_temp.append(re.findall(r'(\d)r',p.get_attribute('src'))[0])
        cnum = ''.join(cnum_temp)


    if int(cnum) != int(num):
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','{}')".format(num))
        locator = (
        By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))

    locator =(By.XPATH,'//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr/td')
    WebDriverWait(driver,30).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//table[@id='MoreInfoList1_DataGrid1']//tr")
    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        try:
            ggstart_time = content.xpath("./td[3]/text()")[0].strip()
        except:ggstart_time = '网页错误'
        url = "http://58.222.225.18" + content.xpath("./td/a/@href")[0]
        temp = [name, ggstart_time, url]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    total_page = int(WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,'//font[@color="blue"][2]/b'))).text)
    driver.quit()
    return total_page


data = [

    ["gcjs_zhaobiao_gg", "http://58.222.225.18/ggzy/ShowInfo/MoreInfo.aspx?CategoryNum=004001001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgysjg_gg", "http://58.222.225.18/ggzy/ShowInfo/MoreInfo.aspx?CategoryNum=004001002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_dayi_gg", "http://58.222.225.18/ggzy/ShowInfo/MoreInfo.aspx?CategoryNum=004001003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://58.222.225.18/ggzy/ShowInfo/MoreInfo.aspx?CategoryNum=004001004",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://58.222.225.18/ggzy/ShowInfo/MoreInfo.aspx?CategoryNum=004001005",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhaobiao_zjfb_gg", "http://58.222.225.18/ggzy/ShowInfo/MoreInfo.aspx?CategoryNum=004001006",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"直接发包"}), f2],

    ["gcjs_jiaotong_zhaobiao_gg", "http://58.222.225.18/ggzy/jyxx/004002/004002001/MoreInfo.aspx?CategoryNum=004002001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_jiaotong_zhongbiaohx_gg",
     "http://58.222.225.18/ggzy/jyxx/004002/004002004/MoreInfo.aspx?CategoryNum=004002004",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_jiaotong_zhongbiao_gg",
     "http://58.222.225.18/ggzy/jyxx/004002/004002005/MoreInfo.aspx?CategoryNum=004002005",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_yucai_gg", "http://58.222.225.18/ggzy/jyxx/004003/004003001/MoreInfo.aspx?CategoryNum=004003001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://58.222.225.18/ggzy/jyxx/004003/004003003/MoreInfo.aspx?CategoryNum=004003003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://58.222.225.18/ggzy/jyxx/004003/004003004/MoreInfo.aspx?CategoryNum=004003004",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_shuili_zhaobiao_gg", "http://58.222.225.18/ggzy/jyxx/004007/004007001/MoreInfo.aspx?CategoryNum=004007001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhongbiaohx_gg", "http://58.222.225.18/ggzy/jyxx/004007/004007005/MoreInfo.aspx?CategoryNum=004007005",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_biangeng_gg", "http://58.222.225.18/ggzy/jyxx/004007/004007003/MoreInfo.aspx?CategoryNum=004007003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhongbiao_gg", "http://58.222.225.18/ggzy/jyxx/004007/004007006/MoreInfo.aspx?CategoryNum=004007006",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_zhao_zhong_gc_gg", "http://58.222.225.18/ggzy/jyxx/004009/004009009/MoreInfo.aspx?CategoryNum=004009009",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"工程"}), f2],
    ["jqita_gqita_zhao_zhong_hw_gg", "http://58.222.225.18/ggzy/jyxx/004009/004009010/MoreInfo.aspx?CategoryNum=004009010",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"货物"}), f2],
    ["jqita_gqita_zhao_zhong_fw_gg", "http://58.222.225.18/ggzy/jyxx/004009/004009011/MoreInfo.aspx?CategoryNum=004009011",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"服务"}), f2],
    #
    ["zfcg_zhaobiao_gkzb_gg",
     "http://58.222.225.18/ggzy/jyxx/004003/004003002/004003002001/MoreInfo.aspx?CategoryNum=004003002001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"公开招标"}), f2],
    ["zfcg_zhaobiao_xj_gg",
     "http://58.222.225.18/ggzy/jyxx/004003/004003002/004003002003/MoreInfo.aspx?CategoryNum=004003002003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"询价"}), f2],
    ["zfcg_zhaobiao_jzxtp_gg",
     "http://58.222.225.18/ggzy/jyxx/004003/004003002/004003002004/MoreInfo.aspx?CategoryNum=004003002004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"竞争性谈判"}), f2],
    ["zfcg_zhaobiao_dyly_gg",
     "http://58.222.225.18/ggzy/jyxx/004003/004003002/004003002005/MoreInfo.aspx?CategoryNum=004003002005",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"单一来源"}), f2],

    ["zfcg_zhaobiao_wsjj_gg",
     "http://58.222.225.18/ggzy/jyxx/004003/004003002/004003002006/MoreInfo.aspx?CategoryNum=004003002006",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp,**kwargs):
    est_meta(conp, data=data, diqu="江苏省泰州市",**kwargs)
    est_html(conp, f=f3,**kwargs)


if __name__ == "__main__":
    # conp=["postgres", "since2015", "192.168.3.171", "jiangsu", "taizhou"]
    # work(conp)
    driver = webdriver.Chrome()
    url = "http://58.222.225.18/ggzy/ShowInfo/MoreInfo.aspx?CategoryNum=004001001"
    driver.get(url)
    f1(driver, 64)
    f1(driver, 268)
    f1(driver, 344)
    driver.quit()
