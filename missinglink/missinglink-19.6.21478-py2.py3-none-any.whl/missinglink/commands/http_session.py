# -*- coding: utf-8 -*-
from missinglink.commands.mali_version import MissinglinkVersion


def create_http_session():
    import requests

    session = requests.session()

    session.headers.update({'User-Agent': 'ml_cli/{}'.format(MissinglinkVersion.get_missinglink_cli_version())})

    return session
