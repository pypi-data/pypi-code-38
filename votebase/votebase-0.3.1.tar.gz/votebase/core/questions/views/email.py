from django.utils.translation import ugettext as _

from votebase.core.questions.forms.email import EmailForm
from votebase.core.questions.models import Question
from votebase.core.questions.views.textfield import TextfieldCreateView, TextfieldUpdateView


class EmailCreateView(TextfieldCreateView):
    form_class = EmailForm
    kind = Question.KIND_EMAIL

    def get_context_data(self, **kwargs):
        context = super(EmailCreateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Create email')
        context['content_title'] = _(u'Create email')
        context['form'].fields['title'].initial = _(u'Your email')
        return context


class EmailUpdateView(TextfieldUpdateView):
    form_class = EmailForm
    kind = Question.KIND_EMAIL

    def get_context_data(self, **kwargs):
        context = super(EmailUpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Update email')
        context['content_title'] = _(u'Update email')
        return context