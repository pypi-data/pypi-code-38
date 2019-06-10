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

_name_ = "xinyi"


def f1(driver, num):
    locator = (By.XPATH, "//div[@id='dataList']/ul/li")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    locator = (By.ID, 'pageBtns')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//*[@id='dataList']/ul/li/div[2]/p").text
    cnum = driver.find_element_by_xpath("//div[@id='pageBtns']//span").text[0]
    for _ in range(abs(int(num) - int(cnum))):
        time.sleep(1)
        if int(num) > int(cnum):
            driver.find_element_by_class_name('layui-laypage-next').click()
        else:
            driver.find_element_by_class_name('layui-laypage-prev').click()

        locator = (By.XPATH, "//*[@id='dataList']/ul/li/div[2]/p[not(contains(string(),'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        time.sleep(0.5)

    locator = (By.ID, "dataList")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    locator = (By.XPATH, "//*[@id='dataList']/ul/li/div[2]/p")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    link = driver.current_url.split('&')[-1]
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//*[@id='dataList']/ul/li")
    for content in content_list:
        name = (content.xpath("./div[1]/p/text()")[0] if content.xpath("./div[1]/p/text()") != [] else '') + content.xpath("./div[2]/p/text()")[0]
        ggstart_time = content.xpath('./div[3]/p/text()')[0]
        url = "http://www.xyggzyjy.com/publicity/publicityInfo.html?" + "id=" + re.findall("(\d+)", content.xpath("./@onclick")[0])[0] + "&first_type=0&i=0&two_type_id=0&" + link
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.ID, 'pageBtns')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    length_a = driver.find_elements_by_xpath("//div[@id='pageBtns']//a")
    total_page = int(len(length_a)) - 1
    driver.quit()
    return int(total_page)


def before(f, xmtype, ggtype):
    def wrap(*args):
        driver = args[0]
        switch(driver, xmtype, ggtype)
        return f(*args)

    return wrap


type = {
    "建设工程":
        {
            "招标公告": "javascript:changeTwoType(41,0)",
            "未入围公示": "javascript:changeTwoType(43,2)",
            "最高限价公示": "javascript:changeTwoType(42,1)",
            "评标结果公示": "javascript:changeTwoType(43,2)",
            "中标结果公告": "javascript:changeTwoType(45,4)"
        },

    "政府采购":
        {
            "资格预审": "javascript:changeTwoType(35,1)",
            "采购公告": "javascript:changeTwoType(34,0)",
            "更正公告": "javascript:changeTwoType(37,3)",
            "结果公告": "javascript:changeTwoType(38,4)",
        },
    "药械物资":
        {
            "采购公告": "javascript:changeTwoType(63,0)",
            "更正公告": "javascript:changeTwoType(66,3)",
            "结果公告": "javascript:changeTwoType(67,4)",
            "采购需求": "javascript:changeTwoType(65,2)",
        },
    "其他交易":
        {
            "采购公告": "javascript:changeTwoType(47,0)",
            "结果公告": "javascript:changeTwoType(49,2)",
        },
}


def switch(driver, xmtype, ggtype):
    locator = (By.ID, "dataList")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//*[@id="dataList"]/ul/li/div[2]/p').text

    driver.execute_script(type[xmtype][ggtype])
    if ggtype != "招标公告":
        locator = (By.XPATH, "//*[@id='dataList']/ul/li/div[2]/p[not(contains(string(),'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))


def f3(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "article-info")
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

    div = soup.find('div', class_='article-info')
    return div


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="江苏省新沂市", **kwargs)
    est_html(conp, f=f3, **kwargs)


