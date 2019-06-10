# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""HTTP server that offers part of AML SDK functionality."""

import argparse
from contextlib import closing
import functools
import logging
import os
import random
import re
import shlex
import socket
import string
import sys
import urllib.parse

from azureml.exceptions import AuthenticationException, ProjectSystemException, AzureMLException
import azureml.contrib.server.sdk as sdk

logger = logging.getLogger(__name__)
app_secret = [None]  # boxed string to initialize this later

flaskInstalled = True
try:
    from flask import Flask, request, jsonify, make_response, Response
    from werkzeug.routing import PathConverter
except ImportError as e:
    flaskInstalled = False

    class _DummyApp(object):
        def route(self, *args, **kwargs):
            return lambda x: x

        def errorhandler(self, *args, **kwargs):
            return lambda x: x

        def run(self, *args, **kwargs):
            pass
    app = _DummyApp()
else:
    # custom converter needed because flask's built-in ones don't support slashes, encoded or not
    class _RawConverter(PathConverter):
        regex = '.*?'
    app = Flask(__name__)
    app.url_map.converters['raw'] = _RawConverter


class ClientError(AzureMLException):
    """Exception that maps to a HTTP 400 response."""

    def __init__(self, message, status_code=400):
        """Constructor."""
        super(ClientError, self).__init__(message)
        self.status_code = status_code


class BadArgumentsException(ClientError):
    """Exception from incorrect arguments received."""

    def __init__(self):
        """Constructor."""
        super(BadArgumentsException, self).__init__('Invalid arguments.')


def print_exceptions(function):
    """Print exceptions to console and rethrows."""
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            logger.debug('url: {}'.format(request.url))
            if request.is_json:
                logger.debug('json: {}'.format(request.get_json(silent=True)))
            logger.debug(e, exc_info=True)
            raise
    return wrapper


def validate_secret(function):
    """Decorate a request handler to validate the communication token in the request."""
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        given_secret = request.headers.get('secret')
        if given_secret == app_secret[0]:
            return function(*args, **kwargs)
        return 'invalid secret', 401
    return wrapper


@app.errorhandler(AuthenticationException)
def handle_authentication_exception(err):
    """Handle AuthenticationException by responding with a HTTP 401."""
    return make_response(jsonify({"message": str(err)}), 401)


@app.errorhandler(ProjectSystemException)
def handle_project_system_exception(err):
    """Handle ProjectSystemException."""
    # TODO using magic string for 'Project not found.' and 'Workspace not found.'
    # TODO err.message is tuple of 1 element, not a string
    # if err.message and err.message.find(' not found') != -1:
    #     return make_response(jsonify({"message": err.message}), 404)
    return handle_error(err)


@app.errorhandler(ClientError)
def handle_bad_argument_exception(err):
    """Handle ClientError."""
    return make_response(jsonify({"message": err.message}), err.status_code)


# TODO:
# - CloudError: AzureError: token errors
# - should expose stacktrace?
@app.errorhandler(Exception)
def handle_error(err):
    """Defaul error handler."""
    def _extract_message(exc):
        return [str(exc), *_extract_message(exc.__cause__)] if exc else []
    message = ": ".join(_extract_message(err))
    return make_response(jsonify({"message": message}), 500)


# Workspaces

@app.route("/workspaces", methods=["GET"])
@validate_secret
@print_exceptions
def list_workspaces():
    """Handle requests for listing workspaces."""
    subscription_id = request.args.get('subscriptionId')
    resource_group = request.args.get('resourceGroup')
    name = request.args.get('name')
    if not subscription_id:
        raise BadArgumentsException()
    if resource_group and name:
        result = [sdk.get_workspace_by_name(_get_auth_token(), subscription_id, resource_group, name)]
    else:
        result = sdk.list_workspaces(_get_auth_token(), subscription_id, resource_group)
    return jsonify(result)


