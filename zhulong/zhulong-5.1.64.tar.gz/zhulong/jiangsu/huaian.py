import re

from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import gg_meta, gg_html, est_html, est_meta, add_info
import time

_name_="huaian"
def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='menu-right-items']")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//li[@class='menu-right-item clearfix'][1]/a").get_attribute("href")[-60:]
    if driver.find_element_by_xpath('//div[@class="page1"]').text == '':
        cnum=1
    else: cnum = int(driver.find_element_by_xpath('//div[@class="page1"]/ul/li/a[contains(@class,"wb-page-number")]').text.split('/')[0])

    if int(num) != cnum:
        url = re.sub('pageing=\d+','pageing='+str(num),driver.current_url)
        driver.get(url)
        locator = (By.XPATH, "//li[@class='menu-right-item clearfix'][1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    data = []
    content_list = body.xpath("//ul[@class='menu-right-items']/li")
    for content in content_list:
        name = content.xpath('./a/text()')[0]
        ggstart_time = content.xpath('./span/text()')[0].strip()
        url_temp = content.xpath("./a/@href")[0]
        if "http" not in url_temp:
            url = "http://222.184.89.82" + content.xpath("./a/@href")[0]
        else:url = url_temp
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):

    locator = (By.XPATH, '//div[@class="page1"]')
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    if driver.find_element_by_xpath('//div[@class="page1"]').text == '':total_page=1
    else:total_page = int(driver.find_element_by_xpath('//div[@class="page1"]/ul/li/a[contains(@class,"wb-page-number")]').text.split('/')[1])


    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "article-block")
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
    div = soup.find('div', class_='article-block')
    # print(div)
    return div


data = [
    # 工程建设
    ["gcjs_zhaobiao_gg", "http://222.184.89.82/EpointWeb/jyxx/003001/003001001/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://222.184.89.82/EpointWeb/jyxx/003001/003001002/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg", "http://222.184.89.82/EpointWeb/jyxx/003001/003001003/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgysjg_gg", "http://222.184.89.82/EpointWeb/jyxx/003001/003001004/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://222.184.89.82/EpointWeb/jyxx/003001/003001005/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhaobiao_zjfb_gg", "http://222.184.89.82/EpointWeb/jyxx/003001/003001006/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"直接发包"}), f2],
    ["gcjs_yucai_gg", "http://222.184.89.82/EpointWeb/jyxx/003001/003001008/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_zhaobiao_gg", "http://222.184.89.82/EpointWeb/jyxx/003006/003006001/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_zhongbiao_gg", "http://222.184.89.82/EpointWeb/jyxx/003006/003006003/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_yucai_gg", "http://222.184.89.82/EpointWeb/jyxx/003006/003006004/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_biangeng_gg", "http://222.184.89.82/EpointWeb/jyxx/003006/003006002/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_liubiao_gg", "http://222.184.89.82/EpointWeb/jyxx/003006/003006006/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_gg", "http://222.184.89.82/EpointWeb/jyxx/003007/003007001/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_zhongbiao_gg", "http://222.184.89.82/EpointWeb/jyxx/003007/003007002/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://222.184.89.82/EpointWeb/jyxx/003002/003002001/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_dyly_gg", "http://222.184.89.82/EpointWeb/jyxx/003002/003002002/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"单一来源"}), f2],
    ["zfcg_zgys_gg", "http://222.184.89.82/EpointWeb/jyxx/003002/003002007/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://222.184.89.82/EpointWeb/jyxx/003002/003002003/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://222.184.89.82/EpointWeb/jyxx/003002/003002005/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg", "http://222.184.89.82/EpointWeb/jyxx/003002/003002004/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    # 机电设备
    ["zfcg_zhaobiao_jdsb_gg", "http://222.184.89.82/EpointWeb/jyxx/003004/003004001/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"机电设备"}), f2],
    ["zfcg_biangeng_jdsb_gg", "http://222.184.89.82/EpointWeb/jyxx/003004/003004002/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"机电设备"}), f2],
    ["zfcg_gqita_zgysjg_zhonghx_jdsb_gg", "http://222.184.89.82/EpointWeb/jyxx/003004/003004005/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"机电设备"}), f2],
    ["zfcg_zhongbiao_jdsb_gg", "http://222.184.89.82/EpointWeb/jyxx/003004/003004003/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"机电设备"}), f2],
    # 区县项目 清江浦
    ["zfcg_zhaobiao_qingjiangpu_gg", "http://222.184.89.82/EpointWeb/jyxx/003009/003009001/003009001001/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"清江浦"}), f2],
    ["zfcg_zhongbiao_qingjiangpu_gg", "http://222.184.89.82/EpointWeb/jyxx/003009/003009001/003009001002/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"清江浦"}), f2],
    # 区县项目 淮阴
    ["zfcg_zhaobiao_huaiyin_gg", "http://222.184.89.82/EpointWeb/jyxx/003009/003009003/003009003001/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"淮阴"}), f2],
    ["zfcg_zhongbiao_huaiyin_gg", "http://222.184.89.82/EpointWeb/jyxx/003009/003009003/003009003002/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"淮阴"}), f2],

    # 区县项目 淮安
    ["zfcg_zhaobiao_huaian_gg", "http://222.184.89.82/EpointWeb/jyxx/003009/003009004/003009004001/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"淮安"}), f2],
    ["zfcg_zhongbiao_huaian_gg", "http://222.184.89.82/EpointWeb/jyxx/003009/003009004/003009004002/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"淮安"}), f2],
    # 区县项目 涟水
    ["zfcg_zhaobiao_lianshui_gg", "http://222.184.89.82/EpointWeb/jyxx/003009/003009005/003009005001/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"涟水"}), f2],
    ["zfcg_zhongbiao_huaiyin_gg", "http://222.184.89.82/EpointWeb/jyxx/003009/003009005/003009005002/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"涟水"}), f2],

    # 区县项目 洪泽
    ["zfcg_zhaobiao_hongze_gg", "http://222.184.89.82/EpointWeb/jyxx/003009/003009006/003009006001/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"洪泽"}), f2],
    ["zfcg_zhongbiao_hongze_gg", "http://222.184.89.82/EpointWeb/jyxx/003009/003009006/003009006002/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"洪泽"}), f2],
    # 区县项目 盱眙
    ["zfcg_zhaobiao_huaiyin_gg", "http://222.184.89.82/EpointWeb/jyxx/003009/003009007/003009007001/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"盱眙"}), f2],
    ["zfcg_zhongbiao_huaiyin_gg", "http://222.184.89.82/EpointWeb/jyxx/003009/003009007/003009007002/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"盱眙"}), f2],

    # 区县项目 金湖
    ["zfcg_zhaobiao_jinhu_gg", "http://222.184.89.82/EpointWeb/jyxx/003009/003009008/003009008001/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"金湖"}), f2],
    ["zfcg_zhongbiao_jinhu_gg", "http://222.184.89.82/EpointWeb/jyxx/003009/003009008/003009008002/?pageing=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"金湖"}), f2],

]


def work(conp,**kwargs):
    est_meta(conp, data=data, diqu="江苏省淮安市",**kwargs)
    est_html(conp, f=f3,**kwargs)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "jiangsu", "huaian"])
    # driver= webdriver.Chrome()
    # driver.get("http://222.184.89.82/EpointWeb/jyxx/003006/003006004/?pageing=1")
    # print(f2(driver))
    # for i in range(1,5):print(f1(driver,i))
    # driver.get("http://222.184.89.82/EpointWeb/jyxx/003006/003006004/")
    # for i in range(1,6):print(f1(driver,i))
