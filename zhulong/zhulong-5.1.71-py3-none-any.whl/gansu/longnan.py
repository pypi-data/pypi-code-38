import pandas as pd  
import re 
from selenium import webdriver 
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
import sys 
import time
from zhulong.util.etl import gg_meta,gg_html,est_meta,est_html

from zhulong.util.etl import add_info


_name_='longnan'

# driver=webdriver.Chrome()
# url='http://www.lnsggzyjy.cn/jyxx/002001/002001008/about.html'
# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//ul[@class='ewb-info-items']/li[1]//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    url=driver.current_url

    if 'about' in url:
        cnum =1
    else:
        cnum=int(re.findall("/(\d+).html",url)[0])

    if num!=cnum:
        page_count = len(driver.page_source)
        if num == 1:
            url=re.sub("/\d+.html",'about.html',url)
        else:
            url=re.sub("/\d+.html","/%s.html"%num,url)

        val=driver.find_element_by_xpath("//ul[@class='ewb-info-items']/li[1]//a").get_attribute('href')[-30:-5]
        driver.get(url)

        locator=(By.XPATH,"//ul[@class='ewb-info-items']/li[1]//a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver, 10).until(lambda driver: len(driver.page_source) != page_count)
    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    ul=soup.find("ul",class_="ewb-info-items")
    lis=ul.find_all("li")

    data=[]

    for li in lis:
        a=li.find("a")
        name=a['title']
        href=a['href']
        ggstart_time=li.find("span",class_='ewb-date').get_text()
        if 'http' in href:
            href=href
        else:
            href='http://www.lnsggzyjy.cn'+href
        tmp=[name,ggstart_time,href]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 

def f2(driver):

    locator=(By.XPATH,"//ul[@class='ewb-info-items']/li[1]//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    try:

        locator = (By.XPATH, '//ul[@class="ewb-page-items clearfix"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        total=int(driver.find_element_by_xpath("//li[@class='ewb-page-li ewb-page-noborder ewb-page-num']").text.split('/')[1])
    except:
        total=1
    driver.quit()

    return total


def f3(driver,url):

    driver.get(url)

    locator=(By.XPATH,'//div[@class="ewb-info"]/div[contains(@class,"clearfix")][not(contains(@class,"hidden"))][string-length()>50] | '
                      '//div[@class="ewb-article"][string-length()>100]')

    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    ctext = driver.find_element_by_xpath('//span[@id="viewGuid"]').text


    if '建设工程中标结果公告' == ctext:
        driver.find_element_by_xpath('//div[@data-target="h"]/span').click()
        time.sleep(0.5)
        ele=driver.find_element_by_xpath('//div[@data-target="h"]/span')
        driver.execute_script("arguments[0].click()", ele)
        time.sleep(0.5)
        try:
            locator=(By.XPATH,'//div[@id="h"][string-length()>50]')
            WebDriverWait(driver,2).until(EC.presence_of_element_located(locator))
        except:
            driver.find_element_by_xpath('//div[@data-target="h"]/span').click()
            locator = (By.XPATH, '//div[@id="h"][string-length()>50]')
            WebDriverWait(driver, 2).until(EC.presence_of_element_located(locator))

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

    div=soup.find('div',class_='ewb-article')
    if not div:
        div = soup.find('div', class_=["ewb-tabbd tab-view clearfix", "ewb-tabbd clearfix"], attrs={'data-num': '0'})



    return div



data=[

#工程建设

    ["gcjs_zhaobiao_gg","http://www.lnsggzyjy.cn/jyxx/002001/002001001/about.html",["name","ggstart_time","href","info"],f1,f2]

    ,["gcjs_biangeng_gg","http://www.lnsggzyjy.cn/jyxx/002001/002001002/about.html",["name","ggstart_time","href","info"],f1,f2]


    ,["gcjs_zhongbiao_gg","http://www.lnsggzyjy.cn/jyxx/002001/002001003/about.html",["name","ggstart_time","href","info"],f1,f2]

    ,["gcjs_gqita_zbbiangeng_gg","http://www.lnsggzyjy.cn/jyxx/002001/002001004/about.html",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"中标结果公示变更"}),f2]

    ,["gcjs_liubiao_gg","http://www.lnsggzyjy.cn/jyxx/002001/002001005/about.html",["name","ggstart_time","href","info"],f1,f2]

    ,["gcjs_zgys_gg","http://www.lnsggzyjy.cn/jyxx/002001/002001006/about.html",["name","ggstart_time","href","info"],f1,f2]

    ,["gcjs_zhongbiao_jianshe_gg","http://www.lnsggzyjy.cn/jyxx/002001/002001007/about.html",["name","ggstart_time","href","info"],f1,f2]

    ,["gcjs_kongzhijia_gg","http://www.lnsggzyjy.cn/jyxx/002001/002001008/about.html",["name","ggstart_time","href","info"],f1,f2]

    #政府采购

    ,["zfcg_yucai_gg","http://www.lnsggzyjy.cn/jyxx/002002/002002006/about.html",["name","ggstart_time","href","info"],f1,f2]

    ,["zfcg_biangeng_gg","http://www.lnsggzyjy.cn/jyxx/002002/002002002/about.html",["name","ggstart_time","href","info"],f1,f2]


    ,["zfcg_zhongbiao_gg","http://www.lnsggzyjy.cn/jyxx/002002/002002003/about.html",["name","ggstart_time","href","info"],f1,f2]

    ,["zfcg_gqita_zbbiangeng_gg","http://www.lnsggzyjy.cn/jyxx/002002/002002004/about.html",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"中标结果公示变更"}),f2]

    ,["zfcg_liubiao_gg","http://www.lnsggzyjy.cn/jyxx/002002/002002005/about.html",["name","ggstart_time","href","info"],f1,f2]

    ,["zfcg_zhaobiao_gg","http://www.lnsggzyjy.cn/jyxx/002002/002002001/about.html",["name","ggstart_time","href","info"],f1,f2]

    #精准扶贫

    ,["gcjs_zhaobiao_fupin_gg","http://www.lnsggzyjy.cn/jyxx/002005/aboutfp.html",["name","ggstart_time","href","info"],add_info(f1,{"xmlx":"精准扶贫"}),f2]


]



def work(conp,**args):
    est_meta(conp,data=data,diqu="甘肃省陇南市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015",'192.168.3.172',"gansu","longnan"])

    # driver=webdriver.Chrome()
    # url='http://www.lnsggzyjy.cn/jyxx/002001/002001007/20190528/8ba582f2-6e86-46bd-bee5-adce9e2612f6.html'
    # q=f3(driver,url)
    # print(q)
    # driver.get('http://www.lnsggzyjy.cn/jyxx/002001/002001001/about.html')
    # f1(driver,1)