@app.route('/workspaces/<raw:workspace_id>', methods=['GET'])
@validate_secret
@print_exceptions
def get_workspace(workspace_id):
    """Handle requests for fetching workspaces."""
    subscription_id, resource_group, workspace_name = _extract_from_workspace_id(workspace_id)
    result = sdk.get_workspace_by_name(_get_auth_token(), subscription_id, resource_group, workspace_name)
    return jsonify(result)


@app.route('/workspaces/<raw:workspace_id>', methods=['DELETE'])
@validate_secret
@print_exceptions
def delete_workspace(workspace_id):
    """Handle requests for deleting workspaces."""
    subscription_id, resource_group, workspace_name = _extract_from_workspace_id(workspace_id)
    sdk.delete_workspace(_get_auth_token(), subscription_id, resource_group, workspace_name)
    return '', 204


@app.route('/workspaces', methods=['POST'])
@validate_secret
@print_exceptions
def create_workspace():
    """Handle requests for creating workspaces."""
    json = request.get_json()
    logger.debug(json)
    if json:
        subscription_id = json.get('subscriptionId')
        resource_group = json.get('resourceGroup')
        name = json.get('name')
        location = json.get('location')
    if not (json and subscription_id and name):
        raise BadArgumentsException()
    result = sdk.create_workspace(_get_auth_token(), subscription_id, resource_group, name, location)
    return jsonify(result)


# Projects

@app.route('/projects/<raw:project_path>', methods=['GET'])
@validate_secret
@print_exceptions
def get_project_info(project_path):
    """Handle requests for fetching local projects info."""
    result = sdk.get_experiment_info(_get_auth_token(), project_path)
    return jsonify(result)


@app.route('/projects/<raw:project_path>', methods=['PUT'])
@validate_secret
@print_exceptions
def attach_project(project_path):
    """Handle requests for attaching a local project to a history."""
    json = request.get_json()
    logger.debug(json)
    if json:
        workspace_id = json.get('workspaceId')
        experiment_name = json.get('experimentName')
    if not (json and workspace_id and experiment_name):
        raise BadArgumentsException()
    subscription_id, resource_group, workspace_name = _extract_from_workspace_id(workspace_id)
    sdk.attach_project(_get_auth_token(), subscription_id, resource_group, workspace_name,
                       project_path, experiment_name)
    return '', 204


@app.route('/projects/<raw:project_path>', methods=['DELETE'])
@validate_secret
@print_exceptions
def detach_project(project_path):
    """Handle requests for detaching a local project from a history."""
    sdk.detach_project(_get_auth_token(), project_path)
    return '', 204


# Run Configurations

@app.route('/projects/<raw:project_path>/runConfigs', methods=['GET'])
@validate_secret
@print_exceptions
def list_run_configurations(project_path):
    """Handle requests for listing run configurations found in a local project."""
    result = sdk.list_run_configurations(_get_auth_token(), project_path)
    return jsonify(result)


@app.route('/projects/<raw:project_path>/runConfigs/<runConfigName>', methods=['GET'])
@validate_secret
@print_exceptions
def get_run_configuration(project_path, runConfigName):
    """Handle requests for fetching a run configuration from a local project."""
    result = sdk.get_run_configuration(_get_auth_token(), project_path, runConfigName)
    return jsonify(result)


@app.route('/projects/<raw:project_path>/runConfigs/<runConfigName>', methods=['PUT'])
@validate_secret
@print_exceptions
def create_run_configuration(project_path, runConfigName):
    """Handle requests for creating a new run configuration."""
    json = request.get_json()
    logger.debug(json)
    if json:
        target = json.get('target')
        prepare = json.get('autoPrepareEnvironment')
    else:
        target = None
        prepare = None
    result = sdk.create_run_configuration(_get_auth_token(), project_path, runConfigName, target, prepare)
    return jsonify(result)


