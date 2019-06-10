import datetime
from chibi.api import Endpoint
from chibi.internet.api.four_chan.responses import (
    Thread_list as Thread_list_response,
    Post_list as Post_list_response,
)
from chibi.net import download


class Thread_list( Endpoint ):
    def build_response( self, response ):
        return Thread_list_response(
            response, board=self.parameters[ 'board' ])


class Thread( Endpoint ):
    url = 'http://a.4cdn.org/{board}/thread/{thread_number}.json'

    def __init__( self, *args, thread_number, last_modified, **kw ):
        self.thread_number = int( thread_number )
        self.last_modified = datetime.datetime.fromtimestamp( last_modified )
        return super().__init__(
            *args, thread_number=self.thread_number,
            last_modified=self.last_modified, **kw )

    def __repr__( self ):
        return "Thread( url={}, last_modifed={})".format(
            self.format_url, self.parameters[ 'last_modified' ] )

    def build_response( self, response ):
        return Post_list_response( response, board=self.parameters[ 'board' ] )


class Download_image( Endpoint ):
    url = 'http://i.4cdn.org/{board}/{image}{ext}'

    def __repr__( self ):
        return "image( url={} )".format( self.format_url, )

    def download( self, directory=None, file_name=None ):
        return download(
            self.format_url, directory=directory, file_name=file_name )


threads = Thread_list( 'http://a.4cdn.org/{board}/threads.json' )
