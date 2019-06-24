# encoding: utf-8
import logging
import time
import traceback

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger("tools")


_subject = u"{} Method Failed"
_body = u"""
args: {}
kwargs: {}
{}
"""


def _sendMail(mail, func, args, kwargs):
    if not mail:
        return
    mailConfig = isinstance(mail, dict) and mail or {}
    subject = _subject.format(func)
    subject = mailConfig.get("subject", _subject).format(func)
    body = mailConfig.get("body", _body).format(args, kwargs, traceback.format_exc())
    fromEmail = mailConfig.get("fromEmail", settings.DEFAULT_FROM_EMAIL)
    recipientList = mailConfig.get("recipientList", [])
    if recipientList:
        send_mail(subject, body, fromEmail, recipientList)


def retry(count=3, seconds=1, log=logger, mail=None, disableNone=False):
    """TODO: Docstring for retry.

    :count: 重试次数
    :seconds: 重试睡眠的时间
    :log: 日志的logger
    :disableNone: 返回None是否需要重试
    :mail: 是否发送邮件，若发送邮件 bool | dict 格式， 如{'from_email': [], 'recipient_list': []}
    :returns: 被装饰函数的返回值， 若失败则返回None

    """

    def inner(func):
        def wapper(*args, **kwargs):
            for i in range(count):
                try:
                    response = func(*args, **kwargs)
                    if disableNone and response is None:
                        continue
                    return response
                except KeyboardInterrupt:
                    return None
                except Exception:
                    err = traceback.format_exc()
                    log.error(err)
                    time.sleep(seconds)
                _sendMail(mail, func, args, kwargs)

            return None

        return wapper

    return inner
