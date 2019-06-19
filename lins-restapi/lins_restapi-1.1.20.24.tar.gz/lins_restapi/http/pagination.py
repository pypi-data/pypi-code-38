from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class Pagination(PageNumberPagination):
    page_size_query_param = 'per_page'

    def get_paginated_response(self, data):
        headers = {
            'X-Total': self.page.paginator.count,
            'X-Page': self.page.number,
            'X-Per-Page': self.get_page_size(self.request),
        }

        envelope = self.request.query_params.get('envelope', None)
        if envelope and envelope in ('t', 1, '1', 'true'):
            data = {
                'total': headers['X-Total'],
                'page': headers['X-Page'],
                'per_page': headers['X-Per-Page'],
                'data': data
            }

        return Response(data=data, headers=headers)
