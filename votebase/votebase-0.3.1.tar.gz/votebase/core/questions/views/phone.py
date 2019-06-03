from django.utils.translation import ugettext as _

from votebase.core.questions.forms.phone import PhoneForm
from votebase.core.questions.models import Question
from votebase.core.questions.views.textfield import TextfieldCreateView, TextfieldUpdateView


class PhoneCreateView(TextfieldCreateView):
    form_class = PhoneForm
    kind = Question.KIND_PHONE

    def get_context_data(self, **kwargs):
        context = super(PhoneCreateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Create phone')
        context['content_title'] = _(u'Create phone')
        context['form'].fields['title'].initial = _(u'Your phone')
        return context


class PhoneUpdateView(TextfieldUpdateView):
    form_class = PhoneForm
    kind = Question.KIND_PHONE

    def get_context_data(self, **kwargs):
        context = super(PhoneUpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Update phone')
        context['content_title'] = _(u'Update phone')
        return context