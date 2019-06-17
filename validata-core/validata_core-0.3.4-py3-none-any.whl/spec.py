import json

import importlib_resources
from toolz import update_in

import goodtables


def _load_spec():
    with importlib_resources.path('validata_core', 'validata_spec.json') as path:
        with path.open() as fp:
            return json.load(fp)


validata_spec = _load_spec()

spec = update_in(goodtables.spec, ['errors'], lambda errors: {**errors, **validata_spec["errors"]})
