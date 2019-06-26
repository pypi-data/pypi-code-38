# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['canonicalwebteam', 'canonicalwebteam.flask_base']

package_data = \
{'': ['*']}

install_requires = \
['canonicalwebteam.yaml-responses[flask]>=1,<2',
 'flask>=1,<2',
 'talisker[gunicorn,flask,prometheus,raven]>=0.14,<0.15']

setup_kwargs = {
    'name': 'canonicalwebteam.flask-base',
    'version': '0.3.1',
    'description': '',
    'long_description': '# Canonical Webteam Flask-Base\n\nFlask extension that applies common configurations to all of webteam\'s flask apps.\n\n## Usage\n\n``` python3\nfrom canonicalwebteam.flask_base.app import FlaskBase\n\napp = FlaskBase(__name__, "app.name")\n```\n\nOr:\n\n``` python3\nfrom canonicalwebteam.flask_base.app import FlaskBase\n\napp = FlaskBase(\n    __name__,\n    "app.name",\n    template_404="404.html",\n    template_500="500.html",\n    favicon_url="/static/favicon.ico",\n)\n```\n\n## Features\n\n### Redirects and deleted paths\n\nFlaskBase uses [yaml-responses](https://github.com/canonical-web-and-design/canonicalwebteam.yaml-responses) to allow easy configuration of redirects and return of deleted responses, by creating `redirects.yaml`, `permanent-redirects.yaml` and `deleted.yaml` in the site root directory.\n\n### Error templates\n\n`FlaskBase` can optionally use templates to generate the `404` and `500` error responses:\n\n``` python3\napp = FlaskBase(\n    __name__,\n    "app.name",\n    template_404="404.html",\n    template_500="500.html",\n)\n```\n\nThis will lead to e.g. `http://localhost/non-existent-path` returning a `404` status with the contents of `templates/404.html`.\n\n### Redirect /favicon.ico\n\n`FlaskBase` can optionally provide redirects for the commonly queried paths `/favicon.ico`, `/robots.txt` and `/humans.txt` to sensible locations:\n\n``` python3\nfrom canonicalwebteam.flask_base.app import FlaskBase\n\napp = FlaskBase(\n    __name__,\n    "app.name",\n    template_404="404.html",\n    template_500="500.html",\n    favicon_url="/static/favicon.ico",\n    robots_url="/static/robots.txt",\n    humans_url="/static/humans.txt"\n)\n```\n\nThis will lead to e.g. `http://localhost/favicon.ico` returning a `302` redirect to `http://localhost/static/favicon.ico`.\n\n### `robots.txt` and `humans.txt`\n\nIf you create a `robots.txt` or `humans.txt` in the root of your project, these will be served at `/robots.txt` and `/humans.txt` respectively.\n\n## Generating setup.py\n\nIn this project, for the time being, we maintain both a `pyproject.toml` for Poetry and a `setup.py` for traditional Python tooling. If you are developing on the module, you should update `pyproject.toml` first and then regenerate the `setup.py` using:\n\n``` bash\npoetry install\npoetry run poetry-setup\n```\n\n## Tests\n\nTo run the tests execute `poetry run python -m unittest discover tests`.\n',
    'author': 'Canonical webteam',
    'author_email': 'webteam@canonical.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
