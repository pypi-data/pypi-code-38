import os
import tempfile
import requests
import base64
import time
import json
import fnmatch

from pathlib import Path

import click

from evolvcli.sdk.evolvclient.config import EvolvConfig
from evolvcli.sdk.evolvclient.client import EvolvClient


APPLICATION_JSON = 'application/json'
APPLICATION_YAML = 'application/yaml'

EVOLV_ACCOUNT_ID = ''
EVOLV_CONFIG = None


@click.group()
@click.option('-s', '--domain', default='experiments.evolv.ai', envvar='EVOLV_DOMAIN',
              help='Evolv domain where experiments api lives')
@click.option('-a', '--account-id', default=None, envvar='EVOLV_ACCOUNT_ID', show_default=True,
              help='The account id of the Evolv account being interacted with')
@click.option('-k', '--api-key', default=None, envvar='EVOLV_API_KEY', show_default=True,
              help='An api key to access the api with')
@click.option('-l', '--login', is_flag=True, default=False,
              help='To prompt the user for login information')
def cli(domain, account_id, api_key, login):
    """
    The primary CLI for managing experiments within evolv.ai
    """
    global EVOLV_CONFIG
    global EVOLV_ACCOUNT_ID

    if (login or not _user_has_auth()) and not api_key:
        username = click.prompt("Please enter your Evolv email", type=str)
        password = click.prompt("Please enter your Evolv password", type=str, hide_input=True)
        _set_user_token(domain, username, password)

    EVOLV_ACCOUNT_ID = account_id
    if not EVOLV_ACCOUNT_ID:
        EVOLV_ACCOUNT_ID = click.prompt("Please enter your Evolv account id", type=str)

    if api_key:
        EVOLV_CONFIG = EvolvConfig(domain, api_key=api_key)
    else:
        with open(_find_creds_files('*evolv-creds', tempfile.gettempdir())[0]) as auth_file:
            auth = json.load(auth_file)
            EVOLV_CONFIG = EvolvConfig(domain, bearer_token=auth['access_token'])


@cli.group()
def get():
    """ Get the current state of an entity """
    pass


@get.command('account')
def get_account():
    """ Get the current account information """
    response = EvolvClient(EVOLV_CONFIG).get_account(EVOLV_ACCOUNT_ID)
    _print_dict(response)


@get.command('environment')
@click.argument('environment-id', type=str)
@click.option('--content-only', is_flag=True, help='Get only the content value of the entity')
@click.option('-v', '--version', default=None, help='The version of the entities content to retrieve')
def get_environment(environment_id, content_only, version):
    """ Get an Environment """
    response = EvolvClient(EVOLV_CONFIG).get_environment(environment_id, account_id=EVOLV_ACCOUNT_ID,
                                                         version=version, content_only=content_only)
    if content_only:
        if response.get('response_yaml'):
            _print_dict_as_yaml(response)
        else:
            _print_dict_as_json(response)
    else:
        _print_dict(response)


@get.command('metamodel')
@click.argument('metamodel-id', type=str)
@click.option('--content-only', is_flag=True, help='Get only the content value of the entity')
@click.option('-v', '--version', default=None, help='The version of the entities content to retrieve')
def get_metamodel(metamodel_id, content_only, version):
    """ Get a Metamodel """
    response = EvolvClient(EVOLV_CONFIG).get_metamodel(metamodel_id, account_id=EVOLV_ACCOUNT_ID,
                                                       version=version, content_only=content_only)
    if content_only:
        if response.get('response_yaml'):
            _print_dict_as_yaml(response)
        else:
            _print_dict_as_json(response)
    else:
        _print_dict(response)


@get.command('experiment')
@click.argument('experiment-id', type=str)
@click.argument('metamodel-id', type=str)
@click.option('--content-only', is_flag=True, help='Get only the content value of the entity')
@click.option('-v', '--version', default=None, help='The version of the entities content to retrieve')
def get_experiment(experiment_id, metamodel_id, content_only, version):
    """ Get an Experiment """
    response = EvolvClient(EVOLV_CONFIG).get_experiment(experiment_id, account_id=EVOLV_ACCOUNT_ID,
                                                        metamodel_id=metamodel_id, version=version,
                                                        content_only=content_only)
    if content_only:
        if response.get('response_yaml'):
            _print_dict_as_yaml(response)
        else:
            _print_dict_as_json(response)
    else:
        _print_dict(response)


