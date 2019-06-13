from notebook.utils import url_path_join
import os
import yaml

from .connection import OpenBISConnections, OpenBISConnectionHandler, register_connection
from .dataset import DataSetTypesHandler, DataSetDownloadHandler, DataSetUploadHandler, FileListHandler
from .sample import SampleHandler


def _jupyter_server_extension_paths():
    return [{'module': 'jupyter-openbis-extension.server'}]

def _load_configuration(paths, filename='openbis-connections.yaml'):

    if paths is None:
        paths = []
        home = os.path.expanduser("~")
        paths.append(os.path.join(home, '.jupyter'))

    # look in all config file paths of jupyter
    # for openbis connection files and load them
    connections = []
    for path in paths:
        abs_filename = os.path.join(path, filename)
        if os.path.isfile(abs_filename):
            with open(abs_filename, 'r') as stream:
                try:
                    config = yaml.safe_load(stream)
                    for connection in config['connections']:
                        connections.append(connection)
                except yaml.YAMLexception as e:
                    print(e)
                    return None

    return connections
        

def load_jupyter_server_extension(nb_server_app):
    """Call when the extension is loaded.
    :param nb_server_app: Handle to the Notebook webserver instance.
    """

    # load the configuration file
    # and register the openBIS connections.
    # If username and password is available, try to connect to the server
    connections = _load_configuration(
        paths    = nb_server_app.config_file_paths,
        filename = 'openbis-connections.yaml'
    )

    for connection_info in connections:
        conn = register_connection(connection_info)
        print("Registered: {}".format(conn.url))
        if conn.username and conn.password:
            try:
                conn.login()
                print("Successfully connected to: {}".format(conn.url))
            except ValueError:
                print("Incorrect username or password for: {}".format(conn.url))
            except Exception:
                print("Cannot establish connection to: {}".format(conn.url))

    # Add URL handlers to our web_app
    # see Tornado documentation: https://www.tornadoweb.org
    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    base_url = web_app.settings['base_url']

    # get the file list
    web_app.add_handlers(
        host_pattern,
        [(url_path_join( base_url, '/general/filelist'),
            FileListHandler
        )]
    )


    # DataSet download
    web_app.add_handlers(
        host_pattern, 
        [(url_path_join(
            base_url,
            '/openbis/dataset/(?P<connection_name>.*)?/(?P<permId>.*)?/(?P<downloadPath>.*)'), 
            DataSetDownloadHandler
        )]
    )

    # DataSet upload
    web_app.add_handlers( host_pattern, [(
            url_path_join( base_url, '/openbis/dataset/(?P<connection_name>.*)' ),
            DataSetUploadHandler
        )]
    )

    # DataSet-Types
    web_app.add_handlers(
        host_pattern,
        [(
            url_path_join( base_url, '/openbis/datasetTypes/(?P<connection_name>.*)'
            ),
            DataSetTypesHandler
        )]
    )

    # DataSets for Sample identifier/permId
    web_app.add_handlers(
        host_pattern, 
        [(  
            url_path_join(
                base_url,
                '/openbis/sample/(?P<connection_name>.*)?/(?P<identifier>.*)'
            ), 
            SampleHandler
        )]
    )

    # OpenBIS connections
    web_app.add_handlers(
        host_pattern,
        [(
            url_path_join(
                base_url,
                '/openbis/conns'
            ),
            OpenBISConnections
        )]
    )

    # Modify / reconnect to a connection
    web_app.add_handlers(
        host_pattern, 
        [(
            url_path_join(
                    base_url,
                    '/openbis/conn/(?P<connection_name>.*)'
            ),
            OpenBISConnectionHandler
        )]
    )


