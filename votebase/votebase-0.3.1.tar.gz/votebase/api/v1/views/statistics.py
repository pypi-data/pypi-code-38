from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound, HttpResponseForbidden

#from ....views import APIView
from votebase.api.views import APIView, BasicAuthMixin
from votebase.core.surveys.models import Round


class VotersView(BasicAuthMixin, APIView):
    def get(self, request, **kwargs):
        try:
            segment = Round.objects.get(pk=kwargs.get('segment_pk'))
        except ObjectDoesNotExist:
            return self.return_error_response(HttpResponseNotFound, message='Segment not found.')

        if self.is_auth_string_present(request) and not self.is_authenticated(self.request):
            return self.return_error_response(HttpResponseForbidden, message='Invalid credentials.')

        show_quiz_result = segment.is_quiz_result_visible
        if segment.statistics_policy == Round.STATISTICS_POLICY_PRIVATE or segment.statistics_policy == Round.STATISTICS_POLICY_SECRET:
            # Check basic auth in BasicAuthMixin
            if not self.is_authenticated(request):
                return self.challenge()

            if not request.user.is_authenticated():
                return self.return_error_response(HttpResponseForbidden, message='These statistics are available for survey creator or segment voters only.')

            if segment.statistics_policy == Round.STATISTICS_POLICY_PRIVATE:
                if segment.survey.user != request.user:
                    return self.return_error_response(HttpResponseForbidden, message='These statistics are available for survey creator only.')
                show_quiz_result = True

            if segment.statistics_policy == Round.STATISTICS_POLICY_SECRET:
                if not segment.voter_set.filter(user=request.user).exists() and segment.survey.user != request.user:
                    return self.return_error_response(HttpResponseForbidden, message='These statistics are available for survey creator or segment voters only.')

        voters = []
        for voter in segment.voter_set.all():
            voter_dict = {
                'id': voter.pk,
                'user': voter.user.pk if voter.user else None,
                'hash_key': voter.hash_key,
                'ip_address': voter.ip_address,
                'latitude': voter.latitude,
                'longitude': voter.longitude,
                'continent_code': voter.continent_code,
                'country_name': voter.country_name,
                'country_code': voter.country_code,
                'city': voter.city,
                'area_code': voter.area_code,
                'voting_started': voter.voting_started.strftime(APIView.DATETIME_FORMAT) if voter.voting_started else None,
                'voting_ended': voter.voting_ended.strftime(APIView.DATETIME_FORMAT) if voter.voting_ended else None,
                'voting_duration': voter.voting_duration,
                #'is_irrelevant': voter.is_irrelevant,
                'created': voter.created.strftime(APIView.DATETIME_FORMAT),
                'modified': voter.modified.strftime(APIView.DATETIME_FORMAT)
            }

            if segment.survey.is_quiz() and show_quiz_result:
                voter_dict.update({'quiz_result': voter.quiz_result})

            voter_questions = []
            for voted_question in voter.votedquestion_set.all():
                question = {
                    'id': voted_question.pk,
                    'question_id': voted_question.question.pk,
                    #'weight': voted_question.weight,
                    #'page': voted_question.page,
                    'created': voter.created.strftime(APIView.DATETIME_FORMAT),
                    'modified': voter.modified.strftime(APIView.DATETIME_FORMAT)
                }

                answers = []
                for answer in voted_question.answer_set.all():
                    answers.append({
                        'id': answer.id,
                        'custom': answer.custom,
                        'option': answer.option.pk if answer.option else None,
                        'option_column': answer.option_column.pk if answer.option_column else None,
                        'created': answer.created.strftime(APIView.DATETIME_FORMAT),
                        'modified': answer.modified.strftime(APIView.DATETIME_FORMAT)
                    })
                question['answers'] = answers
                voter_questions.append(question)

            voter_dict['voted_questions'] = voter_questions
            voters.append(voter_dict)

        return self.return_response({'voters': voters})
