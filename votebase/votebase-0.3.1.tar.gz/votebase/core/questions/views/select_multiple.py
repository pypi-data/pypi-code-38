from django.utils.translation import ugettext as _

from votebase.core.questions.forms.general import QuizOptionForm
from votebase.core.questions.forms.select_multiple import SelectMultipleForm
from votebase.core.questions.models import Question
from votebase.core.questions.views.select_single import SelectSingleCreateView, SelectSingleUpdateView


class SelectMultipleCreateView(SelectSingleCreateView):
    form_class = SelectMultipleForm
    kind = Question.KIND_SELECT_MULTIPLE
    option_form_class = QuizOptionForm

    def get_context_data(self, **kwargs):
        context = super(SelectMultipleCreateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Create multiple select')
        context['content_title'] = _(u'Create multiple select')
        return context

class SelectMultipleUpdateView(SelectSingleUpdateView):
    form_class = SelectMultipleForm
    kind = Question.KIND_SELECT_MULTIPLE
    option_form_class = QuizOptionForm

    def get_context_data(self, **kwargs):
        context = super(SelectMultipleUpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Update multiple select')
        context['content_title'] = _(u'Update multiple select')
        return context
