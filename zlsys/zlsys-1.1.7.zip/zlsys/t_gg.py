from lmf.dbv2 import db_command ,db_query 
from datetime import datetime ,timedelta

import datetime 
import time
import re 

def exttime(tstr):
    a=re.findall('[1][0-9]{12}',tstr)
    if a!=[]:
        t=a[0]
        t=int(int(a[0])/1000)

        val=time.localtime(t)
        dt = time.strftime('%Y-%m-%d %H:%M:%S', val)
        return dt

    a=re.findall('([0-9]{4})[\-\\/]([0-9]{1,2})[\-\\/]([0-9]{1,2})',tstr)
    if a!=[]:
        t=a[0] 
        t=t[0]+'-'+(t[1] if len(t[1])==2 else '0%s'%t[1])+'-'+(t[2] if len(t[2])==2 else '0%s'%t[2])+' '+t[3]
        return t 
    return None 


#t_gg生成和更新 发生在数据库中

def est_func(conp):
    sql=r"""



create or replace function ggtype_tran(ggtype text ) returns text 
as $$

data={"pbjieguo":"评标结果公告",
"zhaobiao":"招标公告",
"fuhe_jieguo":"复核结果公告",
"pbjieguo_biangeng":"评标结果变更",
"zhongbiao":"中标公告",
"zhongbiao_biangeng":"中标结果变更公告",
"dayi":"答疑公告",
"liubiao":"流标公告",

"yichang":"异常公告",
"biangeng":"变更公告"

}

if ggtype in data.keys():return data[ggtype]
else:return None


$$ language plpython3u ;


--drop function merge_info(xmjl text, bm_endtime text, tb_endtime text, bzj_time text, kb_time text, pb_time text, db_time text, zhongbiao_hxr text, zhongbiaojia numeric, kzj numeric,bd_guid text);
create or replace function merge_info( xmjl text ,bm_endtime text,tb_endtime text ,bzj_time text 

,kb_time text ,pb_time text ,db_time text ,zhongbiao_hxr text ,zhongbiaojia text ,kzj text,bd_guid text ,bd_bh text,bd_name text,zbr text ,zbdl text,xmjl_dj text ,xmjl_zsbh text  
) returns text 
as $$

import json 
import re 
import time 

def exttime(tstr):
    a=re.findall('[1][0-9]{12}',tstr)
    if a!=[]:
        t=a[0]
        t=int(int(a[0])/1000)

        val=time.localtime(t)
        dt = time.strftime('%Y-%m-%d %H:%M:%S', val)
        return dt

    a=re.findall('([0-9]{4})[\-\\/]([0-9]{1,2})[\-\\/]([0-9]{1,2})',tstr)
    if a!=[]:
        t=a[0] 
        t=t[0]+'-'+(t[1] if len(t[1])==2 else '0%s'%t[1])+'-'+(t[2] if len(t[2])==2 else '0%s'%t[2])
        return t 
    return None 
def extprice(price):
    if price is None:return None 
    CN_NUM = {
        '〇' : 0, '一' : 1, '二' : 2, '三' : 3, '四' : 4, '五' : 5, '六' : 6, '七' : 7, '八' : 8, '九' : 9, '零' : 0,
        '壹' : 1, '贰' : 2, '叁' : 3, '肆' : 4, '伍' : 5, '陆' : 6, '柒' : 7, '捌' : 8, '玖' : 9, '貮' : 2, '两' : 2,
    }

    CN_UNIT = {
        '十' : 10,
        '拾' : 10,
        '百' : 100,
        '佰' : 100,
        '千' : 1000,
        '仟' : 1000,
        '万' : 10000,
        '萬' : 10000,
        '亿' : 100000000,
        '億' : 100000000,
        '兆' : 1000000000000,
    }

    def chinese_to_arabic(cn:str) -> int:
        unit = 0   # current
        ldig = []  # digest
        for cndig in reversed(cn):
            if cndig in CN_UNIT:
                unit = CN_UNIT.get(cndig)
                if unit == 10000 or unit == 100000000:
                    ldig.append(unit)
                    unit = 1
            else:
                dig = CN_NUM.get(cndig)
                if unit:
                    dig *= unit
                    unit = 0
                ldig.append(dig)
        if unit == 10:
            ldig.append(10)
        val, tmp = 0, 0
        for x in reversed(ldig):
            if x == 10000 or x == 100000000:
                val += tmp * x
                tmp = 0
            else:
                tmp += x
        val += tmp
        return val


    a=re.findall('[四〇伍叁零二八三壹六柒貮一捌九五两贰肆玖七陆億兆佰亿万萬十拾仟千百]{3,}',price)
    if a!=[]:
       result=chinese_to_arabic(a[0])

       return result 

    a=re.findall('([1-9][0-9\.]{0,}[0-9]|0\.[0-9]+)[^%]',price)

    if a!=[]:
       result=a[0] 
       if result.count('.')>1: result='.'.join(result.split('.')[:2])
       if '万' in price:
           result=float(result)
           result=result*10000
       if '亿' in price:
           result=float(result)
           result=result*100000000
       return result 
            
    return None 
data={}

if xmjl is not None :data['xmjl']=xmjl 

if bm_endtime is not None:data['bm_endtime']=exttime(bm_endtime)

if tb_endtime is not None :data['tb_endtime']=exttime(tb_endtime) 

if bzj_time is not None:data['bzj_time']=exttime(bzj_time) 

if kb_time is not None:data['kb_time']=exttime(kb_time) 


if db_time is not None:data['db_time']=exttime(db_time) 


if zhongbiao_hxr is not None:data['zhongbiao_hxr']=zhongbiao_hxr 



if bd_guid is not None:data['bd_guid']=bd_guid

if bd_name is not None:data['bd_name']=bd_name

if bd_bh is not None:data['bd_bh']=bd_bh

if zbr is not None:data['zbr']=zbr

if zbdl is not None:data['zbdl']=zbdl

if xmjl_dj is not None:data['xmjl_dj']=xmjl_dj

if xmjl_zsbh is not None:data['xmjl_zsbh']=xmjl_zsbh

if zhongbiaojia is not None:data['zhongbiaojia']=extprice(str(zhongbiaojia ))
if kzj is not None:data['kzj']=extprice(str(kzj ))


data=json.dumps(data,ensure_ascii=False)


return data 
$$ language plpython3u ;


create or replace function exttime(tstr text ) returns text 

as $$
import time 
import re
a=re.findall('[1][0-9]{12}',tstr)
if a!=[]:
        t=a[0]
        t=int(int(a[0])/1000)

        val=time.localtime(t)
        dt = time.strftime('%Y-%m-%d %H:%M:%S', val)
        return dt

a=re.findall('([0-9]{4})[\-\\/]([0-9]{1,2})[\-\\/]([0-9]{1,2}) ([0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2})',tstr)
if a!=[]:
        t=a[0] 
        t=t[0]+'-'+(t[1] if len(t[1])==2 else '0%s'%t[1])+'-'+(t[2] if len(t[2])==2 else '0%s'%t[2])+' '+t[3]
        return t 
return None 

$$ language plpython3u;




    """
    db_command(sql,dbtype="postgresql",conp=conp)






