import smtplib
from email.mime.text import MIMEText
# from config import logger
class Emailsender(object):
    def __init__(self,config):
        #要发给哪些帐号,比如：["466329910@qq.com"]
        self.__tolist=config["tolist"]
        #self.__tolist=[]
        #self.__tolist.append(recipientscfg["tolist"])
        #发送服务器，比如："smtp.139.com"
        self.__host=config["host"]
        #self.__host="smtp.139.com"
        #发送服务器端口号，比如：25或465
        self.__port=config["port"]
        #登录发送服务器的用户名 比如："yukin139"
        self.__user=config["user"]
        #self.__user="yukin139@139.com"
        #登录发送服务器的密码，比如："yukinwtu"
        self.__password=config["password"]
        #self.__password="yukinwtu"
        #邮箱的后缀，比如："139.com"
        self.__postfix=config["postfix"]
        #self.__postfix="139.com"

    def send(self,sub,content):
        #发送者信息
        me=self.__user+"<"+self.__user+"@"+self.__postfix+">"
        # me=self.__user
        #对内容进行编码设定
        msg = MIMEText(content,_charset="utf-8")
        msg["Subject"] = sub
        msg["From"] = me
        msg["To"] = ";".join(self.__tolist)
        s = smtplib.SMTP()
        #s = smtplib.SMTP_SSL()
        try:
            try:
                s.connect(self.__host)
                s.login(self.__user,self.__password)
                s.sendmail(me,self.__tolist,msg.as_string())
                #s.close()
                result=True
            except Exception as e:
                result=False
                print('error:',e)
        finally:
            s.close()
            return result

