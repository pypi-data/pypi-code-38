from coolsignup.conf import conf
from coolsignup.email_account import EmailAccount
from coolsignup.url_add_element import url_add_element
from email.mime.text import MIMEText
from email.utils import formatdate
from postpone import evalr, LazyString as _
from tornado.ioloop import IOLoop

def translate(message, lang):
    return evalr(message, conf.translation_func(lang))

class Mailer(object):

    REGISTRATION_CODE_MESSAGE = _(
"""Hello,

please follow this link to confirm your email address and register at {serviceName}:

{url}

See you in a minute!
"""
    )

    RESET_PASSWORD_CODE_MESSAGE = _(
"""Hello,

you asked to reset your password at {serviceName}.
To set a new password, follow this link:

{url}
"""
    )

    CHANGE_EMAIL_CODE_MESSAGE = _(

"""Hello,

you asked to change the email address associated with your account.
Please follow this link to confirm your new email address:

{url}
"""
    )

    def __init__(self):
        self.serviceName = conf.get('serviceName')
        self.emailCodeLink = conf.get('emailCodeLink')
        smtp_params = conf.get('smtp')
        self.email_account = EmailAccount(
            smtp_params['from'],
            smtp_params['smtpServer'],
            smtp_params['username'],
            smtp_params['password'],
            port = smtp_params['port'],
            sender_name = smtp_params.get('senderName')
        )

    def code_email(self, subject, template, code, to, lang = None):
        msg = MIMEText(
            translate(
                template.format(
                    serviceName = self.serviceName,
                    url = url_add_element(self.emailCodeLink, code)
                ),
                lang or 'en'
            )
        )
        msg['From'] = self.email_account.email
        msg['To'] = to
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = '[%s] %s' % (
            self.serviceName,
            translate(subject, lang or 'en')
        )
        return msg

    def send_email(self, email, to):
        IOLoop.current().spawn_callback(
            self.email_account.send_email,
            email,
            to
        )

    def send_registration_code(self, code, to, lang = None):
        self.send_email(
            self.code_email(
                _('Registration'),
                self.REGISTRATION_CODE_MESSAGE,
                code,
                to,
                lang = lang
            ),
            to
        )

    def send_reset_password_code(self, code, to, lang = None):
        self.send_email(
            self.code_email(
                _('Password reset'),
                self.RESET_PASSWORD_CODE_MESSAGE,
                code,
                to,
                lang = lang
            ),
            to
        )

    def send_change_email_code(self, code, to, lang = None):
        self.send_email(
            self.code_email(
                _('Validation of your new email address'),
                self.CHANGE_EMAIL_CODE_MESSAGE,
                code,
                to,
                lang = lang
            ),
            to
        )

mailer = Mailer()
