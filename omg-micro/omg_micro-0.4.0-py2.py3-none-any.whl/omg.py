import logging
import os
import sys
import traceback

import waitress
import yaml
from docopt import docopt
from flask import Flask, Response, jsonify, make_response, request
from inflection import camelize, underscore
from setproctitle import setproctitle

__all__ = ['Service']

DEFAULT_PORT = '8080'
DEFAULT_ARG_TYPE = str
PORT = int(os.environ.get('PORT', DEFAULT_PORT))
YAML_TEMPLATE = """
omg: 1
lifecycle:
  startup:
    command: ["python3", "/app/service.py"]
info:
  version: 0.0.0
  title: XXXXXX
  description: XXXXXX
  contact:
    name: XXXXXX
    url: XXXXXX
    email: XXXXXX
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT
actions:
""".strip()


class MicroserviceDockerfile:
    @property
    def _dockerfile_path(self):
        return './Dockerfile'

    def ensure_dockerfile(self, skip_if_exists=True):
        if skip_if_exists:
            if os.path.isfile(os.path.abspath(self._dockerfile_path)):
                print(f'Dockerfile {self._dockerfile_path!r} already exists!')
            else:
                print(f'Writing {self._dockerfile_path!r} to disk.')

                # Write the template Dockerfile to disk.
                with open(self._dockerfile_path, 'w') as f:
                    f.write(DOCKERFILE_TEMPLATE)


# @logme.log
class MicroserviceYML:
    @property
    def _yaml_path(self):
        return './microservice.yml'

    @staticmethod
    def _yaml_type_for_annotation(t):
        mapping = {
            int: 'int',
            float: 'float',
            str: 'string',
            list: 'list',
            dict: 'map',
            bool: 'boolean',
            'any': 'any',
        }

        return mapping[t]

    def _render(self):
        data = yaml.safe_load(YAML_TEMPLATE)
        data['actions'] = {}

        for endpoint in self.endpoints.values():

            annotations = endpoint['f'].__annotations__.copy()

            data['actions'][endpoint['name']] = {
                'help': endpoint['f'].__doc__,
                'output': {
                    'type': self._yaml_type_for_annotation(
                        # Default to 'any' type for inoming type annotations.
                        # Also, remove 'return', since we don't need it later.
                        annotations.pop('return', 'any')
                    )
                },
                'http': {
                    'path': endpoint['path'],
                    'method': endpoint['method'],
                    'port': PORT,
                },
            }

            # Add argument information, if available.
            if annotations:
                data['actions'][endpoint['name']]['arguments'] = {}

                for arg in annotations:
                    data['actions'][endpoint['name']]['arguments'][arg] = {
                        'type': self._yaml_type_for_annotation(
                            annotations[arg]
                        ),
                        'required': True,
                        'in': 'query',
                    }

        return data

    def ensure_yaml(self, skip_if_exists=True):
        if skip_if_exists:
            if os.path.isfile(os.path.abspath(self._yaml_path)):
                print(
                    f'Microservice Manifest {self._yaml_path!r} already exists!'
                )
            else:
                print(f'Writing {self._yaml_path!r} to disk.')
                with open(self._yaml_path, 'w') as f:
                    f.write(yaml.safe_dump(self._render()))

        else:
            with open(self._yaml_path, 'w') as f:
                f.write(yaml.safe_dump(self._render()))


