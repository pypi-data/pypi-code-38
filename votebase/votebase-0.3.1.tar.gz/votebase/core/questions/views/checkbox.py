from django.utils.translation import ugettext as _

from votebase.core.questions.forms.checkbox import CheckboxForm
from votebase.core.questions.models import Question
from votebase.core.questions.views.radio import RadioCreateView, RadioUpdateView


class CheckboxCreateView(RadioCreateView):
    form_class = CheckboxForm
    kind = Question.KIND_CHECKBOX

    def get_context_data(self, **kwargs):
        context = super(CheckboxCreateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Create checkbox')
        context['content_title'] = _(u'Create checkbox')
        return context


class CheckboxUpdateView(RadioUpdateView):
    form_class = CheckboxForm
    kind = Question.KIND_CHECKBOX

    def get_context_data(self, **kwargs):
        context = super(CheckboxUpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Update checkbox')
        context['content_title'] = _(u'Update checkbox')
        return context
