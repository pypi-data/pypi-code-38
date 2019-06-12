# -*- coding: utf-8 -*-

import smtplib


# TODO: TEST. THIS MODULE IS ENTIRELY UNTESTED!

class SMTPMailSender(object):

    def __init__(self,
                 server,
                 sender):
        self.server_details = server
        self.sender = sender

    def send(self,
             distribution,
             subject,
             message):

        # Format message
        mail_message = (u"From: {sender}\n"
                        u"To: {distribution}\n"
                        u"Subject: {subject}\n"
                        u"\n"
                        u"{message}"
                        .format(sender=self.sender,
                                distribution=distribution,
                                subject=subject,
                                message=message))
        server = smtplib.SMTP(self.server_details)
        try:
            server.sendmail(self.sender,
                            distribution,
                            mail_message)
        except Exception as e:
            server.quit()  # Server remains open in an exception is raised
            raise Exception(e)

        server.quit()
