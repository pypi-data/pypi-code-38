import re

from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import mark_safe


register = template.Library()


SNIPPETS = [
    (
        r"^GTM-",
        "privacy_killer/google_tag_manager_head.html",
        "privacy_killer/google_tag_manager_body.html",
    ),
    (r"^UA-", "privacy_killer/google_analytics_head.html", None),
]


def _snippets(index):
    parts = []
    for id in getattr(settings, "PRIVACY_KILLER_IDS", ()):
        for snippet in SNIPPETS:
            if re.search(snippet[0], id) and snippet[index]:
                parts.append(render_to_string(snippet[index], {"id": id}))
                break
        else:
            # TODO Emit a warning.
            pass
    return mark_safe("".join(parts))


@register.simple_tag
def privacy_killer_head():
    return _snippets(1)


@register.simple_tag
def privacy_killer_body():
    return _snippets(2)
