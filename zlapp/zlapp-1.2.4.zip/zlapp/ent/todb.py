from zlapp.ent.api import *

from lmf.dbv2 import db_query ,db_write 

import pandas as pd 

from sqlalchemy.dialects.postgresql import JSONB,VARCHAR,TIMESTAMP,INTEGER,TEXT
from datetime import datetime 
import traceback 
import re 

import time
from threading import Thread
from queue import Queue 
from threading import  Semaphore

#df=db_query(sql="with a as (SELECT distinct src->>'creditCode' as tydm  FROM t_base_src) select * from a  where  tydm is not null ",dbtype="postgresql",conp=['postgres',"since2015",'192.168.3.172',"lmf",'public'])
def w_base_src(jgmc,conp):
    data=[]

    w=jgmc
    result=get_base(name=w)
    if result is not None and result is not False:
        t=datetime.now()
        data.append([w,result,t])


    df1=pd.DataFrame(data=data,columns=['jgmc','src','createtime'])

    datadict={"jgmc":VARCHAR(500),"src":JSONB(),'createtime':TIMESTAMP()}
    db_write(df1,'t_base_src',dbtype="postgresql",conp=conp,datadict=datadict,if_exists='append')




def w_sh_src(tydm,conp):
    data=[]

    w=tydm
    result=get_sh(tydm=w)
    if result is not None and result is not False:
        t=datetime.now()
        data.append([w,result,t])


    df1=pd.DataFrame(data=data,columns=['tydm','src','createtime'])

    datadict={"tydm":VARCHAR(500),"src":JSONB(),'createtime':TIMESTAMP}
    db_write(df1,'t_sh_src',dbtype="postgresql",conp=conp,datadict=datadict,if_exists='append')



def w_alter_src(jgmc):
    data=[]

    w=jgmc
    result=get_alters(name=w)
    if result is not None and result is not False:
        t=datetime.now()
        data.append([w,result,t])


    df1=pd.DataFrame(data=data,columns=['jgmc','src','createtime'])

    datadict={"jgmc":VARCHAR(500),"src":JSONB(),'createtime':TIMESTAMP}
    db_write(df1,'t_alter_src',dbtype="postgresql",conp=['postgres','since2015','192.168.3.172','lmf',"public"],datadict=datadict,if_exists='append')


def w_ss_src(jgmc,conp):
    data=[]

    w=jgmc
    result=get_ss(w)
    if result is not None and result is not False:
        t=datetime.now()
        data.append([w,result,t])


    df1=pd.DataFrame(data=data,columns=['word','src','createtime'])

    datadict={"word":VARCHAR(500),"src":JSONB(),'createtime':TIMESTAMP()}
    db_write(df1,'t_ss_src',dbtype="postgresql",conp=conp,datadict=datadict,if_exists='append')



