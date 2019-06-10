import logging
from threading import Thread

from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives

from orionframework.utils import exceptions, template as templates

logger = logging.getLogger(__name__)


def send_as_template(subject, template, recipient_list, context=None,
                     bcc_list=None, cc_list=None, attachments=None,
                     from_email=None, fail_silently=False, connection=None,
                     async=getattr(settings, "ORION_ASYNC_EMAIL", False),
                     whitelist=getattr(settings, "ORION_WHITELISTED_EMAIL_DOMAINS", None),
                     plain_text=False, reply_to=None):
    message = templates.parse(template, context)

    if template.endswith(".html") and not plain_text:

        return send(subject=subject, message=None, from_email=from_email,
                    bcc_list=bcc_list, cc_list=cc_list, attachments=attachments,
                    recipient_list=recipient_list, html_message=message,
                    fail_silently=fail_silently, connection=connection,
                    async=async, whitelist=whitelist, reply_to=reply_to)

    else:

        return send(subject=subject, message=message, from_email=from_email,
                    bcc_list=bcc_list, cc_list=cc_list, attachments=attachments,
                    recipient_list=recipient_list, html_message=None,
                    fail_silently=fail_silently, connection=connection,
                    async=async, whitelist=whitelist, reply_to=reply_to)


def send(subject, message, recipient_list, html_message=None,
         bcc_list=None, cc_list=None, attachments=None,
         from_email=None, fail_silently=False, connection=None,
         async=getattr(settings, "ORION_ASYNC_EMAIL", False),
         whitelist=getattr(settings, "ORION_WHITELISTED_EMAIL_DOMAINS", None),
         reply_to=None):
    mail = EmailMultiAlternatives(subject=subject, body=message,
                                  from_email=from_email, to=recipient_list, bcc=bcc_list,
                                  connection=connection, attachments=attachments,
                                  cc=cc_list, reply_to=reply_to)

    if whitelist:

        allowed = False

        for domain in whitelist:
            for email in recipient_list:
                if email.endswith(domain):
                    allowed = True
                    break

        if not allowed:
            print("================== EMAIL WHITELIST WARNING ==================")
            print("You're about to send an e-mail to a non-whitelisted domain: " + recipient_list.join(", "))
            print("Here is a JSON document representing the message being sent:")
            print("Subject: " + str(subject))
            print("Message: " + str(message))
            print("HTML Message: " + str(html_message))
            print("=============================================================")

            return

    if html_message:
        mail.attach_alternative(html_message, 'text/html')
        mail.content_subtype = "text/html"

    if async:

        service = getattr(settings, "ORION_EMAIL_SERVICE", None)

        if not service:

            service = EmailService()
            service.setDaemon(True)

            settings.ORION_EMAIL_SERVICE = service

            service.queue(mail)

            service.start()

        else:

            service.queue(mail)

    else:

        try:

            logger.info("Sending message: " + str(mail))

            mail.send()

            logger.info("Message sent")
        except Exception as e:

            logger.exception("Could not send e-mail due:" + exceptions.to_string(e))

            if not fail_silently:
                raise

    return mail


class EmailService(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):

        Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs, verbose=verbose)

        self.messages = []

    def queue(self, message):

        self.messages.append(message)

    def run(self):

        Thread.run(self)

        while len(self.messages) > 0:

            message = self.messages.pop()

            try:

                logger.info("Sending message: " + str(message))

                message.send()

                logger.info("Message sent")


            except Exception as e:
                logger.exception("Could not send e-mail due:" + exceptions.to_string(e))

        settings.ORION_EMAIL_SERVICE = None
