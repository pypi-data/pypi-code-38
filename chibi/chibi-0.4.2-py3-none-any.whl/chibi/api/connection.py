from chibi.atlas import Chibi_atlas


class Connections:
    def __init__( self ):
        self._kwargs = {}
        self._connections = {}

    def configure( self, **kw ):
        self._connections = { k: Connection( **v ) for k, v in kw.items() }

    def add( self, name, connection ):
        """
        agrega una nueva connecion

        Parameters
        ==========
        name: string
        connection: `chibi.api.connection.Connection` or dict
        """
        if isinstance( connection, Connection ):
            self._connections[ name ] = connection
        elif isinstance( connection, dict ):
            self._connections[ name ] = Connection( **connection )
        else:
            raise NotImplementedError

    def get( self, alias='default' ):
        if not isinstance( alias, str ):
            raise TypeError(
                "unexpected type '{}' expected '{}'".format(
                    type( alias ), str ) )

        try:
            return self._connections[ alias ]
        except KeyError:
            raise KeyError(
                "there is no connection with name {}".format( alias ) )

    def __getitem__( self, name ):
        return self.get( name )

    def __setitem__( self, name ):
        return self.add( name )


class Connection( Chibi_atlas ):
    pass