@get.command('candidate')
@click.argument('candidate-id', type=str)
@click.argument('metamodel-id', type=str)
@click.argument('experiment-id', type=str)
def get_candidate(candidate_id, metamodel_id, experiment_id):
    """ Get a Candidate """
    response = EvolvClient(EVOLV_CONFIG).get_candidate(candidate_id, account_id=EVOLV_ACCOUNT_ID,
                                                       metamodel_id=metamodel_id, experiment_id=experiment_id)
    _print_dict(response)


@cli.group('list')
def list_all():
    """ List available entities """
    pass


@list_all.command('accounts')
def list_accounts():
    """ List Accounts """
    response = EvolvClient(EVOLV_CONFIG).list_accounts()
    _print_list_of_dicts(response)


@list_all.command('environments')
@click.option('--query', help='A graph query to use for filtering results')
def list_environments(query=None):
    """ List Environments """
    response = EvolvClient(EVOLV_CONFIG).list_environments(account_id=EVOLV_ACCOUNT_ID, query=query)
    _print_list_of_dicts(response)


@list_all.command('metamodels')
@click.option('--query', help='A graph query to use for filtering results')
def list_metamodels(query=None):
    """ List Metamodel """
    response = EvolvClient(EVOLV_CONFIG).list_metamodels(account_id=EVOLV_ACCOUNT_ID, query=query)
    _print_list_of_dicts(response)


@list_all.command('experiments')
@click.argument('metamodel-id', type=str)
@click.option('--query', help='A graph query to use for filtering results')
def list_experiments(metamodel_id, query=None):
    """ List Experiments """
    response = EvolvClient(EVOLV_CONFIG).list_experiments(account_id=EVOLV_ACCOUNT_ID, metamodel_id=metamodel_id,
                                                          query=query)
    _print_list_of_dicts(response)


@list_all.command('candidates')
@click.argument('metamodel-id', type=str)
@click.argument('experiment-id', type=str)
@click.option('--query', help='A graph query to use for filtering results')
def list_candidates(metamodel_id, experiment_id, query=None):
    """ List Candidates """
    response = EvolvClient(EVOLV_CONFIG).list_candidates(account_id=EVOLV_ACCOUNT_ID, metamodel_id=metamodel_id,
                                                         experiment_id=experiment_id, query=query)
    _print_list_of_dicts(response)


@cli.group()
def create():
    """ Create a new entity """
    pass


@create.command('account')
@click.argument('name', type=str)
def create_account(name):
    """
    Create a new account

    :param name: The name of the account to create
    """
    response = EvolvClient(EVOLV_CONFIG).create_account(name)
    _print_dict(response)


@create.command('metamodel')
@click.argument('name', type=str)
@click.argument('file', type=click.File('rb'), default='metamodel.yml')
def create_metamodel(name, file):
    """ Create a new Metamodel """
    if not _confirm_account():
        return

    response = EvolvClient(EVOLV_CONFIG).create_metamodel(name, yaml=file.read().decode('utf-8'),
                                                          account_id=EVOLV_ACCOUNT_ID)
    _print_dict(response)


