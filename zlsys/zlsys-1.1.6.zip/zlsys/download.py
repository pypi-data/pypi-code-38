import hashlib
import base64
from Crypto.Cipher import AES
import zipfile
import sys 
import os 
import requests
import wget 
import shutil
import pandas as pd 

from sqlalchemy.dialects.postgresql import BIGINT,TEXT

from lmf.dbv2 import db_write
import requests 
import re
def get_file_url(shi,jtype,date):
    #jtype='政府采购' or '工程建设'
    date=date.replace('-','')

    if jtype=='zfcg':
        jtype='政府采购'
    else:
        jtype='工程建设'
    txt="GG_%s_%s_%s"%(date,jtype,shi)
    #print(txt)

    txt=hashlib.md5(txt.encode('utf8')).hexdigest()
    #print(txt)


    txt='-'.join([txt[:8],txt[8:12],txt[12:16],txt[16:20],txt[20:]])

    address_url_dict={
        "昆明市":"https://gcjs.kmggzy.com/Common/Framework/FileDownLoad.aspx?PhysicalFilePath=Vit8DroijPVZPyajXU0x08TGzZAkFf9sDjuoXXOoNgo%3d&NewFileName=$$$$$.zip",

        "深圳市":"https://www.szjsjy.com.cn:8001/file/downloadFile?fileId=$$$$$",

        "腾冲市":"http://gcjs.tcsggzyjyw.com/Common/Framework/FileDownLoad.aspx?PhysicalFilePath=%2bfaw0%2fmO%2bhw3jcFUnGJjduz1VYknp5T6dl2zyD%2fVOlY%3d&NewFileName=$$$$$.zip",

        "宜宾市":"http://xjy.yibin.gov.cn/Common/Framework/FileDownLoad.aspx?PhysicalFilePath=%2bHH6mFhYUeYKshNaq6wCFNtubwHNZgE9&OldFileName=&NewFileName=$$$$$.zip",

        "大理州":{"政府采购":"http://www.dlggzy.cn/zfcg-file/downloadFile?fileId=$$$$$",
               "工程建设":"http://www.dlggzy.cn/jsgc-file/downloadFile?fileId=$$$$$"},

        "临沧市":{"政府采购":"http://60.161.139.102/zfcg-file/downloadFile?fileId=$$$$$",
               "工程建设":"http://60.161.139.102/jsgc-file/downloadFile?fileId=$$$$$"},

        "怒江州":{"政府采购":"http://182.246.203.127:8001/zfcg-file/downloadFile?fileId=$$$$$",
               "工程建设":"http://182.246.203.127:8001/jsgc-file/downloadFile?fileId=$$$$$"},

        "曲靖市":{"政府采购":"http://jyxt.qjggzyxx.gov.cn/zfcg-file/downloadFile?fileId=$$$$$",
               "工程建设":"http://jyxt.qjggzyxx.gov.cn/jsgc-file/downloadFile?fileId=$$$$$"},

        "文山州":{"政府采购":"http://wsggzy.cn/zfcg-file/downloadFile?fileId=$$$$$",
               "工程建设":"http://wsggzy.cn/jsgc-file/downloadFile?fileId=$$$$$"},

        "玉溪市":{"政府采购":"http://60.160.190.130:8001/jsgc-file/downloadFile?fileId=$$$$$",
               "工程建设":"http://60.160.190.130:8001/jsgc-file/downloadFile?fileId=$$$$$"},

        "红河州":{"政府采购":"http://www.hhzy.net/zfcg-file/downloadFile?fileId=$$$$$",
               "工程建设":"http://www.hhzy.net/jsgc-file/downloadFile?fileId=$$$$$"},

        "西双版纳州":{"政府采购":"http://www.xsbnggzyjyxx.com/zfcg-file/downloadFile?fileId=$$$$$",
                 "工程建设":"http://www.xsbnggzyjyxx.com/jsgc-file/downloadFile?fileId=$$$$$"},

        "昭通市":{"政府采购":"http://ztggzyjy.zt.gov.cn/zfcg-file/downloadFile?fileId=$$$$$",
               "工程建设":"http://ztggzyjy.zt.gov.cn/jsgc-file/downloadFile?fileId=$$$$$"},

        "楚雄州":{"政府采购":"http://www.cxggzy.cn/zfcg-file/downloadFile?fileId=$$$$$",
               "工程建设":"http://www.cxggzy.cn/jsgc-file/downloadFile?fileId=$$$$$"},

        "德宏州":{"政府采购":"https://jyzx.dh.gov.cn/zfcg-file/downloadFile?fileId=$$$$$",
               "工程建设":"https://jyzx.dh.gov.cn/jsgc-file/downloadFile?fileId=$$$$$"},

        "迪庆州":{"政府采购":"http://183.224.249.60:8001/zfcg-file/downloadFile?fileId=$$$$$",
               "工程建设":"http://183.224.249.60:8001/jsgc-file/downloadFile?fileId=$$$$$"},

        "普洱市":{"政府采购":"http://www.pesggzyjyxxw.com/zfcg-file/downloadFile?fileId=$$$$$",
               "工程建设":"http://www.pesggzyjyxxw.com/jsgc-file/downloadFile?fileId=$$$$$"},

        "保山市":{"政府采购":"http://www.bszwzx.gov.cn/zfcg-file/downloadFile?fileId=$$$$$",
               "工程建设":"http://www.bszwzx.gov.cn/jsgc-file/downloadFile?fileId=$$$$$"},

        "丽江市":{"政府采购":"https://www.ljggzyxx.cn/zfcg-file/downloadFile?fileId=$$$$$",
               "工程建设":"https://www.ljggzyxx.cn/jsgc-file/downloadFile?fileId=$$$$$"},

        "云南省":{"政府采购":"https://www.ynggzy.com/zfcg-file/downloadFile?fileId=$$$$$",
               "工程建设":"https://www.ynggzy.com/jsgc-file/downloadFile?fileId=$$$$$"},

        "遂宁市":"http://jyzx.suining.gov.cn/gcjs/Common/Framework/FileDownLoad.aspx?PhysicalFilePath=2pkK8YuRDyEJJ4Ij6Xwxsw%3d%3d&OldFileName=&NewFileName=$$$$$.zip",

        "雅安市":"http://www.yaggzy.org.cn/gcjs/Common/Framework/FileDownLoad.aspx?PhysicalFilePath=mwTkTLqwpoyPIshveOZc8B%2fOd8bsMbM3&OldFileName=&NewFileName=$$$$$.zip"


    }

    url=address_url_dict[shi]
    if isinstance(url,dict):
        url=url[jtype]
    
    url=url.replace('$$$$$',txt)

    # print(url)
    return  url