@app.route('/projects/<raw:project_path>/runConfigs/<runConfigName>', methods=['DELETE'])
@validate_secret
@print_exceptions
def delete_run_configuration(project_path, runConfigName):
    """Handle requests for deleting run configurations."""
    sdk.delete_run_configuration(_get_auth_token(), project_path, runConfigName)
    return '', 204


# Runs

@app.route('/projects/<raw:project_path>/runs', methods=['POST'])
@validate_secret
@print_exceptions
def submit_run(project_path):
    """Handle requests for submitting experiment runs."""
    json = request.get_json()
    logger.debug(json)
    if json:
        run_config_name = json.get('runConfigName')
        script_path = json.get('scriptPath')
        arguments = json.get('arguments')
        target = json.get('target')
        python_path = json.get('pythonPath')
    if not (json and run_config_name):
        raise BadArgumentsException()
    result = sdk.submit_run(
        _get_auth_token(),
        project_path,
        run_config=run_config_name,
        script=script_path,
        arguments=arguments,
        python_path=python_path,
        target=target
    )
    return jsonify(result)


@app.route('/projects/<raw:project_path>/runs/<raw:run_id>/output-stream', methods=['POST'])
@validate_secret
@print_exceptions
def stream_run_output(project_path, run_id):
    """Handle requests for streams of a run's output."""
    json = request.get_json()
    logger.debug(json)
    if json:
        run_config_name = json.get('runConfigName')
    if not (json and run_config_name):
        raise BadArgumentsException()
    stream = sdk.stream_run_output(_get_auth_token(), project_path, run_config_name, run_id)
    return Response(stream, mimetype='text/plain')


# Models

@app.route('/workspaces/<raw:workspace_id>/models', methods=['POST'])
@validate_secret
@print_exceptions
def register_model(workspace_id):
    """Handle requests for registering models from a file to a workspace."""
    subscription_id, resource_group, workspace_name = _extract_from_workspace_id(workspace_id)
    json = request.get_json()
    logger.debug(json)
    if json:
        model_path = json.get('modelPath')
        model_name = json.get('modelName')
        tags = json.get('tags')
        description = json.get('description')
    if not (json and model_path and model_name):
        raise BadArgumentsException()
    result = sdk.register_model(_get_auth_token(), subscription_id, resource_group, workspace_name,
                                model_path, model_name, tags, description)
    return jsonify(result)


@app.route('/workspaces/<raw:workspace_id>/models/<raw:model_id>/download', methods=['POST'])
@validate_secret
@print_exceptions
def download_model(workspace_id, model_id):
    """Handle requests for downloading models."""
    subscription_id, resource_group, workspace_name = _extract_from_workspace_id(workspace_id)
    json = request.get_json()
    logger.debug(json)
    if json:
        target_dir = json.get('targetDir')
    if not (json and target_dir):
        raise BadArgumentsException()
    sdk.download_model(_get_auth_token(), subscription_id, resource_group, workspace_name,
                       model_id, target_dir)
    return '', 204


# Images

@app.route('/workspaces/<raw:workspace_id>/images', methods=['POST'])
@validate_secret
@print_exceptions
def create_image(workspace_id):
    """Handle requests for creating images."""
    subscription_id, resource_group, workspace_name = _extract_from_workspace_id(workspace_id)
    json = request.get_json()
    logger.debug(json)
    if json:
        directory = json.get('directory')
        name = json.get('name')
        models = json.get('models')
        runtime = json.get('runtime')
        execution_script = json.get('executionScript')
        docker_file = json.get('dockerFile')
        conda_file = json.get('condaFile')
        dependencies = json.get('dependencies')
        schema_file = json.get('schemaFile')
        enable_gpu = json.get('enableGpu')
        tags = json.get('tags')
        description = json.get('description')
        is_async = json.get('async', False)
    if not (json and name and runtime and execution_script and directory):
        raise BadArgumentsException()
    if models and not isinstance(models, list):
        raise BadArgumentsException()
    result = sdk.create_image(_get_auth_token(), subscription_id, resource_group, workspace_name, name, runtime,
                              directory, execution_script, models, docker_file, conda_file, dependencies, schema_file,
                              enable_gpu, tags, description, is_async)
    return jsonify(result)


