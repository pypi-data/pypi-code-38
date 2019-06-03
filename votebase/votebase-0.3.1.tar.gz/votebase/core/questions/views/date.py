from django.utils.translation import ugettext as _

from votebase.core.questions.forms.date import DateForm
from votebase.core.questions.models import Question
from votebase.core.questions.views.textfield import TextfieldCreateView, TextfieldUpdateView


class DateCreateView(TextfieldCreateView):
    form_class = DateForm
    kind = Question.KIND_DATE

    def get_context_data(self, **kwargs):
        context = super(DateCreateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Create date')
        context['content_title'] = _(u'Create date')
        context['form'].fields['title'].initial = _(u'Enter date')
        return context


class DateUpdateView(TextfieldUpdateView):
    form_class = DateForm
    kind = Question.KIND_DATE

    def get_context_data(self, **kwargs):
        context = super(DateUpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Update date')
        context['content_title'] = _(u'Update date')
        return context