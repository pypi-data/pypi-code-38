# -*- coding: utf-8 -*-


class UndeliveredMail(Exception):
    """
    A custom class for undelivered emails
    """
    pass


class MailAlreadySent(Exception):
    """
    A custom class for mail that were already sent
    """
    pass
