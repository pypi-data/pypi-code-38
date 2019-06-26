import logging

from django.core.mail.backends.base import BaseEmailBackend
from django.utils.encoding import force_text

from ievv_opensource.ievv_developemail.models import DevelopEmail


logger = logging.getLogger(__name__)


class DevelopEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        developemails = []
        for email_message in email_messages:
            # message = email_message.message()
            raw_message = email_message.message().as_string()
            developemail = DevelopEmail(
                subject=email_message.subject,
                from_email=email_message.from_email,
                to_emails=', '.join(map(force_text, email_message.to)),
                raw_message=raw_message
            )

            # emailmessage = email.message_from_string(message.message().as_string())
            developemails.append(developemail)

            logger.debug(raw_message)

        DevelopEmail.objects.bulk_create(developemails)
        return len(list(email_messages))
