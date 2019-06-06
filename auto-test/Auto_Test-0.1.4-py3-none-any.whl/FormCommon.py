import random
import time, datetime,os,requests

def getRandomPhone():
    a = ''.join(random.sample('0123456789', 8))
    b = '138' + a
    return b

def getRandomName():
    a = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz',5)) # join()方法用于将序列中的元素以指定的字符连接生成一个新的字符串
    b = '测试' + a
    return b

#各个时间
def getTime(day,hour):
    time1 = (datetime.datetime.now() + datetime.timedelta(days=day, hours=hour)).strftime("%Y-%m-%d %H:00:00")
    return time1

def getTime2(day,hour):
    time2 = (datetime.datetime.now() + datetime.timedelta(days=day, hours=hour)).strftime("%Y-%m-%d %H:%M:00")
    return time2

#获取当前日期
def getDate(day):
    time3 = (datetime.date.today() + datetime.timedelta(days=day)).strftime("%Y-%m-%d")
    return time3

def getDate2(day):
    time4=datetime.date.today() + datetime.timedelta(days=day)
    return time4

Right_List = ['"error":0','"code":"0x000000"','"message":"SUCCESS"','"code":0']
def jsonAssert(json_):
    for element in Right_List:
        if element in str(json_).replace("\'","\"").replace(" ",""):
            return True
    return False


def jsonAssert2(response):
    json_= response.text
    for element in Right_List:
        if element in str(json_).replace("\'","\"").replace(" ",""):
            return True
    return False
#token(ifwzx:服务中心客服，ifwzx2：服务中心销售经理，ixs：销售工作台，ixs1：销售工作台嵌服务中心，ifwzx3：服务中心教务)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


def mail(file,filename):
    mail_user=""    #发送邮件的邮箱
    mail_pass=""   #口令
    mailto_list=['',]  #接收邮件的邮箱
    mail_host="smtp.hfjy.com"  #设置服务器

    msg = MIMEMultipart()
    msg['Subject'] = "[测试报告]" #主题
    msg['From'] = mail_user
    #文字部分
    strstr="测试报告"  #文字内容
    att = MIMEText(strstr,'plain','utf-8')
    msg.attach(att)
    #附件
    att = MIMEApplication(open(file,'rb').read())  #要发送的附件地址
    att.add_header('Content-Disposition', 'attachment', filename=filename) #filename可随意取名
    msg.attach(att)

    server = smtplib.SMTP()
    server.connect(mail_host)   #连接smtp邮件服务器
    server.login(mail_user,mail_pass)   #登录
    server.sendmail(mail_user, mailto_list, msg.as_string())    #发送
    server.close()  #关闭

def get_week_day(date):
    week_day_dict = {
        0:'1',
        1:'2',
        2:'3',
        3:'4',
        4:'5',
        5:'6',
        6:'7',
    }
    day = date.weekday()
    return week_day_dict[day]

def findCase(file_dir):
    case_file = {}
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == '.csv':
                file2=file.split(".csv")[0]
                case_file[file2]=(os.path.join(root, file2))
    return case_file


detail_dict=[]
def getdetail(cases,single_response_time):
    for index,caseName in cases.items():
        solo_item = {
                    "caseName": caseName,
                    "time": single_response_time,
                    "result": 1,
                    "detail": "错误信息"
                }
        detail_dict.append(solo_item)
    return detail_dict

def upload(cases,start_time,single_response_time):
    header = {"Access-Token": "hM3pyPK9Qpq0T_MmopomeQ", "Content-Type": "application/json"}
    details = getdetail(cases,single_response_time)
    body = {
        "group": "G-CRM-PLAN",
        "module": "case_file_name",
        "relatedVersion": "0.1.1",
        "startTime": start_time,
        "reportUrl": "",
        "details": details}
    r = requests.request('POST', '', body=body, header=header)
    print(body)
    print("上传报告结果：" + r.json())


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)



