from urllib.parse import urlencode

from django import template

from .. import payment_url as _payment_url
from ..models import Gateway

register = template.Library()


@register.simple_tag(takes_context=True)
def payment_url(context, gateway, order_id, amount, currency=None, email=None, lang=None):
    return _payment_url(
        gateway=gateway,
        order_id=oreder_id,
        amount=amount,
        currency=currency,
        email=email or getattr(getattr(context.get('request'), 'user', None), 'email', ''),
        lang=lang,
    )
