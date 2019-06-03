from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

register = template.Library()


@register.simple_tag(name='voter_form_result_class', takes_context=True)
def voter_form_result_class(context, form, voter=None):
    try:
        result = form.get_result(form.question, voter)
        if not result:
            klass = 'wrong'

        elif result == 1:
            klass = 'correct'

        else:
            klass = 'partially'

        return u'result-%(class)s' % {
            'class': klass,
        }

    except AttributeError:
        return ''


@register.simple_tag(name='voter_form_result', takes_context=True)
def voter_form_result(context, form, voter=None):
    try:
        result = form.get_result(form.question, voter)
        if not result:
            klass = 'error'
            message = _(u'Wrong answer (0%)')

        elif result == 1:
            klass = 'success'
            message = _(u'Correct answer (100%)')

        else:
            klass = 'warning'
            percent = result * 100
            message = _(u'Partially correct answer (%s%%)') % percent

        result = u'<div class="alert alert-%(class)s">%(message)s</div>' % {
            'class': klass,
            'message': message
        }

        return mark_safe(result)

    except AttributeError:
        return ''


def _get_result_message(percent):
    if percent < 50:      # 0-49
        klass = 'very-bad'
        message = _(u'Very bad!')

    elif percent < 60:    # 50-59
        klass = 'try-harder'
        message = _(u'Try harder next time!')

    elif percent < 70:    # 60-69
        klass = 'could-be-better'
        message = _(u'Well, it could be better!')

    elif percent < 80:    # 70-79
        klass = 'pretty-good'
        message = _(u'Pretty good!')

    elif percent < 90:    # 80-89
        klass = 'great'
        message = _(u'Great!')

    else:
        klass = 'perfect'  # 90-100
        message = _(u'Perfect!')

    return {
        'class': klass,
        'message': message
    }


@register.simple_tag(name='voter_quiz_result_message', takes_context=True)
def voter_quiz_result_message(context, voter):
    stored = voter.quiz_result
    calculated = voter.get_quiz_result()
    percent = stored

    stored_result = _get_result_message(percent)
    if stored == calculated:
        return stored_result['message']

    calculated_result = _get_result_message(calculated)
    return calculated_result['message']


@register.simple_tag(name='voter_quiz_result', takes_context=True)
def voter_quiz_result(context, voter, only_percent=False):
    stored = voter.quiz_result
    calculated = voter.get_quiz_result()
    percent = stored

    if only_percent:
        return '%s%%' % percent

    stored_result_message = _get_result_message(percent)
    stored_result = render_to_string('statistics/helpers/voter_quiz_result.html', {
        'class': stored_result_message['class'],
        'message': stored_result_message['message'],
        'percent': percent,
    })

    if stored == calculated:
        return mark_safe(stored_result)

    stored_result = render_to_string('statistics/helpers/voter_quiz_result.html', {
        'class': stored_result_message['class'],
        'title': _(u'STORED RESULT'),
        'message': stored_result_message['message'],
        'percent': stored,
    })

    calculated_result_message = _get_result_message(calculated)
    calculated_result = render_to_string('statistics/helpers/voter_quiz_result.html', {
        'class': calculated_result_message['class'],
        'title': _(u'CALCULATED RESULT'),
        'message': calculated_result_message['message'],
        'percent': calculated,
    })

    why_so_message = _(u'These results are different, because survey creator changed correct options in quiz questions. Contact him.')

    why_so = u'<div class="alert alert-warning">%(message)s</div>' % {
        'message': why_so_message
    }

    result = '%(stored)s<br>%(calculated)s%(why_so)s<br>' % {
        'stored': stored_result,
        'calculated': calculated_result,
        'why_so': why_so
    }

    return mark_safe(result)