def w_base_est(jgmc):
    data={}
    #,src->>'historyNames'    as jgmcbefore
    sql1="""select 
    src->>'name' as jgmc ,
    ,src->>'creditCode' as tydm
    ,src->>'regNumber'  as zch
    ,src->>'orgNumber'  as jgdm 
    ,src->>'id'  as entid 
    ,to_timestamp((src->>'estiblishTime')::bigint/1000)::timestamp(6) as clrq
    ,src->>'regLocation'  as jgdz
    ,src->>'legalPersonName' as fddbr
    ,src->>'businessScope' as jyfw
    ,src->>'industry'       as jjhy
    ,src->>'companyOrgType'  as jglx
    ,src->>'regCapital'  as zczj 
    ,src->>'regCapitalCurrency' as zczj_bz
    ,src->>'actualCapital'  as zczj_sj
    ,src->>'actualCapitalCurrency' as zczj_sj_bz
    ,src->>'taxNumber'  as taxdm
    ,to_timestamp((src->>'fromTime')::bigint/1000)::timestamp(6)  as fromtime 
    ,to_timestamp((src->>'toTime')::bigint/1000)::timestamp(6)   as totime
    ,src->>'regInstitute'   as djbumen
    ,src->>'regStatus'      as jyzt
    ,src->>'property3'       as engname
    ,src->>'bondNum'         as bondnum

    ,src->>'staffNumRange'    as zggm
    ,src->>'email'           as email
    ,src->>'phoneNumber'     as phone
    ,src->>'websiteList'      as website
    ,src->>'staffList'        as  staff_info
    ,src->>'alias'            as alias 

    ,src->>'revokeDate'      as diaoxiaodate
    ,src->>'revokeReason'      as diaoxiaoreason

    ,src->>'cancelDate'     as zhuxiaodate
    ,src->>'cancelReason'     as zhuxiaoreason


     from t_base_src  where jgmc='%s' """%jgmc

    df1=db_query(sql=sql1,dbtype="postgresql",conp=['postgres','since2015','192.168.3.172','lmf',"public"])
    if not df1.empty:
        a1=df1.to_dict(orient='record')[0]

    data=a1.copy()

    #zczj  zczj_sj 

    #data['changetime']=None
    #datetime(1970,1,1) 

    # data['zhuxiaodate']=datetime(1970,1,1)
    # data['diaoxiaodate']=datetime(1970,1,1)

    tydm=a1['tydm']
    sql2="""SELECT tydm,src->>'holderlist' as sh_info FROM t_sh_src where tydm='%s'"""%tydm
    df2=db_query(sql=sql2,dbtype="postgresql",conp=['postgres','since2015','192.168.3.172','lmf',"public"])
    if not df2.empty:
        a2=df2.to_dict(orient='record')[0]

    data['sh_info']=a2['sh_info']


    df3=pd.DataFrame(data=[data])

    datadict={"jgmc":VARCHAR(500),"tydm":VARCHAR(225),"jgdm":VARCHAR(255),"zch":VARCHAR(255),"entid":VARCHAR(255),"clrq":TIMESTAMP(),"fddbr":VARCHAR(255)
    ,"jgdz":VARCHAR(500),"jyfw":TEXT(),"jjhy":VARCHAR(500),"zggm":VARCHAR(100),"zczj":VARCHAR(100),"zczj_bz":VARCHAR(100),"zczj_sj":VARCHAR(100),"zczj_sj_bz":VARCHAR(100)
    ,"fromtime":TIMESTAMP(),"totime":TIMESTAMP(),"sh_info":JSONB(),"staff_info":JSONB(),"jglx":VARCHAR(100),"phone":VARCHAR(100),"bondnum":VARCHAR(100),"engname":VARCHAR(500)
    ,"alias":VARCHAR(100),"email":VARCHAR(100),"taxdm":VARCHAR(255),"diaoxiaodate":TIMESTAMP(),"diaoxiaoreason":VARCHAR(500),"zhuxiaodate":TIMESTAMP(),"zhuxiaoreason":VARCHAR(500)
    ,"jyzt":VARCHAR(100),"djbumen":VARCHAR(100),'website':VARCHAR(500)
    }
    db_write(df3,'t_base_est',dbtype='postgresql',conp=['postgres','since2015','192.168.3.172','lmf',"public"],if_exists='append',datadict=datadict)
    


# for w in df["name"]:
#     insert_one(w)

def jgmc2tydm(jgmc):
    sql="select tydm from t_base_est where jgmc='%s' "%jgmc 
    df=db_query(sql,dbtype='postgresql',conp=['postgres','since2015','192.168.3.172','lmf',"public"]) 
    if df.empty:return None 
    return df.at[0,'tydm']

