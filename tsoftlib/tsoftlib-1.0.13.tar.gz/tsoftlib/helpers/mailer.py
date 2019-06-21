import smtplib
import os
from os.path import basename
from email import encoders
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

class Mail(object):
    # Options Recievers[list] | Subject[str] | Message[str] | ContentPath[str]
    def __init__(self, creds, options):
        self.options = options
        self.sender = creds['mail']
        self.pw = creds['pw']
        self.server_name = creds['host']
        self.port = creds['port']
    
    def send_mail(self):
        try:
            mail = self.initMail()
            server = smtplib.SMTP(self.server_name, self.port)
            server.connect(self.server_name, self.port)
            
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.sender, self.pw)

            server.sendmail(self.sender, self.options['Recievers'], mail.as_string())
            
        except Exception as err:
            print("Mail Error")
            print(err)
        # finally:
            # server.close()

    def initMail(self):
        mail = MIMEMultipart()

        mail['From'] = self.sender
        mail['To'] = COMMASPACE.join(self.options['Recievers'])
        mail['Date'] = formatdate(localtime=True)
        mail['Subject'] = self.options['Subject']

        contentPath = self.options['ContentPath']

        msg = MIMEText(self.options['Message'])        
        msg.replace_header("Content-Type", "text/html;charset=utf-8")
        
        if contentPath is not None:
            with open(contentPath, 'rb') as file:
                part = MIMEBase('applictaion', 'octet-stream')

                part.set_payload(file.read())
                filename = os.path.basename(contentPath)

                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment',filename=filename)

                mail.attach(part)
                file.close()

        mail.attach(msg)

        return mail


# Mail
def mail(creds, recipents, subject, body, contentPath=None):
    m = Mail(creds, options = {
        'Recievers' : recipents,
        'Subject': subject,
        'Message': body,
        'ContentPath': contentPath
    })

    m.send_mail()

