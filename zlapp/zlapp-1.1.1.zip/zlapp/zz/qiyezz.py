from lmfgg.table.tbpre import get_pure_tbs
from lmfgg.table.tbpre import get_tb
from lmf.dbv2 import db_query ,db_write
from lmf.bigdata import pg2pg
from bs4 import BeautifulSoup
from lmfgg.table.tbdata import ext1
import re
import pandas as pd 
htmlparser="lxml"

def zzext(page):
    soup1=BeautifulSoup(page,'lxml')

    div=soup1.find('div',class_='user_info spmtop')
    if div is None:return None
    name=div.text.strip() 

    tbs=get_pure_tbs(page)
    if tbs is None:return None
    if len(tbs)<2:return None
    tb0=tbs[0]
    info=ext1(tb0)

    tb1=tbs[1]

    columns=["zzlb","zzbh","zzmc","bgdate","eddate","fbjg"]
    soup=BeautifulSoup(tb1,'html.parser')

    trs=soup.find_all('tr',class_="row")
    data=[]
    headers=["资质类别","资质证书号","资质名称","发证日期","证书有效期","发证机关"]
    if trs!=[]:
        for tr in trs:
            #tmp=[None if tr.find("td",id=re.compile("tb__[0-9]+_%d"%i)) is  None else tr.find("td",id=re.compile("tb__[0-9]+_%d"%i)).text.strip()  for i in range(1,7)]
            tmp=[None if tr.find("td",attrs={"data-header": w}) is  None else tr.find("td",attrs={"data-header": w}).text.strip()  for w in headers]

            data.append(tmp)

    df=pd.DataFrame(data=data,columns=columns)
    df=df.fillna(method='ffill',axis=0)
    df['entname']=name

    if info is not None:
        df["tydm"]=info["统一社会信用代码"] if  "统一社会信用代码" in info.keys() else None

        df["fddbr"]=info["企业法定代表人"] if  "企业法定代表人" in info.keys() else None

        df["jgdz"]=info["企业经营地址"]  if  "企业经营地址" in info.keys() else None

        df["gsd"]=info["企业注册属地"]    if  "企业注册属地" in info.keys() else None

        df["jglx"]=info["企业登记注册类型"] if  "企业登记注册类型" in info.keys() else None
        for w in ["统一社会信用代码","企业法定代表人","企业登记注册类型","企业注册属地","企业经营地址"]:
            if w in info.keys():info.pop(w)
        if info!={}:df["qita"]=info.popitem()[1]
    return df 



def df2df(df):

    df1=pd.DataFrame(columns=['zzlb', 'zzbh', 'zzmc', 'bgdate', 'eddate', 'fbjg', 'entname', 'tydm',
           'fddbr', 'jgdz', 'gsd', 'jglx', 'qita','href'])
    for i in df.index:
        page=df.at[i,'page']
        href=df.at[i,'href']
        dftmp=zzext(page)
        if dftmp is None:continue
        #print(len(dftmp))
        dftmp['href']=href
        df1=df1.append(dftmp)

    return df1

     
# sql="select * from jianzhu.gg_html where href='http://jzsc.mohurd.gov.cn/dataservice/query/comp/compDetail/001607220057195918' "

# # sql="select distinct on(href) * from tc.gg_html "
# conp=["postgres","since2015","192.168.4.188","bid","jianzhu"]
# df=db_query(sql,dbtype="postgresql",conp=conp)


# pg2pg(sql,'qyzz',conp,conp,f=df2df,chunksize=1000)


def zzext2(page):
    soup1=BeautifulSoup(page,'lxml')
    div=soup1.find('div',class_='user_info spmtop')
    if div is None:return None
    name=div.text.strip() 

    tbs=get_pure_tbs(page)
    if tbs is None:return None
    if len(tbs)<2:return None
    tb0=tbs[0]
    info=ext1(tb0)

    tb1=tbs[1]

    columns=["zzlb","zzbh","zzmc","bgdate","eddate","fbjg"]
    soup=BeautifulSoup(tb1,'html.parser')

    trs=soup.find_all('tr',class_="row")
    data=[]
    headers=["资质类别","资质证书号","资质名称","发证日期","证书有效期","发证机关"]
    if trs!=[]:
        for tr in trs:
            #tmp=[None if tr.find("td",id=re.compile("tb__[0-9]+_%d"%i)) is  None else tr.find("td",id=re.compile("tb__[0-9]+_%d"%i)).text.strip()  for i in range(1,7)]
            tmp=[None if tr.find("td",attrs={"data-header": w}) is  None else tr.find("td",attrs={"data-header": w}).text.strip()  for w in headers]

            data.append(tmp)

    df=pd.DataFrame(data=data,columns=columns)
    df=df.fillna(method='ffill',axis=0)
    df['entname']=name

    if info is not None:
        df["tydm"]=info["统一社会信用代码"] if  "统一社会信用代码" in info.keys() else None

        df["fddbr"]=info["企业法定代表人"] if  "企业法定代表人" in info.keys() else None

        df["jgdz"]=info["企业经营地址"]  if  "企业经营地址" in info.keys() else None

        df["gsd"]=info["企业注册属地"]    if  "企业注册属地" in info.keys() else None

        df["jglx"]=info["企业登记注册类型"] if  "企业登记注册类型" in info.keys() else None
        for w in ["统一社会信用代码","企业法定代表人","企业登记注册类型","企业注册属地","企业经营地址"]:
            if w in info.keys():info.pop(w)
        if info!={}:df["qita"]=info.popitem()[1]
    result=df.to_dict(orient='record')
    return result