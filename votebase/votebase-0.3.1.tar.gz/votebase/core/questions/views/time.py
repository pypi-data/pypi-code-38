from django.utils.translation import ugettext as _

from votebase.core.questions.forms.time import TimeForm
from votebase.core.questions.models import Question
from votebase.core.questions.views.textfield import TextfieldCreateView, TextfieldUpdateView


class TimeCreateView(TextfieldCreateView):
    form_class = TimeForm
    kind = Question.KIND_TIME

    def get_context_data(self, **kwargs):
        context = super(TimeCreateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Create time')
        context['content_title'] = _(u'Create time')
        context['form'].fields['title'].initial = _(u'Enter time')
        return context


class TimeUpdateView(TextfieldUpdateView):
    form_class = TimeForm
    kind = Question.KIND_TIME

    def get_context_data(self, **kwargs):
        context = super(TimeUpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Update time')
        context['content_title'] = _(u'Update time')
        return context