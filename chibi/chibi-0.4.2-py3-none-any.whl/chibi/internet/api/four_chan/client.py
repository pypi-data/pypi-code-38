from . import endpoints
from chibi.api import Client as Client_base


class Board( Client_base ):
    def __init__( self, board_name ):
        self.board_name = board_name
        self._format_all_endpoints()

    def threads( self ):
        return self.thread_endpoint.get()

    def _format_all_endpoints( self ):
        self.thread_endpoint = endpoints.threads.format(
            board=self.board_name )
