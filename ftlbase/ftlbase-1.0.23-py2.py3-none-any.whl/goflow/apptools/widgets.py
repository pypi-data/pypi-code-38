# -*- coding: utf-8 -*-

from django.utils.safestring import mark_safe

from common.form import ACAO_WORKFLOW_EDIT
from table.columns.modalcolumn import ModalColumn


class GoFlowWhereColumn(ModalColumn):
    def __init__(self, field=None, header=None, goto='workflow_graph', span_text='project-diagram', span_tip='Onde estou?',
                 key='pk', cls='modal-lg', **kwargs):
        super().__init__(field=field, header=header, goto=goto, span_text=span_text, span_tip=span_tip,
                         key=key, cls=cls, **kwargs)


class GoFlowHistoryColumn(ModalColumn):
    def __init__(self, field=None, header=None, goto='workflow_history', span_text='history', span_tip='História',
                 key='pk', cls='modal-lg', acao=ACAO_WORKFLOW_EDIT, **kwargs):
        super().__init__(field=field, header=header, goto=goto, span_text=span_text, span_tip=span_tip, key=key,
                         cls=cls, acao=acao, **kwargs)


class GoFlowColumn(ModalColumn):
    def render(self, instance):
        part_a = GoFlowWhereColumn(field=self.field, header=self.header).render(instance)
        part_b = GoFlowHistoryColumn(field=self.field, header=self.header).render(instance)

        span_text = 'tasks'
        span_tip = 'Tarefas'
        if hasattr(instance, 'html_to_approve_link'):
            url = '/#' + instance.html_to_approve_link
            # url = '/#/atendimento/' + instance.html_to_approve_link
        elif instance.workitems.last():
            url = '/#' + instance.workitems.last().html_to_approve_link
            # url = '/#/atendimento/' + instance.workitems.last().html_to_approve_link
        else:
            url = '#'
        span = '<i class="far fa-%s" style="font-size:18px;color:#09568d;" data-toggle="tooltip" title="%s"></i>' % (
            span_text, span_tip)
        part_c = mark_safe(u'<a href="%s">%s</a>' % (url, span))

        div = '&nbsp;'

        return part_a + div + part_b + div + part_c + div + div + div + div
