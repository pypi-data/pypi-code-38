import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest

#from ....views import APIView
from votebase.api.views import APIView, BasicAuthMixin
from votebase.core.surveys.models import Survey, Round


class SurveysView(APIView):
    def get(self, request):
        surveys = Survey.objects.by_user(self.api_user)
        result = []
        for survey in surveys:
            result.append({
                'id': survey.pk,
                'title': survey.title,
                'hash_key': survey.hash_key,
                'preface': survey.preface,
                'postface': survey.postface,
                'css': survey.css,
                'is_visible': survey.is_visible,
                'created': survey.created.strftime(APIView.DATETIME_FORMAT),
                'modified': survey.modified.strftime(APIView.DATETIME_FORMAT)
            })
        return self.return_response({'surveys': result})


class SurveyView(BasicAuthMixin, APIView):
    def get(self, request, **kwargs):
        try:
            survey = Survey.objects.by_user(self.api_user).get(pk=kwargs.get('pk'))
        except ObjectDoesNotExist:
            return self.return_error_response(HttpResponseNotFound, message='Survey not found.')

        show_correct_options = False
        show_password = False
        if self.is_auth_string_present(request):
            if not self.is_authenticated(self.request):
                return self.return_error_response(HttpResponseForbidden, message='Invalid credentials.')
            else:
                show_correct_options = self.request.user == survey.user
                show_password = self.request.user == survey.user

        segments = []
        for segment in survey.round_set.all():
            segment_dict = {
                'id': segment.pk,
                #'ancestor': segment.ancestor.pk,
                'title': segment.title,
                'slug': segment.slug,
                'hash_key': segment.hash_key,
                'duration': segment.duration,
                'date_from': segment.date_from.strftime(APIView.DATETIME_FORMAT) if segment.date_from else None,
                'date_to': segment.date_to.strftime(APIView.DATETIME_FORMAT) if segment.date_to else None,
                'permission_level': segment.permission_level,
                'statistics_policy': segment.statistics_policy,
                'is_secured': segment.is_secured(),
                'count_questions': segment.count_questions,
                'finish_url': segment.finish_url,
                'finish_url_title': segment.finish_url_title,
                'email_threshold': segment.email_treshold,
                'is_active': segment.is_active,
                'is_anonymous': segment.is_anonymous,
                'is_repeatable': segment.is_repeatable,
                'is_quiz_result_visible': segment.is_quiz_result_visible,
                'is_quiz_correct_options_visible': segment.is_quiz_correct_options_visible,
                'is_viewable': segment.is_viewable,
                'is_shuffle': segment.is_shuffle,
                'created': segment.created.strftime(APIView.DATETIME_FORMAT),
                'modified': segment.modified.strftime(APIView.DATETIME_FORMAT)
            }

            # show password only if user is authenticated and it is survey creator
            if show_password:
                segment_dict.update({
                    'password': segment.password
                })

            segments.append(segment_dict)

        questions = []
        for question in survey.question_set.all().order_by('weight'):
            options = []
            for option in question.option_set.all().order_by('weight'):
                option_dict = {
                    'id': option.id,
                    'title': option.title,
                    'image': option.image_in_base64,
                    'image_url': u'%s%s' % (settings.HOST_URL, option.image.url) if option.image else None,
                    'image_width': option.image_width if option.image else None,
                    'image_height': option.image_height if option.image else None,
                    'image_position': option.image_position if option.image else None,
                    'orientation': option.orientation,
                    'weight': option.weight,
                    'created': option.created.strftime(APIView.DATETIME_FORMAT),
                    'modified': option.modified.strftime(APIView.DATETIME_FORMAT)
                }

                # only survey creator can see correct options of quiz question!
                if question.is_quiz and show_correct_options:
                    option_dict.update({'is_correct': option.is_correct})

                options.append(option_dict)

            questions.append({
                'id': question.id,
                'kind': question.kind,
                'title': question.title,
                'category': question.category,
                'image': question.image_in_base64,
                'image_url': u'%s%s' % (settings.HOST_URL, question.image.url) if question.image else None,
                'image_width': question.image_width if question.image else None,
                'image_height': question.image_height if question.image else None,
                'image_position': question.image_position if question.image else None,
                'weight': question.weight,
                'is_required': question.is_required,
                'is_quiz': question.is_quiz,
                'created': question.created.strftime(APIView.DATETIME_FORMAT),
                'modified': question.modified.strftime(APIView.DATETIME_FORMAT),
                'options': options
            })

        result = {
            'id': survey.pk,
            'title': survey.title,
            'hash_key': survey.hash_key,
            'preface': survey.preface,
            'postface': survey.postface,
            'css': survey.css,
            'is_visible': survey.is_visible,
            'created': survey.created.strftime(APIView.DATETIME_FORMAT),
            'modified': survey.modified.strftime(APIView.DATETIME_FORMAT),
            'segments': segments,
            'questions': questions,
        }
        return self.return_response(result)


