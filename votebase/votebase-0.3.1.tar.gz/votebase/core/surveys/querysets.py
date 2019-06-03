from django.db import models


class SurveyQuerySet(models.QuerySet):
    def by_user(self, user):
        """ Gets surveys owned by user """
        return self.filter(user=user)

    def quizzes(self):
        """ Gets quizzes only """
        from votebase.core.questions.models import Question
        quiz_questions = Question.objects.filter(is_quiz=True)
        return self.filter(pk__in=quiz_questions.values_list('survey__pk', flat=True)).distinct()

    def not_quizzes(self):
        """ Gets non-quizzes only """
        from votebase.core.questions.models import Question
        quiz_questions = Question.objects.filter(is_quiz=True)
        return self.exclude(pk__in=quiz_questions.values_list('survey__pk', flat=True)).distinct()
