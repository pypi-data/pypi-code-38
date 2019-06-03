from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(name='get_voting_form', takes_context=True)
def get_voting_form(context, question, index=1):
    return render_to_string('votebase/helpers/form.html', {
        'form': question.get_voting_form(post_data=None, number=index),
    })

@register.simple_tag(name='get_design_form', takes_context=True)
def get_design_form(context, question, index=1):
    return render_to_string('votebase/helpers/form.html', {
        'form': question.get_design_form(post_data=None, number=index),
        })

@register.simple_tag(name='question_label', takes_context=True)
def question_label(context, question, number=None):
    if not number:
        number = question.get_number()

    label = question.get_label(number)

    if question.is_required:
        label += mark_safe(' <span class="required">*</span>')

    return label
