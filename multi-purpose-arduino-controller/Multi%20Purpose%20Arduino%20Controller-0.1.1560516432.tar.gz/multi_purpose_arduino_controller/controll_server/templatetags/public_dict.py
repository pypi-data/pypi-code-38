from django import template

#if manage.py is called directly
if len(__name__.split(".")) == 2:
    from controll_server.settings import CONFIG
else:
    from ..controll_server.settings import CONFIG



register = template.Library()


@register.filter(name="pub_dict")
def get_from_public_dict(args, default):
    path = ["public"] + args.strip().split(",")
    return CONFIG.get(*path, default=default)
