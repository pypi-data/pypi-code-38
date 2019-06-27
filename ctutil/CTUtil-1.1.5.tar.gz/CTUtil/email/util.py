from typing import Dict, Union, List, Type, Set
import os
from jinja2 import Environment, select_autoescape, FileSystemLoader
from CTUtil.types import EmailTypes

_BASE_FILE = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    loader=FileSystemLoader(os.path.join(_BASE_FILE, 'template')),
    auto_reload=select_autoescape(['html', 'xml']))


class ProcessEmail(type):
    manage: set = set()

    def __new__(cls, clsname, bases, clsdict):
        _type = type(clsname, bases, clsdict)
        cls.manage.add(_type)
        return _type


class BaseEmail(metaclass=ProcessEmail):
    template: str = ''
    work_dir: str = os.getcwd()


class CingTaEmail(object):

    SENED_EMAIL: str = '{name} <service@cingta.com>'

    def __init__(self,
                 title: str,
                 to_email: List[str],
                 model: Type[EmailTypes]=EmailTypes.DEMAND,
                 msg: Union[str, None]=None,
                 from_email_name: str='cingta',
                 **kwargs) -> None:

        self.SENED_EMAIL = self.SENED_EMAIL.format(name=from_email_name)
        self.msg: str = msg if msg else ''

        self.to_email: List[str] = to_email
        self._html_model: Union[EmailTypes, BaseEmail] = model
        self.title = title
        self.kwargs: Dict[str, str] = kwargs

    def _make_email_text(self) -> str:
        text = """{msg}""".format(msg=self.msg)
        return text

    @property
    def email_msg(self) -> Dict[str, str]:
        data = {
            'subject': self.title,
            'message': self._make_email_text(),
            'from_email': self.SENED_EMAIL,
            'recipient_list': self.to_email,
            'html_message': self._html_text() if not self.msg else None,
        }
        return data

    def _html_text(self) -> str:
        html_text = self.kwargs.setdefault('html_string', '')
        if html_text:
            return html_text
        if isinstance(self._html_model, EmailTypes):
            template = env.get_template(self._set_model_template).render(**self.kwargs)
            return template
        _env = Environment(
            loader=FileSystemLoader(os.path.join(self._html_model.work_dir, 'template')),
            auto_reload=select_autoescape(['html', 'xml']))
        template = _env.get_template(self._html_model.template).render(**self.kwargs)
        return template

    @property
    def _set_model_template(self) -> str:
        email_type_mapping_template: Dict[EmailTypes, str] = {
            EmailTypes.DEMAND: 'email_need.html',
            EmailTypes.BUG: 'email_bug.html',
            EmailTypes.RECRUIT: 'email_zhaoping.html',
            EmailTypes.REGISTER: 'email_register.html',
            EmailTypes.MODIFYPASS: 'email_modifypass.html',
        }
        if self._html_model not in email_type_mapping_template:
            raise ValueError('not this html model')
        template: str = email_type_mapping_template.setdefault(self._html_model)
        return template

    def __unicode__(self) -> str:
        return 'send email: {} to {}'.format(
            self.SUBJECT_STRING,
            self.email, )
