#!/usr/bin/env python
# coding: utf-8
from django import template

register = template.Library()


class TableNode(template.Node):
    template_name = "table/table.html"

    def __init__(self, table):
        self.table = template.Variable(table)

    def render(self, context):
        table = self.table.resolve(context)
        # context = Context({'table': table})
        t = template.loader.get_template(self.template_name)
        # Preparação da titleForm
        if table.opts.titleForm:
            obj = table.opts.titleForm.get_tableForm_instance(context)
            titleForm = table.opts.titleForm(instance=obj) if obj else None
        else:
            titleForm = None
        # Preparação da footerForm
        if table.opts.footerForm:
            obj = table.opts.footerForm.get_tableForm_instance(context)
            footerForm = table.opts.footerForm(instance=obj) if obj else None
        else:
            footerForm = None
        return t.render({'table': table, 'titleForm': titleForm, 'footerForm': footerForm})


class SimpleTableNode(TableNode):
    template_name = "table/simple_table.html"


@register.tag
def render_table(parser, token):
    try:
        tag, table = token.split_contents()
    except ValueError:
        msg = '%r tag requires a single arguments' % token.split_contents()[0]
        raise template.TemplateSyntaxError(msg)
    return TableNode(table)


@register.tag
def render_simple_table(parser, token):
    try:
        tag, table = token.split_contents()
    except ValueError:
        msg = '%r tag requires a single arguments' % token.split_contents()[0]
        raise template.TemplateSyntaxError(msg)
    return SimpleTableNode(table)
