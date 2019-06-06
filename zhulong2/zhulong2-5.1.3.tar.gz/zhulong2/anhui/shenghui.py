import pandas as pd
import re
from lxml import etree
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zhulong2.util.etl import est_meta, est_html, add_info

_name_ = 'anhui_shenghui'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='frameNews']")
    WebDriverWait(driver, 20).until(EC.visibility_of_any_elements_located(locator))
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
    div = soup.find('div', class_='frameNews')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//*[@id="bodyMain"]/div/div[3]/table/tbody/tr[1]/td[1]/a')
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//*[@id="bodyMain"]/div/div[3]/table/tbody/tr[1]/td[1]/a').get_attribute(
        "href")[-30:]
    cnum = driver.find_element_by_xpath('//li[@class="selectedLi"]').text
    url = driver.current_url

    if int(cnum) != int(num):
        url1 = re.sub(r"pageNum=\d+", 'pageNum=' + str(num), url)
        driver.get(url1)
        locator = (
        By.XPATH, '//*[@id="bodyMain"]/div/div[3]/table/tbody/tr[1]/td[1]/a[not(contains(@href,"%s"))] ' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//*[@id="bodyMain"]/div/div[3]/table/tbody/tr')
    for content in content_list:
        ggstart_time = content.xpath('./td[last()]/a/text()')[0].strip().strip('[').strip(']')
        name = re.sub(r'\s+', '', content.xpath("./td[1]/a/text()")[0])
        href = 'http://www.ahzfcg.gov.cn' + content.xpath("./td[1]/a/@href")[0].strip()
        temp = [name, ggstart_time, href]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//*[@id="bodyMain"]/div/div[3]/div[2]/div/ul/li[14]/label/span')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = re.findall(r'共 (\d+) 页', driver.find_element_by_xpath(
        '//*[@id="bodyMain"]/div/div[3]/div[2]/div/ul/li[14]/label/span').text)[0]
    driver.quit()
    return int(total_page)


data = [
    # #
    ["zfcg_zhongbiao_gg",
     "http://www.ahzfcg.gov.cn/cmsNewsController/getCgggNewsList.do?channelCode=sjcg_zbgg&dist_code=340000&bid_type=108&pProviceCode=340000&areacode_prov=340000&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_danyilaiyuan_gg",
     "http://www.ahzfcg.gov.cn/cmsNewsController/getCgggNewsList.do?channelCode=sjcg_dyly&dist_code=340000&bid_type=115&pProviceCode=340000&areacode_prov=340000&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'单一来源'}), f2],
    ["zfcg_zhaobiao_gg",
     "http://www.ahzfcg.gov.cn/cmsNewsController/getCgggNewsList.do?channelCode=sjcg_cggg&dist_code=340000&bid_type=011&pProviceCode=340000&areacode_prov=340000&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg",
     "http://www.ahzfcg.gov.cn/cmsNewsController/getCgggNewsList.do?channelCode=sjcg_zzgg&dist_code=340000&bid_type=113&pProviceCode=340000&areacode_prov=340000&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.ahzfcg.gov.cn/cmsNewsController/getCgggNewsList.do?channelCode=sjcg_gzgg&dist_code=340000&bid_type=110&pProviceCode=340000&areacode_prov=340000&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_chengjiao_gg",
     "http://www.ahzfcg.gov.cn/cmsNewsController/getCgggNewsList.do?channelCode=sjcg_cjgg&dist_code=340000&bid_type=110&pProviceCode=340000&areacode_prov=340000&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'成交'}), f2],

    ["zfcg_gqita_gg",
     "http://www.ahzfcg.gov.cn/cmsNewsController/getCgggNewsList.do?channelCode=sjcg_qtgg&dist_code=340000&title=&bid_type=107&pProviceCode=340000&areacode_prov=340000&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="安徽省省会", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.4.175", "zfcg", "anhui_shenghui"], pageloadtimeout=60)
    # url = "http://www.ahzfcg.gov.cn/cmsNewsController/getCgggNewsList.do?channelCode=sjcg_cggg&dist_code=340000&bid_type=011&pProviceCode=340000&areacode_prov=340000&pageNum=1"
    # d = webdriver.Chrome()
    # d.get(url)
    # for i in range(3500,7700):
    #     print(f1(d, i))
    #
    # f2(d)
