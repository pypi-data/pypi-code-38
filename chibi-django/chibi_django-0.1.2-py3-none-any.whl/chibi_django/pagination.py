import math

from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param


class Link_header_pagination( pagination.PageNumberPagination ):
    page_size_query_param = 'page_size'

    page_total_count_header = 'X-Pagination-Total-Count'
    page_count_header = 'X-Pagination-Page-Count'
    current_page_header = 'X-Pagination-Current-Page'
    size_page_header = 'X-Pagination-Per-Page'

    def get_paginated_response( self, data, request=None, serializer=None ):
        self.request = request or self.request
        self._data = data
        self._serializer = serializer

        self._generate_page_data()

        next_url = self.get_next_link()
        previous_url = self.get_previous_link()

        link = self.create_header_link( next_url, previous_url )

        headers = self.create_header( link )
        return self.create_response( data, headers )

    def create_header_link( self, next_url, previous_url ):
        if next_url is not None and previous_url is not None:
            link = '<{next_url}>; rel="next", <{previous_url}>; rel="prev"'
        elif next_url is not None:
            link = '<{next_url}>; rel="next"'
        elif previous_url is not None:
            link = '<{previous_url}>; rel="prev"'
        else:
            link = ''
        link = link.format( next_url=next_url, previous_url=previous_url )
        return link

    def create_header( self, link ):
        result = {
            self.page_total_count_header: self._data_count,
            self.page_count_header: min( self._page_size, len( self._data ) ),
            self.current_page_header: self._page_number + 1,
            self.size_page_header: self._page_size
        }
        if link:
            result[ 'Link' ] = link
        return result

    def create_response( self, data, headers ):
        if self._serializer is not None:
            serializer = self._serializer( data, many=True )
            return Response( serializer.data, headers=headers )
        else:
            return Response( data, headers=headers )

    def get_pages( self, data=None ):
        return math.ceil( self._data_count / self._page_size )

    def check_data( self, data ):
        return data

    def check_is_last_page( self ):
        return self._page_number in self.last_page_strings

    def _generate_page_data( self ):
        self.get_data_count()
        self._page_size = self.get_page_size( self.request )
        if self._page_size > 100:
            self._page_size = 100
        self._num_pages = self.get_pages( self._data )
        self._page_number = self.request.query_params.get(
            self.page_query_param, 0 )
        self._page_number = int( self._page_number )

        if self.check_is_last_page():
            self._page_number = self._num_pages

    def get_data_count( self ):
        try:
            self._data_count = self.page.paginator.count
        except:
            self._data_count = len( self._data )


class Paginate_search_es( Link_header_pagination ):
    def get_pages( self, data ):
        return math.ceil( data.count() / self._page_size )

    def create_response( self, data, headers ):
        start = self._page_size * ( self._page_number - 1  )
        if start < 0:
            start = 0
        end = start + self._page_size
        if self._serializer is not None:
            serializer = self._serializer( self._data[ start:end ].execute(),
                                           many=True )
            return Response( serializer.data, headers=headers )
        else:
            data = data[ start:end ].execute()
            result_data = []
            for d in data:
                result_data.append( d.to_dict() )
            return Response( result_data, headers=headers )

    def get_data_count( self ):
        try:
            self._data_count = self.page.paginator.count
        except:
            self._data_count = self._data.count()

    def get_next_link( self ):
        if self._page_number >= self._num_pages:
            return None
        url = self.request.build_absolute_uri()
        page_number = self._page_number + 1
        return replace_query_param( url, self.page_query_param, page_number )

    def get_previous_link( self ):
        if self._page_number == 1:
            return None
        url = self.request.build_absolute_uri()
        page_number = self._page_number - 1
        return replace_query_param( url, self.page_query_param, page_number )
