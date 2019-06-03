from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from votebase.core.questions.forms.radio import RadioForm
from votebase.core.questions.models import Question
from votebase.core.questions.views.general import OptionsQuestionCreateView, \
    OptionsQuestionUpdateView


class RadioCreateView(OptionsQuestionCreateView):
    form_class = RadioForm
    kind = Question.KIND_RADIO

    def get_context_data(self, **kwargs):
        context = super(RadioCreateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Create radio')
        context['content_title'] = _(u'Create radio')
        return context


class RadioUpdateView(OptionsQuestionUpdateView):
    form_class = RadioForm
    kind = Question.KIND_RADIO

    def get_form(self, form_class=None):
        form = super(RadioUpdateView, self).get_form(form_class)
        form.fields['image'].widget.attrs['remove_url'] = \
            reverse('questions_delete_image', args=(self.question.pk, ))
        return form

    def get_context_data(self, **kwargs):
        context = super(RadioUpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Update radio')
        context['content_title'] = _(u'Update radio')
        return context
