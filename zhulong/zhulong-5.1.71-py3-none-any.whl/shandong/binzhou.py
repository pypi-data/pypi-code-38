import time
import pandas as pd
import re
from collections import OrderedDict
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
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="binzhou"



def f1(driver, num):
    try:
        cnum = int(driver.find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]/font').text)
    except:
        cnum = 1
    val = driver.find_element_by_xpath('//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a').get_attribute('href')[-35:]
    if num != cnum:
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','{}')".format(num))
        locator = (By.XPATH, "//*[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]/td[2]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("table", id="MoreInfoList1_DataGrid1")
    trs = tbody.find_all("tr")
    data = []
    for tr in trs:
        try:
            a = tr.find("a")
            td = tr.find_all("td")[2]
            tmp = [a["title"], td.text.strip(), "http://www.bzggzyjy.gov.cn" + a["href"]]
            data.append(tmp)
        except:
            a = tr.find_all("td")[1]
            td = tr.find_all("td")[2]
            tmp = [a.text.strip(), td.text.strip(), "-"]
            data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df




def f2(driver):
    try:
        locator = (By.ID, 'MoreInfoList1_Pager')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        txt=driver.find_element_by_xpath("//a[contains(string(),'尾页')]").get_attribute("title")
        total=re.findall("第([0-9]*)页",txt)[0]
        total=int(total)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH, "//div[contains(@id,'menutab')][@style=''][string-length()>30] | //div[contains(@id,'menutab')][not(@style)][string-length()>30] | //table[@id='tblInfo'][string-length()>30] | //td[@id='TDContent'][string-length()>30]")
    WebDriverWait(driver,30).until(EC.presence_of_all_elements_located(locator))
    before=len(driver.page_source)
    time.sleep(0.1)
    after=len(driver.page_source)
    i=0
    while before!=after:
        before=len(driver.page_source)
        time.sleep(0.1)
        after=len(driver.page_source)
        i+=1
        if i>5:break
    page=driver.page_source
    soup=BeautifulSoup(page,'html.parser')
    if "TDContent" in page:
        div = soup.find('table',id='tblInfo')
        if div == None:
            div=soup.find('td',id='TDContent')
    else:
        div=soup.find("div",id=re.compile('menutab.*'),style=False)
        if div == None:
            div = soup.find("div", id=re.compile('menutab.*'), style='')
    return div


def get_data():
    data = []
    # 工程建设部分
    xs = OrderedDict([("市本级", "001"), ("滨城区", "002"), ("沾化区", "003"), ("惠民县", "004"), ("阳信县", "005"), ("无棣县", "006"),
                      ("博兴县", "007"), ("邹平县", "008"), ("北海新区", "009"), ("开发区", "010"), ("高新区", "011")])
    # "http://www.bzggzyjy.gov.cn/bzweb/002/002004/002004001/"
    ggtype = OrderedDict([("zhaobiao", "001"), ("zhongbiaohx", "002"), ("biangeng", "003")])

    for w1 in ggtype.keys():
        for w2 in xs.keys():
            p1 = "002004%s" % (ggtype[w1])
            p2 = "002004%s%s" % (ggtype[w1], xs[w2])
            href = "http://www.bzggzyjy.gov.cn/bzweb/002/002004/%s/%s/MoreInfo.aspx?CategoryNum=%s" % (p1, p2, p2)

            tb = "gcjs_%s_diqu%s_gg" % (w1, xs[w2])
            col = ["name", "ggstart_time", "href", "info"]
            tmp = [tb, href, col, add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)

    # 政府采购部分
    # 招标
    zbfs = OrderedDict(
        [("公开招标", "001"), ("网上竞价", "002"), ("竞争性谈判", "003"), ("询价", "004"), ("邀请招标", "005"), ("定点采购", "007"),
         ("竞争性磋商", "008")])

    for w1 in zbfs.keys():

        for w2 in xs.keys():
            p1 = "002005001%s" % (zbfs[w1])
            p2 = "002005001%s%s" % (zbfs[w1], xs[w2])
            href = "http://www.bzggzyjy.gov.cn/bzweb/002/002005/002005001/%s/%s/MoreInfo.aspx?CategoryNum=%s" % (
            p1, p2, p2)

            tmp = ['zfcg_zhaobiao_diqu%s_zbfs%s_gg' % (xs[w2], zbfs[w1]), href,
                   ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": w2, "zbfs": w1}), f2]
            data.append(tmp)

    # 变更和yucai 中标 yanshou feibiao
    ggtype2 = OrderedDict(
        [("biangeng", "002"), ("yucai", "004"), ("zhongbiao", "003"), ("yanshou", "006"), ("liubiao", "007"),
         ("hetong", "005")])

    for w1 in ggtype2.keys():

        for w2 in xs.keys():
            p1 = "002005%s" % (ggtype2[w1])
            p2 = "002005%s%s" % (ggtype2[w1], xs[w2])
            href = "http://www.bzggzyjy.gov.cn/bzweb/002/002005/%s/%s/MoreInfo.aspx?CategoryNum=%s" % (p1, p2, p2)
            tmp = ['zfcg_%s_diqu%s_gg' % (w1, xs[w2]), href, ["name", "ggstart_time", "href", "info"],
                   add_info(f1, {"diqu": w2}), f2]

            data.append(tmp)
    data1 = data.copy()
    remove_arr = ["zfcg_zhaobiao_diqu004_zbfs002_gg", "zfcg_zhaobiao_diqu007_zbfs002_gg",
                  "zfcg_zhaobiao_diqu007_zbfs004_gg", "zfcg_zhaobiao_diqu009_zbfs005_gg",
                  "zfcg_zhaobiao_diqu008_zbfs005_gg", "zfcg_zhaobiao_diqu009_zbfs005_gg",
                  "zfcg_zhaobiao_diqu011_zbfs005_gg", "zfcg_zhaobiao_diqu003_zbfs007_gg",
                  "zfcg_zhaobiao_diqu003_zbfs007_gg", "zfcg_zhaobiao_diqu006_zbfs007_gg",
                  "zfcg_zhaobiao_diqu009_zbfs007_gg", "zfcg_zhaobiao_diqu009_zbfs005_gg",
                  "zfcg_zhaobiao_diqu009_zbfs005_gg"]
    for w in data:
        if w[0] in remove_arr: data1.remove(w)
    return data1
    # 创建data

data = get_data()

def work(conp, **args):
    est_meta(conp, data=data, diqu="山东省滨州市", **args)
    est_html(conp, f=f3, **args)

# 修改日期：2019/6/28
if __name__=='__main__':
    work(conp=["postgres","zhulong.com.cn","192.168.169.47","shandong","binzhou"], pageloadtimeout=180,num=1, headless= False)

    #
    # driver = webdriver.Chrome()
    # d = f3(driver, 'http://www.bzggzyjy.gov.cn/bzweb/ZtbInfo/ZtbDyDetail.aspx?type=3&InfoID=003b08dc-3305-4762-bb4b-5fab2b53567a&CategoryNum=002005002007')
    # print(d)