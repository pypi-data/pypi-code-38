from sqlalchemy import create_engine

from cnxdb.config import discover_settings


def prepare(settings=None):
    """This function prepares an application/script for use with this codebase.

    :return: an environment dictionary containing the newly created
             ``engines``, ``settings`` and a ``closer`` function.
             The ``engines`` value is a ``sqlalchemy.engine.Engine`` instance
             that can be used to connect to the database.
    :rtype: dict

    .. seealso::
       For instructions on how to use this function see: :ref:`scripting_usage`

    """
    # Get the settings
    settings = discover_settings(settings)
    engines = {
        'common': create_engine(settings['db.common.url']),
        'readonly': create_engine(settings['db.readonly.url']),
        'super': create_engine(settings['db.super.url']),
    }

    def closer():
        for e in engines.values():
            e.dispose()

    return {'closer': closer, 'engines': engines, 'settings': settings}
