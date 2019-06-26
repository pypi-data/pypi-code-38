import traceback
import logging
import datetime
import smtplib

from algonaut.settings import settings
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText
from email.utils import format_datetime

logger = logging.getLogger(__name__)

def send_email(to, subject, text=None, html=None, config=None):

    logger.info("Sending an e-mail...")

    if config is None:
        config = settings.get('smtp')

    if text is None and html is None:
        raise ValueError("text or html (or both) needs to be defined!")

    sender_name = settings.get('name', '[No-Name]')

    msg = MIMEMultipart('alternative')
    msg['From'] = config['from']
    msg['To'] = to
    msg['Subject'] = Header(subject, 'utf-8')
    msg['Date'] = format_datetime(datetime.datetime.utcnow())

    if text:
        msg.attach(MIMEText(text, 'plain', 'utf-8'))
    if html:
        msg.attach(MIMEText(html, 'html', 'utf-8'))
    
    if settings.get('test'):
        if hasattr(settings, 'test_queue'):
            settings.test_queue.put({'type' : 'email', 'data' : msg})
        return msg

    try:
        if config.get('ssl'):
            smtp = smtplib.SMTP_SSL(config['server'], config['port'])
        else:
            smtp = smtplib.SMTP(config['server'], config['port'])
        smtp.ehlo()
        if config.get('tls'):
            smtp.starttls()
        smtp.ehlo()
        smtp.login(config['username'], config['password'])
        smtp.sendmail(msg['From'],msg['To'],msg.as_string().encode("ascii"))
        smtp.quit()
        logger.info("Successfully sent e-mail.")
    except:
        logger.error("Could not send e-mail:", traceback.format_exc())
