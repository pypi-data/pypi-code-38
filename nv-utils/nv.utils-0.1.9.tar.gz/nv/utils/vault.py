import os

from pathlib import Path

import hvac


def get_vault_client(*args, token_file=None, **kwargs):
    if token_file:
        fp = Path(token_file)
        with fp.open(mode='r') as f:
            token = f.read()
    else:
        token = os.environ.get('VAULT_TOKEN', None)

    kwargs.setdefault('token', token)

    ca_bundle = os.environ.get('VAULT_CACERT', None)
    if ca_bundle:
        kwargs.setdefault('verify', ca_bundle)

    return hvac.Client(*args, **kwargs)
