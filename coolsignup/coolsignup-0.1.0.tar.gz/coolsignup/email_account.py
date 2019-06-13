from smtplib import SMTP

class EmailAccount(object):
    def __init__(self, email, smtp_server, username, password,
     port = 587, sender_name = None):
        self.email = email
        self.smtp_server = smtp_server
        self.username = username
        self.password = password
        self.port = port
        self.sender_name = sender_name or email

    def send_email(self, email, to):
        with SMTP(self.smtp_server, port = self.port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(self.username, self.password)
            smtp.sendmail(self.email, to, email.as_string())
