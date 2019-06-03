from django.db import models

from votebase.core.questions.models import Option


class AnswerManager(models.Manager):
    def get_vote_for_true_false(self, voter, question):
        rows = Option.objects.rows_by_question(question)
        result = []

        answered_options = self.model.objects.filter(
            voter=voter, question=question
        ).values_list('option__pk', flat=True)

        for row in rows:
            if row.pk in answered_options:
                result.append(True)
            else:
                result.append(False)
        return result

    def get_vote_for_matrix(self, voter, question):
        rows = Option.objects.rows_by_question(question)
        result = []

        values = dict(self.model.objects.filter(
            voter=voter, question=question
        ).values_list('option__pk', 'option_column__pk'))

        for row in rows:
            if row.pk in values:
                result.append(values[row.pk])
            else:
                result.append(None)

        return result

    def get_vote_for_multiplematrix(self, voter, question):
        rows = Option.objects.rows_by_question(question)
        answers = self.model.objects.filter(voter=voter, question=question)
        results = {}

        for row in rows:
            results[row.pk] = []
            row_answers = answers.filter(option=row)

            for answer in row_answers:
                results[answer.option_id].append(answer.option_column_id)

        return [results[row.pk] for row in rows]


class VoterQuerySet(models.query.QuerySet):
    def by_survey(self, survey):
        return self.filter(round__in=survey.round_set.all())

    def by_segment(self, segment):
        return self.filter(round=segment)

    def by_user(self, user):
        return self.filter(user=user)


class VotedQuestionManager(models.Manager):
    def get_voter_questions(self, voter):
        question_list = voter.votedquestion_set.values_list('question', flat=True)
        return voter.survey.question_set.filter(pk__in=question_list)
