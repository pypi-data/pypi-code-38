"""
Set module version
"""
from pysgs.mailer import Mailer

__author__ = "Esteban Solorzano"
__version__ = '0.1.2'

"""
The default mailer session
"""
MAILER_SESSION = None


def setup_session(**kwargs):
    """
    Set up the mailer session, passing through any parameters
    to the constructor.
    """
    global MAILER_SESSION
    MAILER_SESSION = Mailer(**kwargs)


def mailer(api_key, **kwargs):
    """
    Get the mailer session, creating one if needed.
    :return: The mailer session
    """
    kwargs['api_key'] = api_key

    if MAILER_SESSION is None:
        setup_session(**kwargs)

    return MAILER_SESSION