def t_gg_update(conp,quyu,diqu):

    user,passwd,host,db,schema=conp

    tbs1=db_query("""select tablename from pg_tables where schemaname='%s'  order by tablename """%schema
        ,dbtype="postgresql",conp=conp)['tablename'].values.tolist()

    print("更新,表插入到t_gg")
    print(tbs1)
    if 't_gg' not in tbs1:
        sql="""
SELECT  gg_file as guid,gg_name ,gg_href as href ,"public".exttime(gg_fabutime)::timestamp(0) as fabu_time ,public.ggtype_tran(ggtype) as ggtype

,'%s' as quyu ,'%s' as diqu,jytype

, now()::timestamp(0) as create_time

,public.merge_info(xmjl, bm_endtime ,  tb_endtime 

,  bzj_time , kb_time ,  pb_time
,  db_time ,zhongbiao_hxr,zhongbiaojia,kzj,bd_guid,bd_bh ,bd_name ,zbr  ,zbdl ,xmjl_dj  ,xmjl_zsbh 
) as info ,page into %s.t_gg
 from %s.t_gg_src 
    """%(quyu,diqu,schema,schema)
    else:

        sql="""

insert into %s.t_gg
SELECT distinct on(guid) gg_file as guid,gg_name ,gg_href as href ,"public".exttime(gg_fabutime)::timestamp(0) as fabu_time ,public.ggtype_tran(ggtype) as ggtype

,'%s' as quyu ,'%s' as diqu,jytype

, now()::timestamp(0) as create_time

,public.merge_info(xmjl, bm_endtime ,  tb_endtime 

,  bzj_time , kb_time ,  pb_time
,  db_time ,zhongbiao_hxr,zhongbiaojia,kzj,bd_guid,bd_bh ,bd_name ,zbr  ,zbdl ,xmjl_dj  ,xmjl_zsbh 
) as info ,page 

from %s.t_gg_src  as b where not exists(select 1 from %s.t_gg as a where a.guid=b.gg_file)
            """%(schema,quyu,diqu,schema,schema)
    db_command(sql,dbtype="postgresql",conp=conp)



#conp=['postgres','since2015','192.168.4.175','zlsys','yunnan_qujingshi']
# t_gg_update(conp,'zlsys_sichuan_yibinshi','四川宜宾市')