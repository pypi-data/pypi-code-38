import requests

from chibi.atlas import Chibi_atlas_ignore_case


class Response:
    def __init__( self, response ):
        self._response = response

    @property
    def headers( self ):
        try:
            return self._headers
        except AttributeError:
            self._headers = Chibi_atlas_ignore_case( self._response.headers )
            return self._headers

    @property
    def body( self ):
        return self._response.text

    @property
    def native( self ):
        try:
            return self._native
        except AttributeError:
            if self.is_json:
                self._native = self.parse_like_json()
            elif self.is_xml:
                self._native = self.parse_like_xml()
            else:
                raise NotImplementedError
            return self._native

    @property
    def content_type( self ):
        return self.headers[ 'Content-Type' ]

    @property
    def is_json( self ):
        return self.content_type == 'application/json'

    @property
    def is_xml( self ):
        return self.content_type == 'application/xml'

    @property
    def status_code( self ):
        return self._response.status_code

    def parse_like_json( self ):
        json_result = self._response.json()
        if isinstance( json_result, list ):
            result = list( json_result )
        elif isinstance( json_result, dict ):
            result = dict( json_result )
        return result

    def parse_like_xml( self ):
        raise NotImplementedError


class Endpoint():
    url = None

    def __init__( self, url=None, **kw ):
        if url is None:
            self._url = self.url
        else:
            self._url = url
        self.parameters = kw

    @property
    def assigned_url( self ):
        if self._url is not None:
            return self._url
        else:
            return self.url

    @property
    def format_url( self ):
        return self._url_format()

    def get( self ):
        response = requests.get( self.format_url )
        return self.build_response( response )

    def build_response( self, response ):
        return Response( response )

    def _url_format( self ):
        return self._url.format( **self.parameters )

    def format( self, **kw ):
        url = self.assigned_url.format( **kw )
        return self.__class__( url, **kw )

    def __copy__( self ):
        return self.__class__( **vars( self ) )

    def __dict__( self ):
        result = { 'url': self._url }
        result.update( self.parameters )
        return result
