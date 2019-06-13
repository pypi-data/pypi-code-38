import os
from pybis import Openbis
from notebook.base.handlers import IPythonHandler

openbis_connections = {}

def register_connection(connection_info):

    conn = OpenBISConnection(
        name                = connection_info.get('name'),
        url                 = connection_info.get('url'),
        verify_certificates = connection_info.get('verify_certificates', False),
        username            = connection_info.get('username'),
        password            = connection_info.get('password'),
        status              = 'not connected',
    )
    openbis_connections[conn.name] = conn
    return conn


class OpenBISConnection:
    """register an openBIS connection
    """

    def __init__(self, **kwargs):
        for needed_key in ['name', 'url']:
            if needed_key not in kwargs:
                raise KeyError("{} is missing".format(needed_key))

        for key in kwargs:
            setattr(self, key, kwargs[key])

        openbis = Openbis(
            url = self.url,
            verify_certificates = self.verify_certificates
        )
        self.openbis = openbis
        self.status = "not connected"

    def is_session_active(self):
        return self.openbis.is_session_active()

    def check_status(self):
        if self.openbis.is_session_active():
            self.status = "connected"
        else:
            self.status = "not connected"

    def login(self, username=None, password=None):
        if username is None:
            username=self.username
        if password is None:
            password=self.password
        self.openbis.login(
            username = username,
            password = password
        )
        # store username and password in memory
        self.username = username
        self.password = password
        self.status  = 'connected'

    def get_info(self):
        return {
            'name'    : self.name,
            'url'     : self.url,
            'status'  : self.status,
            'username': self.username,
            'password': self.password,
        }

class OpenBISConnections(IPythonHandler):

    def post(self):
        """create a new connection

        :return: a new connection object
        """
        data = self.get_json_body()
        conn = register_connection(data)
        if conn.username and conn.password:
            try:
                conn.login()
            except Exception:
                pass
        self.get()
        return

    def get(self):
        """returns all available openBIS connections
        """

        connections= []
        for conn in openbis_connections.values():
            conn.check_status()
            connections.append(conn.get_info())

        self.write({
            'status'     : 200,
            'connections': connections,
            'cwd'        : os.getcwd()
        })
        return


class OpenBISConnectionHandler(IPythonHandler):
    """Handle the requests to /openbis/conn
    """

    def put(self, connection_name):
        """reconnect to a current connection
        :return: an updated connection object
        """
        data = self.get_json_body()

        try:
            conn = openbis_connections[connection_name]
        except KeyError:
            self.set_status(404)
            self.write({
                "reason" : 'No such connection: {}'.format(data)
            })
            return

        try:
            conn.login(data.get('username'), data.get('password'))
        except ConnectionError:
            self.set_status(500)
            self.write({
                "reason": "Could not establish connection to {}".format(connection_name)
            })
            return
        except ValueError:
            self.set_status(401)
            self.write({
                "reason": "Incorrect username or password for {}".format(connection_name)
            })
            return

        self.write({
            'status'     : 200,
            'connection': conn.get_info(),
            'cwd'        : os.getcwd()
        })

    def get(self, connection_name):
        """returns  information about a connection name
        """

        try:
            conn = openbis_connections[connection_name]
        except KeyError:
            self.set_status(404)
            self.write({
                "reason" : 'No such connection: {}'.format(connection_name)
            })
            return

        conn.check_status()

        self.write({
            'status'     : 200,
            'connection': conn.get_info(),
            'cwd'        : os.getcwd()
        })
        return

