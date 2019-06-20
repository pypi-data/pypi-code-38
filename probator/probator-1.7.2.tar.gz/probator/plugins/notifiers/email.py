"""Email based notification system"""
import re
import smtplib
import uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from probator import get_local_aws_session
from probator.config import dbconfig
from probator.constants import RGX_EMAIL_VALIDATION_PATTERN, ConfigOption
from probator.database import db
from probator.exceptions import EmailSendError
from probator.plugins.notifiers import BaseNotifier
from probator.schema import Email


class EmailNotifier(BaseNotifier):
    name = 'Email Notifier'
    ns = 'notifier_email'
    notifier_type = 'email'
    validation = RGX_EMAIL_VALIDATION_PATTERN
    options = (
        ConfigOption('enabled', True, 'bool', 'Enable the Email notifier plugin'),
        ConfigOption('from_address', 'changeme@domain.tld', 'string', 'Sender address for emails'),
        ConfigOption('method', 'ses', 'string', 'EMail sending method, either ses or smtp'),
        ConfigOption('from_arn', '', 'string', 'If using cross-account SES, this is the "From ARN", otherwise leave blank'),
        ConfigOption('return_path_arn', '', 'string', 'If using cross-account SES, this is the "Return Path ARN", otherwise leave blank'),
        ConfigOption('source_arn', '', 'string', 'If using cross-account SES, this is the "Source ARN", otherwise leave blank'),
        ConfigOption('ses_region', 'us-west-2', 'string', 'Which SES region to send emails from'),
        ConfigOption('smtp_server', 'localhost', 'string', 'Address of the SMTP server to use'),
        ConfigOption('smtp_port', 25, 'int', 'Port for the SMTP server'),
        ConfigOption('smtp_username', '', 'string', 'Username for SMTP authentication. Leave blank for no authentication'),
        ConfigOption('smtp_password', '', 'string', 'Password for SMTP authentication. Leave blank for no authentication'),
        ConfigOption('smtp_tls', False, 'bool', 'Use TLS for sending emails'),
    )

    def __init__(self):
        super().__init__()
        self.sender = self.dbconfig.get('from_address', self.ns)

    def notify(self, subsystem, recipient, subject, body_html, body_text):
        """Method to send a notification

        A plugin may use only part of the information, but all fields are required.

        Args:
            subsystem (`str`): Name of the subsystem originating the notification
            recipient (`str`): Recipient email address
            subject (`str`): Subject / title of the notification
            body_html (`str`): HTML formatted version of the message
            body_text (`str`): Text formatted version of the message

        Returns:
            `None`
        """
        if not re.match(RGX_EMAIL_VALIDATION_PATTERN, recipient, re.I):
            raise ValueError('Invalid recipient provided')

        email = Email()
        email.timestamp = datetime.now()
        email.subsystem = subsystem
        email.sender = self.sender
        email.recipients = recipient
        email.subject = subject
        email.uuid = uuid.uuid4()
        email.message_html = body_html
        email.message_text = body_text

        method = dbconfig.get('method', self.ns, 'ses')
        try:
            if method == 'ses':
                self.__send_ses_email([recipient], subject, body_html, body_text)

            elif method == 'smtp':
                self.__send_smtp_email([recipient], subject, body_html, body_text)

            else:
                raise ValueError(f'Invalid email method: {method}')

            db.session.add(email)
            db.session.commit()
        except Exception as ex:
            raise EmailSendError(ex)

    def __send_ses_email(self, recipients, subject, body_html, body_text):
        """Send an email using SES

        Args:
            recipients (`1ist` of `str`): List of recipient email addresses
            subject (str): Subject of the email
            body_html (str): HTML body of the email
            body_text (str): Text body of the email

        Returns:
            `None`
        """
        source_arn = dbconfig.get('source_arn', self.ns)
        return_arn = dbconfig.get('return_path_arn', self.ns)

        session = get_local_aws_session()
        ses = session.client('ses', region_name=dbconfig.get('ses_region', self.ns, 'us-west-2'))

        body = {}
        if body_html:
            body['Html'] = {
                'Data': body_html
            }
        if body_text:
            body['Text'] = {
                'Data': body_text
            }

        ses_options = {
            'Source': self.sender,
            'Destination': {
                'ToAddresses': recipients
            },
            'Message': {
                'Subject': {
                    'Data': subject
                },
                'Body': body
            }
        }

        # Set SES options if needed
        if source_arn and return_arn:
            ses_options.update({
                'SourceArn': source_arn,
                'ReturnPathArn': return_arn
            })

        ses.send_email(**ses_options)

    def __send_smtp_email(self, recipients, subject, html_body, text_body):
        """Send an email using SMTP

        Args:
            recipients (`list` of `str`): List of recipient email addresses
            subject (str): Subject of the email
            html_body (str): HTML body of the email
            text_body (str): Text body of the email

        Returns:
            `None`
        """
        smtp = smtplib.SMTP(
            dbconfig.get('smtp_server', self.ns, 'localhost'),
            dbconfig.get('smtp_port', self.ns, 25)
        )
        source_arn = dbconfig.get('source_arn', self.ns)
        return_arn = dbconfig.get('return_path_arn', self.ns)
        from_arn = dbconfig.get('from_arn', self.ns)
        msg = MIMEMultipart('alternative')

        # Set SES options if needed
        if source_arn and from_arn and return_arn:
            msg['X-SES-SOURCE-ARN'] = source_arn
            msg['X-SES-FROM-ARN'] = from_arn
            msg['X-SES-RETURN-PATH-ARN'] = return_arn

        msg['Subject'] = subject
        msg['To'] = ','.join(recipients)
        msg['From'] = self.sender

        # Check body types to avoid exceptions
        if html_body:
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
        if text_body:
            text_part = MIMEText(text_body, 'plain')
            msg.attach(text_part)

        # TLS if needed
        if dbconfig.get('smtp_tls', self.ns, False):
            smtp.starttls()

        # Login if needed
        username = dbconfig.get('smtp_username', self.ns)
        password = dbconfig.get('smtp_password', self.ns)
        if username and password:
            smtp.login(username, password)

        smtp.sendmail(self.sender, recipients, msg.as_string())
        smtp.quit()
