import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zhulong2.util.etl import est_meta, est_html, add_info

_name_ = 'jiangsu_huaian'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='list-lb']")
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
    div = soup.find('div', class_='list-lb')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="list-lb"]')
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//div[@class="list-lb"]/ul/li/a').get_attribute("href")[-40:]

    cnum = re.findall('(\d+)/', driver.find_element_by_xpath('//span[@id="info"]').text)[0]
    if int(cnum) != int(num):
        url = re.sub(r'list[_\d]*\.', "list." if num == 1 else ('list_' + str(num) + '.'), driver.current_url)
        driver.get(url)
        locator = (By.XPATH, '//div[@class="list-lb"]/ul/li/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="list-lb"]/ul/li')
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()

        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://zfcgzx.huaian.gov.cn/" + content.xpath("./a/@href")[0]
        temp = [name, ggstart_time, url]
        # print(temp)
        data.append(temp)
    # print(data[0])
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):

    locator = (By.XPATH, '//span[@id="info"]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = re.findall('/(\d+)', driver.find_element_by_xpath('//span[@id="info"]').text)[0]
    driver.quit()
    return int(total_page)


data = [
    #




    ["zfcg_zgys_gg",
     "http://zfcgzx.huaian.gov.cn/zbcg/cggg/column1/list.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_gk_sxq_gg",
     "http://zfcgzx.huaian.gov.cn/col/7646_415211/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'公开','area':'市辖区'}), f2],
    ["zfcg_zhaobiao_gk_qjpq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17087_758155/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'公开','area':'清江浦区'}), f2],
    ["zfcg_zhaobiao_gk_hyq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17088_713786/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'公开','area':'淮阴区'}), f2],
    ["zfcg_zhaobiao_gk_haq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17089_262412/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'公开','area':'淮安区'}), f2],
    ["zfcg_zhaobiao_gk_hz_gg",
     "http://zfcgzx.huaian.gov.cn/col/17090_464532/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'公开','area':'洪泽区'}), f2],
    ["zfcg_zhaobiao_gk_jhx_gg",
     "http://zfcgzx.huaian.gov.cn/col/17091_783853/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'公开','area':'金湖县'}), f2],
    ["zfcg_zhaobiao_gk_xyx_gg",
     "http://zfcgzx.huaian.gov.cn/col/17092_144688/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'公开','area':'盱眙县'}), f2],
    ["zfcg_zhaobiao_gk_lsx_gg",
     "http://zfcgzx.huaian.gov.cn/col/17093_184578/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'公开','area':'涟水县'}), f2],
    ["zfcg_zhaobiao_gk_kfq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17094_543212/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'公开','area':'开发区'}), f2],


    ["zfcg_zhaobiao_tp_sxq_gg",
     "http://zfcgzx.huaian.gov.cn/col/7648_343742/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'竞争性谈判','area':'市辖区'}), f2],
    ["zfcg_zhaobiao_tp_qjpq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17103_353228/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'竞争性谈判','area':'清江浦区'}), f2],
    ["zfcg_zhaobiao_tp_hyq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17104_182424/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'竞争性谈判','area':'淮阴区'}), f2],
    ["zfcg_zhaobiao_tp_haq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17105_561732/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'竞争性谈判','area':'淮安区'}), f2],
    ["zfcg_zhaobiao_tp_hz_gg",
     "http://zfcgzx.huaian.gov.cn/col/17106_814714/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'竞争性谈判','area':'洪泽区'}), f2],
    ["zfcg_zhaobiao_tp_jhx_gg",
     "http://zfcgzx.huaian.gov.cn/col/17107_582661/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'竞争性谈判','area':'金湖县'}), f2],
    ["zfcg_zhaobiao_tp_xyx_gg",
     "http://zfcgzx.huaian.gov.cn/col/17108_467778/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'竞争性谈判','area':'盱眙县'}), f2],
    ["zfcg_zhaobiao_tp_lsx_gg",
     "http://zfcgzx.huaian.gov.cn/col/17109_387863/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'竞争性谈判','area':'涟水县'}), f2],
    ["zfcg_zhaobiao_tp_kfq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17110_864738/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'竞争性谈判','area':'开发区'}), f2],





    ["zfcg_zhaobiao_xj_sxq_gg",
     "http://zfcgzx.huaian.gov.cn/col/7651_843614/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'市辖区'}), f2],
    ["zfcg_zhaobiao_xj_qjpq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17127_241613/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'清江浦区'}), f2],
    ["zfcg_zhaobiao_xj_hyq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17128_443644/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'淮阴区'}), f2],
    ["zfcg_zhaobiao_xj_haq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17129_218728/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'淮安区'}), f2],
    ["zfcg_zhaobiao_xj_hz_gg",
     "http://zfcgzx.huaian.gov.cn/col/17130_346846/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'洪泽区'}), f2],
    ["zfcg_zhaobiao_xj_jhx_gg",
     "http://zfcgzx.huaian.gov.cn/col/17131_156461/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'金湖县'}), f2],
    ["zfcg_zhaobiao_xj_xyx_gg",
     "http://zfcgzx.huaian.gov.cn/col/17132_631725/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'盱眙县'}), f2],
    ["zfcg_zhaobiao_xj_lsx_gg",
     "http://zfcgzx.huaian.gov.cn/col/17133_418251/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'涟水县'}), f2],
    ["zfcg_zhaobiao_xj_kfq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17134_281124/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'开发区'}), f2],


    ["zfcg_gqita_qjpq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17167_368558/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'清江浦区'}), f2],
    ["zfcg_gqita_hyq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17168_113414/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'淮阴区'}), f2],
    ["zfcg_gqita_haq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17169_147346/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'淮安区'}), f2],
    ["zfcg_gqita_hz_gg",
     "http://zfcgzx.huaian.gov.cn/col/17170_822321/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'洪泽区'}), f2],
    ["zfcg_gqita_jhx_gg",
     "http://zfcgzx.huaian.gov.cn/col/17171_233445/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'金湖县'}), f2],
    ["zfcg_gqita_xyx_gg",
     "http://zfcgzx.huaian.gov.cn/col/17172_516536/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'盱眙县'}), f2],
    ["zfcg_gqita_lsx_gg",
     "http://zfcgzx.huaian.gov.cn/col/17173_233177/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'涟水县'}), f2],
    ["zfcg_gqita_kfq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17174_762678/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价','area':'开发区'}), f2],




    ["zfcg_zhongbiao_sxq_gg",
     "http://zfcgzx.huaian.gov.cn/col/7652_848872/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'市辖区'}), f2],
    ["zfcg_zhongbiao_qjpq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17135_173775/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'清江浦区'}), f2],
    ["zfcg_zhongbiao_hyq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17136_421323/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'淮阴区'}), f2],
    ["zfcg_zhongbiao_haq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17137_583375/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'淮安区'}), f2],
    ["zfcg_zhongbiao_hz_gg",
     "http://zfcgzx.huaian.gov.cn/col/17138_554738/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'洪泽区'}), f2],
    ["zfcg_zhongbiao_jhx_gg",
     "http://zfcgzx.huaian.gov.cn/col/17139_162856/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'金湖县'}), f2],
    ["zfcg_zhongbiao_xyx_gg",
     "http://zfcgzx.huaian.gov.cn/col/17140_641487/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'盱眙县'}), f2],
    ["zfcg_zhongbiao_lsx_gg",
     "http://zfcgzx.huaian.gov.cn/col/17141_284284/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'涟水县'}), f2],
    ["zfcg_zhongbiao_kfq_gg",
     "http://zfcgzx.huaian.gov.cn/col/17142_333831/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'开发区'}), f2],





    ["zfcg_zhaobiao_yq_gg",
     "http://zfcgzx.huaian.gov.cn/zbcg/cggg/column3/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'邀请'}), f2],
    ["zfcg_zhaobiao_cs_gg",
     "http://zfcgzx.huaian.gov.cn/zbcg/cggg/column6/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'竞争性磋商'}), f2],
    ["zfcg_zhaobiao_dyly_gg",
     "http://zfcgzx.huaian.gov.cn/zbcg/cggg/column6/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'单一来源'}), f2],
    ["zfcg_zhongbiao_gg",
     "http://zfcgzx.huaian.gov.cn/zbcg/cggg/column10/list.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg",
     "http://zfcgzx.huaian.gov.cn/zbcg/cggg/column11/list.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://zfcgzx.huaian.gov.cn/zbcg/cggg/column12/list.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_jz_gg",
     "http://zfcgzx.huaian.gov.cn/jzcgml/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'集中采购'}), f2],


]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省淮安市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jiangsu_huaian"])