# Web Services

@app.route('/workspaces/<raw:workspace_id>/services', methods=['POST'])
@validate_secret
@print_exceptions
def create_service_from_image(workspace_id):
    """Handle requests for creating web services from existing images."""
    subscription_id, resource_group, workspace_name = _extract_from_workspace_id(workspace_id)
    json = request.get_json()
    logger.debug(json)
    if json:
        name = json.get('name')
        image_id = json.get('imageId')
        deployment_config_params = json.get('deploymentConfig')
        deployment_target_name = json.get('deploymentTarget')
        # aci or aks
        deployment_type = json.get('deploymentType')
        is_async = json.get('async', False)
    if not (json and name and image_id and ((deployment_config_params and deployment_type) or deployment_target_name)):
        raise BadArgumentsException()
    result = sdk.create_service_from_image(_get_auth_token(), subscription_id, resource_group, workspace_name, name,
                                           image_id, deployment_config_params, deployment_target_name, deployment_type,
                                           is_async)
    return jsonify(result)


@app.route('/workspaces/<raw:workspace_id>/services-from-registered-models', methods=['POST'])
@validate_secret
@print_exceptions
def create_service_from_registered_models(workspace_id):
    """Handle requests for creating web services from registered models."""
    subscription_id, resource_group, workspace_name = _extract_from_workspace_id(workspace_id)
    json = request.get_json()
    logger.debug(json)
    if json:
        name = json.get('name')
        model_ids = json.get('modelIds')
        image_config_params = json.get('imageConfig')
        deployment_config_params = json.get('deploymentConfig')
        deployment_target_name = json.get('deploymentTarget')
        # aci or aks
        deployment_type = json.get('deploymentType')
        is_async = json.get('async', False)
    if not (json and name and image_config_params and
            ((deployment_config_params and deployment_type) or deployment_target_name)):
        raise BadArgumentsException()
    if model_ids and not isinstance(model_ids, list):
        raise BadArgumentsException()
    result = sdk.create_service_from_registered_models(
        _get_auth_token(), subscription_id, resource_group, workspace_name, name, image_config_params, model_ids,
        deployment_config_params, deployment_target_name, deployment_type, is_async
    )
    return jsonify(result)


@app.route('/workspaces/<raw:workspace_id>/services-from-models', methods=['POST'])
@validate_secret
@print_exceptions
def create_service_from_models(workspace_id):
    """Handle requests for creating web services from model files."""
    subscription_id, resource_group, workspace_name = _extract_from_workspace_id(workspace_id)
    json = request.get_json()
    logger.debug(json)
    if json:
        name = json.get('name')
        model_paths = json.get('modelPaths')
        image_config_params = json.get('imageConfig')
        deployment_config_params = json.get('deploymentConfig')
        deployment_target_name = json.get('deploymentTarget')
        # aci or aks
        deployment_type = json.get('deploymentType')
        is_async = json.get('async', False)
    if not (json and name and image_config_params and
            ((deployment_config_params and deployment_type) or deployment_target_name)):
        raise BadArgumentsException()
    if model_paths and not isinstance(model_paths, list):
        raise BadArgumentsException()
    result = sdk.create_service_from_models(
        _get_auth_token(), subscription_id, resource_group, workspace_name, name, image_config_params, model_paths,
        deployment_config_params, deployment_target_name, deployment_type, is_async
    )
    return jsonify(result)


# Generate URLs to history web app views

