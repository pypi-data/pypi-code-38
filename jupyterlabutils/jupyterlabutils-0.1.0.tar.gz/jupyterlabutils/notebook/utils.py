"""Utility functions for LSST JupyterLab notebook environment
"""
import bokeh
import os
from urllib.parse import urljoin


def format_bytes(n):
    """ Format bytes as text

    >>> format_bytes(1)
    '1 B'
    >>> format_bytes(1234)
    '1.23 kB'
    >>> format_bytes(12345678)
    '12.35 MB'
    >>> format_bytes(1234567890)
    '1.23 GB'
    >>> format_bytes(1234567890000)
    '1.23 TB'
    >>> format_bytes(1234567890000000)
    '1.23 PB'

    (taken from dask.distributed, where it is not exported)
    """
    if n > 1e15:
        return '%0.2f PB' % (n / 1e15)
    if n > 1e12:
        return '%0.2f TB' % (n / 1e12)
    if n > 1e9:
        return '%0.2f GB' % (n / 1e9)
    if n > 1e6:
        return '%0.2f MB' % (n / 1e6)
    if n > 1e3:
        return '%0.2f kB' % (n / 1000)
    return '%d B' % n


def get_proxy_url(port):
    """Assumes the LSST environment and that nbserverproxy is running.
    Returns the external address that will resolve to the supplied port
    """
    if not port:
        return None

    base_url = os.environ.get('EXTERNAL_URL') or 'http://localhost:8888'
    service_url_path = os.environ.get('JUPYTERHUB_SERVICE_PREFIX')
    proxy_url_path = 'proxy/{port}'.format(port=port)
    return urljoin(urljoin(base_url, service_url_path), proxy_url_path)


def get_hostname():
    """Utility function to return hostname or, failing that, "localhost".
    """
    return os.environ.get('HOSTNAME') or 'localhost'


def show_with_bokeh_server(obj):
    """Method to wrap bokeh with proxy URL
    """
    def jupyter_proxy_url(port):
        """Construct proxy URL from environment
        """
        # If port is None we're asking about the URL
        # for the origin header.
        return get_proxy_url(port) or '*'

    bokeh.io.show(obj, notebook_url=jupyter_proxy_url)
