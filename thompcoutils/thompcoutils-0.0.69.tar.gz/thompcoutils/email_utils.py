from thompcoutils.config_utils import ConfigManager
from thompcoutils.log_utils import get_logger
import smtplib
import os
from email import encoders
import mimetypes
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
import logging

if os.name == 'nt' or os.name == "posix":
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
else:
    # noinspection PyUnresolvedReferences
    from email.MIMEMultipart import MIMEMultipart
    # noinspection PyUnresolvedReferences
    from email.MIMEText import MIMEText
    # noinspection PyUnresolvedReferences
    from email.MIMEApplication import MIMEApplication


class EmailConfig:
    def __init__(self, cfg_mgr=None, username=None, password=None, from_user=None, smtp=None, port=None,
                 section="email connection"):
        if cfg_mgr is None:
            self.username = username
            self.password = password
            self.from_user = from_user
            self.smtp = smtp
            self.port = port
        else:
            self.username = cfg_mgr.read_entry(section, "username", "myname@google.com")
            self.password = cfg_mgr.read_entry(section, "password", "mySecretPassword")
            self.from_user = cfg_mgr.read_entry(section, "from", "Email Sender")
            self.smtp = cfg_mgr.read_entry(section, "smtp", "smtp.gmail.com")
            self.port = cfg_mgr.read_entry(section, "port", 587)


class EmailSender:
    def __init__(self, email_cfg):
        self.email_connection = email_cfg

    def send(self, to_email, subject, message, attach_files=None):
        logger = get_logger()
        server = None
        try:
            server = smtplib.SMTP(self.email_connection.smtp, self.email_connection.port)
            server.ehlo()
            server.starttls()
            server.login(self.email_connection.username, self.email_connection.password)
            outer_msg = MIMEMultipart('alternative')
            sender = self.email_connection.from_user
            recipients = to_email
            outer_msg['Subject'] = subject
            outer_msg.attach(MIMEText(message, "html"))
            outer_msg['From'] = self.email_connection.from_user
            if isinstance(recipients, list):
                outer_msg['To'] = ", ".join(recipients)
            else:
                outer_msg['To'] = recipients
            if attach_files is not None:
                for filename in attach_files:
                    file_type, encoding = mimetypes.guess_type(filename)
                    if file_type is None or encoding is not None:
                        file_type = 'application/octet-stream'
                    maintype, subtype = file_type.split('/', 1)
                    if maintype == 'text':
                        with open(filename) as fp:
                            msg = MIMEText(fp.read(), _subtype=subtype)
                    elif maintype == 'image':
                        with open(filename, 'rb') as fp:
                            msg = MIMEImage(fp.read(), _subtype=subtype)
                    elif maintype == 'audio':
                        with open(filename, 'rb') as fp:
                            msg = MIMEAudio(fp.read(), _subtype=subtype)
                    else:
                        with open(filename, 'rb') as fp:
                            msg = MIMEBase(maintype, subtype)
                            msg.set_payload(fp.read())
                        encoders.encode_base64(msg)
                    msg.add_header('Content-Disposition', 'attachment', filename=filename)
                    outer_msg.attach(msg)
            server.sendmail(sender, recipients, outer_msg.as_string())
            logger.debug("Successfully sent mail to " + str(recipients))
        except Exception as e:
            logger.warning("Failed to send mail to {} because {}".format(to_email, str(e)))
        finally:
            if server is not None:
                server.quit()


def main():
    create_file = False
    # use parameters
    mail_from_parms = EmailSender(EmailConfig(username="my email",
                                              password="my password",
                                              from_user="Test Utils",
                                              smtp="smtp.gmail.com",
                                              port=587))
    # use config
    temp_filename = "testing EmailCfg only.cfg"
    if create_file:
        if os.path.isfile(temp_filename):
            os.remove(temp_filename)
    cfg_mgr = ConfigManager(temp_filename, create=create_file)
    if create_file:
        EmailConfig(cfg_mgr=cfg_mgr)
        cfg_mgr.write(temp_filename)
        raise Exception("Should never get here!")
    email_cfg = EmailConfig(cfg_mgr)
    mail_from_cfg = EmailSender(email_cfg)

    mail_from_parms.send(to_email="Jordan@ThompCo.com", subject="this is a test from emailSender",
                         message="Here is the message using parameters passed in with an attached file",
                         attach_files=[os.path.basename(__file__)])
    mail_from_parms.send(to_email="Jordan@ThompCo.com", subject="this is a test from emailSender",
                         message="Here is the message using parameters passed in")
    mail_from_cfg.send(to_email="Jordan@ThompCo.com", subject="this is a test from emailSender",
                       message="Here is the message using values from a configuration file with an attached file",
                       attach_files=[os.path.basename(__file__)])
    mail_from_cfg.send(to_email="Jordan@ThompCo.com", subject="this is a test from emailSender",
                       message="Here is the message using values from a configuration file")


if __name__ == "__main__":
    main()
