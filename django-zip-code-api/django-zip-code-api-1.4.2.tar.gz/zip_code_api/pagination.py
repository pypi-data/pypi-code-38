# -*- coding: utf-8 -*-
from rest_framework.pagination import PageNumberPagination as RestPageNumberPagination
from rest_framework.response import Response
from zip_code_api.conf import settings

class HeaderPagination(RestPageNumberPagination):
    page_size = settings.ZIP_CODE_PAGE_SIZE

    def get_paginated_response(self, data):
        if hasattr(self, 'page'):
            headers = {
                'X-Page': self.page.number,
                'X-Per-Page': self.page_size,
                'X-Total': self.page.paginator.count,
                'X-Total-Pages': self.page.paginator.num_pages,
                'Access-Control-Expose-Headers': 'X-Page, X-Per-Page, X-Total, X-Total-Pages',
            }

            if self.page.has_next():
                headers['X-Next-Page'] = self.page.next_page_number()
                headers['Access-Control-Expose-Headers'] += ', X-Next-Page'

            if self.page.has_previous():
                headers['X-Prev-Page'] = self.page.previous_page_number()
                headers['Access-Control-Expose-Headers'] += ', X-Prev-Page'
        else:
            headers = {
                'X-Page': 1,
                'X-Per-Page': 0,
                'X-Total': 0,
                'X-Total-Pages': 1,
                'Access-Control-Expose-Headers': 'X-Page, X-Per-Page, X-Total, X-Total-Pages',
            }

        return Response(data, headers = headers)
