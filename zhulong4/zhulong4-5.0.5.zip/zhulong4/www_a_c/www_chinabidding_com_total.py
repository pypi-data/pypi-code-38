import time
from collections import OrderedDict
from pprint import pprint

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json



from zhulong4.util.etl import est_tbs, est_meta, est_html, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.chinabidding.com/search/proj.htm"
# chrome_option=webdriver.ChromeOptions()
# chrome_option.add_argument("--headless")
# chrome_option.add_argument("--no-sandbox")
# driver = webdriver.Chrome(chrome_options=chrome_option)
# driver.maximize_window()
# driver.get(url)



_name_ = 'www_chinabidding_com'


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="as-pager-body"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    if page_total_num==1:
        cnum=1
    else:
        cnum = driver.find_element_by_xpath('//a[@class="current"]').text

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//ul[@class="as-pager-body"]/li[1]/a').get_attribute('href')[-24:-5]

        driver.execute_script('searchSubmit(%s)' % num)

        locator = (By.XPATH, '//ul[@class="as-pager-body"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='as-pager-body')
    trs = div.find_all('li')
    for tr in trs:
        href = tr.a['href']
        name = tr.a.h5.find_all('span')[1]['title']
        ggstart_time = tr.a.h5.find_all('span')[2].get_text().strip('发布时间：')
        strongs=tr.a.div.find_all('strong')

        address = strongs[1].get_text()
        gg_hangye = strongs[0].get_text()

        if len(strongs) == 3:
            zjly=strongs[2].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.chinabidding.com' + href

        if 'zjly' in locals():
            info = {'diqu': address, 'gg_hangye': gg_hangye,'zjly':zjly}
        else:
            info={'diqu':address,'gg_hangye':gg_hangye}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    global page_total_num
    locator = (By.XPATH, '//ul[@class="as-pager-body"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        total = driver.find_element_by_xpath('//div[@class="as-pager-pagation"]//a[last()-1]').text

        total = int(total)
    except:
        if '没找到与搜索条件相关的信息' in driver.page_source:
            total=0
        else:
            total=1
    page_total_num=total
    driver.quit()

    return total



def f3(driver, url):

    driver.get(url)

    locator = (By.XPATH, '//div[@class="as-article"][string-length()>10]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    time.sleep(0.1)
    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 10: break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    div = soup.find('div', class_="as-article")

    return div

def chang_type(f,num):
    def inner(*args):
        driver=args[0]
        locator = (By.XPATH, '//ul[@class="as-pager-body"]/li[1]/a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        ctext=driver.find_element_by_xpath('//ul[@class="table-list-items as-index-list"]/li[2]/a[@class="tag-li on"]').text

        if ctext == '招标公告' and int(num) != 1:
            val = driver.find_element_by_xpath('//ul[@class="as-pager-body"]/li[1]/a').get_attribute('href')[-24:-5]
            driver.find_element_by_xpath('//ul[@class="table-list-items as-index-list"]/li[2]/a[%s]' % num).click()
            locator = (By.XPATH, '//ul[@class="as-pager-body"]/li[1]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        return f(*args)
    return inner


def chang_hangye(f,num1,num2):
    def inner(*args):
        driver=args[0]
        locator = (By.XPATH, '//ul[@class="as-pager-body"]/li[1]/a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        ctext=driver.find_element_by_xpath('//select[@id="normIndustry"]/following-sibling::span').text

        if '所有行业' in ctext:
            val = driver.find_element_by_xpath('//ul[@class="tag-list"]/li/span').text
            driver.execute_script('document.getElementById("normIndustry").style="display:block"')
            select_hangye=Select(driver.find_element_by_xpath('//select[@id="normIndustry"]'))
            select_hangye.select_by_value(str(num1))

            # driver.find_element_by_xpath('//button[@type="submit"]').click()
            locator = (By.XPATH, '//ul[@class="tag-list"]/li/span[text() != %s]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator=(By.XPATH,'//ul[@class="as-pager-body"]/li[1]/a')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        cctext=driver.find_element_by_xpath('//select[@id="zoneCode"]/following-sibling::span').text
        if '所有地区' in cctext:
            val = driver.find_element_by_xpath('//ul[@class="tag-list"]/li/span').text
            driver.execute_script('document.getElementById("zoneCode").style="display:block"')
            select_hangye = Select(driver.find_element_by_xpath('//select[@id="zoneCode"]'))
            select_hangye.select_by_value(str(num2))

            # driver.find_element_by_xpath('//button[@type="submit"]').click()
            locator = (By.XPATH, '//ul[@class="tag-list"]/li/span[text() != %s]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, '//ul[@class="as-pager-body"]/li[1]/a')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        return f(*args)
    return inner

def get_data():

    ###获得zonecode和hangye_dict

    # url = "http://www.chinabidding.com/search/proj.htm"
    # page_source=requests.get(url).text
    #
    # soup=BeautifulSoup(page_source,'html.parser')
    # ###获得行业dict
    # hangye_options=soup.find('select',id='normIndustry').find_all('option')[1:]
    # hangye_dict=OrderedDict()
    # for opt in hangye_options:
    #     hangye_value=opt.get('value')
    #     hangye_name=opt.get_text()
    #     dict_={hangye_value:hangye_name}
    #     hangye_dict.update(**dict_)
    # ###获得地区dict
    # zonecode=OrderedDict()
    # diqu_options=soup.find('select',id='zoneCode').find_all('option',value=re.compile('^.{3}$'))[:-3]
    # for opt in diqu_options:
    #     diqu_value=opt.get('value')
    #     diqu_name=opt.get_text().strip('--')
    #     dict_={diqu_value:diqu_name}
    #     zonecode.update(**dict_)

    data=[]

    zonecode=OrderedDict(
        [('11*', '北京'), ('12*', '天津'), ('13*', '河北'), ('14*', '山西'), ('15*', '内蒙古'), ('21*', '辽宁'), ('22*', '吉林'),
         ('23*', '黑龙江'), ('31*', '上海'), ('32*', '江苏'), ('33*', '浙江'), ('34*', '安徽'), ('35*', '福建'), ('37*', '山东'),
         ('36*', '江西'), ('41*', '河南'), ('42*', '湖北'), ('43*', '湖南'), ('44*', '广东'), ('45*', '广西'), ('46*', '海南'),
         ('50*', '重庆'), ('51*', '四川'), ('52*', '贵州'), ('53*', '云南'), ('54*', '西藏'), ('61*', '陕西'), ('62*', '甘肃'),
         ('63*', '青海'), ('64*', '宁夏'), ('65*', '新疆')])
    hangye_dict=OrderedDict(
        [('01', '农产品'), ('02', '能源(石油/石化/煤炭/新能源)'), ('03', '食品饮料烟草'), ('04', '纺织服装皮革'), ('05', '包装'), ('06', '工艺礼品玩具'),
         ('07', '化工'), ('08', '医药'), ('09', '五金'), ('10', '电子'), ('11', '机械设备'), ('12', '交通运输'), ('13', '办公用品'),
         ('14', '仪器仪表'), ('15', 'IT、通讯及信息技术'), ('16', '工程建筑行业'), ('17', '安全防护'), ('18', '传媒、广电'), ('19', '家居行业'),
         ('20', '橡胶塑胶'), ('21', '印刷'), ('22', '冶金矿产'), ('23', '家用电器'), ('24', '电气'), ('25', '建筑建材'), ('26', '电力'),
         ('27', '运动、休闲'), ('28', '居民服务和其它服务业'), ('29', '商业贸易(综合类企业)'), ('30', '纸业'), ('31', '物流运输'), ('32', '通信及信息服务'),
         ('33', '批发零售、住宿餐饮'), ('34', '金融保险'), ('35', '房产物业'), ('36', '租赁和商务服务'), ('37', '科研技术和地质勘查护'),
         ('38', '水利、环境和公共设施管理'), ('39', '文化、教育、体育、娱乐服务'), ('40', '卫生、社会保障福利'), ('41', '国际、社会组织与公共管理'), ('42', '出版印刷'),
         ('43', '软件服务'), ('44', '咨询培训'), ('45', '维护清洗'), ('46', '会展服务'), ('47', '代理经营'), ('48', '网络通信'), ('49', '其他服务'),
         ('50', '环保设备')])

    ggtype1 = OrderedDict([("zhaobiao", "1"), ("biangeng", "2"), ("zhongbiaohx", "3"), ("zhongbiao", "4")])
    for w0 in ggtype1.keys():
        for w1 in hangye_dict.keys():
            for w2 in zonecode.keys():
                href = 'http://www.chinabidding.com/search/proj.htm'
                tmp = ["qy_{0}_hangye{1}_diqu{2}_gg".format(w0,w1,w2.strip('*')), href, ["name", "ggstart_time", "href", 'info'],
                       chang_type( chang_hangye( add_info(f1, {"hangye":hangye_dict[w1] }),w1,w2 ),ggtype1[w0] ),
                       chang_type( chang_hangye(f2,w1,w2),ggtype1[w0])]
                data.append(tmp)

    # remove_arr = [""]
    data1 = data.copy()
    # for w in data:
    #     if w[0] in remove_arr: data1.remove(w)

    return data1

data=get_data()



def work(conp, **args):

    est_meta(conp, data=data, diqu="中国国际工程咨询有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch3", "www_chinabidding_com"],headless=False,num=1,total=2)
    pass