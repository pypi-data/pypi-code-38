from django.utils.translation import ugettext as _

from votebase.core.questions.forms.gender import GenderForm
from votebase.core.questions.forms.general import OptionForm
from votebase.core.questions.models import Question
from votebase.core.questions.views.general import OptionsQuestionCreateView, OptionsQuestionUpdateView


class GenderCreateView(OptionsQuestionCreateView):
    form_class = GenderForm
    option_form_class = OptionForm
    kind = Question.KIND_GENDER
    can_add = False

    def get_context_data(self, **kwargs):
        context = super(GenderCreateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Create gender')
        context['content_title'] = _(u'Create gender')
        context['form'].fields['title'].initial = _(u'What is your gender?')
        context['formset'].forms[0].fields['title'].initial = _(u'Male')
        context['formset'].forms[1].fields['title'].initial = _(u'Female')

        return context

class GenderUpdateView(OptionsQuestionUpdateView):
    form_class = GenderForm
    option_form_class = OptionForm
    kind = Question.KIND_GENDER
    can_add = False
    can_delete = False

    def get_context_data(self, **kwargs):
        context = super(GenderUpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Update gender')
        context['content_title'] = _(u'Update gender')
        return context
