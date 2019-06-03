from django import template

register = template.Library()


@register.filter(name='statistics_graph_url')
def statistics_graph_url(question, type):
    kind = str(question.kind).lower()
    return 'statistics_graph_%s_%s' % (kind, type)
