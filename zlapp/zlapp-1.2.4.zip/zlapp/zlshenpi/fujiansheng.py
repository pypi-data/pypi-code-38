
from bs4 import BeautifulSoup

import collections

import json
from zlapp.zlshenpi.core import ext_tb1


def ext_page(page,fabu_time,info=None):

    fabu_time=str(fabu_time)
    soup=BeautifulSoup(page,'html.parser')

    result={}

    d1=ext_tb1(str(soup.find_all('table',attrs={"class":"zhuce_table_style txxx_table_style"})[0]))

    # xmdw=tbs[1].th.text.strip()
    span=soup.find_all('span',attrs={"name":'enterpristName'})

    if len(span)>0:
        xmdw=span[0].text.strip()
    else:
        xmdw=""
    tr=soup.find_all('tr',attrs={"class":"itemInfo"})
    if len(tr)>0:
        xmzt=tr[0].find_all('td')[-2].text.strip()
    else:
        xmzt=""
    result={
    "xmmc":d1['项目名称'],
    "xmdm":d1['项目编码'],
    "xmdw":xmdw,
    "xmtz":d1['项目总投资(万元)'],
    "xmzt":xmzt,
    "xmdz":d1['建设详细地址'],
    "xmgk":d1['主要建设内容及规模'],
    "fabu_time":fabu_time,
    }

    return json.dumps(result,ensure_ascii=False)





