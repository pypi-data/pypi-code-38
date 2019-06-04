from typing import List

from abc import ABCMeta, abstractmethod


class EmailApiABC(metaclass=ABCMeta):
    @abstractmethod
    def sendSms(self, mobile: str, contents: str) -> None:
        """ Send SMS

        Send an SMS to a mobile phone.
        
        :param mobile: The addresses to send the email to.
        :param contents: The contents of the email.

        """

    @abstractmethod
    def sendEmail(self, addresses: List[str], subject: str, contents: str,
                  isHtml: bool) -> None:
        """ Send Email

        Send an email.

        :param addresses: The addresses to send the email to.
        :param subject: The subject of the email
        :param contents: The contents of the email.
        :param isHtml: Is the email contents HTML

        """