def w_alter_est(jgmc):
    tydm=jgmc2tydm(jgmc)
    if tydm is None:
        return None
    data=[]

    sql="select jgmc,src from t_alter_src where jgmc='%s'"%jgmc
    df=db_query(sql=sql,dbtype="postgresql",conp=['postgres','since2015','192.168.3.172','lmf',"public"])
    if df.empty:return None 
    src=df.at[0,'src']
    for w in src:
        tmp={}
        tmp['before']=re.sub('<[^><]*>','',w["contentBefore"])
        tmp['after']=re.sub('<[^><]*>','',w["contentAfter"])
        tmp['changetime']=re.sub('<[^><]*>','',w["changeTime"])
        if 'changeItem' in w.keys(): 
            tmp['changeitem']=re.sub('<[^><]*>','',w["changeItem"])
        else:
            tmp['changeitem']=None


        tmp['createtime']=w['createTime']
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df=df.assign(rn=df.sort_values(['createtime'], ascending=False).groupby(['before','after','changetime'])
        .cumcount()+1 ).query('rn<=1')[['before','after','changetime','changeitem','createtime']]
    df['tydm']=tydm 
    datadict={"tydm":VARCHAR(255),"before":VARCHAR(500),'after':VARCHAR(500),'changetime':VARCHAR(500),"changetime":VARCHAR(500),'createtime':VARCHAR(500),'inserttime':TIMESTAMP()}
    df['inserttime']=datetime.now()
    db_write(df,'t_alter_est',dbtype='postgresql',conp=['postgres','since2015','192.168.3.172','lmf',"public"],if_exists='append',datadict=datadict)



class write_base_src_class:

    def __init__(self,arr,conp):
        self.sema=Semaphore(1)
        self.arr_q=Queue()
        self.j=len(arr)
        self.cn=0
        self.conp=conp
        for i in arr:
            self.arr_q.put(i)
        self.bg=time.time()
    def w_base_src_t(self):
        while not self.arr_q.empty():
            try:
                x=self.arr_q.get(block=False)
            except:
                traceback.print_exc()
                continue
            if x is None:continue
            try:
                w_base_src(x,self.conp)
            except:
                traceback.print_exc() 

            self.sema.acquire()
            self.ed=time.time()
            cost=int(self.ed-self.bg)
            self.cn+=1
            if self.cn%1000==0:
                print("插入%d条，共%d条,耗时%d 秒"%(self.cn,self.j,cost))
                self.ed=time.time()
            self.sema.release()
    def write_base_src(self,num=None):
        ths=[]
        if num is None:num=5 if self.j<1000 else 10 
        print("共%d个，%d个线程"%(self.j,num))
        for _ in range(num):
            t=Thread(target=self.w_base_src_t)
            ths.append(t)
        for t in ths:
            t.start()
        for t in ths:
            t.join()

# def write_base_src(arr,conp):

#     sema=Semaphore(1)
#     arr_q=Queue()
#     j=len(arr)
#     cn=0
#     for i in arr:
#         arr_q.put(i)
#     def w_base_src_t():
        
#         global cn 
#         print(cn)
#         print(type(arr_q)) 
#         while not arr_q.empty():
#             try:
#                 x=arr_q.get(block=False)
#             except:
#                 traceback.print_exc()
#                 continue
#             if x is None:continue
#             try:
#                 w_base_src(x,conp)
#             except:
#                 traceback.print_exc() 

#             sema.acquire()
#             cn+=1
#             if cn%100==0:
#                 print("插入%d条，共%d条"%(cn,j))
#             sema.release()


#     ths=[]
#     for _ in range(4):
#         t=Thread(target=w_base_src_t)
#         ths.append(t)
#     for t in ths:
#         t.start()
#     for t in ths:
#         t.join()

    # i=0
    # j=len(arr)
    # bg=time.time()
    # for w in arr:
    #     try:
    #         w_base_src(w,conp)
    #         i+=1
    #         if i%100==0:
    #             ed=time.time()
    #             cost=int(ed-bg)
    #             print("插入%d条，共%d条，耗时%d秒"%(i,j,cost))
    #             bg=time.time()
    #     except:
    #         traceback.print_exc()

