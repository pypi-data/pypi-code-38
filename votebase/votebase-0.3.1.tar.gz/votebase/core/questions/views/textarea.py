from django.utils.translation import ugettext as _

from votebase.core.questions.forms.textarea import TextareaForm
from votebase.core.questions.models import Question
from votebase.core.questions.views.textfield import TextfieldCreateView, TextfieldUpdateView


class TextareaCreateView(TextfieldCreateView):
    form_class = TextareaForm
    kind = Question.KIND_TEXTAREA

    def get_context_data(self, **kwargs):
        context = super(TextareaCreateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Create textarea')
        context['content_title'] = _(u'Create textarea')
        return context


class TextareaUpdateView(TextfieldUpdateView):
    form_class = TextareaForm
    kind = Question.KIND_TEXTAREA

    def get_context_data(self, **kwargs):
        context = super(TextareaUpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Update textarea')
        context['content_title'] = _(u'Update textarea')
        return context