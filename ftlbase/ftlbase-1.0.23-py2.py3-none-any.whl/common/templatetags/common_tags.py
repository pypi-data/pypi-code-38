#!/usr/bin/env python
# coding: utf-8
import re

from django import template

register = template.Library()


class CommonMenuMensagens(template.Node):
    template_name = "menu_mensagens.html"

    # def __init__(self, usuario):
    #     self.usuario = template.Variable(usuario)

    def render(self, context):
        t = template.loader.get_template(self.template_name)
        # atendimentos = Atendimento.get_atendimentos_novos()
        # return t.render({'atendimentos': atendimentos})
        menu_mensagens = {}
        return t.render({'menu_mensagens': menu_mensagens})


@register.tag
def common_menu_mensagens(parser, token):
    return CommonMenuMensagens()


USER_AGENT_REGEX = re.compile(
    r'randroid|avantgo|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|'
    r'ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|opera m(ob|in)i|palm( os)?|'
    r'phone|p(ixi|re)\\/|plucker|pocket|psp|symbian|treo|up\\.(browser|link)|'
    r'vodafone|wap|indows (ce|phone)|xda|xiino', re.M)


@register.filter()
def is_mobile(request):
    ua = request.META.get('HTTP_USER_AGENT', '').lower()
    if USER_AGENT_REGEX.search(ua):
        return True
    return False
