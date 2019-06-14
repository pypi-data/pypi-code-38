from django import template

register = template.Library()


def verbose(value, attr_name):
    fields = value.__class__._meta.fields
    verbose_name = [f.verbose_name for f in fields if f.name == attr_name].pop()
    if verbose_name:
        return verbose_name
    else:
        return ""


register.filter('verbose', verbose)
