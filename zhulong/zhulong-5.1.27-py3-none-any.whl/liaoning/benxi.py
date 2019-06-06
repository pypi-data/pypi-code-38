import random
import re

from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_html,est_meta
import time

_name_='benxi'
def f1(driver, num):
    locator = (By.ID, "demo1")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    cnum = driver.find_element_by_xpath('//div[@id="demo1"]/span[@class="current"]').text
    val = driver.find_element_by_xpath('//*[@id="contList"]/ul/li[1]/a').get_attribute("href")[-20:]
    time.sleep(random.randint(30,60))
    while int(cnum) != int(num):
        mdid = driver.execute_script('return mdid.value')
        driver.execute_script("""      
            var pageNum = 20;
            var myPagination = $("#demo1").myPagination({
                currPage: %s,
            ajax: {
                on: true,
                url: "FPACT_Action!findDataByPage.action",
                dataType: 'json',
                param:'mdid='+"%s" + '&pageNum='+pageNum,
                callback:function(data){
                    var result = data.pageContentList;
                    if(result!=null&&result.length>0){
                        var insetViewData = "";
                        insetViewData="<ul>";
                        var columnLength = result.length;
                        var outMenu = "";
                        var intx=$("#intx").val();
                        var inty=$("#inty").val();
                        var intz=$("#intz").val();
                        for(var i = 0; i<columnLength; i=i+1){
                            insetViewData +=dowithInfo(result[i],intx,inty,intz);
            }
                insetViewData+="</ul>";
            $("#contList").html(insetViewData);
                }else{
            $("#demo1").hide();
            }
            }
            }
	  });"""%(num,mdid))

        locator = (By.XPATH, "//*[@id='contList']/ul/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//*[@id="contList"]/ul/li')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//*[@id="contList"]/ul/li')
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://www.bxggzyjy.com/"+content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df



def f2(driver):
    locator = (By.XPATH, '//*[@id="demo1"]/a')
    WebDriverWait(driver, 40).until(EC.visibility_of_element_located(locator))
    total_page=driver.find_element_by_xpath('//*[@id="demo1"]/a[contains(string(),"尾页")]').get_attribute('title')
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "mContent")
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
    div = soup.find('div', class_='mContent')
    return div




data = [



    ["zfcg_liubiao_jy_gg",
     "http://www.bxggzyjy.com/frontpage/second.jsp?intx=4&inty=0&intz=4&pageNum=20&mdid=120022,1200222,1200223,1200224,1200225,1200226,1200227,1200228,120222,1202222,1202223,1202224,1202225,1202226,1202227,1202228,120225,1202252,1202253,1202254,1202255,1202256,1202257,1202258,120228,1202282,1202283,1202284,1202285,1202286,1202287,1202288,120302,1203022,1203023,1203024,1203025,1203026,1203027,1203028",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["zfcg_zhaobiao_gg",
     "http://www.bxggzyjy.com/frontpage/second.jsp?intx=4&inty=1&intz=2&pageNum=20&mdid=120019,1200192,1200193,1200194,1200195,1200196,1200197,1200198",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_jy_gg",
     "http://www.bxggzyjy.com/frontpage/second.jsp?intx=4&inty=0&intz=3&pageNum=20&mdid=120020,1200202,1200203,1200204,1200205,1200206,1200207,1200208,120220,1202202,1202203,1202204,1202205,1202206,1202207,1202208,120224,1202242,1202243,1202244,1202245,1202246,1202247,1202248,120227,1202272,1202273,1202274,1202275,1202276,1202277,1202278,120301,1203012,1203013,1203014,1203015,1203016,1203017,1203018",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_jy_gg",
     "http://www.bxggzyjy.com/frontpage/second.jsp?intx=4&inty=1&intz=2&pageNum=20&mdid=120019,1200192,1200193,1200194,1200195,1200196,1200197,1200198",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.bxggzyjy.com/frontpage/second.jsp?intx=4&inty=1&intz=3&pageNum=20&mdid=120020,1200202,1200203,1200204,1200205,1200206,1200207,1200208",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg",
     "http://www.bxggzyjy.com/frontpage/second.jsp?intx=4&inty=1&intz=4&pageNum=20&mdid=120022,1200222,1200223,1200224,1200225,1200226,1200227,1200228",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg",
     "http://www.bxggzyjy.com/frontpage/second.jsp?intx=4&inty=2&intz=2&pageNum=20&mdid=120219,1202192,1202193,1202194,1202195,1202196,1202197,1202198",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.bxggzyjy.com/frontpage/second.jsp?intx=4&inty=2&intz=3&pageNum=20&mdid=120220,1202202,1202203,1202204,1202205,1202206,1202207,1202208",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_liubiao_gg",
     "http://www.bxggzyjy.com/frontpage/second.jsp?intx=4&inty=2&intz=4&pageNum=20&mdid=120222,1202222,1202223,1202224,1202225,1202226,1202227,1202228",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_qita_zhaobiao_gg",
     "http://www.bxggzyjy.com/frontpage/second.jsp?intx=4&inty=5&intz=2&pageNum=20&mdid=120300,1203002,1203003,1203004,1203005,1203006,1203007,1203008",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_qita_zhongbiao_gg",
     "http://www.bxggzyjy.com/frontpage/second.jsp?intx=4&inty=5&intz=3&pageNum=20&mdid=120301,1203012,1203013,1203014,1203015,1203016,1203017,1203018",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_qita_liubiao_gg",
     "http://www.bxggzyjy.com/frontpage/second.jsp?intx=4&inty=5&intz=4&pageNum=20&mdid=120302,1203022,1203023,1203024,1203025,1203026,1203027,1203028",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

def work(conp,**args):
    est_meta(conp, data=data, diqu="辽宁省本溪市",**args)
    est_html(conp, f=f3,**args)

#
# 辽宁-本溪   特别容易挂
# date ： 2019年4月4日16:53:02
#
if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.4.175", "liaoning", "benxi"])
    # url = "http://www.bxggzyjy.com/frontpage/second.jsp?intx=4&inty=2&intz=3&pageNum=20&mdid=120220,1202202,1202203,1202204,1202205,1202206,1202207,1202208"
    # driver = webdriver.Chrome()
    # driver.get(url)
    # for i in range(1,183):f1(driver,i)
    # driver.quit()

# url = "http://www.bxggzyjy.com/frontpage/second.jsp?intx=4&inty=0&intz=4&pageNum=20&mdid=120022,1200222,1200223,1200224,1200225,1200226,1200227,1200228,120222,1202222,1202223,1202224,1202225,1202226,1202227,1202228,120225,1202252,1202253,1202254,1202255,1202256,1202257,1202258,120228,1202282,1202283,1202284,1202285,1202286,1202287,1202288,120302,1203022,1203023,1203024,1203025,1203026,1203027,1203028"
# driver = webdriver.Chrome()
# driver.get(url)