class write_sh_src_class:

    def __init__(self,arr,conp):
        self.sema=Semaphore(1)
        self.arr_q=Queue()
        self.j=len(arr)
        self.cn=0
        self.conp=conp
        for i in arr:
            self.arr_q.put(i)
        self.bg=time.time()
    def w_sh_src_t(self):
        while not self.arr_q.empty():
            try:
                x=self.arr_q.get(block=False)
            except:
                traceback.print_exc()
                continue
            if x is None:continue
            try:
                w_sh_src(x,self.conp)
            except:
                traceback.print_exc() 

            self.sema.acquire()
            self.ed=time.time()
            cost=int(self.ed-self.bg)
            self.cn+=1
            if self.cn%1000==0:
                print("插入%d条，共%d条,耗时%d 秒"%(self.cn,self.j,cost))
                self.ed=time.time()
            self.sema.release()
    def write_sh_src(self,num=None):
        ths=[]
        if num is None:num=5 if self.j<1000 else 10 
        print("共%d个，%d个线程"%(self.j,num))
        for _ in range(num):
            t=Thread(target=self.w_sh_src_t)
            ths.append(t)
        for t in ths:
            t.start()
        for t in ths:
            t.join()

# def write_sh_src(arr,conp):


#     i=0
#     j=len(arr)
#     for w in arr:
#         try:
#             w_sh_src(w,conp)
#             i+=1
#             if i%100==0:
#                 print("插入%d条，共%d条"%(i,j))
#         except:
#             traceback.print_exc()


def write_ss_src(arr,conp):
    i=0
    j=len(arr)
    bg=time.time()
    for w in arr:
        try:
            w_ss_src(w,conp)
            i+=1
            if i%100==0:
                ed=time.time()
                cost=int(ed-bg)
                print("插入%d条，共%d条，耗时%d秒"%(i,j,cost))
                bg=time.time()
        except:
            traceback.print_exc()

def write_alter_src(arr):
    i=0
    j=len(arr)
    for w in arr:
        try:
            w_alter_src(w)
            i+=1
            if i%100==0:
                print("插入%d条，共%d条"%(i,j))
        except:
            traceback.print_exc()




def write_base_est(arr):
    i=0
    j=len(arr)
    for w in arr:
        try:
            w_base_est(w)
            i+=1
            if i%100==0:
                print("插入%d条，共%d条"%(i,j))
        except:
            traceback.print_exc()



def write_alter_est(arr):
    i=0
    j=len(arr)
    bg=time.time()
    for w in arr:

        try:
            w_alter_est(w)
            i+=1
            if i%100==0:
                ed=time.time()
                cost=int(ed-bg)
                print("插入%d条，共%d条，耗时%d秒"%(i,j,cost))
                bg=time.time()
        except:
            traceback.print_exc()



######

def add_t_base_src():
    conp=['postgres','since2015','192.168.4.188','bid','ent']
    df=db_query(sql="""select * from(select distinct(entname)  as name from ent.ent as b 
        where not exists(select 1 from ent.t_base_src as a where a.jgmc=b.entname ) and tag!= -1) as t  
        order by random() """
        ,dbtype="postgresql",conp=conp)

    arr=df['name']
    write_base_src_class(arr,conp).write_base_src()
    #write_base_src(arr,conp)

def add_t_sh_src():
    conp=['postgres','since2015','192.168.4.188','bid','ent']
    df=db_query(sql="""select * from(select distinct(tydm)  as tydm from ent.t_base_est as b where not exists(select 1 from ent.t_sh_src as a where a.tydm=b.tydm and b.tydm is not null)) as t 
        order by random() """
        ,dbtype="postgresql",conp=['postgres','since2015','192.168.4.188','bid','ent'])

    arr=df['tydm']
    write_sh_src_class(arr,conp).write_sh_src()
    #write_sh_src(arr,conp)
#add_t_sh_src()


def add_t_ss_src():
    conp=['postgres','since2015','192.168.4.188','bid','ent']
    sql="""
    SELECT word FROM "ent"."ss" as b where tag!= -1 and not exists(select word from ent.t_ss_src as a where a.word=b.word)
    and not exists(select jgmc from ent.t_base_src as c where c.jgmc=b.word) """
    df=db_query(sql,dbtype="postgresql",conp=conp)
    arr=df['word']
    write_ss_src(arr,conp=conp)



#add_t_sh_src()
