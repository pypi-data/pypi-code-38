import time
from collections import OrderedDict
from pprint import pprint

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zhulong.util.etl import est_html, est_meta, add_info

_name_="liaocheng"



def f1(driver, num):
    """
    进行翻页，并获取数据
    :param driver: 已经访问了url
    :param num: 返回的是从第一页一直到最后一页
    :return:
    """
    locator = (By.XPATH, '//table[@cellspacing="3"]/tbody/tr[1]/td/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    if "Paging=" not in url:
        cnum = 1
    else:
        cnum = int(re.findall("Paging=(\d+)", url)[0])
    if num != cnum:
        if "Paging=" not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url = url + s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        val = driver.find_element_by_xpath("//table[@cellspacing='3']/tbody/tr[1]/td/a").get_attribute('href')[-45:]
        driver.get(url)
        locator = (By.XPATH, "//table[@cellspacing='3']/tbody/tr[1]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    html_data = driver.page_source
    soup = BeautifulSoup(html_data, 'html.parser')
    ul = soup.find("div", class_="content")
    tb = ul.find_all("div", recursive=False)[0]
    lis = tb.find_all("tr")
    data = []
    for li in lis:
        a = li.find("a").extract()
        title = a["title"]
        link = "http://www.lcsggzyjy.cn" + a["href"]
        span = li.find_all("font")[-1]
        tmp = [title, span.text.strip(), link]
        data.append(tmp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    """
    返回总页数
    :param driver:
    :return:
    """
    url = driver.current_url
    if ('本栏目暂时没有内容' in driver.page_source) or ('404' in driver.title):
        return 0
    locator = (By.XPATH, '//table[@cellspacing="3"]/tbody/tr[1]/td/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, '//td[@class="huifont"]')
        page_num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        # 获取总页数
        num = re.findall(r'/(\d+)', page_num)[0]
    except:
        num = 1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    time.sleep(2)
    driver.switch_to.default_content()
    locator = (By.XPATH, "//div[@class='detail-content'][string-length()>10] | //div[contains(@id,'menutab')][@style=''][string-length()>15] | //div[contains(@id,'menutab')][not(@style)][string-length()>15]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
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
    div = soup.find('div', class_="detail-content")
    if div == None:
        div=soup.find("div",id=re.compile("menutab.*"), style='')
    return div



def get_data():
    # 工程建设、医疗采购、其他项目
    xs11=OrderedDict([("市直","001"),("东昌府区","002"),("经济开发区","003"),("高新区","004"),("旅游度假区","005")
        ,("临清市","006"),("冠县","007"),("莘县","008"),("阳谷县","009")
        ,("东阿县", "010"), ("茌平县", "011"), ("高唐县", "012")])
    xs1=OrderedDict([("市直","001"),("东昌府区","002"),("经济开发区","003"),("高新区","004"),("旅游度假区","005")
        ,("嘉明开发区","006"),("其他县市","007"),("临清市","008"),("冠县","009"),("莘县","010"),("阳谷县","011")
        ,("东阿县", "012"), ("茌平县", "013"), ("高唐县", "014")])
    lx11 = OrderedDict([("qita", "005")])
    lx=OrderedDict([("sheji","001"),("shigong","002"),("jianli","003"),("huowu","004")])
    # 工程建设
    ggtype1=OrderedDict([("zhaobiao","001"),("biangeng","002"),("zhongbiao","003"),("liubiao","005")])
    data=[]
    # 工程建设
    for w1 in ggtype1.keys():
        for w2 in lx11.keys():
            for w3 in xs11.keys():
                p1 = "079001%s" % (ggtype1[w1])
                p2 = "079001%s%s" % (ggtype1[w1], lx11[w2])
                p3 = "079001%s%s%s" % (ggtype1[w1], lx11[w2], xs11[w3])
                href = "http://www.lcsggzyjy.cn/lcweb/jyxx/079001/%s/%s/%s/" % (p1, p2, p3)
                gclx_dict = {"sheji": "设计", "shigong": "施工", "jianli": "监理", "huowu": "货物", "qita": "其他"}
                if w2 in gclx_dict.keys():
                    gclx = gclx_dict[w2]
                else:
                    gclx = None
                tmp = ["gcjs_%s_%s_diqu%s_gg" % (w1, w2, xs11[w3]), href, ["name", "ggstart_time", "href", "info"],add_info(f1,{"diqu":w3,"gclx":gclx}),f2]
                data.append(tmp)

    for w1 in ggtype1.keys():
        for w2 in lx.keys():
            for w3 in xs1.keys():
                p1="079001%s"%(ggtype1[w1])
                p2="079001%s%s"%(ggtype1[w1],lx[w2])
                p3 = "079001%s%s%s" % (ggtype1[w1], lx[w2], xs1[w3])
                href="http://www.lcsggzyjy.cn/lcweb/jyxx/079001/%s/%s/%s/"%(p1,p2,p3)
                gclx_dict = {"sheji":"设计","shigong":"施工","jianli":"监理","huowu":"货物","qita":"其他"}
                if w2 in gclx_dict.keys():
                    gclx = gclx_dict[w2]
                else:gclx=None
                tmp=["gcjs_%s_%s_diqu%s_gg"%(w1,w2,xs1[w3]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w3,"gclx":gclx}),f2]
                data.append(tmp)


    # 政府采购
    xs2=OrderedDict([("市直","007"),("东昌府区","008"),("经济开发区","009"),("高新区","010"),("旅游度假区","011")
        ,("嘉明开发区","012"),("其他县市","013"),("临清市","014"),("冠县","015"),("莘县","016"),("阳谷县","017")
        ,("东阿县", "018"), ("茌平县", "019"), ("高唐县", "020")])
    xs22=OrderedDict([("市直","006"),("东昌府区","007"),("经济开发区","008"),("高新区","009"),("旅游度假区","010")
        ,("嘉明开发区","011"),("其他县市","012"),("临清市","013"),("冠县","014"),("莘县","015"),("阳谷县","016")
        ,("东阿县", "017"), ("茌平县", "018"), ("高唐县", "019")])
    # 政府采购、医疗采购、其他项目
    ggtype2=OrderedDict([("zhaobiao","001"),("biangeng","002"),("zhongbiao","003"),("liubiao","004")])
    # 政府采购
    ggtype22=OrderedDict([("biangeng","002"),("liubiao","004")])
    for w1 in ggtype2.keys():
        for w2 in xs2.keys():
            # if (w1=="zhaobiao") and (xs2[w2] in ["015","016"]):
            #     continue
            # elif (w1=="zhongbiao") and (xs2[w2] in ["014"]):
            #     continue
            p1="079002%s"%(ggtype2[w1])
            p2="079002%s%s"%(ggtype2[w1],xs2[w2])
            href="http://www.lcsggzyjy.cn/lcweb/jyxx/079002/%s/%s/"%(p1,p2)
            tmp=["zfcg_%s_diqu%s_gg"%(w1,xs2[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)

    for w1 in ggtype22.keys():
        for w2 in xs22.keys():
            # if (w1=="biangeng") and (xs2[w2] in ["013","015","016","020"]):
            #     continue
            # elif (w1=="liubiao") and (xs2[w2] in ["013","014","015","016","020"]):
            #     continue
            p1="079002%s"%(ggtype22[w1])
            p2="079002%s%s"%(ggtype22[w1],xs22[w2])
            href="http://www.lcsggzyjy.cn/lcweb/jyxx/079002/%s/%s/"%(p1,p2)
            tmp=["zfcg_%s_diqu%s_gg"%(w1,xs22[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)

    # 医用采购
    for w1 in ggtype2.keys():
        for w2 in xs1.keys():
            # if (w1=="zhaobiao") and (xs1[w2] in ["006","008","010","009","011"]):
            #     continue
            # elif (w1=="biangeng") and (xs1[w2] in ["003","004","005","006","007","008","010","011","014"]):
            #     continue
            # elif (w1=="zhongbiao") and (xs1[w2] in ["006","008","009","010","011"]):
            #     continue
            # elif (w1=="liubiao") and (xs1[w2] in ["004","005","006","008","010","011","012"]):
            #     continue
            p1="079005%s"%(ggtype2[w1])
            p2="079005%s%s"%(ggtype2[w1],xs1[w2])
            href="http://www.lcsggzyjy.cn/lcweb/jyxx/079005/%s/%s/"%(p1,p2)
            tmp=["yiliao_%s_diqu%s_gg"%(w1,xs1[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)


    for w1 in ggtype2.keys():
        for w2 in xs1.keys():
            # if (w1=="zhaobiao") and (xs1[w2] in ["006","008","010","011"]):
            #     continue
            # elif (w1=="biangeng") and (xs1[w2] in ["006","008","009","010","011"]):
            #     continue
            # elif (w1=="zhongbiao") and (xs1[w2] in ["006","008","009","010","011"]):
            #     continue
            # elif (w1=="liubiao") and (xs1[w2] in ["006","008","009","010","011","013"]):
            #     continue
            p1="079006%s"%(ggtype2[w1])
            p2="079006%s%s"%(ggtype2[w1],xs1[w2])
            href="http://www.lcsggzyjy.cn/lcweb/jyxx/079006/%s/%s/"%(p1,p2)
            tmp=["qsy_%s_diqu%s_gg"%(w1,xs1[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)


    for w2 in xs1.keys():
        # if (xs1[w2] in ["010"]):
        #     continue
        p1="079002006001%s"%(xs1[w2])
        href="http://www.lcsggzyjy.cn/lcweb/jyxx/079002/079002006/079002006001/%s/"%(p1)
        tmp=["zfcg_yucai_diqu%s_gg"%(xs1[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2,"jylx":"信息公开"}),f2]
        data.append(tmp)

    for w2 in xs1.keys():
        # if (xs1[w2] in ["004","007","010","011","012","013","014"]):
        #     continue
        p1="079002006003%s"%(xs1[w2])
        href="http://www.lcsggzyjy.cn/lcweb/jyxx/079002/079002006/079002006003/%s/"%(p1)
        tmp=["zfcg_yanshou_diqu%s_gg"%(xs1[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2,"jylx":"信息公开"}),f2]
        data.append(tmp)


    # 医用采购
    xs3=OrderedDict([("市直","001"),("东昌府区","002"),("经济开发区","003"),("高新区","004"),("旅游度假区","005")
        ,("嘉明开发区","006"),("其他县市","007"),("东阿县","008"),("高唐县","009"),("茌平县","010"),("阳谷县","011")
        ,("冠县", "012"), ("莘县", "013"), ("临清市", "014")])
    for w2 in xs3.keys():
        # if (xs3[w2] in ["003","005","006","007","008","011","013","014"]):
        #     continue
        p1="079005005015%s"%(xs3[w2])
        href="http://www.lcsggzyjy.cn/lcweb/jyxx/079005/079005005/079005005015/%s/"%(p1)
        tmp=["yiliao_yucai_diqu%s_gg"%(xs3[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2,"jylx":"信息公开"}),f2]
        data.append(tmp)

    # 信息公开
    xs12=OrderedDict([("市直","001"),("东昌府区","002"),("经济开发区","003"),("高新区","004"),("旅游度假区","005")
        ,("嘉明开发区","006"),("其他县市","007"),("东阿县","008"),("高唐县","009"),("茌平县","010"),("阳谷县","011")
        ,("冠县", "012"), ("莘县", "013"), ("临清市", "014")])

    for w2 in xs12.keys():
        # if (xs1[w2] not in ["001","002","003","005"]):
        #     continue
        p1="079006005018%s"%(xs12[w2])
        href="http://www.lcsggzyjy.cn/lcweb/jyxx/079006/079006005/079006005018/%s/"%(p1)
        tmp=["qsy_gqita_danyilaiyuan_diqu%s_gg"%(xs12[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2,"zbfs":"单一来源","jylx":"信息公开"}),f2]
        data.append(tmp)

    for w2 in xs12.keys():
        # if (xs12[w2] in ["011","012","013","014"]):
        #     continue
        p1="079006005015%s"%(xs12[w2])
        href="http://www.lcsggzyjy.cn/lcweb/jyxx/079006/079006005/079006005015/%s/"%(p1)
        tmp=["qsy_yucai_diqu%s_gg"%(xs12[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2,"jylx":"信息公开"}),f2]
        data.append(tmp)


    data1=data.copy()
    # arr=['zfcg_zhaobiao_diqu014_gg','zfcg_zhaobiao_diqu016_gg','zfcg_biangeng_diqu013_gg','zfcg_biangeng_diqu015_gg','zfcg_biangeng_diqu016_gg',
    #      'zfcg_zhongbiao_diqu014_gg','zfcg_liubiao_diqu013_gg','zfcg_liubiao_diqu014_gg','zfcg_liubiao_diqu015_gg','zfcg_liubiao_diqu016_gg',
    #      'gcjs_zhaobiao_sheji_diqu004_gg','gcjs_zhaobiao_sheji_diqu006_gg','gcjs_zhaobiao_sheji_diqu008_gg','gcjs_zhaobiao_sheji_diqu009_gg',
    #      'gcjs_zhaobiao_sheji_diqu010_gg','gcjs_zhaobiao_sheji_diqu011_gg','gcjs_zhaobiao_sheji_diqu012_gg','gcjs_zhaobiao_sheji_diqu013_gg',
    #      'gcjs_zhaobiao_shigong_diqu006_gg','gcjs_zhaobiao_shigong_diqu008_gg','gcjs_zhaobiao_shigong_diqu009_gg','gcjs_zhaobiao_shigong_diqu010_gg',
    #      'gcjs_zhaobiao_shigong_diqu011_gg','gcjs_zhaobiao_shigong_diqu012_gg','gcjs_zhaobiao_shigong_diqu013_gg','gcjs_zhaobiao_jianli_diqu006_gg',
    #      'gcjs_zhaobiao_jianli_diqu008_gg','gcjs_zhaobiao_jianli_diqu009_gg','gcjs_zhaobiao_jianli_diqu010_gg',
    #      'gcjs_zhaobiao_jianli_diqu011_gg','gcjs_zhaobiao_jianli_diqu012_gg','gcjs_zhaobiao_jianli_diqu013_gg',
    #      'gcjs_zhaobiao_huowu_diqu006_gg','gcjs_zhaobiao_huowu_diqu008_gg','gcjs_zhaobiao_huowu_diqu009_gg',
    #      'gcjs_zhaobiao_huowu_diqu010_gg','gcjs_zhaobiao_huowu_diqu011_gg','gcjs_zhaobiao_huowu_diqu012_gg',
    #      'gcjs_zhaobiao_huowu_diqu013_gg','gcjs_zhaobiao_huowu_diqu014_gg','gcjs_zhaobiao_qita_diqu004_gg',
    #      'gcjs_zhaobiao_qita_diqu006_gg','gcjs_zhaobiao_qita_diqu007_gg','gcjs_zhaobiao_qita_diqu008_gg','gcjs_zhaobiao_qita_diqu009_gg',
    #      'gcjs_zhaobiao_qita_diqu010_gg','gcjs_zhaobiao_qita_diqu011_gg','gcjs_zhaobiao_qita_diqu013_gg','gcjs_zhaobiao_qita_diqu014_gg',
    #      'gcjs_biangeng_sheji_diqu001_gg','gcjs_biangeng_sheji_diqu004_gg','gcjs_biangeng_sheji_diqu006_gg','gcjs_biangeng_sheji_diqu007_gg',
    #      'gcjs_biangeng_sheji_diqu008_gg','gcjs_biangeng_sheji_diqu009_gg','gcjs_biangeng_sheji_diqu010_gg','gcjs_biangeng_sheji_diqu011_gg',
    #      'gcjs_biangeng_sheji_diqu012_gg','gcjs_biangeng_sheji_diqu013_gg','gcjs_biangeng_sheji_diqu014_gg','gcjs_biangeng_shigong_diqu006_gg',
    #      'gcjs_biangeng_shigong_diqu008_gg','gcjs_biangeng_shigong_diqu009_gg','gcjs_biangeng_shigong_diqu010_gg','gcjs_biangeng_shigong_diqu011_gg',
    #      'gcjs_biangeng_shigong_diqu012_gg','gcjs_biangeng_shigong_diqu013_gg','gcjs_biangeng_jianli_diqu001_gg','gcjs_biangeng_jianli_diqu004_gg',
    #      'gcjs_biangeng_jianli_diqu006_gg','gcjs_biangeng_jianli_diqu007_gg','gcjs_biangeng_jianli_diqu008_gg','gcjs_biangeng_jianli_diqu009_gg',
    #      'gcjs_biangeng_jianli_diqu010_gg','gcjs_biangeng_jianli_diqu011_gg','gcjs_biangeng_jianli_diqu012_gg','gcjs_biangeng_jianli_diqu013_gg',
    #      'gcjs_biangeng_huowu_diqu002_gg','gcjs_biangeng_huowu_diqu003_gg','gcjs_biangeng_huowu_diqu004_gg',
    #      'gcjs_biangeng_huowu_diqu006_gg','gcjs_biangeng_huowu_diqu007_gg','gcjs_biangeng_huowu_diqu008_gg','gcjs_biangeng_huowu_diqu009_gg',
    #      'gcjs_biangeng_huowu_diqu010_gg','gcjs_biangeng_huowu_diqu011_gg','gcjs_biangeng_huowu_diqu012_gg','gcjs_biangeng_huowu_diqu013_gg',
    #      'gcjs_biangeng_huowu_diqu014_gg','gcjs_biangeng_qita_diqu001_gg','gcjs_biangeng_qita_diqu003_gg','gcjs_biangeng_qita_diqu004_gg',
    #      'gcjs_biangeng_qita_diqu005_gg','gcjs_biangeng_qita_diqu006_gg','gcjs_biangeng_qita_diqu007_gg','gcjs_biangeng_qita_diqu008_gg',
    #      'gcjs_biangeng_qita_diqu009_gg','gcjs_biangeng_qita_diqu010_gg','gcjs_biangeng_qita_diqu011_gg','gcjs_biangeng_qita_diqu012_gg',
    #      'gcjs_biangeng_qita_diqu013_gg','gcjs_biangeng_qita_diqu014_gg','gcjs_zhongbiao_sheji_diqu004_gg','gcjs_zhongbiao_sheji_diqu006_gg',
    #      'gcjs_zhongbiao_sheji_diqu007_gg','gcjs_zhongbiao_sheji_diqu008_gg','gcjs_zhongbiao_sheji_diqu009_gg','gcjs_zhongbiao_sheji_diqu010_gg',
    #      'gcjs_zhongbiao_sheji_diqu011_gg','gcjs_zhongbiao_sheji_diqu012_gg','gcjs_zhongbiao_sheji_diqu013_gg','gcjs_zhongbiao_shigong_diqu006_gg',
    #      'gcjs_zhongbiao_shigong_diqu007_gg','gcjs_zhongbiao_shigong_diqu008_gg','gcjs_zhongbiao_shigong_diqu009_gg','gcjs_zhongbiao_shigong_diqu010_gg',
    #      'gcjs_zhongbiao_shigong_diqu011_gg','gcjs_zhongbiao_shigong_diqu012_gg','gcjs_zhongbiao_shigong_diqu013_gg',
    #      'gcjs_zhongbiao_jianli_diqu006_gg','gcjs_zhongbiao_jianli_diqu007_gg','gcjs_zhongbiao_jianli_diqu008_gg',
    #      'gcjs_zhongbiao_jianli_diqu009_gg','gcjs_zhongbiao_jianli_diqu010_gg','gcjs_zhongbiao_jianli_diqu011_gg',
    #      'gcjs_zhongbiao_jianli_diqu012_gg','gcjs_zhongbiao_jianli_diqu013_gg','gcjs_zhongbiao_huowu_diqu004_gg',
    #      'gcjs_zhongbiao_huowu_diqu006_gg','gcjs_zhongbiao_huowu_diqu007_gg','gcjs_zhongbiao_huowu_diqu008_gg',
    #      'gcjs_zhongbiao_huowu_diqu009_gg','gcjs_zhongbiao_huowu_diqu010_gg','gcjs_zhongbiao_huowu_diqu011_gg',
    #      'gcjs_zhongbiao_huowu_diqu012_gg','gcjs_zhongbiao_huowu_diqu013_gg','gcjs_zhongbiao_qita_diqu004_gg',
    #      'gcjs_zhongbiao_qita_diqu006_gg','gcjs_zhongbiao_qita_diqu007_gg','gcjs_zhongbiao_qita_diqu008_gg',
    #      'gcjs_zhongbiao_qita_diqu009_gg','gcjs_zhongbiao_qita_diqu010_gg','gcjs_zhongbiao_qita_diqu011_gg',
    #      'gcjs_zhongbiao_qita_diqu012_gg','gcjs_zhongbiao_qita_diqu013_gg','gcjs_zhongbiao_qita_diqu014_gg',
    #      'gcjs_liubiao_sheji_diqu002_gg','gcjs_liubiao_sheji_diqu004_gg','gcjs_liubiao_sheji_diqu006_gg',
    #      'gcjs_liubiao_sheji_diqu007_gg','gcjs_liubiao_sheji_diqu008_gg','gcjs_liubiao_sheji_diqu009_gg',
    #      'gcjs_liubiao_sheji_diqu010_gg','gcjs_liubiao_sheji_diqu011_gg','gcjs_liubiao_sheji_diqu012_gg',
    #      'gcjs_liubiao_sheji_diqu013_gg','gcjs_liubiao_sheji_diqu014_gg','gcjs_liubiao_shigong_diqu006_gg',
    #      'gcjs_liubiao_shigong_diqu008_gg','gcjs_liubiao_shigong_diqu009_gg','gcjs_liubiao_shigong_diqu010_gg',
    #      'gcjs_liubiao_shigong_diqu011_gg','gcjs_liubiao_shigong_diqu012_gg','gcjs_liubiao_shigong_diqu013_gg',
    #      'gcjs_liubiao_shigong_diqu014_gg','gcjs_liubiao_jianli_diqu006_gg','gcjs_liubiao_jianli_diqu008_gg',
    #      'gcjs_liubiao_jianli_diqu009_gg','gcjs_liubiao_jianli_diqu010_gg','gcjs_liubiao_jianli_diqu011_gg',
    #      'gcjs_liubiao_jianli_diqu012_gg','gcjs_liubiao_jianli_diqu013_gg','gcjs_liubiao_jianli_diqu014_gg',
    #      'gcjs_liubiao_huowu_diqu002_gg','gcjs_liubiao_huowu_diqu003_gg','gcjs_liubiao_huowu_diqu004_gg',
    #      'gcjs_liubiao_huowu_diqu005_gg','gcjs_liubiao_huowu_diqu006_gg','gcjs_liubiao_huowu_diqu007_gg',
    #      'gcjs_liubiao_huowu_diqu008_gg','gcjs_liubiao_huowu_diqu009_gg','gcjs_liubiao_huowu_diqu010_gg',
    #      'gcjs_liubiao_huowu_diqu011_gg','gcjs_liubiao_huowu_diqu012_gg','gcjs_liubiao_huowu_diqu013_gg',
    #      'gcjs_liubiao_huowu_diqu014_gg','gcjs_liubiao_qita_diqu001_gg',]
    # for w in data:
        # if w[0] in arr:data1.remove(w)

    tmp = [["zfcg_gqita_danyilaiyuan_gg" ,"http://www.lcsggzyjy.cn/lcweb/jyxx/079002/079002006/079002006006/",
           ["name", "ggstart_time", "href", "info"],  add_info(f1,{"zbfs":"单一来源","jylx":"信息公开"}), f2],

           ["yiliao_yanshou_diqu009_gg", "http://www.lcsggzyjy.cn/lcweb/jyxx/079005/079005005/079005005017/079005005017009/",
            ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "茌平县"}), f2]
           ]
    data1.extend(tmp)
    return data1

data=get_data()



def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省聊城市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","liaocheng"])





