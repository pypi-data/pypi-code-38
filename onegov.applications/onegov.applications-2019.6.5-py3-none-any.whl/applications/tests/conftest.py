import json
import os
import pkgutil
import pytest


@pytest.fixture(scope="session")
def applications():
    this_path = pkgutil.get_loader('onegov.applications').path
    json_path = os.path.join(os.path.dirname(this_path), 'applications.json')

    with open(json_path) as f:
        applications = json.load(f)

    def include_application(application):
        app = os.environ.get('ONEGOV_APPLICATION', application['package'])
        return app == application['package']

    return [
        (
            application['package'],
            os.path.dirname(pkgutil.get_loader(application['package']).path)
        )
        for application in applications
        if include_application(application)
    ]
