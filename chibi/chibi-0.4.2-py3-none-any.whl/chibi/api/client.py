from .connection import Connections


class Client:
    def __init__( self, connection_name='default', _connections=None ):
        if _connections is None:
            self._connections = self._build_connections_class()
        else:
            self._connections = _connections
        self._default_connection_name = connection_name

    def using( self, name ):
        """
        cambia la connecion y crea un nuevo cliente de la misma clase

        Parameters
        ==========
        name: str
            nombre de la connecion que se quiere usar

        Returns
        =======
        py:class`Client`

        Raises
        ======
        KeyError
            cuando no encunetra el nombre de la connecion
        """
        self._connections[ name ]
        return self.__class__( name, _connections=self._connections )

    def extract_connections( self ):
        """
        obtiene las coneciones del cliente

        Returns
        =======
        py:class`chibi.api.connection.Connections`
        """
        return self._connections

    def get_connection( self ):
        """
        Obtiene la connecion actual

        Returns
        =======
        py:class`chibi.api.connection.Connection`
        """
        return self._connections.get( self._default_connection_name )

    def _get_my_connection( self ):
        """
        obtiene la connection asignada a este cliente

        Returns
        =======
        py:class`chibi.api.connection.Connection`
        """
        return self._connecitons.get( self._my_connection_name )

    def _build_connections_class( self ):
        """
        contrulle el objeto de las conneciones

        Returns
        =======
        py:class`chibi.api.connection.Connections`
        """
        return Connections()
