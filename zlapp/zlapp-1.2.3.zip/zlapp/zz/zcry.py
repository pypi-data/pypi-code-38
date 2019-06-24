import pandas as pd 
from lmf.dbv2 import db_query ,db_write
from bs4 import BeautifulSoup 
from lmf.bigdata import pg2pg
import re  



def extpage(page):
    soup=BeautifulSoup(page,'lxml')

    dls=soup.find_all('dl')
    data=[]
    for dl in dls:
        adict={}
        dt=dl.find('dt')

        dds=dl.find_all('dd')
        

        zcdw=dt.find('a')
        if zcdw is not None:
            zcdw=zcdw.text.strip()
            adict['注册单位']=zcdw
        else:
            tmp=list(filter(lambda x:len(x)>=4,dt.strings))
            adict['注册单位']=tmp[-1].strip()

        for dd in dds:
            tmp=list(filter(lambda x:x!='\\n',dd.strings))
            if 1<len(tmp):
                adict[tmp[0].replace('：','')]=tmp[1]
            else:
                adict[tmp[0].replace('：','')]=None

        data.append(adict)
    return data 

def df2df(df):
    data=[]

    for i in df.index:

        href=df.at[i,'ryxx_href']
        name=df.at[i,'ryxx_name']
        gender=df.at[i,'sex']
        id_type=df.at[i,'id_type']
        zjhm=df.at[i,'id_number']
        page=df.at[i,'zyzcxx']
        try:
            pagedata=extpage(page)
            for w in pagedata:
               
                tmp={"name":name,"href":href,"gender":gender,"zj_type":id_type,"zjhm":zjhm}
                tmp["zclb"]=w["注册类别"] if '注册类别' in w.keys() else None 
                tmp["zhuanye"]=w["注册专业"] if '注册专业' in w.keys() else None 
                tmp["zsbh"]=w["证书编号"] if '证书编号' in w.keys() else None 
                tmp["yzh"]=w["执业印章号"] if '执业印章号' in w.keys() else None
                tmp["youxiao_date"]=w["有效期"] if '有效期' in w.keys() else None  
                tmp["entname"]=w["注册单位"] if '注册单位' in w.keys() else None  

                data.append(tmp)
        except:
            print(href)
    df1=pd.DataFrame(data=data)
    return df1 




def extpage2(page):
    try:
        soup=BeautifulSoup(page,'lxml')

        dls=soup.find_all('dl')
        data=[]
        for dl in dls:
            adict={}
            dt=dl.find('dt')

            dds=dl.find_all('dd')
            

            zcdw=dt.find('a')
            if zcdw is not None:
                zcdw=zcdw.text.strip()
                adict['注册单位']=zcdw
            else:
                tmp=list(filter(lambda x:len(x)>=4,dt.strings))
                adict['注册单位']=tmp[-1].strip()

            for dd in dds:
                tmp=list(filter(lambda x:x!='\\n',dd.strings))
                if 1<len(tmp):
                    adict[tmp[0].replace('：','')]=tmp[1]
                else:
                    adict[tmp[0].replace('：','')]=None

            data.append(adict)
        if data==[]:return None 
        return data
    except:
        return None  