@app.route('/workspaces/<raw:workspace_id>/experiment-url', methods=['GET'])
@validate_secret
@print_exceptions
def get_experiment_url(workspace_id):
    """Respond with URL to an experiment view.

    URL is...
    - run details if experiment name and run Id are given
    - report view if experiment name and report Id are given
    - experiment list view by default
    """
    experiment_name = request.args.get('experimentName', '')
    run_id = request.args.get('runId', '')
    report_id = request.args.get('reportId', '')
    all_route_params = {
        'host': 'mlworkspace.azure.ai',
        'workspace_id': workspace_id,
        'experiment_name': urllib.parse.quote(experiment_name, safe=''),
        'run_id': urllib.parse.quote(run_id, safe=''),
        'report_id': urllib.parse.quote(report_id, safe='')
    }
    if experiment_name:
        if run_id:
            template = 'https://{host}/experiments{workspace_id}/experiment/{experiment_name}/run/{run_id}'
        elif report_id:
            template = 'https://{host}/experiments{workspace_id}/experiment/{experiment_name}/report/{report_id}'
        else:
            template = 'https://{host}/experiments{workspace_id}/experiment/{experiment_name}'
    else:
        template = 'https://{host}/experiments{workspace_id}'
    url = template.format(**all_route_params)

    return jsonify({'url': url})


@app.route('/shutdown', methods=['GET'])
@validate_secret
@print_exceptions
def shutdown():
    """Handle request to shutdown the HTTP server."""
    logger.debug('Server shutting down...')
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return '', 204


@app.route('/version', methods=['GET'])
def version():
    """Version JSON."""
    return jsonify({'version': 1})


def _extract_from_workspace_id(workspace_id):
    regex = '/subscriptions/(.+)/resourceGroups/(.+)/providers/Microsoft\\.MachineLearningServices/workspaces/(.+)'
    matches = re.search(regex, workspace_id)
    if matches:
        return matches.group(1), matches.group(2), matches.group(3)
    raise ClientError('Invalid Workspace ID')


def _get_auth_token():
    auth_header = request.headers.get('authorization')
    if not auth_header:
        raise AuthenticationException('Missing authentication token in request')
    pair = auth_header.split(maxsplit=1)
    if len(pair) == 2 and pair[0].lower() == 'bearer' and pair[1]:
        return pair[1]
    return None


def _find_free_port():
    # https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def _random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


if __name__ == '__main__':
    if not flaskInstalled:
        print('ERROR: flask is not installed', file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', type=int, help='Server\'s port number. Defaults to a dynamic port.')
    parser.add_argument('--secret', '-s', help='Server\'s secret communication token. Defaults to a random string.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Prints more info for each request.')
    parser.add_argument('--log-file', '-lf', help='Log to the given file.')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='Show exception traces in response and enables live reloads.')
    parsed_args = None
    # setting default arguments through env. vars is convenient for debugging
    if os.environ.get('AML_SERVER_ARGS'):
        args_from_env = shlex.split(os.environ.get('AML_SERVER_ARGS'), posix='win' not in sys.platform)
        parsed_args = parser.parse_args(args=args_from_env)
    parsed_args = parser.parse_args(namespace=parsed_args)

    port = parsed_args.port or _find_free_port()
    secret = parsed_args.secret or _random_string(64)
    verbose_enabled = parsed_args.verbose
    debug_enabled = parsed_args.debug
    log_file = parsed_args.log_file

    if log_file:
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        sdk.logger.addHandler(handler)

    if verbose_enabled:
        logger.setLevel(logging.DEBUG)
        sdk.logger.setLevel(logging.DEBUG)

    if debug_enabled:
        # use env. vars. to maintain same port/secret across reloads
        if not os.environ.get('WERKZEUG_RUN_MAIN'):
            os.environ['AML_SERVER_PORT'] = str(port)
            os.environ['AML_SERVER_SECRET'] = secret
        else:
            port = int(os.environ.get('AML_SERVER_PORT', port))
            secret = os.environ.get('AML_SERVER_SECRET', secret)

    if not (debug_enabled and os.environ.get('WERKZEUG_RUN_MAIN')):
        print('SERVER PORT: {}'.format(port))
        print('SERVER SECRET: {}'.format(secret))
    app_secret[0] = secret
    app.run(debug=debug_enabled, port=port)
