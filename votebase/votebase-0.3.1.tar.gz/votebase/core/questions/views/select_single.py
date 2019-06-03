from django.utils.translation import ugettext as _

from votebase.core.questions.forms.general import QuizOptionForm
from votebase.core.questions.forms.select_single import SelectSingleForm
from votebase.core.questions.models import Question
from votebase.core.questions.views.radio import RadioUpdateView, RadioCreateView


class SelectSingleCreateView(RadioCreateView):
    form_class = SelectSingleForm
    kind = Question.KIND_SELECT_SINGLE
    option_form_class = QuizOptionForm

    def get_context_data(self, **kwargs):
        context = super(SelectSingleCreateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Create single select')
        context['content_title'] = _(u'Create single select')
        return context

class SelectSingleUpdateView(RadioUpdateView):
    form_class = SelectSingleForm
    kind = Question.KIND_SELECT_SINGLE
    option_form_class = QuizOptionForm

    def get_context_data(self, **kwargs):
        context = super(SelectSingleUpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Update single select')
        context['content_title'] = _(u'Update single select')
        return context
