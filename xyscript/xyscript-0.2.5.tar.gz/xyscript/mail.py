#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
from email.mime.image import MIMEImage 
from email.header import Header
from email.utils import parseaddr,formataddr
import xyscript.globalvar as gv

mail_host = "smtp.163.com"  # 设置服务器
mail_user = "idouko@163.com"  # 用户名
mail_pass = "XYCoder02"  # 三方邮箱口令
sender = 'idouko@163.com'# 发送者邮箱
receivers = ['m18221031340@163.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

class Email():
    def __init__(self,receiver):
        global receivers
        if len(receiver) > 0:
            receivers = receiver
            # print (receivers)
        # print(receivers)

    def send_package_email(self,success,url=None,image=None):
        #PROJECT_ADDRESS, PROJECT_BRANCH, TEST_PLATFORM, NET_ENV, PROJECT_VERSION, PROJECT_BUILD, NOTIFICATION_EMAILS
        address = gv.get_value("PROJECT_ADDRESS")
        branch = gv.get_value("PROJECT_BRANCH")
        platform = gv.get_value("TEST_PLATFORM")
        env = gv.get_value("NET_ENV")
        version = gv.get_value("PROJECT_VERSION")
        build = gv.get_value("PROJECT_BUILD")
        emails = gv.get_value("NOTIFICATION_EMAILS")

        
        string = ""
        if success:
            string = "您好！\n      项目打包成功，详情如下：\n 项目地址：%s\n打包分支：%s\n打包平台：%s\n打包网络环境：%s\n版本号：%s\n编译号：%s\n" %(address,branch,platform,env,version,build)
        else:
            string = "您好！\n      项目打包失败，请注意查看错误日志！信息如下：\n项目地址：%s\n打包分支：%s\n打包平台：%s\n打包网络环境：%s\n版本号：%s\n编译号：%s\n" %(address,branch,platform,env,version,build)
        # Email(emails).sendemail(string,"此邮件来自自动化打包","iOS项目组",image='/Users/xycoder/Desktop/IOS/国电南自/iosofolddf/数据工厂-老/platforms/ios/www/hongjian/images/0_big.png')


    def sendemail(self, content ,subject, form_name, cc=None ,htmltext=None ,image=None , filepath=None):
        global receivers
        
        subject = subject#邮件来源
        #构建信息体
        message = MIMEMultipart('mixed') 
        
        #下面的主题，发件人，收件人，日期是显示在邮件页面上的。
        message['From'] = formataddr([form_name, sender])
        message['To'] = ";".join(receivers)
        message['Subject'] = Header(subject, 'utf-8')#编码方式
        if cc != None:
            message["Cc"] = cc

        #构造文字内容   
        text = content    
        text_plain = MIMEText(text,'plain', 'utf-8')    
        message.attach(text_plain)    

        if image != None:
            #构造图片链接
            sendimagefile=open(image,'rb').read()
            image = MIMEImage(sendimagefile)
            image.add_header('Content-ID','<image1>')
            image["Content-Disposition"] = 'attachment; filename="testimage.png"'
            message.attach(image)

        if htmltext != None:
            #构造html
            #发送正文中的图片:由于包含未被许可的信息，网易邮箱定义为垃圾邮件，报554 DT:SPM ：<p><img src="cid:image1"></p>
            html = htmltext   
            text_html = MIMEText(html,'html', 'utf-8')
            text_html["Content-Disposition"] = 'attachment; filename="texthtml.html"'   
            message.attach(text_html)    


        if filepath != None:
            #构造附件
            sendfile=open(filepath,'rb').read()
            text_att = MIMEText(sendfile, 'base64', 'utf-8') 
            text_att["Content-Type"] = 'application/octet-stream'  
            #以下附件可以重命名成aaa.txt  
            #text_att["Content-Disposition"] = 'attachment; filename="aaa.txt"'
            #另一种实现方式
            # text_att.add_header('Content-Disposition', 'attachment', filename='aaa.txt')
            #以下中文测试不ok
            #text_att["Content-Disposition"] = u'attachment; filename="中文附件.txt"'.decode('utf-8')
            message.attach(text_att)  

        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, receivers, message.as_string())
            print("邮件发送成功")
        except smtplib.SMTPException as e:
            print("Error: 无法发送邮件" + str(e))

# if __name__ == "__main__":
    # Email([]).send_package_email(False)