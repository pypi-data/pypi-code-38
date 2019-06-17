from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from .models import Question, Vote


@require_POST
def vote(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if question.can_vote(request) or True:
        prefix = request.POST.get('prefix')
        form = question.answer_form_class(prefix=prefix, data=request.POST)
        if form.is_valid():
            Vote.objects.create(answer=form.cleaned_data['answer'])
            question.set_voted(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