# get_file_url('临沧市','zfcg','20190622')

def jiemi(content):
    length=16
    count=len(content)
    if count < length:
        add = (length - count)
        # \0 backspace
        # text = text + ('\0' * add)
        content = content + ('\0' * add).encode('utf-8')
    elif count > length:
        add = (length - (count % length))
        # text = text + ('\0' * add)
        content = content + ('\0' * add).encode('utf-8')
    key="BXCPSJCJBXCPSJCJ".encode('utf-8')
    iv="BiaoXunChanPinSJ".encode()

    aes = AES.new(key, AES.MODE_CBC, iv) 
    content=aes.decrypt(content)
    return content 


def jiemi_file(path1,path2):
    #path1=sys.path[0]+"\\7fa90751-6123-f743-4e0d-b5af1f961081.zbj"

    #path2=sys.path[0]+"\\w3.zip"

    with open(path1,'rb') as f:
        content=f.read()
        #u = s.decode("utf-8-sig")
        #s = u.encode("utf-8")
    with  open(path2,'wb') as f:
         content1=jiemi(content)
         f.write(content1)

def unzip_file(zip_src, dst_dir):
    r = zipfile.is_zipfile(zip_src)
    if r:     
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)       
    else:
        print('This is not zip')


def down_file(url,file_src):

    headers={

        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    }
    print('开始下载文件 %s'%file_src)
    res=requests.get(url,stream=True,headers=headers,verify=False,timeout=40)
    count=0
    with open(file_src, 'wb') as fd:
        for chunk in res.iter_content(chunk_size=1024):
            if chunk:
                fd.write(chunk)

                count +=1
                if count % 10240 == 0:
                    print('下载 %s MB'%(count//1024))

    print('下载完成,共下载 %.2f MB'%(count/1024))
    return True


def getfile(shi,jytype,date):
    address_dict={"昆明市":"kunming","深圳市":"shenzhen","腾冲市":"tengchong",
                  "宜宾市":"yibin","大理州":"dali","临沧市":"lincang",
                  "怒江州":"nujiang","曲靖市":"qujing","文山州":"wenshan",
                  "玉溪市":"yuxi","红河州":"honghe","西双版纳州":"xishuangbanna",
                  "昭通市":"zhaotong","楚雄州":"chuxiong","德宏州":"dehong","迪庆州":"diqing",
                  "普洱市":"puer","保山市":"baoshan","遂宁市":"suining","云南省":"yunnan",
                  "丽江市":"lijiang","雅安市":"yaanshi"
                  }


    shi1='_'.join([address_dict[shi],jytype])


    url=get_file_url(shi,jytype,date)


    tmpdir="/bsttmp"
    dir1="/bsttmp/%s"%shi1
    name="%s.zip"%shi1
    name1="%s_jiemi.zip"%shi1

    if os.path.exists(dir1):
        shutil.rmtree(dir1)
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)
    if not os.path.exists(dir1):
        os.mkdir(dir1)

    file_path='%s/%s'%(dir1,name)
    file_path1='%s/%s'%(dir1,name1)
    file_path2="%s/file"%dir1

    if  os.path.exists(file_path):
        os.remove(file_path)

    # wget.download(url,file_path)
    down_file(url,file_path)

    jiemi_file(file_path,file_path1)

    unzip_file(file_path1,file_path2)
    return file_path2,shi1





def write_html(path,conp,tbname):
    # path="D:\\bsttmp\\kuming_gcjs\\file"
    # conp=["postgres",'since2015','192.168.4.188','base','cdc']
    # tbname="cdc_html"
    arr=os.listdir(path)
    data=[]
    count=1
    for w in arr:
            if w.endswith('html'):
                with open(os.path.join(path,w),'r',encoding='utf8') as f:
                    content=f.read()
                    tmp=[w[:-5],content]
                    data.append(tmp)
            if count==1:

                df=pd.DataFrame(data=data,columns=['guid','page'])
                datadict={"guid":TEXT(),'page':TEXT()}
                db_write(df,tbname,dbtype='postgresql',conp=conp,if_exists='replace',datadict=datadict)
                data=[]
            elif count%1000==0:
                df=pd.DataFrame(data=data,columns=['guid','page'])
                datadict={"guid":TEXT(),'page':TEXT()}
                db_write(df,tbname,dbtype='postgresql',conp=conp,if_exists='append',datadict=datadict)
                data=[]
                print("写入1000")
            count+=1
    df=pd.DataFrame(data=data,columns=['guid','page'])
    datadict={"guid":TEXT(),'page':TEXT()}
    db_write(df,tbname,dbtype='postgresql',conp=conp,if_exists='append',datadict=datadict)


def write_gg(path,conp,tbname,jytype=None):
    if jytype=='gcjs':jytype="工程建设"
    if jytype=='zfcg':jytype="政府采购"
    # path="D:\\bsttmp\\kuming_gcjs\\file"
    # conp=["postgres",'since2015','192.168.4.188','base','cdc']
    # tbname="cdc_gg"
    arr=os.listdir(path)
    for w in arr:
        if w.endswith('csv'):
            #print(w)
            csv=w 
            break

    dfs=pd.read_csv(os.path.join(path,csv),sep='\001',quotechar='\002',chunksize=1000)

    count=1

    for df in dfs:
        df.columns=['bd_guid','bd_bh','bd_name','zbr','zbdl','xmjl','xmjl_dj','xmjl_zsbh','bm_endtime','bm_endtime_src','tb_endtime','tb_endtime_src'
            ,'bzj_time','bzj_time_src','kb_time','kb_time_src','pb_time','pb_time_src','db_time','db_time_src','pb_time','pb_time_src','zhongbiao_hxr','zhongbiao_hxr_src','kzj'
            ,'kzj_src','zhongbiaojia','zhongbiaojia_src','bd_dizhi','diqu','ggtype','gg_name','gg_fabutime','gg_file','gg_fujian_file','gg_href'
            ]
        df['jytype']=jytype
        datadict={ w:TEXT() for w in df.columns}
        
        if count==1:
            db_write(df,tbname,dbtype='postgresql',conp=conp,datadict=datadict)
        else:
            db_write(df,tbname,dbtype='postgresql',conp=conp,if_exists='append',datadict=datadict)
            print("写入第%d "%count)
        count+=1


def write_all(path,conp,prefix,jytype=None):
    tbname1=prefix+'_html_cdc'
    tbname2=prefix+'_gg_cdc'
    write_html(path,conp,tbname1)
    write_gg(path,conp,tbname2,jytype)


# path="D:\\bsttmp\\kuming_gcjs\\file"
# conp=["postgres",'since2015','192.168.4.188','base','cdc']
# prefix="kunming_gcjs"
# write_all(path,conp,prefix)



def update(shi,jytype,date,conp):
    path,prefix=getfile(shi,jytype,date)
    print("%s 文件下载完毕！"%path)
    if jytype=='gcjs':jytype="工程建设"
    if jytype=='zfcg':jytype="政府采购"
    write_all(path,conp,prefix,jytype)

#update("宜宾市","gcjs",'2019-06-24',["postgres",'since2015','192.168.4.175','zlsys','sichuan_yibinshi'])
#update("遂宁市","zfcg",'2019-06-26',["postgres",'since2015','192.168.4.175','zlsys','sichuan_suiningshi'])

# path="D:\\bsttmp\\昆明工程建设存量"

# conp=["postgres",'since2015','192.168.4.188','base','cdc']

# tb1="kunming_gcjs_html"
# tb2="kunming_gcjs_gg"
# write_html(path,conp,tb1)
# write_gg(path,conp,tb2)
#update("腾冲市","zfcg",'2019-05-30',["postgres",'since2015','192.168.4.188','base','cdc'])
#update("腾冲市","gcjs",'2019-05-30',["postgres",'since2015','192.168.4.174','biaost','cdc'])


# path="C:\\Users\\Administrator\\Downloads\\6d7f2a3f-1231-6334-0aae-ca8c3c9c28d9.zip"


# jiemi_file(path,'/bsttmp/test')


# path="D:\\bsttmp\\昆明工程建设存量"
# conp=["postgres",'since2015','192.168.4.175','zlsys','yunnan_kunming']
# tbname="gg"
# write_gg(path,conp,tbname)
# tbname="gg_html"

# write_html(path,conp,tbname)