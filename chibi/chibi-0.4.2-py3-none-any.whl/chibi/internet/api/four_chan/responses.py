from chibi.api.endpoint import Response
from chibi.atlas import Chibi_atlas
from functools import reduce
import datetime


class Thread_list( Response ):
    def __init__( self, *args, board, **kw ):
        super().__init__( *args, **kw )
        self.board = board

    @property
    def native( self ):
        try:
            return self._native
        except AttributeError:
            from chibi.internet.api.four_chan.endpoints import Thread
            raw_list = self._response.json()
            threads = reduce(
                ( lambda x, y: x + y ),
                ( page[ 'threads' ] for page in raw_list ) )

            self._native = [
                Thread(
                    board=self.board, thread_number=t[ 'no' ],
                    last_modified=t[ 'last_modified' ] )
                for t in threads ]
            return self._native


class Post( Chibi_atlas ):
    def __init__( self, *args, time, **kw ):
        from chibi.internet.api.four_chan.endpoints import Download_image
        time = datetime.datetime.fromtimestamp( time )
        if 'filename' in kw:
            image_url = Download_image(
                board=kw[ 'board' ], image=kw[ 'tim' ], ext=kw[ 'ext' ] )
            has_image = True
        else:
            image_url = None
            has_image = False
        super().__init__(
            *args, time=time, image_url=image_url, has_image=has_image, **kw )


class Post_list( Response ):
    def __init__( self, *args, board, **kw ):
        super().__init__( *args, **kw )
        self.board = board

    @property
    def native( self ):
        try:
            return self._native
        except AttributeError:
            raw_list = self._response.json()[ 'posts' ]

            self._native = [
                Post( board=self.board, **post ) for post in raw_list ]
            return self._native
