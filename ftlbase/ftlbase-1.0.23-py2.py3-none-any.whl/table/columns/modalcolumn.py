from django.urls import reverse
from django.utils.safestring import mark_safe

from common.form import ACAO_VIEW
from table.columns import Column
from table.utils import Accessor


class ModalColumn(Column):
    goto = None

    def __init__(self, field=None, header=None, goto='obrigatorio', span_text='obrigatorio', span_tip='obrigatorio',
                 key='pk', cls='modal-lg', acao=ACAO_VIEW, **kwargs):
        kwargs['safe'] = False
        self.goto = goto
        self.span_text = span_text
        self.span_tip = span_tip
        self.key = key
        self.cls = cls
        self.acao = acao
        super().__init__(field=field, header=header, **kwargs)

    def render(self, instance):
        if hasattr(instance, 'instance'):
            i = instance.instance
        else:
            i = instance
        pk = Accessor(self.key).resolve(i)
        url = reverse(self.goto, args=[pk])
        span = '<i class="far fa-%s" style="font-size:18px;color:#09568d;" data-toggle="tooltip" title="%s"></i>' % (
            self.span_text, self.span_tip)
        url = mark_safe(u"<a href='#' onclick='ftl_modal(%s, %s, \"%s\", \"%s: %s\", \"%s\"); return false;'>%s</a>" % (
            pk, self.acao, url, self.span_tip, i.pk, self.cls, span))
        return url