# @logme.log
class Microservice(MicroserviceYML, MicroserviceDockerfile):
    def __init__(self, name, root_path='.'):
        self.logger = logging.getLogger(__name__)
        self.name = name
        self.root_path = os.path.abspath(root_path)
        self.endpoints = {}

        print(f'Initiating {self.name!r} service.')

        self.flask = Flask(__name__)

    def ensure(self, skip_if_exists=True):
        # Ensure the Dockerfile exists.
        self.ensure_dockerfile(skip_if_exists=skip_if_exists)

        # Ensure the YAML exists.
        self.ensure_yaml(skip_if_exists=skip_if_exists)

    def serve(self, ensure=False, **kwargs):
        # Set the process title.
        setproctitle(self.name)

        # Ensure, if needed.
        if ensure:
            self.ensure()

        # Bind to PORT, automatically.
        listen = f'*:{PORT}'
        if 'listen' in kwargs:
            listen = kwargs.pop('listen')

        # Serve the service.
        waitress.serve(app=self.flask, listen=listen, **kwargs)

    def add(
        self, f, *, name: str = None, path: str = None, method: str = 'get'
    ):
        # Infer the service name.
        name = name or camelize(f.__name__)
        # Infer the service URI. Note: Expects '/', like Flask.
        path = path or f'/{underscore(name)}'

        # Store the service, for later use.
        self.endpoints[name] = {
            'name': name,
            'path': path,
            'f': f,
            'method': method,
        }

        self._register_endpoints()

    def register(
        self, name: str = None, path: str = None, method: str = 'get'
    ):
        def decorator(f):
            self.add(f=f, path=path, method=method)
            return f

        return decorator

    def _register_endpoint(self, service):
        f = service['f']
        rule = service['path']
        endpoint = service['name']

        def view_func(**kwargs):

            # Check type annoytations of enpoint function,
            # Flag query parameters as usable, if it appears to be applicable.

            params = {}
            json = request.get_json()

            # Whitelist function arguments.
            for arg in f.__annotations__:
                if arg in request.args:
                    params[arg] = request.args[arg]

                if json:
                    if arg in json:
                        params[arg] = json[arg]

                # TODO:; grab values from HTTP Headers.
                # TODO:  gab balues from multipart upload.

            # Pass all query parameters as function arguments, if applicable.
            print(f'Calling {rule!r} with args: {params!r}.')

            # Call the function.
            try:
                result = f(**params)
            except TypeError:
                keys = repr([v for v in f.__annotations__.keys()])
                result = make_response(
                    f"Invalid parameters passed. Expected: {keys}", 412
                )
                self.logger.warn(
                    f'Calling {rule!r} with args: {params!r} failed!'
                )

            # Return the result immediately, if it is a Flask Response.
            if isinstance(result, Response):
                return result

            # Return the result, relying on JSON, then falling back to bytes.
            try:
                return jsonify(result)
            except ValueError:
                return result

        try:
            self.flask.add_url_rule(
                rule=rule, endpoint=endpoint, view_func=view_func
            )
            print(f'Registering Flask endpoint: {rule!r}')

        except AssertionError:
            # TODO: Fix this.
            pass

    def _register_endpoints(self):
        for endpoint in self.endpoints.values():
            self._register_endpoint(endpoint)


def import_entrypoint(entrypoint):
    # Remove .py from specified entrypoint (developer experience).
    entrypoint = entrypoint.replace('.py', '')

    if ':' in entrypoint:
        split = entrypoint.split(':')
        if len(split) > 2:
            print(
                "Please provide the entrypoint in 'module:microservice' format."
            )
            sys.exit(1)
        import_name = split[0]
        microservice = split[1]

    else:
        import_name = entrypoint
        microservice = 'service'

    module = __import__(import_name)
    return getattr(module, microservice)


def cli():
    """OMG.py Generator.

Usage:
  omg-generate [<entrypoint>]

Generates a microservice.yml file, based on the omg.py Microservice entrypoint given.

Options:
  -h --help     Show this screen.
    """

    sys.path += [os.getcwd()]
    args = docopt(cli.__doc__)
    entrypoint = args['<entrypoint>']

    # Sane defaults.
    entrypoint = entrypoint if entrypoint else 'service:service'

    # Import the microservice.
    try:
        service = import_entrypoint(entrypoint=entrypoint)
    except (ImportError, ModuleNotFoundError) as e:
        print(f'Problem importing {entrypoint!r}.')
        traceback.print_traceback(e)
        print('Aborting.')
        sys.exit(1)

    # Run ensure on microservice.
    try:
        service = service.ensure(skip_if_exists=False)
        print()
        print('{!r} written to disk!'.format('microservice.yml'))
    except AttributeError:
        print(
            f'The entrypoint provided ({entrypoint!r}) does not appear to be a Microservice instance.'
        )
        print('Aborting.')
        sys.exit(1)


if __name__ == '__main__':
    cli()
