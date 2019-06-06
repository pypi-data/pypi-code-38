import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from configs.Config import SurfingConfig
import click, cli, os

configs = SurfingConfig()

# 防止没设置时出错
email_info = configs.surfing.email if hasattr(configs, "surfing") and hasattr(configs.surfing, "email") else ""
smtpserver = email_info.smtpserver if hasattr(email_info, "smtpserver") else "smtp.exmail.qq.com"
user = email_info.user if hasattr(email_info, "user") else "it_devops@surfingtech.cn"
password = email_info.password if hasattr(email_info, "password") else "it_devops@surfingtech.cn"
sender = email_info.sender if hasattr(email_info, "sender") else "it_devops@surfingtech.cn"
cc = email_info.cc if hasattr(email_info, "cc") else ["surfing_it@surfingtech.cn"]


class SendMailController:

    def __init__(self,
                 smtpserver=smtpserver,
                 user=user,
                 password=password,
                 sender=sender,
                 receivers=[],
                 cc=cc,
                 ):

        # 保证配置文件配置没问题
        assert hasattr(configs, "surfing"), "没有找到配置文件，请核对你的配置文件是否存在，并设置了surfing的key"
        assert hasattr(configs.surfing, "email"), "没有找到配置文件，请核对你的配置文件是否存在，并有邮件配置信息"

        self.smtpserver = smtpserver  # 设置服务器
        self.user = user  # 用户名
        self.password = password  # 密码
        self.sender = sender  # 发件人
        self.receivers = receivers  # 收件人列表
        self.cc = cc  # 抄送人列表

    def send_mail(self, sub, content, sender=None, receivers=None, cc=None, attachment=[]):
        """
        :param str sub:  标题
        :param str content: 邮件正文
        :param str sender: 发邮件人邮箱
        :param list receivers: 接受邮件人列表
        :param list cc: 抄送人列表
        :return None:
        """
        if sender is not None:
            self.sender = sender
        if receivers is not None:
            self.receivers.extend(receivers)
        if cc is not None:
            self.cc.extend(cc)

        assert len(self.receivers) != 0, "收件人不能 None"
        cli.info("开始发送邮件了")

        msg = MIMEMultipart()
        msg['Subject'] = sub
        msg['From'] = self.sender
        msg['To'] = ";".join(self.receivers)
        msg["cc"] = ";".join(self.cc)
        msg.attach(MIMEText(content))

        # 循环附件列表，添加每一个附件
        if len(attachment) > 0:
            for path in attachment:
                assert os.path.exists(path) and os.path.isfile(path), "附件文件不存在或者不是文件"

                file_name = path.split("/")[-1]
                part = MIMEApplication(open(path, 'rb').read())
                part.add_header('Content-Disposition', 'attachment', filename=file_name)
                msg.attach(part)

        s = smtplib.SMTP()
        try:
            s.connect(self.smtpserver)  # 连接smtp服务器
            s.login(self.user, self.password)  # 登陆服务器
            s.sendmail(self.sender, self.receivers + self.cc, msg.as_string())  # 发送邮件

            cli.info("邮件发送成功")
            return True

        except Exception as e:
            cli.warning("邮件发送失败")
            print(e)
            print(self)
            return False
        finally:
            s.close()

    def send_mail_with_attachment(self, sub, content, sender=None, receivers=None, cc=None, attachment=[]):
        """
            send_mail 的包装
        :param str sub:  标题
        :param str content: 邮件正文
        :param str sender: 发邮件人邮箱
        :param list receivers: 接受邮件人列表
        :param list cc: 抄送人列表
        :param list attachment: 附件文件列表
        :return None:
        """
        self.send_mail(sub, content, sender=sender, receivers=receivers, cc=cc, attachment=attachment)

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(self)


if __name__ == '__main__':
    pass
    controller = SendMailController()
    print(controller)
    controller.send_mail("测试邮件标题", "这是一封测试邮件", receivers=['babbage@surfingtech.cn'])
    # print(hasattr(configs.surfing, "email"))