@create.command('environment')
@click.argument('name', type=str)
@click.option('config', '-c', '--config', type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option('-p', '--protected', default=False, is_flag=True, help='Print verbose logging')
def create_environment(name, config, protected):
    """ Create a new Environment """
    if not _confirm_account():
        return

    content = None
    content_type = None

    if config is not None:
        assert config.endswith('.yml') or config.endswith('.json')
        content = Path(config).read_text()
        content_type = APPLICATION_YAML if config.endswith('.yml') else APPLICATION_JSON

    response = EvolvClient(EVOLV_CONFIG).create_environment(name, account_id=EVOLV_ACCOUNT_ID, default=False,
                                                            content=content, content_type=content_type,
                                                            protected=protected)
    _print_dict(response)


@create.command('experiment')
@click.argument('name', type=str)
@click.argument('metamodel-id', type=str)
@click.argument('optimization-targets', type=str)
@click.argument('environment-id', type=str)
@click.option('-t', '--experiment-type', type=click.Choice(['ABN', 'EVO', 'CONTROL']), default='CONTROL',
              show_default=True,
              help='Type of experiment to run')
@click.option('-ps', '--population-size', default=10, show_default=True,
              help='Number of candidates to test concurrently')
@click.option('-b', '--budget', default=None,
              help='Number participants to test before terminating')
@click.option('-mv', '--metamodel-version', default=None,
              help='Version of the metamodel to associate the experiment with')
@click.option('-p', '--precursor', default=None,
              help='The id of an experiment to initialize from')
@click.option('-av', '--algorithm-version', default=None,
              help='The version of the algorithms to use for this experiment')
@click.option('-cr', '--estimated-cr', '--estimated-conversion-rate', default=5.0,
              type=click.FloatRange(0.0, 100.0), help='The estimated conversion rate of the experiment')
@click.option('-tc/-ntc', '--long-tail-correction/--no-long-tail-correction', default=True,
              help='To use long tail correction or not')
@click.option('-s', '--sample-rate', default=100, type=click.IntRange(0, 100),
              help='The percentage traffic allocation')
@click.option('-sn', '--target-confidence', default='STANDARD', show_default=True,
              type=click.Choice(['LOW', 'STANDARD', 'HIGH']), help='The level of confidence needed before progressing')
@click.option('-aq', '--audience-query-file', type=click.Path(exists=True), default=None,
              help='Json file defining the experiments audience filters.')
@click.option('config', '-c', '--config', type=click.Path(exists=True, dir_okay=False, readable=True))
def create_experiment(
        name,
        metamodel_id,
        optimization_targets,
        environment_id,
        experiment_type,
        population_size,
        budget,
        metamodel_version,
        precursor,
        algorithm_version,
        estimated_cr,
        long_tail_correction,
        sample_rate,
        target_confidence,
        audience_query_file,
        config):
    """ Create an Experiment """

    if not _confirm_account():
        return

    evolv_client = EvolvClient(EVOLV_CONFIG)
    if not metamodel_version:
        # if no Metamodel version use latest
        metamodel = evolv_client.get_metamodel(metamodel_id, account_id=EVOLV_ACCOUNT_ID)
        if not metamodel:
            raise Exception("There was no Metamodel with the id {}".format(metamodel_id))
        metamodel_version = metamodel['content_version']

    audience_query = None
    content = None
    content_type = None

    if audience_query_file:
        with open(audience_query_file, 'r') as json_data:
            audience_query = json_data.read()

    if config is not None:
        assert config.endswith('.yml') or config.endswith('.json')

        content = Path(config).read_text()
        content_type = APPLICATION_YAML if config.endswith('.yml') else APPLICATION_JSON

    response = evolv_client.create_experiment(name=name, metamodel_id=metamodel_id, metamodel_version=metamodel_version,
                                              account_id=EVOLV_ACCOUNT_ID,
                                              optimization_targets=optimization_targets.split(','),
                                              environment_id=environment_id, experiment_type=experiment_type,
                                              population_size=population_size,
                                              budget=budget, precursor=precursor, algorithm_version=algorithm_version,
                                              estimated_cr=estimated_cr, long_tail_correction=long_tail_correction,
                                              sample_rate=sample_rate, target_confidence=target_confidence,
                                              audience_query=audience_query, content=content, content_type=content_type)
    _print_dict(response)


@create.command('candidate')
@click.argument('metamodel-id', type=str)
@click.argument('metamodel-version', type=str)
@click.argument('environment-id', type=str)
@click.argument('experiment-id', type=str)
@click.argument('file', type=click.Path(exists=True), default='genome.json')
@click.option('-a', '--allocation_probability', default=1.0, show_default=True,
              help='The probability that the candidate will be allocated.')
def create_candidate(metamodel_id, metamodel_version, environment_id, experiment_id, file, allocation_probability):
    """ Create a candidate. """

    if not _confirm_account():
        return

    with open(file, 'r') as json_data:
        genome = json_data.read()

    response = EvolvClient(EVOLV_CONFIG).create_candidate(metamodel_id=metamodel_id,
                                                          metamodel_version=metamodel_version, genome=genome,
                                                          account_id=EVOLV_ACCOUNT_ID, environment_id=environment_id,
                                                          experiment_id=experiment_id,
                                                          allocation_probability=allocation_probability)
    _print_dict(response)


@cli.group()
def update():
    """ Update a entity """
    pass


@update.command('metamodel')
@click.argument('metamodel-id', type=str)
@click.argument('file', type=click.File('rb'), default='metamodel.yml')
def update_metamodel(metamodel_id, file):
    """ Update the content of an existing Metamodel """
    if not _confirm_account():
        return

    evolv_client = EvolvClient(EVOLV_CONFIG)
    metamodel = evolv_client.get_metamodel(metamodel_id, account_id=EVOLV_ACCOUNT_ID)
    if not metamodel:
        raise Exception("Failed to retrieve the previous metamodel.")

    response = evolv_client.update_metamodel(metamodel_id=metamodel_id, name=metamodel['name'],
                                             content=file.read().decode('utf-8'),
                                             content_type=APPLICATION_YAML,
                                             account_id=EVOLV_ACCOUNT_ID)
    _print_dict(response)


@update.command('environment')
@click.argument('environment-id', type=str)
@click.argument('file', type=click.File('rb'), default='environment.yml')
def update_environment(environment_id, file):
    """ Update the content of an existing Environment """
    if not _confirm_account():
        return

    evolv_client = EvolvClient(EVOLV_CONFIG)
    environment = evolv_client.get_environment(environment_id, account_id=EVOLV_ACCOUNT_ID)
    if not environment:
        raise Exception("Failed to retrieve the previous environments.")

    response = evolv_client.update_environment(environment_id=environment_id, name=environment['name'],
                                               content=file.read().decode('utf-8'),
                                               content_type=APPLICATION_YAML
                                               if '.yml' in file.name else APPLICATION_JSON,
                                               account_id=EVOLV_ACCOUNT_ID)
    _print_dict(response)


@update.command('experiment')
@click.argument('experiment-id', type=str)
@click.argument('metamodel-id', type=str)
@click.option('-a', '--abort', is_flag=True, default=False, help='Whether or not to stop a running experiment.')
@click.option('-ar', '--abort-reason', help='Reason for stopping the experiment.', default=None)
def update_experiment(experiment_id, metamodel_id, abort, abort_reason):
    """ Update an existing Experiment """
    if not _confirm_account():
        return

    response = EvolvClient(EVOLV_CONFIG).update_experiment(experiment_id=experiment_id, abort=abort,
                                                           abort_reason=abort_reason,
                                                           account_id=EVOLV_ACCOUNT_ID, metamodel_id=metamodel_id)
    _print_dict(response)


def _print_dict_as_yaml(d):
    click.echo(d.get('content'))


def _print_dict_as_json(d):
    click.echo(json.dumps(d, sort_keys=True, indent=2))


def _print_dict(d):
    if isinstance(d, dict):
        for k, v in d.items():
            click.echo('{}: {}'.format(k, v))
        click.echo()
    else:
        click.echo(d)


def _print_list_of_dicts(l):
    if not l:
        click.echo("There were no entities found.")
        return

    if isinstance(l, list):
        for d in l:
            _print_dict(d)
    else:
        click.echo(l)


def _confirm_account():
    if not click.confirm('You are currently set to interact with account: {},'
                         ' do you want to continue?'.format(EVOLV_ACCOUNT_ID)):
        return False
    return True


def _user_has_auth():
    try:
        cred_files = _find_creds_files('*evolv-creds', tempfile.gettempdir())
        f = open(cred_files[0], 'r')
        data = json.load(f)
        expiry = data['expires_at']
        if expiry < time.time():
            return False
        return True
    except Exception:
        return False


def _create_json_auth_file(file_contents):
    old_cred_files = _find_creds_files('*evolv-creds', tempfile.gettempdir())
    for file in old_cred_files:
        os.remove(file)

    temp = tempfile.NamedTemporaryFile(suffix='evolv-creds', delete=False)
    temp.write(json.dumps(file_contents).encode())


def _find_creds_files(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def _set_user_token(domain, username, password):
    try:
        username_password = base64.b64encode((username + ':' + password).encode()).decode()
        response = requests.get('https://{}/v1/login'.format(domain),
                                headers={'Authorization': 'Basic {}'.format(username_password)})

        if not response.ok:
            raise Exception("Response to login user failed.")

        token_response = response.json()
        token_response['expires_at'] = token_response['expires_in'] + time.time()
        _create_json_auth_file(token_response)
    except Exception as e:
        raise Exception("Response to login user failed.")


if __name__ == '__main__':
    cli()
