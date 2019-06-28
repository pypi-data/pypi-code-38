#!/usr/bin/env python
# coding: utf-8
from django.template import Context, Template
from django.template.loader import get_template
from django.utils.safestring import mark_safe


class SearchBox(object):
    def __init__(self, visible=True, placeholder=None):
        self.visible = visible
        self.placeholder = placeholder or "Search"

    @property
    def dom(self):
        if self.visible:
            return "<'col-sm-6 col-md-6 col-lg-6'B><'col-sm-3 col-md-3 col-lg-3'f>"
        else:
            return "<'col-sm-6 col-md-6 col-lg-6'><'col-sm-3 col-md-3 col-lg-3'>"


class ExtButton(object):
    def __init__(self, visible=True, template=None, template_name=None, context=None, template_href=None,
                 template_className=None):
        self.visible = visible
        self.context = Context(context)
        if visible:
            if template:
                try:
                    self.template = Template(template)
                except Exception as v:
                    self.template = Template(str(template))
            else:
                self.template = get_template(template_name)
        self.template_href = template_href or ''
        self.template_className = template_className or ''

    @property
    def dom(self):
        if self.visible:
            # return "<'col-sm-7 col-md-7 col-lg-7 ext-btn'>"
            return "<'ext-btn'>"
        else:
            # return "<'col-sm-7 col-md-7 col-lg-7'>"
            return ""

    @property
    def html(self):
        if self.visible:
            return mark_safe(self.template.render(self.context).strip())
        else:
            return ''

    @property
    def href(self):
        if self.visible:
            return mark_safe(self.template_href.strip())
        else:
            return ''

    @property
    def className(self):
        if self.visible:
            return mark_safe(self.template_className.strip())
        else:
            return ''


class StdButton(object):
    """
    Botões padrão de uso:
        create: inclui registro
        next: url para a ação de criate
        pdf: gera pdf da página corrente
        excel: gera arquivo xlsx da página corrente
        copy: copia página corrente para o clipboard
        ret: retorna do cadastro atual para a lista
    """

    def __init__(self, visible=True, create=None, print=True, pdf=False, excel=False, copy=False, ret=None):
        self.visible = visible
        # print('visible=',visible)
        if create is None:
            self.create = {"text": 'Incluir novo registro',
                           "icon": '<i class="far fa-plus-square fa-fw" style="color:#ffffff;"></i>',
                           "href": 'add',
                           "className": 'btn btn-primary btn-sm',
                           }
        else:
            self.create = create
        self.print = print
        self.pdf = pdf
        self.excel = excel
        self.copy = copy
        self.ret = ret


class InfoLabel(object):
    def __init__(self, visible=True, format=None):
        self.visible = visible
        self.format = format or "Total _TOTAL_"

    @property
    def dom(self):
        if self.visible:
            return "<'col-sm-3 col-md-3 col-lg-3'i>"
        else:
            return "<'col-sm-3 col-md-3 col-lg-3'>"
            # return "<'col-sm-2 col-md-2 col-lg-2'>"


class Pagination(object):
    def __init__(self, visible=True, length=10, first=None,
                 last=None, prev=None, next=None):
        self.visible = visible
        self.length = length
        self.first = first or "First"
        self.last = last or "Last"
        self.prev = prev or "Prev"
        self.next = next or "Next"

    @property
    def dom(self):
        if self.visible:
            return "<'col-sm-5 col-md-5 col-lg-5'p>"
        else:
            return "<'col-sm-5 col-md-5 col-lg-5'>"
            # return ("<'col-sm-4 col-md-4 col-lg-4 col-sm-offset-1 "
            #         "col-md-offset-1 col-lg-offset-1'>")


class LengthMenu(object):
    def __init__(self, visible=True):
        self.visible = visible

    @property
    def dom(self):
        if self.visible:
            return "<'col-sm-1 col-md-1 col-lg-1'l>"
        else:
            return "<'col-sm-1 col-md-1 col-lg-1'>"
