"""
Profile subcommand
"""
import copy
import logging
import tempfile

from functools import lru_cache
from typing import Callable, List

from .base import BaseSubcommand

from compose_flow.compose import merge_profile
from compose_flow.config import get_config
from compose_flow.errors import EnvError, NoSuchProfile, ProfileError
from compose_flow.utils import render, yaml_dump, yaml_load

COPY_ENV_VAR = 'CF_COPY_ENV_FROM'


def get_kv(item: str) -> tuple:
    """
    Returns the item split at equal
    """
    item_split = item.split('=', 1)
    key = item_split[0]

    try:
        val = item_split[1]
    except IndexError:
        val = None

    return key, val


def listify_kv(d: dict) -> list:
    """
    Returns an equal-delimited list of the dictionary's key/value pairs

    When the value is null the equal is not appended
    """
    return [f'{k}={v}' if v else k for k, v in d.items()]


class Profile(BaseSubcommand):
    """
    Subcommand for managing profiles
    """
    update_version_env_vars = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._compiled_profile = None
        self._data = None

    @property
    def filename(self) -> str:
        """
        Returns the filename for this profile
        """
        args = self.workflow.args

        return f'compose-flow-{args.profile}.yml'

    @classmethod
    def fill_subparser(cls, parser, subparser):
        subparser.add_argument('action')

    @property
    def data(self):
        if self._data:
            return self._data

        compose_content = self.load()

        self._data = yaml_load(compose_content)

        return self._data

    def cat(self):
        """
        Prints the loaded compose file to stdout
        """
        print(self.load())

    def _check_services(self, check_fn: Callable, data: dict) -> list:
        """
        Runs all services through the given check function

        Args:
            check_fn: the check function to run
            data: the service data dict

        Returns:
            list of errors
        """
        env_data = self.workflow.environment.data
        errors = []

        for name, service_data in data['services'].items():
            errors.extend(check_fn(name, service_data, env_data))

        return errors

    def check(self):
        """
        Checks the profile against some rules
        """
        checks = self.workflow.subcommand.profile_checks

        errors = []
        for check in checks:
            check_fn = getattr(self, check)

            errors.extend(self._check_services(check_fn, self.data))

        if errors:
            raise ProfileError('\n'.join(errors))

    @staticmethod
    def check_env(name: str, service_data: dict, env_data: dict) -> list:
        """
        Checks that environment is properly defined

        Returns:
            list of errors
        """
        errors = []
        for item in service_data.get('environment', []):
            # when a variable has an equal sign, it is setting
            # the value, so don't check the environment for this variable
            if '=' in item:
                continue

            if item not in env_data:
                errors.append(f'{item} not found in environment for service={name}')

        return errors

    # noinspection PyUnusedLocal
    @staticmethod
    def check_constraints(name: str, service_data: dict, env_data: dict) -> list:
        """
        Checks that constraints are defined

        Returns:
            list of errors
        """
        errors = []
        service_message = f'not found in service={name}; please add node constraints to deploy.placement.constraints'

        deploy = service_data.get('deploy', {})

        # if the service is global, no constraints needed
        if 'global' in deploy.get('mode', {}):
            return errors

        # check to see that a node constraint has been defined
        constraints = deploy.get('placement', {}).get('constraints', [])
        if not constraints:
            errors.append(f'constraints {service_message}')
        else:
            for constraint in constraints:
                if constraint.startswith('node.'):
                    break
            else:
                errors.append(f'node constraints {service_message}')

        return errors

    def check_resources(self, name: str, service_data: dict, env_data: dict) -> list:
        """
        Checks that resources are defined

        Returns:
            list of errors
        """
        errors = []
        service_message = f'not found in service={name}; please add reservations and limits to deploy.resources'

        # check to see that a node constraint has been defined
        resources = service_data.get('deploy', {}).get('resources', {})
        if not resources:
            errors.append(f'resource constraints {service_message}')

            # short-circuit early, nothing else to check
            return errors

        for item in ('limits', 'reservations'):
            if 'memory' in resources.get(item, {}):
                break
        else:
            errors.append(f'memory constraints {service_message}')

        return errors

    def cf_config_expand(self, data):
        expand_config = data['compose_flow']['expand']
        for service_name, config in expand_config.items():
            base_service = data['services'].pop(service_name)
            replicas = base_service['deploy']['replicas']

            increment_config = expand_config[service_name].get('increment')

            for idx in range(replicas):
                _service_name = f'{service_name}{idx+1}'
                _service = copy.deepcopy(base_service)

                _service['deploy'].pop('replicas')

                if increment_config:
                    for (
                        _increment_config_name,
                        _increment_config_data,
                    ) in increment_config.items():
                        fn_name = f'cf_config_expand_increment_{_increment_config_name}'
                        _service = getattr(self, fn_name)(
                            _increment_config_data, idx, _service
                        )

                data['services'][_service_name] = _service

    def cf_config_expand_increment_env(
        self, increment_config: dict, item_index: int, service: dict
    ) -> dict:
        if not isinstance(service['environment'], list):
            raise NotImplementedError(
                'environment dictionary is not supported, use list format'
            )

        new_env = []
        for item in service['environment']:
            if '=' not in item:
                new_env.append(item)

                continue

            k, v = item.split('=', 1)
            if k not in increment_config:
                new_env.append(item)

                continue

            v_int = int(v)

            new_env.append(f'{k}={v_int+item_index}')

        service['environment'] = new_env

        return service

    def cf_config_expand_increment_ports(
        self, increment_config: dict, item_index: int, service: dict
    ) -> dict:
        new_ports = []

        for item in service['ports']:
            source, dest = item.split(':')
            source_i = int(source)
            dest_i = int(dest)

            if increment_config.get('source_port', False):
                source_i += item_index

            if increment_config.get('destination_port', False):
                dest_i += item_index

            new_ports.append(f'{source_i}:{dest_i}')

        service['ports'] = new_ports

        return service

    def _check_cf_config(self, data):
        """
        Expands out any services that should be duplicated
        """
        cf_config_sections = list(data.get('compose_flow', {}).keys())
        for item in cf_config_sections:
            fn_name = f'cf_config_{item}'

            getattr(self, fn_name)(data)

        return data

    def _compile(self, profile: dict) -> str:
        """
        Compiles the profile into a single docker compose file

        Args:
            profile: The profile name to compile

        Returns:
            compiled compose file as a string
        """
        if self._compiled_profile:
            return self._compiled_profile

        content = merge_profile(profile)

        # perform transformations on the compiled profile
        if content:
            data = yaml_load(content)

            # check if the environment needs to be copied from another service
            data = self._copy_environment(data)

            # see if any services need to be expanded out
            data = self._check_cf_config(data)

            # drop the compose_flow section if it exists
            data.pop('compose_flow', None)

            # for each service inject DOCKER_STACK and DOCKER_SERVICE
            for service_name, service_data in data.get('services', {}).items():
                service_environment = service_data.setdefault('environment', [])

                # convert the service_environment into a dict
                service_environment_d = {}
                for item in service_environment:
                    item_split = item.split('=', 1)
                    k = item_split[0]

                    if len(item_split) > 1:
                        v = item_split[1]
                    else:
                        v = None

                    service_environment_d[k] = v

                for k, v in (
                        ('DOCKER_SERVICE', service_name),
                        ('DOCKER_STACK', self.workflow.args.config_name),
                ):
                    if k not in service_environment_d:
                        service_environment_d[k] = v

                # reconstruct the k=v list honoring empty values
                service_environment_l = []
                for k, v in service_environment_d.items():
                    if v is None:
                        val = k
                    else:
                        val = f'{k}={v}'
                    service_environment_l.append(val)

                # dump back out as list
                service_data['environment'] = service_environment_l

                # enforce resources
                self.set_resources(service_name, service_data)

            content = yaml_dump(data)

        self._compiled_profile = content

        return content

    def _copy_environment(self, data):
        """
        Processes CF_COPY_ENV_FROM environment entries
        """
        environments = {}

        # first get the env from each service
        for service_name, service_data in data['services'].items():
            environment = service_data.get('environment')
            if environment:
                _env = {}

                for item in environment:
                    k, v = get_kv(item)

                    _env[k] = v

                environments[service_name] = _env

        # go through each service environment and apply any copies found
        for service_name, service_data in data['services'].items():
            environment = service_data.get('environment')
            if not environment:
                continue

            new_env = {}
            for item in environment:
                key, val = get_kv(item)
                new_env[key] = val

                if not item.startswith(COPY_ENV_VAR):
                    continue

                _env = environments.get(val)
                if not _env:
                    raise EnvError(
                        f'Unable to find val={val} to copy into service_name={service_name}'
                    )

                new_env.update(_env)

            service_data['environment'] = listify_kv(new_env)

        return data

    @classmethod
    @lru_cache()
    def get_all_checks(cls) -> List[str]:
        """
        Returns a list of all the method names that are checks in this class

        Returns:
            list of strings
        """
        checks = []

        for fn_name in dir(cls):
            if fn_name.startswith('check_'):
                checks.append(fn_name)

        return checks

    def get_profile_compose_file(self, profile: dict):
        """
        Processes the profile to generate the compose file
        """
        content = self._compile(profile)
        fh = tempfile.TemporaryFile(mode='w+')

        # render the file
        try:
            rendered = render(content, env=self.workflow.environment.data)
        except EnvError as exc:
            if not self.workflow.subcommand.is_missing_profile_okay(exc):
                raise

            return fh

        fh.write(rendered)
        fh.flush()

        fh.seek(0, 0)

        return fh

    def load(self) -> str:
        """
        Loads the compose file that is generated from all the items listed in the profile
        """
        fh = self.get_profile_compose_file(self.profile_files)

        return fh.read()

    @property
    def logger(self):
        return logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    @property
    def profile_files(self) -> dict:
        """
        Returns the profile data found in the dc.yml file
        """
        config = get_config()
        if not config:
            return {}

        profile_name = self.workflow.args.profile

        # when there is no profile name, return just docker-compose.yml
        if profile_name is None:
            return ['docker-compose.yml']

        try:
            profile = config['profiles'][profile_name]
        except KeyError:
            raise NoSuchProfile(f'profile={profile_name}')

        return profile

    def set_resources(self, name: str, service_data: dict) -> None:
        """
        Fills in missing resources
        """
        resources = service_data.get('deploy', {}).get('resources', {})

        # init limits and reservations
        changed = False
        for item, opposite_item in (
                ('limits', 'reservations'),
                ('reservations', 'limits'),
        ):
            resources.setdefault(item, {})
            resources.setdefault(opposite_item, {})

            # if a memory reservation is set, but there is no memory limit, match
            if 'memory' in resources[item]:
                if 'memory' not in resources[opposite_item]:
                    self.logger.warning(f'matching {opposite_item} with {item} for service {name}')

                    resources[opposite_item]['memory'] = resources[item]['memory']

                    changed = True

        if changed:
            service_data.setdefault('deploy', {})['resources'] = resources

    @lru_cache()
    def write(self) -> None:
        """
        Writes the loaded compose file to disk
        """
        with open(self.filename, 'w') as fh:
            fh.write(yaml_dump(self.data))
