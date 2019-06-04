import smtplib
from email.mime.text import MIMEText
from email.header import Header


class SmtpClient(object):

    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def send_text(self, to_addr, subject, text):
        msg = MIMEText(text, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = self.username
        msg['To'] = to_addr
        server = smtplib.SMTP(self.host, 25)
        server.login(self.username, self.password)
        server.sendmail(self.username, [to_addr], msg.as_string())
        server.quit()

if __name__ == "__main__":
    c = SmtpClient("smtp.139.com", "13798106142@139.com", "")
    c.send_text("448075543@qq.com", "test", "hello test!!!")
