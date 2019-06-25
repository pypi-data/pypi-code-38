import random
from collections import OrderedDict
from urllib import parse

import pandas as pd
import re
import requests
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
import json
import time
from zhulong2.util.etl import est_html, est_meta, add_info, est_meta_large
from zhulong2.util.fake_useragent import UserAgent
_name_ = "guangdong_shenghui"


tt_url = None
payloadData = None
def f1_data(driver, num):
    locator = (By.XPATH, "//table[@class='m_m_dljg']/tbody/tr[2]/td[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@class='aspan1']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@class='m_m_dljg']/tbody/tr[2]/td[last()]/a").get_attribute('href')[-30:]
        driver.execute_script("javascript:turnOverPage({})".format(num))
        locator = (By.XPATH, "//table[@class='m_m_dljg']/tbody/tr[2]/td[last()]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    n = 0
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("table", class_="m_m_dljg")
    trs = tbody.find_all("tr")
    data = []
    url = driver.current_url
    for tr in trs[1:]:
        a = tr.find_all('a')[-1]
        if ('queryAcceptanceList.do' in url) or ('queryCityAcceptanceList.do' in url):
            try:
                title = tr.find_all('td')[1]['title'].strip()
            except:
                title = tr.find_all('td')[1].text.strip()
        else:
            try:
                title = tr.find_all('td')[3]['title'].strip()
            except:
                title = tr.find_all('td')[3].text.strip()
        if 'queryPrjReqList.do' in url:
            td = tr.find_all('td')[-3].text.strip()
        elif ('queryAcceptanceList.do' in url) or ('queryCityAcceptanceList.do' in url):
            td = tr.find_all('td')[-5].text.strip()
        else:
            td = tr.find_all('td')[-4].text.strip()
        href = a['href'].strip()
        link = 'http://www.gdgpo.gov.cn' + href

        info = {'info_html': '{}'.format(tr)}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f1_requests(driver, num):
        try:
            proxies_data = webdriver.DesiredCapabilities.CHROME
            proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
            proxy = proxies_chromeOptions[0].split('=')[1]
            proxies = {'http': '%s' % proxy}
        except:
            proxies = ''
        user_agents = UserAgent()
        user_agent = user_agents.chrome
        headers = {
            'User-Agent': user_agent,
        }
        Dats = {
            'pageIndex': num,
            'pageSize': 15,
            'pointPageIndexId': num-1,
        }
        datas = {**payloadData, **Dats}
        # print(datas)
        # 下载超时
        timeOut = 120
        time.sleep(random.uniform(1, 3))
        if proxies:
            res = requests.post(url=tt_url, headers=headers, data=datas, proxies=proxies, timeout=timeOut)
        else:
            res = requests.post(url=tt_url, headers=headers, data=datas, timeout=timeOut)
        # 需要判断是否为登录后的页面
        if res.status_code != 200:
            raise ConnectionError
        else:
            html = res.text
            soup = BeautifulSoup(html, 'html.parser')
            uls = soup.find("ul", class_="m_m_c_list")
            if '没有数据' in uls.text.strip():
                return pd.DataFrame()
            lis = uls.find_all("li")
            data = []
            for tr in lis:
                a = tr.find_all('a')
                try:
                    title = a[-1]['title'].strip()
                except:
                    title = a[-1].text.strip()
                td = tr.find('em').text.strip()
                href = a[-1]['href'].strip()
                if 'http' in href:
                    link = href
                else:
                    link = 'http://www.gdgpo.gov.cn' + href
                span = tr.find('span').text.strip()
                info = {}
                try:
                    leixing = span.split('·')[0].split('[')[1].strip()
                    diqu = span.split('·')[1].split(']')[0].strip()
                    info['lx'] = leixing
                    info['diqu'] = diqu
                except:
                    diqu = span.split('[')[1].split(']')[0].strip()
                    info['diqu'] = diqu
                if info:
                    info = json.dumps(info, ensure_ascii=False)
                else:
                    info = 'none'
                tmp = [title, td, link, info]
                data.append(tmp)
            df = pd.DataFrame(data=data)
            return df


def f1(driver, num):
    n = 0
    url = driver.current_url
    if ('queryPlanList.do' in url) or ('queryPrjReqList.do' in url) or ('queryAcceptanceList.do' in url) or (
            'queryCityPlanList.do' in url) or ('queryCityAcceptanceList.do' in url):
        try:
            df = f1_data(driver, num)
            return df
        except:
            n += 1
            if n < 5:
                time.sleep(2 * n)
                driver.refresh()
                return f1_data(driver, num)
            else:
                raise ConnectionError
    else:
        try:
            df = f1_requests(driver, num)
            return df
        except:
            n += 1
            if n < 5:
                time.sleep(2 * n)
                return get_pageall(tt_url, payloadData)
            else:
                raise ConnectionError


def f2(driver):
    url = driver.current_url
    if ('queryPlanList.do' in url) or ('queryPrjReqList.do' in url) or ('queryAcceptanceList.do' in url) or ('queryCityPlanList.do' in url) or ('queryCityAcceptanceList.do' in url):
        locator = (By.XPATH, "//table[@class='m_m_dljg']/tbody/tr[2]/td[last()]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "(//span[@class='aspan'])[last()]")
            num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        except:
            num = 1
        driver.quit()
        return int(num)
    else:
        global tt_url,payloadData
        tt_url=''
        n = 0
        start_url = driver.current_url
        payloadData = {}
        for st in start_url.rsplit('&'):
            if 'http' in st:
                tt_url = st
                continue
            sz = st.split('=')
            payloadData[sz[0]] = parse.unquote(sz[1], 'utf-8')
        try:
            page_num = get_pageall(tt_url, payloadData)
        except:
            n += 1
            if n < 5:
                time.sleep(2*n)
                return get_pageall(tt_url, payloadData)
            else:
                raise ConnectionError
        driver.quit()
        return int(page_num)


def get_pageall(tt_url, payloadData):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    Data = {
        'pageIndex': 1,
        'pageSize': 15,
        'pointPageIndexId': 1,
    }
    datas = {**Data, **payloadData}
    # print(datas)
    # 下载超时
    timeOut = 120
    time.sleep(random.uniform(1, 3))
    res = requests.post(url=tt_url, headers=headers, data=datas, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')
        uls = soup.find("ul", class_="m_m_c_list")
        if '没有数据' in uls.text.strip():
            return 0
        total = soup.find_all('span', class_='aspan')[-1].text.strip()
        num = int(total)
        return num


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='zw_c_c_cont'][string-length()>30]")
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
    div = soup.find('div', class_='zw_c_cont')
    return div




def get_data():
    data = []
    sitewebName = OrderedDict([("省直", "省直"),
                               ("佛山市", "佛山市,顺德区,南海区,三水区,高明区,禅城区"),
                               ("梅州市", "梅州市,蕉岭县,平远县,五华县,丰顺县,大埔县,兴宁市,梅县区,梅江区"),
                               ("河源市", "河源市,河源市高新区,江东新区,紫金县,和平县,东源县,连平县,龙川县,源城区"),
                               ("阳江市", "阳江市,海陵区,阳江高新区,阳东区,阳西县,阳春市,江城区"),
                               ("清远市", "清远市,广清产业园,清远高新区,阳山县,佛冈县,连州市,英德市,清新区,清城区,连南瑶族自治县,连山壮族瑶族自治县"),
                               ("东莞市", "高埗镇,石碣镇,茶山镇,东坑镇,桥头镇,清溪镇,大朗镇,寮步镇,沙田镇,洪梅镇,望牛墩镇,虎门镇,南城街道,万江街道,东城街道,莞城街道,东莞市"),
                               ("中山市", "中山市"),
                               ("揭阳市", "揭阳市,揭阳高新区,普侨区,大南山区,空港经济区,蓝城区,揭西县,惠来县,普宁市,揭东区,榕城区,大南海工业区"),
                               ("云浮市", "云浮市,云浮新区,云安区,郁南县,新兴县,罗定市,云城区"),
                               ("汕头市", "汕头市,南澳县,澄海区,潮阳区,潮南区,濠江区,龙湖区,金平区"),
                               ("江门市", "江门市,恩平市,开平市,鹤山市,台山市,新会区,蓬江区,江海区"),
                               ("湛江市", "湛江市,南三区,东海岛,开发区,徐闻县,遂溪县,雷州市,吴川市,廉江市,麻章区,坡头区,霞山区,赤坎区"),
                               ("茂名市", "茂名市,水东湾新城,茂名高新区,滨海区,信宜市,化州市,高州市,电白区,茂南区"),
                               ("广州市", "广州市,广州开发区,南沙区,从化区,增城区,番禺区,花都区,黄埔区,白云区,海珠区,荔湾区,越秀区,天河区"),
                               ("肇庆市", "肇庆市,新区,肇庆高新区,德庆县,封开县,怀集县,广宁县,四会市,高要市,鼎湖区,端州区"),
                               ("潮州市", "潮州市,经济开发区,枫溪区,饶平县,潮安区,湘桥区"),
                               ("深圳市", "深圳市,龙岗区,宝安区,盐田区,南山区,罗湖区,福田区"),
                               ("汕尾市", "汕尾市,红海湾,陆河县,海丰县,陆丰市,城区"),
                               ("惠州市", "惠州市,仲恺高新区,大亚湾,惠东县,龙门县,博罗县,惠阳区,惠城区"),
                               ("韶关市", "韶关市,新丰县,翁源县,仁化县,始兴县,南雄市,乐昌市,曲江区,武江区,浈江区,乳源瑶族自治县"),
                               ("珠海市", "珠海市,珠海高新区,金湾区,斗门区,香洲区"),
                               ])

    sitewebId = OrderedDict([("省直", "4028889705bebb510105bec068b00003"),
                           ("佛山市", "4028889705bebb510105bec1f8670004,297e6a6a49176e84014917f9fad20e48,297e6a6a49176e84014917f91c370e45,297e6a6a49176e84014917f7f0670e42,297e6a6a49176e84014917f6ef9c0e3f,297e6a6a49176e84014917f4ce960e3c"),
                           ("梅州市", "4028889705bedd7e0105beec36890004,297e6a6a49176e840149182a8a500e7d,297e6a6a49176e8401491829dfb00e7c,297e6a6a49176e840149182916880e7b,297e6a6a49176e8401491828272c0e7a,297e6a6a49176e8401491827381d0e79,297e6a6a49176e84014918267e7f0e78,297e6a6a49176e8401491825c7fd0e77,297e6a6a49176e8401491824f18d0e76"),
                           ("河源市", "4028889705bedd7e0105beed4b240005,40288ba96b167094016b1883a0e90b3c,40288ba95aec0b9e015af034e181604e,297e6a6a49176e8401491832a3e50e87,297e6a6a49176e8401491831f0110e86,297e6a6a49176e840149183132010e85,297e6a6a49176e84014918304f8f0e84,297e6a6a49176e840149182fad390e83,297e6a6a49176e840149182ef2a20e82"),
                           ("阳江市", "4028889705bedd7e0105bef239d20006,40288ba95544e898015547e0570b209b,40288ba95544e898015547de877c2073,297e6a6a49176e8401491835b3cb0e8b,297e6a6a49176e8401491834fd1a0e8a,297e6a6a49176e840149183451520e89,297e6a6a49176e8401491833a4af0e88"),
                           ("清远市", "4028889705bedd7e0105bef333260007,40288ba955d2a6fe0155de1d3d852ac0,40288ba95544e89801554a0333ae4443,297e6a6a49176e840149183a58040e91,297e6a6a49176e8401491839a96e0e90,297e6a6a49176e8401491838f4df0e8f,297e6a6a49176e840149183840ec0e8e,297e6a6a49176e84014918378d950e8d,297e6a6a49176e840149183690c10e8c,297e6a6a49176e840149183bce5a0e93,297e6a6a49176e840149183b1a770e92"),
                           ("东莞市", "40288ba95f25b257015f4c9577f21d70,40288ba95f25b257015f4c94a97d1d45,40288ba95f25b257015f4c93e3cf1d42,40288ba95f25b257015f4c9182301d25,40288ba95f25b257015f4c8f9b2d1ce3,40288ba95f25b257015f4c8a35c81c23,40288ba95f25b257015f4c87e00b1bac,40288ba95f25b257015f4c85d39d1ab6,40288ba95f25b257015f4c847df01a5b,40288ba95f25b257015f4c8081a91968,40288ba95f25b257015f4c7ea6b61956,40288ba95f25b257015f4c7b259617be,40288ba95f25b257015f4c79b73b175d,40288ba95f25b257015f4c786f4416f3,40288ba95f25b257015f4c77166b1648,40288ba95f25b257015f4c75e8f6162e,4028889705bedd7e0105bef45f220008"),
                           ("中山市", "4028889705bedd7e0105bef51d7f0009"),
                           ("揭阳市", "4028889705bedd7e0105bef673b8000b,40288ba954d705830154d7bfa5920022,297e55e84b2b5b59014b39a671f544a7,297e55e84b2b5b59014b39a4e2944493,297e55e84b2b5b59014b39a3047b446c,297e55e84b2b5b59014b39a0cda343f2,297e6a6a49176e840149184e2d920e9b,297e6a6a49176e840149184d65060e9a,297e6a6a49176e840149184a04910e99,297e6a6a49176e8401491848e4740e98,297e6a6a49176e8401491847b78b0e97,40288ba954d705830154d7be3b5a001f"),
                           ("云浮市", "4028889705bedd7e0105bef70a69000c,40288ba95cae24c7015caefda85e5536,297e6a6a49176e8401491853b2a60ea0,297e6a6a49176e8401491851fd0f0e9f,297e6a6a49176e840149185101240e9e,297e6a6a49176e840149185034640e9d,297e6a6a49176e840149184f0a590e9c"),
                           ("汕头市", "4028889705bebb510105becdbed40009,297e6a6a49176e84014917f3953f0e3b,297e6a6a49176e84014917f25f800e3a,297e6a6a49176e84014917f177060e39,297e6a6a49176e84014917f08b320e38,297e6a6a49176e84014917eeaf460c0d,297e6a6a49176e84014917edca26052e,297e6a6a49176e84014917ea40500024"),
                           ("江门市", "4028889705bebb510105becf79c2000a,297e6a6a49176e840149181c4a690e6b,297e6a6a49176e840149181b845d0e6a,297e6a6a49176e840149181ab2dc0e69,297e6a6a49176e8401491819ec060e68,297e6a6a49176e84014918191c880e67,297e6a6a49176e8401491818512e0e66,297e6a6a49176e840149181771e80e65"),
                           ("湛江市", "4028889705bebb510105bed04b88000b,40288ba856f087ee01570871576d3672,40288ba9562c996a015644fa89953004,40288ba9562c996a015644f7e3842ee0,297e6a6a49176e840149180d92480e5c,297e6a6a49176e840149180c857c0e5b,297e6a6a49176e840149180b89920e5a,297e6a6a49176e840149180a99a80e59,297e6a6a49176e8401491809bb0e0e58,297e6a6a49176e8401491808cf490e57,297e6a6a49176e8401491807fc140e56,297e6a6a49176e8401491806f81e0e55,297e6a6a49176e8401491805ff010e54"),
                           ("茂名市", "4028889705bebb510105bed1471d000c,40288ba95bc9e24f015bd73b455f0cec,40288ba95544e89801554a00b1654418,40288ba95544e898015549ff9982440f,297e6a6a49176e840149182018be0e70,297e6a6a49176e840149181f54e30e6f,297e6a6a49176e840149181ea60f0e6e,297e6a6a49176e840149181dfb9e0e6d,297e6a6a49176e840149181d3f040e6c"),
                           ("广州市", "4028889705bebb510105bec9f3490006,40288ba95a4015db015a40a6592a0d80,40288ba8595d2b7601596d8c73af4e94,297e6a6a49176e84014917ded7270015,297e6a6a49176e84014917ddcfa80014,297e6a6a49176e84014917dc58870013,297e6a6a49176e84014917db613e0012,297e6a6a49176e84014917da5ea00011,297e6a6a49176e84014917d9381d0010,297e6a6a49176e84014917d84882000f,297e6a6a49176e84014917d70c8c000e,297e6a6a49176e84014917d577ad000d,297e6a6a49176e84014917c983a4000c"),
                           ("肇庆市", "4028889705bebb510105bed24c86000d,40288ba955b363eb0155b43bb7732888,40288ba95544e89801554a01bdb44423,297e6a6a49176e84014918163c680e64,297e6a6a49176e8401491815544b0e63,297e6a6a49176e840149181478eb0e62,297e6a6a49176e8401491813b6d50e61,297e6a6a49176e8401491812e2480e60,297e6a6a49176e8401491811d6090e5f,297e6a6a49176e84014918107d8e0e5e,297e6a6a49176e840149180f46d60e5d"),
                           ("潮州市", "4028889705bedd7e0105bef5da47000a,40288ba95c3aa249015c3d824d833081,297e55e84b2b5b59014b39c6bebe46de,297e6a6a49176e8401491845c3100e96,297e6a6a49176e840149184392de0e95,297e6a6a49176e8401491841ddd20e94"),
                           ("深圳市", "4028889705bebb510105becb72d30007,297e6a6a49176e84014917e549b4001c,297e6a6a49176e84014917e4323f001b,297e6a6a49176e84014917e342750018,297e6a6a49176e84014917e2463c0017,297e6a6a49176e84014917e0efd40016,297e6a6a483e68ef014844cdbb960035"),
                           ("汕尾市", "4028889705bebb510105bed6e6ac000f,40288ba95544e898015547efc2bd2277,297e6a6a49176e840149182de3e30e81,297e6a6a49176e840149182d2c480e80,297e6a6a49176e840149182c884c0e7f,297e6a6a49176e840149182bd6ba0e7e"),
                           ("惠州市", "4028889705bebb510105bed2e21f000e,40288ba954e33a3d0154eb481eb95d68,40288ba954e33a3d0154eaebe59c527c,297e6a6a49176e84014918240f980e75,297e6a6a49176e840149182335fc0e74,297e6a6a49176e840149182284c80e73,297e6a6a49176e8401491821c4760e72,297e6a6a49176e84014918211a820e71"),
                           ("韶关市", "4028889705bebb510105becc5dbf0008,297e6a6a49176e8401491802b6110e52,297e6a6a49176e8401491801d5830e51,297e6a6a49176e840149180091530e50,297e6a6a49176e84014917ffc7be0e4e,297e6a6a49176e84014917fef42b0e4d,297e6a6a49176e84014917fe1c440e4c,297e6a6a49176e84014917fd03d50e4b,297e6a6a49176e84014917fc0c9c0e4a,297e6a6a49176e84014917fb15920e49,297e6a6a49176e840149180428b00e53"),
                           ("珠海市", "4028889705bebb510105bec522060005,40288ba855aef0750155b493435363b4,297e6a6a49176e84014917e83ff30021,297e6a6a49176e84014917e74fbc001e,297e6a6a49176e84014917e65c2b001d"),
                            ])

    regionIds = OrderedDict([("省直", ""),("佛山市", "0105"), ("梅州市", "0108"), ("河源市", "0107"), ("阳江市", "0114"), ("清远市", "0118"),
                             ("东莞市", "0111"), ("中山市", "0112"), ("揭阳市", "0120"), ("云浮市", "0121"), ("汕头市", "0104"),
                             ("江门市", "0113"), ("湛江市", "0115"), ("茂名市", "0116"), ("广州市", "0101"), ("肇庆市", "0117"),
                             ("潮州市", "0119"), ("深圳市", "0102"), ("汕尾市", "0110"), ("惠州市", "0109"), ("韶关市", "0106"), ("珠海市", "0103")
                             ])

    channelCode = OrderedDict([("zhaobiao", "0005"), ("biangeng", "0006"), ("zhongbiao", "0008"),("gqita_fanpai", "0017"), ("gqita_zhao_liu_pljz", "-3")])

    # 省级采购
    for w1 in channelCode.keys():
        for w2 in sitewebName.keys():
            p1 = sitewebId[w2]
            p2 = regionIds[w2]
            href = "http://www.gdgpo.gov.cn/queryMoreInfoList.do&channelCode=%s&sitewebName=%s&sitewebId=%s&regionIds=%s" \
                   % (channelCode[w1], sitewebName[w2],p1, p2)
            tb = "zfcg_%s_sj_diqu%s_gg" % (w1, p2)
            col = ["name", "ggstart_time", "href", "info"]
            tmp = [tb, href, col, add_info(f1, {"diqu1": w2}), f2]
            data.append(tmp)


    sx_sitewebId = OrderedDict([("省直", "4028889705bebb510105bec068b00003"),
                               ("佛山市", "4028889705bebb510105bec1f8670004"),
                               ("梅州市", "4028889705bedd7e0105beec36890004"),
                               ("河源市", "4028889705bedd7e0105beed4b240005"),
                               ("阳江市", "4028889705bedd7e0105bef239d20006"),
                               ("清远市", "4028889705bedd7e0105bef333260007"),
                               ("东莞市", "4028889705bedd7e0105bef45f220008"),
                               ("中山市", "4028889705bedd7e0105bef51d7f0009"),
                               ("揭阳市", "4028889705bedd7e0105bef673b8000b"),
                               ("云浮市", "4028889705bedd7e0105bef70a69000c"),
                               ("汕头市", "4028889705bebb510105becdbed40009"),
                               ("江门市", "4028889705bebb510105becf79c2000a"),
                               ("湛江市", "4028889705bebb510105bed04b88000b"),
                               ("茂名市", "4028889705bebb510105bed1471d000c"),
                               ("广州市", "4028889705bebb510105bec9f3490006"),
                               ("肇庆市", "4028889705bebb510105bed24c86000d"),
                               ("潮州市", "4028889705bedd7e0105bef5da47000a"),
                               ("深圳市", "4028889705bebb510105becb72d30007"),
                               ("汕尾市", "4028889705bebb510105bed6e6ac000f"),
                               ("惠州市", "4028889705bebb510105bed2e21f000e"),
                               ("韶关市", "4028889705bebb510105becc5dbf0008"),
                               ("珠海市", "4028889705bebb510105bec522060005"),
                            ])

    # 市县采购
    for w1 in channelCode.keys():
        for w2 in sx_sitewebId.keys():
            p2 = regionIds[w2]
            href = "http://www.gdgpo.gov.cn/queryMoreCityCountyInfoList2.do&channelCode=%s&sitewebId=%s" % (channelCode[w1], sx_sitewebId[w2])
            tb = "zfcg_%s_sx_diqu%s_gg" % (w1, p2)
            col = ["name", "ggstart_time", "href", "info"]
            tmp = [tb, href, col, add_info(f1, {"diqu1": w2}), f2]
            data.append(tmp)
    data1 = data.copy()
    remove_arr = []
    for w in data:
        if w[0] in remove_arr: data1.remove(w)
    return data1
    # 创建data

data = get_data()


data1 = [
    ["zfcg_yucai_gg", "http://www.gdgpo.gov.cn/queryPrjReqList.do",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_cgjh_shengji_gg", "http://www.gdgpo.gov.cn/queryPlanList.do",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '采购计划', 'diqu1': '省级'}), f2],
#
    ["zfcg_gqita_cgjh_shixian_gg", "http://www.gdgpo.gov.cn/queryCityPlanList.do",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '地方采购计划', 'diqu1': '市县'}), f2],

    ["zfcg_yanshou_shengji_gg", "http://www.gdgpo.gov.cn/queryAcceptanceList.do",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu1': '省级'}), f2],

    ["zfcg_yanshou_shixian_gg", "http://www.gdgpo.gov.cn/queryCityAcceptanceList.do",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu1': '市县'}), f2],
]

data.extend(data1)
# print(data)

def work(conp, **args):
    est_meta_large(conp, data=data, diqu="广东省省会", **args)
    est_html(conp, f=f3, **args)


# 修改日期：2019/6/25
# 页数太多，跑不完，总是会跳回首页，详情页加载慢
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "guangdong"],pageloadtimeout=120,interval_page=100,num=45)

    # driver=webdriver.Chrome()
    # url = "http://www.gdgpo.gov.cn/queryMoreCityCountyInfoList2.do&channelCode=0008&sitewebId=4028889705bedd7e0105bef239d20006"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver=webdriver.Chrome()
    # url = "http://www.gdgpo.gov.cn/queryMoreCityCountyInfoList2.do&channelCode=0008&sitewebId=4028889705bedd7e0105bef239d20006"
    # driver.get(url)
    # for i in range(6, 10):
    #     df=f1(driver, i)
    #     print(df.values)
