import json
import pytz

from django.conf import settings
from django.contrib.gis.geoip import GeoIP
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from votebase.api.views import APIView, BasicAuthMixin
from votebase.core.questions.models import Question, Option
from votebase.core.surveys.models import Round
from votebase.core.utils import mail
from votebase.core.voting.models import Voter, VotedQuestion, Answer


class VotingView(BasicAuthMixin, APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, **kwargs):
        try:
            segment = Round.objects.get(pk=kwargs.get('segment_pk'))
            survey = segment.survey

            if survey.user != self.api_user:
                return self.return_error_response(HttpResponseForbidden, message='It is not your segment.')

        except ObjectDoesNotExist:
            return self.return_error_response(HttpResponseNotFound, message='Segment not found.')

        if not segment.is_active:
            return self.return_error_response(HttpResponseForbidden, message='Segment is not active.')

        if not segment.is_date_in_range():
            return self.return_error_response(HttpResponseForbidden, message='Segment is not active now.')

        if not request.body:
            return self.return_error_response(HttpResponseBadRequest, message='POST data are missing.')

        try:
            data = json.loads(request.body)
        except ValueError as e:
            return self.return_error_response(HttpResponseBadRequest, message='Request POST data is in incorrect format.')

        voter = data.get('voter', None)
        if voter is None:
            return self.return_error_response(HttpResponseBadRequest, message='Voter data are missing.')

        if 'user_id' in voter:
            # Check basic auth in BasicAuthMixin
            if not self.is_authenticated(request):
                return self.challenge()

            if not request.user.is_authenticated() or request.user.is_authenticated() and voter['user_id'] != request.user.pk:
                return self.return_error_response(HttpResponseForbidden, message='Invalid user id')

            # Repeatable voting
            if not segment.is_repeatable and segment.user_already_voted(request.user):
                return self.return_error_response(HttpResponseForbidden, message='User already voted in this segment and repeatable voting in this segment is not permitted.')
        else:
            # Permission restriction
            if segment.permission_level == Round.PERMISSION_LEVEL_REGISTERED and not request.user.is_authenticated():
                return self.return_error_response(HttpResponseForbidden, message='This segment is available for registered users only.')

        if segment.is_secured():
            if not 'password' in data:
                return self.return_error_response(HttpResponseForbidden, message='Segment is secured by password.')

            password = data.get('password')
            if segment.password != password:
                return self.return_error_response(HttpResponseForbidden, message='Password is incorrect.')

        voted_questions = data.get('voted_questions', None)
        if voted_questions is None:
            return self.return_error_response(HttpResponseBadRequest, message='Voted questions data are missing.')

        answers = data.get('answers', None)
        if answers is None:
            return self.return_error_response(HttpResponseBadRequest, message='Answers data are missing.')

        #data = {
        #    'voter': {
        #        'user_id': 123,  # optional
        #        'voting_started' voting_started,
        #    },
        #    'voted_questions': [question1.pk, question2.pk, question3.pk, question4.pk],
        #    'answers': [
        #        {
        #            'question_id': question.pk,
        #            'option_id': option.pk,
        #            'option_column_id': option_column.pk,
        #            'custom': 'Abrakadabra'
        #        },{
        #            'question_id': question.pk,
        #            'custom': 'erik',
        #        },{
        #            'question_id': question.pk,
        #            'option_id': option.pk,
        #        },{
        #            'question_id': question.pk,
        #            'option_id': option.pk,
        #        },
        #    ]

        # Geolocation
        g = GeoIP()
        location = g.city(request.META['REMOTE_ADDR']) or {}

        # get voting time details
        voting_started = voter.get('voting_started', None)
        if voting_started is None:
            return self.return_error_response(HttpResponseBadRequest, message="Voter's voting_started attribute is missing.")

        try:
            from dateutil import parser
            voting_started = parser.parse(voting_started)
            voting_started = voting_started.astimezone(pytz.timezone(settings.TIME_ZONE))
        except (TypeError, ValueError):
            return self.return_error_response(HttpResponseBadRequest, message='voting_started attribute is in incorrect format. It must be in %s format.' % APIView.DATETIME_FORMAT)

        voting_ended = now()
        voting_ended = voting_ended.astimezone(pytz.timezone(settings.TIME_ZONE))

        if voting_ended < voting_started:
            return self.return_error_response(HttpResponseBadRequest, message='voting_started attribute has incorrect value. It has to be before %s and it is %s' % (voting_ended.strftime(APIView.DATETIME_FORMAT), voting_started.strftime(APIView.DATETIME_FORMAT)))

        voting_duration = (voting_ended - voting_started).seconds

        # Create voter
        voter = Voter.objects.create(
            ip_address=request.META.get('REMOTE_ADDR', ''),
            survey=survey,
            round=segment,
            latitude=location.get('latitude', None),
            longitude=location.get('longitude', None),
            continent_code=location.get('continent_code', None),
            country_name=location.get('country_name', None),
            country_code=location.get('country_code', None),
            city=location.get('city', None),
            area_code=location.get('area_code', None),
            voting_started=voting_started,
            voting_ended=voting_ended,
            voting_duration=voting_duration,
            is_api_voter=True
        )

        if request.user.is_authenticated():
            voter.user = request.user
            voter.save()

        # Save all answers
        questions_in_answers_pks = []
        for index, answer in enumerate(answers):
            question_pk = answer.get('question_id', None)
            questions_in_answers_pks.append(question_pk)

            if question_pk is None:
                voter.delete()
                return self.return_error_response(HttpResponseBadRequest, message='Question id in answer data is missing.')
            else:
                try:
                    question_pk = int(question_pk)
                    question = Question.objects.get(pk=int(question_pk))
                except TypeError:
                    voter.delete()
                    return self.return_error_response(HttpResponseBadRequest, message='Question id attribute is in incorrect format.' % question_pk)
                except ObjectDoesNotExist:
                    voter.delete()
                    return self.return_error_response(HttpResponseBadRequest, message='Question with id %s does not exist.' % question_pk)

            # check if question belongs to survey
            if question.survey != survey:
                voter.delete()
                return self.return_error_response(HttpResponseBadRequest, message='Question with id %s does not belong to survey of segment with id %s.' % (question_pk, segment.pk))

            option_pk = answer.get('option_id', None)
            if option_pk is not None:
                try:
                    option = Option.objects.get(pk=int(option_pk), orientation=Option.ORIENTATION_ROW)
                except TypeError:
                    voter.delete()
                    return self.return_error_response(HttpResponseBadRequest, message='Option id attribute %s is in incorrect format.' % option_pk)
                except ObjectDoesNotExist:
                    voter.delete()
                    return self.return_error_response(HttpResponseBadRequest, message='Option with id %s does not exist.' % option_pk)

                # check if option belongs to question
                if option.question != question:
                    voter.delete()
                    return self.return_error_response(HttpResponseBadRequest, message='Option with id %s does not belong to question with id %s.' % (option_pk, question_pk))
            else:
                option = None

            option_column_pk = answer.get('option_column_id', None)
            if option_column_pk is not None:
                try:
                    option_column = Option.objects.get(pk=int(option_column_pk), orientation=Option.ORIENTATION_COLUMN)
                except TypeError:
                    voter.delete()
                    return self.return_error_response(HttpResponseBadRequest, message='Option column id attribute %s is in incorrect format.' % option_column_pk)
                except ObjectDoesNotExist:
                    voter.delete()
                    return self.return_error_response(HttpResponseBadRequest, message='Option column with id %s does not exist.' % option_column_pk)

                # check if option_column belongs to question
                if option_column.question != question:
                    voter.delete()
                    return self.return_error_response(HttpResponseBadRequest, message='Option with id %s does not belong to question with id %s.' % (option_pk, question_pk))
            else:
                option_column = None

            # TODO:
            # check if question accepts custom value

            Answer.objects.create(
                voter=voter,
                question=question,
                custom=answer.get('custom', None),
                option=option,
                option_column=option_column
            )

        # check if voted_questions is list of unique values
        if len(voted_questions) != len(set(voted_questions)):
            voter.delete()
            return self.return_error_response(HttpResponseBadRequest, message='voted_questions attribute has to be list of unique items')

        # Get list of all required questions (pks)
        required_questions_pks = set(survey.question_set.filter(is_required=True).values_list('pk', flat=True))

        # Check if voter voted in all required questions (voted_questions)
        if not required_questions_pks.issubset(set(voted_questions)):
            voter.delete()
            return self.return_error_response(HttpResponseBadRequest, message='voted_questions attribute does not contain all required questions.')

        # Check if voter voted in all required questions (answers)
        if not required_questions_pks.issubset(set(questions_in_answers_pks)):
            voter.delete()
            return self.return_error_response(HttpResponseBadRequest, message='answers attribute does not contain all required questions.')

        #  Save voted questions list of voter
        unique_voted_questions = []
        for index, question_pk in enumerate(voted_questions):
            if question_pk in unique_voted_questions:
                continue
            unique_voted_questions.append(question_pk)

            try:
                question = Question.objects.get(pk=int(question_pk))
                VotedQuestion.objects.create(
                    voter=voter,
                    question=question,
                    weight=index
                )
            except TypeError:
                voter.delete()
                return self.return_error_response(HttpResponseBadRequest, message='Voted questions data are in incorrect format.')
            except ObjectDoesNotExist:
                voter.delete()
                return self.return_error_response(HttpResponseBadRequest, message='Question with id %s does not exist.' % question_pk)

        # Save voter quiz result
        if survey.is_quiz():
            voter.quiz_result = voter.get_quiz_result()
            voter.save()

            # Send email with quiz results to voter if permitted
            if segment.is_quiz_result_visible and voter:
                if voter.user:
                    voter.send_quiz_result()

        # Send email about new voter if necessary
        try:
            if not segment.voter_set.count() % segment.email_treshold:
                mail.new_voters(segment, request)
        except ZeroDivisionError:
            pass

        voter_json = {
            'id': voter.pk,
            'user_id': voter.user.pk if voter.user else None,
            'segment_id': voter.round.pk,
            'quiz_result': voter.quiz_result,
            'hash_key': voter.hash_key,
            'ip_address': voter.ip_address,
            'latitude': voter.latitude,
            'longitude': voter.longitude,
            'continent_code': voter.continent_code,
            'country_code': voter.country_code,
            'country_name': voter.country_name,
            'city': voter.city,
            'area_code': voter.area_code,
            'voting_started': voter.voting_started.strftime(APIView.DATETIME_FORMAT) if voter.voting_started else None,
            'voting_ended': voter.voting_ended.strftime(APIView.DATETIME_FORMAT) if voter.voting_ended else None,
            'voting_duration': voter.voting_duration,
            'flag': voter.flag,
            'is_api_voter': voter.is_api_voter,
            'is_irrelevant': voter.is_irrelevant,

            'created': voter.created.strftime(APIView.DATETIME_FORMAT),
            'modified': voter.modified.strftime(APIView.DATETIME_FORMAT)
        }

        return self.return_response({
            #'code': 200,
            'message': 'Voting successfully saved.',
            'voter': voter_json
        })
