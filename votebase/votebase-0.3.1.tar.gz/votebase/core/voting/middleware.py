from django.http import Http404
from django.shortcuts import redirect
from django.utils import translation


class VotingFallbackMiddleware:
    def process_response(self, request, response):
        if response.status_code != 404:
            return response

        translation.activate(request.LANGUAGE_CODE)
        path = request.path_info.strip('/')
        path = path.strip('v/')

        try:
            round_pk = 0

            if not path.count('/'):
                if path.isdigit():
                    round_pk = path
            else:
                segments = path.split('/')
                if segments[0].isdigit():
                    round_pk = segments[0]
            if round_pk:
                return redirect('voting_vote', pk=round_pk)
        except Http404:
            return response
        return response
