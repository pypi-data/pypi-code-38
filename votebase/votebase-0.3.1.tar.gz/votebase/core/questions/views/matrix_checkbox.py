from django.utils.translation import ugettext as _

from votebase.core.questions.forms.matrix_checkbox import MatrixCheckboxForm
from votebase.core.questions.models import Question
from votebase.core.questions.views.matrix_radio import MatrixRadioCreateView, MatrixRadioUpdateView


class MatrixCheckboxCreateView(MatrixRadioCreateView):
    form_class = MatrixCheckboxForm
    kind = Question.KIND_MATRIX_CHECKBOX

    def get_context_data(self, **kwargs):
        context = super(MatrixCheckboxCreateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Create checkbox matrix')
        context['content_title'] = _(u'Create checkbox matrix')
        return context

class MatrixCheckboxUpdateView(MatrixRadioUpdateView):
    form_class = MatrixCheckboxForm
    kind = Question.KIND_MATRIX_CHECKBOX

    def get_context_data(self, **kwargs):
        context = super(MatrixCheckboxUpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Update checkbox matrix')
        context['content_title'] = _(u'Update checkbox matrix')
        return context
