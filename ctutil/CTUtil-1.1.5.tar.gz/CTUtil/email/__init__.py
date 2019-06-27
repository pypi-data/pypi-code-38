from CTUtil.email.util import CingTaEmail, BaseEmail
from django.core.mail import send_mail
from typing import List, Union, Type
from CTUtil.types import EmailTypes, FuncCallBack

__all__ = ('CingTaEmail', 'BaseEmail', 'send_mail', 'EmailTypes',
           'FuncCallBack')


def send_cingta_email(
        title: str,
        to_email: List[str],
        model: Type[EmailTypes]=EmailTypes.DEMAND,
        msg: Union[None, str]=None,
        from_email_name: str='cingta',
        **kwargs) -> Type[FuncCallBack]:
    mail: CingTaEmail = CingTaEmail(title, to_email, model, msg, from_email_name, **kwargs)
    try:
        send_mail(**mail.email_msg)
        return FuncCallBack.SUCCESS
    except BaseException as e:
        raise e