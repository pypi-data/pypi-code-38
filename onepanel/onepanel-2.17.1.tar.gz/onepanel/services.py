from onepanel.utilities.original_connection import Connection


def get_connection():
    """Creates a connection object and loads the default credentials"""
    conn = Connection()
    conn.load_credentials()

    return conn
