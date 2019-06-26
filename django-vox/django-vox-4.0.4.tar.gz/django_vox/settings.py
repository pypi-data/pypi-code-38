import importlib.util
import re
import sys

import django.conf

from django_vox.backends.base import load_backend

__all__ = (
    "BACKENDS",
    "INBOX_LIMIT",
    "THROW_EXCEPTIONS",
    "ACTIVITY_REGEX",
    "ISSUE_METHOD",
    "MARKDOWN_EXTRAS",
    "MARKDOWN_LINK_PATTERNS",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_FROM_NUMBER",
    "TWITTER_CONSUMER_KEY",
    "TWITTER_CONSUMER_SECRET",
    "TWITTER_TOKEN_KEY",
    "TWITTER_TOKEN_SECRET",
    "XMPP_JID",
    "XMPP_PASSWORD",
    "POSTMARK_TOKEN",
)


# General settings
BACKENDS = []
INBOX_LIMIT = 500
THROW_EXCEPTIONS = getattr(django.conf.settings, "DEBUG", False)
ACTIVITY_REGEX = r"activity/(?P<id>[0-9a-z\-]+)/$"
ISSUE_METHOD = "django_vox.models.Notification.issue_now"

# Markdown settings
URL_PATTERN = re.compile(
    r"((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]"
    r"+(:[0-9]+)?|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+"
    r"~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)"
)
MARKDOWN_EXTRAS = ["footnotes", "link_patterns", "smarty-pants", "tables"]
MARKDOWN_LINK_PATTERNS = [(URL_PATTERN, r"\1")]

# Twilio
TWILIO_ACCOUNT_SID = None
TWILIO_AUTH_TOKEN = None
TWILIO_FROM_NUMBER = None

# Twitter settings
TWITTER_CONSUMER_KEY = None
TWITTER_CONSUMER_SECRET = None
TWITTER_TOKEN_KEY = None
TWITTER_TOKEN_SECRET = None

# XMPP settings
XMPP_JID = None
XMPP_PASSWORD = None

# Postmark
POSTMARK_TOKEN = None


class _Sneaky:
    def __init__(self, name):
        self.module = sys.modules[name]
        sys.modules[name] = self
        # sphinx would like me to do something like this, but it
        # breaks things right now
        # for name in __all__:
        #     if name != 'BACKENDS':
        #         setattr(self, name, getattr(self.module, name))

    def __getattr__(self, name):
        # call module.__init__ after import introspection is done
        django_setting_name = "DJANGO_VOX_" + name
        if name in __all__:
            attr = getattr(django.conf.settings, django_setting_name, None)
            if attr is not None:
                return attr
            elif name == "BACKENDS":
                return _Sneaky.get_backends()
        result = getattr(self.module, name)
        if result is None:
            raise django.conf.ImproperlyConfigured(
                "Please set {} in your settings".format(django_setting_name)
            )
        return result

    @staticmethod
    def get_backends():
        result = []
        # Automatically set based on libraries available
        default_backends = [
            "django_vox.backends.markdown_email",
            "django_vox.backends.template_email",
            "django_vox.backends.twilio",
            "django_vox.backends.twitter",
            "django_vox.backends.xmpp",
            # This backend requires lot of setup
            # "django_vox.backends.activity",
            # this backend is not very user-friendly
            # "django_vox.backends.html_email",
            # disabled because they're proprietary or not commonly used
            # "django_vox.backends.postmark_email",
            # "django_vox.backends.slack",
            # "django_vox.backends.json_webhook",
        ]
        for cls_str in default_backends:
            cls = load_backend(cls_str)
            for dep in cls.DEPENDS:
                if importlib.util.find_spec(dep) is None:
                    continue
            result.append(cls_str)
        return result


_Sneaky(__name__)
