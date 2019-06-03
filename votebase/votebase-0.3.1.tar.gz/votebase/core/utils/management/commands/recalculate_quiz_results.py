from progressbar import ProgressBar, Percentage, Bar
from django.core.management.base import BaseCommand, CommandError
from votebase.core.surveys.models import Survey
from votebase.core.voting.models import Voter


class Command(BaseCommand):
    args = '<survey_id>'
    help = 'Recalculates stored quiz results of voters in surveys with changed correct options'

    def handle(self, *args, **options):
        quiz_surveys = Survey.objects.filter(question__is_quiz=True).distinct()
        print('Number of quiz surveys: {}'.format(quiz_surveys.count()))

        for survey in quiz_surveys:
            print('[{}] {}'.format(survey.id, survey))

        try:
            survey_id = args[0]
        except IndexError:
            raise CommandError('Missing survey ID!')

        voters = Voter.objects.filter(round__survey__id=survey_id)

        num_voters = voters.count()

        print('Total number of voters: {}'.format(num_voters))

        progress_bar = ProgressBar(widgets=[Percentage(), Bar()], maxval=num_voters).start()
        i = 1
        updated_voters = 0

        for voter in voters:
            stored_quiz_result = voter.quiz_result
            calculated_quiz_result = voter.get_quiz_result()
            #need_to_recalculate = stored_quiz_result != calculated_quiz_result
            need_to_recalculate = True

            if need_to_recalculate:
                print('{}: {}% => {}%'.format(voter, stored_quiz_result, calculated_quiz_result))
                voter.quiz_result = calculated_quiz_result

                self.recalculate_voted_questions_quiz_results(voter)

                voter.save()
                updated_voters += 1

            progress_bar.update(i+1)

        print('\nUpdated voters: {}'.format(updated_voters))

    def recalculate_voted_questions_quiz_results(self, voter):
        for voted_question in voter.votedquestion_set.all().select_related('question'):
            if not voted_question.question.is_quiz:
                voted_question.quiz_result = None
            else:
                voted_question.quiz_result = voter.get_question_result(voted_question.question)

            voted_question.save()
