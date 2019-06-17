# coding: utf-8
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import traceback

class email():
    def __init__(self,neirong,geshi_plain_or_html,png_name_s,shoujianren):
        if png_name_s!="":
            try:
                sender = 'ceshi@vdongchina.com'#发邮件地址
                receiver = shoujianren#收邮件地址
                # receiver="chenjunya@vdongchina.com"
                subject = '出现Bug'#标题
                smtpserver = 'smtp.163.com'#服务器
                username = 'ceshi@vdongchina.com'#登录用户名
                password = 'Vd1234567'#授权代码，或者登录密码
                msg=MIMEMultipart()
                msg.attach(MIMEText(neirong, geshi_plain_or_html, 'utf-8'))  # 中文需参数‘utf-8'，单字节字符不需要，邮件正文
                msg['Subject'] = Header(subject, 'utf-8') #调用标题
                msg['From'] = 'ceshi@vdongchina.com'#发件人地址
                msg['To'] = ",".join( receiver)#收件人地址
                att1 = MIMEText(open(png_name_s, 'rb').read(), 'base64', 'utf-8')
                att1["Content-Type"] = 'application/octet-stream'
                # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
                att1["Content-Disposition"] = 'attachment; filename=erroe.png'
                msg.attach(att1)
                smtp = smtplib.SMTP()
                smtp.connect('smtp.exmail.qq.com')#服务器
                smtp.login(username, password)#执行登录
                smtp.sendmail(sender, receiver, msg.as_string())#执行发邮件，发件人，收件人，内容+内容
                smtp.quit()#关闭邮箱链接
            except Exception as e:
                ee=traceback.format_exc()
                print(ee)
        if png_name_s=="":
            try:
                sender = 'ceshi@vdongchina.com'  # 发邮件地址
                receiver = shoujianren  # 收邮件地址
                # receiver = ["chenjunya@vdongchina.com","mengwenhao@vdongchina.com"]  # 收邮件地址
                subject = '出现Bug'  # 标题
                smtpserver = 'smtp.163.com'  # 服务器
                username = 'ceshi@vdongchina.com'  # 登录用户名
                password = 'Vd1234567'  # 授权代码，或者登录密码

                msg=MIMEText(neirong, geshi_plain_or_html, 'utf-8')  # 中文需参数‘utf-8'，单字节字符不需要，邮件正文
                msg['Subject'] = Header(subject, 'utf-8')  # 调用标题
                msg['From'] = 'ceshi@vdongchina.com'  # 发件人地址
                msg['To'] = ",".join( receiver)  # 收件人地址


                smtp = smtplib.SMTP()
                smtp.connect('smtp.exmail.qq.com')  # 服务器
                smtp.login(username, password)  # 执行登录
                smtp.sendmail(sender, receiver, msg.as_string())  # 执行发邮件，发件人，收件人，内容+内容
                smtp.quit()  # 关闭邮箱链接
            except Exception as e:
                ee = traceback.format_exc()
                print(ee)



if __name__ == "__main__":
    youjian=["chenjunya@vdongchina.com"]
    try:
        a="ss"
        int(a)
    except Exception as e:
        email("ssssss:<br>%s"%{e},"html","","chenjunya@vdongchina.com")

