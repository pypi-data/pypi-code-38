from django.utils.translation import ugettext as _

from votebase.core.questions.forms.true_false import TrueFalseForm
from votebase.core.questions.models import Question
from votebase.core.questions.views.checkbox import CheckboxCreateView, CheckboxUpdateView


class TrueFalseCreateView(CheckboxCreateView):
    form_class = TrueFalseForm
    kind = Question.KIND_TRUE_FALSE

    def get_context_data(self, **kwargs):
        context = super(CheckboxCreateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Create true/false')
        context['content_title'] = _(u'Create true/false')
        return context


class TrueFalseUpdateView(CheckboxUpdateView):
    form_class = TrueFalseForm
    kind = Question.KIND_TRUE_FALSE

    def get_context_data(self, **kwargs):
        context = super(CheckboxUpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Update true/false')
        context['content_title'] = _(u'Update true/false')
        return context
