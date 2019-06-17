#最通用的时间解析
import time 
import re 

from bs4 import BeautifulSoup

#from lmf.dbv2 import db_query


def exttime_fpage(page):
    if page is None:  
        return None
    soup=BeautifulSoup(page,'lxml')
    txt=re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]','',soup.text)
    partterns=[
        "(?:信息时间|发稿时间)[:：](20[0-2][0-9])[\-/\\年\.]((?:[0][1-9])|(?:1[0-2])|(?:[1-9]))[\-/\\月\.]((?:0[1-9])|(?:[1-3][0-9])|(?:[0-9]))[^0-9]"
        ]
    for p in partterns:
        a=re.findall(p,txt)
        if a!=[]:
            data=a[0]
            date1=data[0]+'-'+ (data[1] if len(data[1])==2 else '0%s'%data[1] )+'-'+(data[2] if len(data[2])==2 else '0%s'%data[2])
            return date1 
    return None 



def exttime_fgg(t1):


    if t1 is None:return None 



    a=re.findall('([1-9][0-9]{3})[\-\./\\年]([0-9]{1,2})[\-\./\\月]([0-9]{1,2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})',t1)

    if a!=[]:
        x='-'.join(a[0][:3]) +' '+':'.join(a[0][3:])
        return x


    a=re.findall('([1-9][0-9]{3})[\-\./\\年]([0-9]{1,2})[\-\./\\月]([0-9]{1,2})',t1)
    if a!=[]:
        x='-'.join(a[0])
        return x


    a=re.findall('^([0-2][0-9])[\-\./\\年]([0-9]{1,2})[\-\./\\月]([0-9]{1,2})',t1)
    if a!=[]:
        x='20'+'-'.join(a[0])
        return x


    a=re.findall('^20[0-9]{2}[0-2][0-9][0-3][0-9]',t1)

    if a!=[]:
       x=a[0]
       return x

    #2018--1-1-

    a=re.findall('^(20[0-9]{2})--([0-9]{1,2})-([0-9]{1,2})',t1)

    if a!=[]:

             
       x='-'.join([a[0][0],a[0][1] if a[0][1]!='0' else '1' ,a[0][2] if a[0][2]!='0' else '1'])

       
       return x



    if ' CST ' in t1:
        try:
           x=time.strptime(t1,'%a %b %d %H:%M:%S CST %Y')
           x=time.strftime('%Y-%m-%d %H:%M:%S',x)
        except:
           x=''
        if x!='':return x


    return None 