class SegmentView(BasicAuthMixin, APIView):
    def get(self, request, **kwargs):
        try:
            segment = Round.objects.by_user(self.api_user).get(pk=kwargs.get('pk'))
        except ObjectDoesNotExist:
            return self.return_error_response(HttpResponseNotFound, message='Segment not found.')

        show_password = False
        if self.is_auth_string_present(request):
            if not self.is_authenticated(self.request):
                return self.return_error_response(HttpResponseForbidden, message='Invalid credentials.')
            else:
                show_password = self.request.user == segment.survey.user

        result = {
            #'id': segment.pk,
            'survey_id': segment.survey.pk,
            #'ancestor': segment.ancestor.pk,
            'title': segment.title,
            'slug': segment.slug,
            'hash_key': segment.hash_key,
            'duration': segment.duration,
            'date_from': segment.date_from.strftime(APIView.DATETIME_FORMAT) if segment.date_from else None,
            'date_to': segment.date_to.strftime(APIView.DATETIME_FORMAT) if segment.date_to else None,
            'is_secured': segment.is_secured(),
            'permission_level': segment.permission_level,
            'statistics_policy': segment.statistics_policy,
            'count_questions': segment.count_questions,
            'finish_url': segment.finish_url,
            'finish_url_title': segment.finish_url_title,
            'email_threshold': segment.email_treshold,
            'is_active': segment.is_active,
            'is_anonymous': segment.is_anonymous,
            'is_repeatable': segment.is_repeatable,
            'is_quiz_result_visible': segment.is_quiz_result_visible,
            'is_quiz_correct_options_visible': segment.is_quiz_correct_options_visible,
            'is_viewable': segment.is_viewable,
            'is_shuffle': segment.is_shuffle,
            'created': segment.created.strftime(APIView.DATETIME_FORMAT),
            'modified': segment.modified.strftime(APIView.DATETIME_FORMAT)
        }

        # show password only if user is authenticated and it is survey creator
        if show_password:
            result.update({
                'password': segment.password
            })
        return self.return_response(result)


class SegmentUpdateView(BasicAuthMixin, APIView):
    def post(self, request, **kwargs):
        # Check basic auth in BasicAuthMixin
        if not self.is_authenticated(request):
            return self.challenge()

        try:
            segment = Round.objects.by_user(self.api_user).get(pk=kwargs.get('pk'))
        except ObjectDoesNotExist:
            return self.return_error_response(HttpResponseNotFound, message='Segment not found.')

        if segment.survey.user != request.user:
            return self.return_error_response(HttpResponseForbidden, message='It is not your segment.')

        is_segment_changed = False

        if request.POST:
            try:
                data = json.loads(request.body)
            except ValueError:
                return self.return_error_response(HttpResponseBadRequest, message='Request POST data is in incorrect format.')

            if 'is_active' in data:
                is_active = data.get('is_active')
                if segment.is_active != is_active:
                    is_segment_changed = True
                    segment.is_active = is_active
                    segment.save()

        message = 'Segment successfully updated.' if is_segment_changed else 'Nothing changed.'

        return self.return_response({
            #'code': 200,
            'message': message
        })
