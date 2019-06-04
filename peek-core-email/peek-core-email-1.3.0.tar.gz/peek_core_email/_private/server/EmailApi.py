import logging
from typing import List

from peek_core_email._private.server.EmailUtil import SendEmail
from peek_core_email._private.storage import Setting
from peek_core_email._private.storage.Setting import globalSetting
from peek_core_email.server.EmailApiABC import EmailApiABC
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class EmailApi(EmailApiABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    def shutdown(self):
        pass

    @deferToThreadWrapWithLogger(logger)
    def sendSms(self, mobile: str, contents: str) -> None:

        session = self._ormSessionCreator()

        try:

            settings = globalSetting(session)

            if not settings[Setting.EMAIL_ENABLED]:
                logger.debug("SMS sending is disabled, not sending to '%s' for : %s",
                             mobile, contents)
                return

            smsEmailPostfix = settings[Setting.SMS_NUMBER_EMAIL_POSTFIX]

            email = mobile + smsEmailPostfix
            email = email.replace("+", "")

            emailer = SendEmail(self._ormSessionCreator)
            emailer.sendBlocking(
                message=contents,
                subject="",
                recipients=[email],
                html=False
            )

        finally:
            session.close()

    @deferToThreadWrapWithLogger(logger)
    def sendEmail(self, addresses: List[str], subject: str,
                  contents: str, isHtml: bool) -> None:
        session = self._ormSessionCreator()

        try:

            settings = globalSetting(session)

            if not settings[Setting.EMAIL_ENABLED]:
                logger.debug("Email sending is disabled, not sending to '%s' for : %s",
                             addresses, subject)
                return

            emailer = SendEmail(self._ormSessionCreator)

            emailer.sendBlocking(
                message=contents,
                subject=subject,
                recipients=addresses,
                html=isHtml
            )

        finally:
            session.close()
