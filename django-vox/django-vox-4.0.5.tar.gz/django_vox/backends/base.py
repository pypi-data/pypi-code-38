import inspect
import pydoc

import dataclasses
from typing import List

import django.conf
import django.core.mail.backends.base
import django.core.mail.backends.smtp
import django.template
import django.utils.html
from django.template import Context

__ALL__ = ("Backend", "template_from_string", "load_backend")


def load_backend(backend_str: str):
    thing = pydoc.locate(backend_str)
    if thing is None:
        raise RuntimeError("Unable to locate backend {}".format(backend_str))
    if inspect.ismodule(thing):
        thing = getattr(thing, "Backend", None)
        if not inspect.isclass(thing):
            raise RuntimeError(
                "Backend module {} must have class 'Backend'".format(backend_str)
            )
        else:
            return thing
    if inspect.isclass(thing):
        return thing
    raise RuntimeError("Backend {} must be a class or module".format(backend_str))


def html_format(text: str):
    escaped = django.utils.html.escape(text)
    return escaped.replace("\r\n", "<br/>").replace("\n", "<br/>")


@dataclasses.dataclass
class AttachmentData:
    data: bytes
    mime: str


class Backend:

    USE_SUBJECT = False
    USE_ATTACHMENTS = False
    USE_FROM_ADDRESS = False
    ESCAPE_HTML = True
    DEPENDS = ()
    EDITOR_TYPE = "basic"
    ALLOW_MANUAL_SENDING = True

    def __init__(self):
        """
        Import any modules or initialize any resources you need for sending.

        This is only used when actually sending messages and not used for
        building or previewing them. The lifetime of a backend object isn't
        all that long right now.
        """
        pass

    @classmethod
    def build_message(
        cls,
        subject: str,
        body: str,
        parameters: dict,
        attachments: List[AttachmentData],
    ):
        template = template_from_string(body)
        context = Context(parameters, autoescape=cls.ESCAPE_HTML)
        return template.render(context)

    @classmethod
    def preview_message(cls, subject: str, body: str, parameters: dict):
        message = cls.build_message(subject, body, parameters, [])
        if not cls.ESCAPE_HTML:
            message = html_format(message)
        return message

    @classmethod
    def get_from_address(cls, provided_address, parameters: dict):
        if not cls.USE_FROM_ADDRESS:
            return ""
        if not provided_address:
            return cls.get_default_from_address()
        context = Context(parameters, autoescape=False)
        return template_from_string(provided_address).render(context)

    @classmethod
    def get_default_from_address(cls) -> str:
        """
        Gets the default from address

        You only need to implement this is you have
        USE_FROM_ADDRESS = True. This base method should normally never
        get called (unless an empty from address is normal for your backend).
        """
        return ""

    # instance methods
    def send_message(self, from_address: str, to_addresses: List[str], message: str):
        raise NotImplementedError


def template_from_string(text: str, using=None) -> django.template.base.Template:
    """
    Convert a string into a template object,
    using a given template engine or using the default backends
    from settings.TEMPLATES if no engine was specified.
    """
    # This function is based on django.template.loader.get_template,
    # but uses Engine.from_string instead of Engine.get_template.
    engines = django.template.engines
    engine_list = engines.all() if using is None else [engines[using]]
    exception = None
    for engine in engine_list:
        try:
            return engine.from_string(text).template
        except django.template.exceptions.TemplateSyntaxError as e:
            exception = e
    raise exception
