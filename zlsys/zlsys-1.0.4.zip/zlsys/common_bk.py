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

#exam: http://www.dlggzy.cn/jsgc-file/downloadFile?fileId={GG_20190611_工程建设_大理州}
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
    if shi=='昆明市':
        url="""https://gcjs.kmggzy.com/Common/Framework/FileDownLoad.aspx?PhysicalFilePath=Vit8DroijPVZPyajXU0x08TGzZAkFf9sDjuoXXOoNgo%%3d&NewFileName=%s.zip"""%txt
    elif shi=='深圳市':
        url="https://www.szjsjy.com.cn:8001/file/downloadFile?fileId=%s"%txt
    elif shi=="腾冲市":
        url="http://gcjs.tcsggzyjyw.com/Common/Framework/FileDownLoad.aspx?PhysicalFilePath=%%2bfaw0%%2fmO%%2bhw3jcFUnGJjduz1VYknp5T6dl2zyD%%2fVOlY%%3d&NewFileName=%s.zip"%txt
    elif shi=='宜宾市':
         url="http://xjy.yibin.gov.cn/Common/Framework/FileDownLoad.aspx?PhysicalFilePath=%%2bHH6mFhYUeYKshNaq6wCFNtubwHNZgE9&OldFileName=&NewFileName=%s.zip"%txt
    elif shi=='大理州':
        url="http://www.dlggzy.cn/jsgc-file/downloadFile?fileId=%s"%txt

    return url 


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


def down_file(url,dir):

    headers={

        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    }

    file_name=re.findall('NewFileName=(.+?)$',url)[0]
    file_src=os.path.join(dir,file_name)

    res=requests.get(url,stream=True,headers=headers,verify=False,timeout=40)

    with open(file_src, 'wb') as fd:
        for chunk in res.iter_content(chunk_size=1024):
            if chunk:
                fd.write(chunk)
    return True


def getfile(shi,jytype,date):
    if shi=='昆明市':
        shi1='kuming_%s'%jytype
    elif shi=='深圳市':
        shi1="shenzhen_%s"%jytype
    elif shi=='腾冲市':
        shi1="tengchong_%s"%jytype

    elif shi=='宜宾市':
        shi1="yibin_%s"%jytype
    elif shi=='大理州':
        shi1="dalizhou_%s"%jytype

    url=get_file_url(shi,jytype,date)
    print(url)

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
    wget.download(url,file_path)

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
                with open(path+"\\"+w,'r',encoding='utf8') as f:
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

    dfs=pd.read_csv(path+"\\"+csv,sep='\001',quotechar='\002',chunksize=1000)

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

#update("宜宾市","gcjs",'2019-06-05',["postgres",'since2015','192.168.4.188','bid','zlsys'])

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
update("大理州","gcjs",'2019-06-11',["postgres",'since2015','192.168.4.188','bid','zlsys'])