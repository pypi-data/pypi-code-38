"""
Contains methods for sending emails.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""

import smtplib
import subprocess
import socket
import logging

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(sender, recipients, subject, message_text,
               message_html='', method='sendmail', **kwargs):
    """Sends an email to someone

    :param str sender: Who the email is from
    :param recipients: Who to send the email to
    :type recipients: str or list
    :param str subject: The subject of the email
    :param str message_text: The text version of the message
    :param str message_html: The html version of the message
    :param str method: Method of sending email, based on
                       utilities available. Valid entries are:

                       - 'smtplib': uses the default  stplib.SMTP()
                       - 'sendmail': uses the system ``sendmail`` command

    :param kwargs: Keyword arguments for setting additional values
                   depending on the email method:

                   - 'smtplib': Keyword arguments can be 'host' and 'port'
                   - 'sendmail': No keyword arguments are supported
    """

    msg = MIMEMultipart('alternative')

    msg['Subject'] = subject
    msg['From'] = sender

    if isinstance(recipients, list):
        msg['To'] = ','.join(recipients)
    else:
        msg['To'] = recipients

    msg.attach(MIMEText(message_text, 'plain'))

    if message_html != '':
        msg.attach(MIMEText(message_html, 'html'))

    if method == 'smtplib':
        try:
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', 25)
            smtp_server = smtplib.SMTP(host, port)
            smtp_server.sendmail(sender, recipients, msg.as_string())
            smtp_server.quit()
        except socket.error:
            logging.error('You do not have a valid SMPT server set up.')

    elif method == 'sendmail':
        proc = subprocess.Popen(['sendmail', '-t'], stdin=subprocess.PIPE)
        proc.communicate(input=msg.as_string())

    else:
        logging.error('That is not a valid email method option: method = %s', method)