data = [
    # # 工程建设
    ["gcjs_zhaobiao_gg",
     "http://www.xyggzyjy.com/publicity/publicityList.html?id=1&i=0&icon_cur=/publicReource/upload/20180727/1532679950297.png",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "建设工程", "招标公告"), before(f2, "建设工程", "招标公告")],
    ["gcjs_zgysjg_gg",
     "http://www.xyggzyjy.com/publicity/publicityList.html?id=1&i=0&icon_cur=/publicReource/upload/20180727/1532679950297.png",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "建设工程", "未入围公示"), before(f2, "建设工程", "未入围公示")],
    ["gcjs_kongzhijia_gg",
     "http://www.xyggzyjy.com/publicity/publicityList.html?id=1&i=0&icon_cur=/publicReource/upload/20180727/1532679950297.png",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "建设工程", "最高限价公示"), before(f2, "建设工程", "最高限价公示")],
    ["gcjs_zhongbiaohx_gg",
     "http://www.xyggzyjy.com/publicity/publicityList.html?id=1&i=0&icon_cur=/publicReource/upload/20180727/1532679950297.png",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "建设工程", "评标结果公示"), before(f2, "建设工程", "评标结果公示")],
    ["gcjs_zhongbiao_gg",
     "http://www.xyggzyjy.com/publicity/publicityList.html?id=1&i=0&icon_cur=/publicReource/upload/20180727/1532679950297.png",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "建设工程", "中标结果公告"), before(f2, "建设工程", "中标结果公告")],
    # #
    # # 药械物资
    ["yiliao_zhaobiao_gg",
     "http://www.xyggzyjy.com/publicity/publicityList.html?id=4&i=3&icon_cur=/publicReource/upload/20180727/1532679970360.png",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "药械物资", "采购公告"), before(f2, "药械物资", "采购公告")],
    ["yiliao_zhongbiao_gg",
     "http://www.xyggzyjy.com/publicity/publicityList.html?id=4&i=3&icon_cur=/publicReource/upload/20180727/1532679970360.png",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "药械物资", "结果公告"), before(f2, "药械物资", "结果公告")],
    ["yiliao_biangeng_gg",
     "http://www.xyggzyjy.com/publicity/publicityList.html?id=4&i=3&icon_cur=/publicReource/upload/20180727/1532679970360.png",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "药械物资", "更正公告"), before(f2, "药械物资", "更正公告")],

    ["yiliao_yucai_gg",
     "http://www.xyggzyjy.com/publicity/publicityList.html?id=4&i=3&icon_cur=/publicReource/upload/20180727/1532679970360.png",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "药械物资", "采购需求"), before(f2, "药械物资", "采购需求")],
    # 政府采购
    ["zfcg_zgys_gg",
     "http://www.xyggzyjy.com/publicity/publicityList.html?id=2&i=1&icon_cur=/publicReource/upload/20180727/1532679957706.png",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "政府采购", "资格预审"), before(f2, "政府采购", "资格预审")],
    ["zfcg_zhaobiao_gg",
     "http://www.xyggzyjy.com/publicity/publicityList.html?id=2&i=1&icon_cur=/publicReource/upload/20180727/1532679957706.png",
     ["name", "ggstart_time", "href", "info"], before(f1, "政府采购", "采购公告"), before(f2, "政府采购", "采购公告")],
    ["zfcg_biangeng_gg",
     "http://www.xyggzyjy.com/publicity/publicityList.html?id=2&i=1&icon_cur=/publicReource/upload/20180727/1532679957706.png",
     ["name", "ggstart_time", "href", "info"], before(f1, "政府采购", "更正公告"), before(f2, "政府采购", "更正公告")],
    ["zfcg_gqita_zhong_liu_gg",
     "http://www.xyggzyjy.com/publicity/publicityList.html?id=2&i=1&icon_cur=/publicReource/upload/20180727/1532679957706.png",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "政府采购", "结果公告"), before(f2, "政府采购", "结果公告")],
    # #
    ["jqita_zhaobiao_gg",
     "http://www.xyggzyjy.com/publicity/publicityList.html?id=7&i=6&icon_cur=/publicReource/upload/20180727/1532680007486.png",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "其他交易", "采购公告"), before(f2, "其他交易", "采购公告")],
    ["jqita_zhongbiao_gg",
     "http://www.xyggzyjy.com/publicity/publicityList.html?id=7&i=6&icon_cur=/publicReource/upload/20180727/1532680007486.png",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "其他交易", "结果公告"), before(f2, "其他交易", "结果公告")],
]

if __name__ == '__main__':

    conp = ["postgres", "since2015", "192.168.3.171", "jiangsu", "xinyi"]

