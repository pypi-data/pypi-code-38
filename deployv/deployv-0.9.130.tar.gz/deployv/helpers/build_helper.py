from deployv.helpers import utils
from deployv.helpers.clone_oca_dependencies import run as clone_oca_deps
from deployv.base.errors import BuildError
from deployv.instance import ODOO_BINARY, SAAS_VERSIONS
import docker
from docker import APIClient as Client
from jinja2 import Environment, FileSystemLoader
from os import path, getenv
from tempfile import mkdtemp
import shutil
import logging
import simplejson as json
import spur
import re
from branchesv import utils as branches_utils
from branchesv.branches import load as load_branches


_logger = logging.getLogger(__name__)


class BuildImage(object):

    def __init__(self, config, full_stack_image=False):
        """ Helper that builds new docker images

            :param config: Config Config object with the format used by deployv.
            :param full_stack_image: If True, creates a new image with full stack tools, that is:
                                     - PostgreSQL
                                     - Nginx
                                     - Supervisor
                                     - Odoo
                                     - Openssh-server
        """
        self.client = Client()
        self._config = config
        self.version = config.version
        self.version_image = config.version
        self.working_folder = config.working_folder
        self.temp_working_folder = ''
        self.force = config.force
        self.full_stack_image = full_stack_image
        if not config.tag:
            config.tag = self._generate_image_name()
        self.new_image_name = config.tag
        if self.version in SAAS_VERSIONS:
            self.version_image = SAAS_VERSIONS[self.version]
        if full_stack_image and not self._config.container_config.get('build_image'):
            self.base_image_name = self._config.container_config.get('image_name')
        elif self._config.container_config.get('base_image_name'):
            self.base_image_name = self._config.container_config.get('base_image_name')
        else:
            self.base_image_name = utils.clean_string(
                'vauxoo/odoo-{ver}-image'.format(ver=self.version_image.replace('.', '')))
        self._templates_path = path.join(
            path.dirname(path.abspath(__file__)), '..', 'templates')
        self.files_path = path.join(self._templates_path, 'files')

    def _generate_image_name(self):
        """ Generates the name that the new image will have depending on the parameters
        used to build it, the name is created as follows:

        - Exactly one repo: { repo_name }-{ repo_branch }
        - Zero or more than one repo: { task_id }_{ customer_id }_image
        - full_stack_image = True: { task_id }_full_odoo_stack

        :return: New image name
        """
        repositories = list(self._config.instance_config.get('repositories'))
        if self.full_stack_image:
            name = '{tid}_full_odoo_stack'.format(tid=self._config.instance_config.get('task_id'))
        elif self._config.container_config.get('start_postgres_image'):
            name = '{tid}_postgres_image'.format(tid=self._config.instance_config.get('task_id'))
        elif len(repositories) == 1:
            repo = repositories[0]
            name = '{repo}{branch}'.format(repo=repo.get('name'), branch=repo.get('branch'))
        elif len(repositories) == 2:
            for repo in repositories:
                if repo.get('name') == 'odoo':
                    repositories.remove(repo)
                    name = '{repo}{branch}'.format(repo=repositories[0].get('name'),
                                                   branch=repositories[0].get('branch'))
                    break
            else:
                name = '{tid}_{cid}_image'.format(
                    tid=self._config.instance_config.get('task_id'),
                    cid=self._config.instance_config.get('customer_id'))
        else:
            name = '{tid}_{cid}_image'.format(tid=self._config.instance_config.get('task_id'),
                                              cid=self._config.instance_config.get('customer_id'))
        return utils.clean_string(name)

    def _render_odoo_service(self):
        """ Render the supervisor configuration file for Odoo depending on the version

        :return: None
        """
        env = Environment(loader=FileSystemLoader(self._templates_path))
        template = env.get_template('odoo_service.conf.jinja')
        service_file = template.render({'odoo_binary': ODOO_BINARY[self.version]})
        _logger.debug('Rendering supervisor config for Odoo %s', self.version)
        with open(path.join(self._files_folder, 'odoo_service.conf'), 'w') as text_file:
            text_file.write(service_file)

    def _render_postgres_service(self, psql_version=False):
        """ Render the supervisor configuration file for postgres depending on the `full_stack`
        parameter.

        :return: None
        """
        psql_version = psql_version or '9.6'
        env = Environment(loader=FileSystemLoader(self._templates_path))
        template = env.get_template('postgres_service.conf.jinja')
        service_file = template.render({'psql_version': psql_version})
        _logger.debug('Rendering supervisor config for Postgresql')
        with open(path.join(self._files_folder, 'postgres_service.conf'), 'w') as text_file:
            text_file.write(service_file)

    def _render_entrypoint_image(self):
        """ Render the entrypoint_image script

        :return: None
        """
        env = Environment(loader=FileSystemLoader(path.join(self._templates_path, 'files')))
        template = env.get_template('entrypoint_image.jinja')
        odoo_binarys = " ".join(["-e "+i for i in ODOO_BINARY.values()])
        service_file = template.render({'odoo_binarys': odoo_binarys})
        _logger.debug('Rendering supervisor config for Odoo %s', self.version)
        with open(path.join(self._files_folder, 'entrypoint_image'), 'w') as text_file:
            text_file.write(service_file)

    def _render_create_user_db(self):
        """ Render the create_user script sql

        :return: None
        """
        env = Environment(loader=FileSystemLoader(path.join(self._templates_path, 'files')))
        template = env.get_template('create_user.jinja')
        service_file = template.render(
            {'db_user': self._config.instance_config.get('config').get('db_user'),
             'db_password': self._config.instance_config.get('config').get('db_password')})
        _logger.debug('Rendering supervisor config for Odoo %s', self.version)
        with open(path.join(self._files_folder, 'create_user.sql'), 'w') as text_file:
            text_file.write(service_file)

    def _create_working_folder(self):
        """ Creates the working directory with the needed subdirectories and
            copies the files that will be used for the build.

            :return: dictionary containing the paths created inside the working folder
        """
        res = {}
        if path.isdir(self.working_folder) and self.force:
            shutil.rmtree(self.working_folder)
        if not path.isdir(self.working_folder):
            utils.makedir(self.working_folder)
        self.temp_working_folder = mkdtemp(prefix='deployv_', dir=self.working_folder)
        self._files_folder = path.join(self.temp_working_folder, 'files')
        try:
            shutil.copytree(self.files_path, self._files_folder)
        except OSError:
            _logger.error('The specified working folder already exists and it is not empty,'
                          ' use --force to remove it')
            raise
        self._render_odoo_service()
        self._render_entrypoint_image()
        self._render_create_user_db()
        instance_path = path.join(self._files_folder, 'instance')
        extra_path = path.join(instance_path, 'extra_addons')
        utils.makedir(instance_path)
        utils.makedir(extra_path)
        res.update({'instance': instance_path, 'extra_addons': extra_path})
        return res

    def _search_odoo_repo(self):
        """ Iterates over the repositories that will be used for the build to see
        if the odoo repo is specified or not by checking if a repo will be cloned in the
        path expected by supervisor. This is used to know whether to clone
        the default vauxoo/odoo repo or not.

        :return: dict with the info of the odoo repo if the odo repo was specified by the user
                 in the correct path, default one otherwise
        """
        res = {
            "name": "odoo",
            "path": "odoo",
            "commit": "",
            "depth": 1,
            "branch": self.version,
            "repo_url": {
                "origin": "https://github.com/Vauxoo/odoo.git"
            }
        }
        for repo in self._config.instance_config.get('repositories'):
            if repo.get('name') == 'odoo' and repo.get('path') == 'odoo':
                res = repo
                break
        return res

    def _clone_dependencies(self, instance_path, extra_path):
        """ Clones the repo odoo, the repositories specified in the config and
            all their oca dependencies inside the working folder.

            :param instance_path: Path to the instance folder where the odoo repo will be cloned.
            :param extra_path: Path to the extra_addons folder that will contain all of the other
                               repos that will be cloned (base repo and oca dependencies).
            :return: True if no error is raised.
        """
        odoo_repo = self._search_odoo_repo()
        if odoo_repo not in self._config.instance_config.get('repositories'):
            self._config.instance_config.get('repositories').append(odoo_repo)
        for repo in self._config.instance_config.get('repositories'):
            if not repo.get('branch'):
                repo.update({'branch': self.version})
            if not repo.get('name'):
                repo.update({
                    'name': branches_utils.name_from_url(repo.get('repo_url').get('origin'))}
                )
        temp_folder = self._config.temp_folder
        res = load_branches(self._config.instance_config.get('repositories'),
                            instance_path, temp_folder)
        if res:
            raise BuildError(res.get('msg'))
        clone_oca = clone_oca_deps(extra_path, extra_path, self.version)
        if not clone_oca[0]:
            raise BuildError(clone_oca[1])
        res = load_branches(self._config.instance_config.get('repositories'),
                            instance_path, temp_folder)
        if res:
            raise BuildError(res.get('msg'))
        return True

    def _generate_apt_requirements(self):
        """ Creates a file called apt_dependencies.txt in the deployv/templates/files with all
        the apt dependencies specified in the apt_install parameter in the json, this file is used
        by the install_deps.py script to install those dependencies during the build
        """
        deps_path = path.join(self._files_folder, 'apt_dependencies.txt')
        apt_requirements = self._config.container_config.get('apt_install')
        if not apt_requirements:
            return False
        with open(deps_path, 'w') as fileobj:
            for requirement in apt_requirements:
                fileobj.write(requirement + '\n')
        return deps_path

    def _create_image(self, template, values):
        """ Build a new image using a Dockerfile created by rendering a template with the
            parameters provided by the user.

            :param template: name of the template that will be used to create the dockerfile,
                             Dockerfile.jinja for the full stack image and build_dockerfile.jinja
                             for the image with the repos and their oca dependencies.
            :param values: values used to render the template

            :return: Name of the new image.
        """
        _logger.info('pulling base image %s', self.base_image_name)
        res = False
        try:
            self.client.pull(self.base_image_name)
        except docker.errors.NotFound:
            _logger.debug('Image not found in hub')
        env = Environment(loader=FileSystemLoader(self._templates_path))
        template = env.get_template(template)
        docker_file = template.render(values)
        with open(path.join(self.temp_working_folder, 'Dockerfile'), 'w') as text_file:
            text_file.write(docker_file)
        _logger.info('Building image')
        streams = []
        ansi_escape = re.compile(r'\x1b[^m]*m')
        for line in self.client.build(path=self.temp_working_folder, timeout=3600,
                                      rm=True, tag=self.new_image_name):
            obj = json.loads(line)
            if obj.get('stream'):
                # Keep a history of the streams. This is because sometimes the
                # messages get cut in the middle between streams.
                streams.append(obj.get('stream'))
                _logger.info(obj.get('stream').strip())
            elif obj.get('error'):
                _logger.error(obj.get('error').strip())
                # If we have a stream history, get the last five streamed messages.
                # This is to join any possible splitted message.
                if streams:
                    msg = "".join(streams[-5:])
                else:
                    # Else, just get the generic error message.
                    msg = obj.get('error')
                # Get only the last line from the error, because that's the
                # actual error message, and skip the traceback.
                msg = [val for val in ansi_escape.sub('', msg).split("\n") if val]
                raise BuildError(msg[len(msg)-1].strip())
        image_sha = self.client.images(name=self.new_image_name, quiet=True)
        res = image_sha and utils.decode(image_sha[0]).split(':')[1][:10]
        return res

    def _find_file(self, file_path, file_name):
        """Searches for a file with the provided name in the provided path,
        reads it, and returns its contents.

        :param file_path: Path where the search will be done
        :param file_name: Name of the file to find
        :return: The contents of the file or False if the file was not found
        """
        shell = spur.LocalShell()
        file_path = shell.run(
            ['find', file_path, '-name', file_name]
        )
        file_path = file_path.output.strip()
        if not path.exists(file_path):
            return False
        with open(file_path, 'r') as obj:
            file_contents = obj.read()
        return file_contents

    def _get_variables(self):
        """Searches for a file named `variables` among the cloned repositories
        and parses it to make the variables within it usable during the build.

        :return: List of environment variables (strings) in the format `var=val`
        :rtype: list
        """
        variables = self._find_file(self.temp_working_folder, 'variables.sh')
        if not variables:
            return []
        variables = variables.replace('export', '').strip().split('\n')
        return variables

    def _apply_patches(self, instance_path):
        """Searches for a file named `patches.txt` and applies the git patches
        specified in it directly in the specified repositories.
        """
        res = {'result': []}
        shell = spur.LocalShell()
        patches = self._find_file(self.temp_working_folder, 'patches.txt')
        if not patches:
            return res
        patches = patches.strip().split('\n')
        headers = [
            '--header=Authorization: token %s' % getenv('GITHUB_TOKEN'),
            '--header=Accept: application/vnd.github.VERSION.patch'
        ]
        for patch in patches:
            patch_parts = patch.split(' ', 1)
            repo = patch_parts[0]
            url = patch_parts[1]
            file_path = path.join(self._config.temp_folder, 'deployv.patch')
            cmd = ['wget', url, '-O', file_path]
            if 'api.github.com' in url:
                _logger.debug('A patch from a private repo will be applied: %s', url)
                cmd += headers
            try:
                shell.run(cmd)
            except spur.results.RunProcessError as error_obj:
                error = ('An error occurred while downloading the patch %s:\n%s' %
                         (url, error_obj.stderr_output))
                _logger.error(error)
                return {'error': error}
            repo_path = path.join(instance_path, repo)
            try:
                shell.run(['patch', '-f', '-p1', '-i', file_path, '-d', repo_path])
            except spur.results.RunProcessError as error_obj:
                error = ('An error occurred while applying the patch %s:\n%s' %
                         (url, error_obj.stderr_output))
                _logger.error(error)
                return {'error': error}
            shell.run(['rm', file_path])
            res.get('result').append(url)
        return res

    def build(self):
        """ Main method that builds the new image using the information
            provided by the user.

            :return: Dictionary with the name of the new image
        """
        res = {}
        _logger.info('Building image')
        try:
            paths = self._create_working_folder()
        except IOError as error:
            utils.clean_files([self.temp_working_folder])
            res.update({'error': utils.get_error_message(error)})
            return res
        if self._config.container_config.get('build_image'):
            try:
                self._clone_dependencies(paths['instance'], paths['extra_addons'])
            except spur.results.RunProcessError as error:
                utils.clean_files([self.temp_working_folder])
                res.update({"error": utils.get_error_message(error)})
                return res
            except BuildError as error:
                _logger.exception('Could not clone the repos: %s', utils.get_error_message(error))
                utils.clean_files([self.temp_working_folder])
                res.update({'error': utils.get_error_message(error)})
                return res
            variables = self._get_variables()
            psql_variable = [variable for variable in variables if 'PSQL_VERSION' in variable]
            psql_version = psql_variable and psql_variable[0].split('=')[1]
            if not psql_version:
                psql_version = '9.6'
                variables.append('PSQL_VERSION=9.6')
            self._generate_apt_requirements()
            self._render_postgres_service(psql_version)
            patches_res = self._apply_patches(paths['instance'])
            if patches_res.get('error'):
                return patches_res
            _logger.info('Patches applied: %s', '\n'.join(patches_res.get('result')))
            values = {
                'version': self.version,
                'variables': variables,
                'base_image_name': self.base_image_name,
                'full_stack': self.full_stack_image,
                'db_user': self._config.instance_config.get('config').get('db_user'),
                'db_password': self._config.instance_config.get('config').get('db_password'),
            }
            template = 'build_dockerfile.jinja'
            res = self._start_build(template, values)
            if not res.get('result'):
                utils.clean_files([self.temp_working_folder])
                return res
            self.base_image_name = res.get('result').get('image_name')
        if self.full_stack_image:
            values = {
                'base_image_name': self.base_image_name,
                'db_owner': self._config.instance_config.get('config').get('db_owner'),
                'db_owner_passwd': self._config.instance_config.get('config').get(
                    'db_owner_passwd'),
                'db_user': self._config.instance_config.get('config').get('db_user'),
                'db_password': self._config.instance_config.get('config').get('db_password'),
                'db_name': self._config.instance_config.get('config').get('db_name')
            }
            template = 'Dockerfile.jinja'
            res = self._start_build(template, values)
        utils.clean_files([self.temp_working_folder])
        return res

    def _start_build(self, template, values):
        res = {}
        try:
            sha = self._create_image(template, values)
        except IOError as error:
            res.update({'error': utils.get_error_message(error)})
            return res
        except BuildError as error:
            error = utils.get_error_message(error)
            if "This image has already been build with deployv" in error:
                error = ('An image that has already been built with deployv'
                         ' can\'t be used to build another image.')
            res.update({'error': error})
            return res
        res.update({'result': {'image_name': self.new_image_name, 'image_sha': sha}})
        return res


def add_repo(config, branch, name, repo_path, repo_url):
    """ Creates a dictionary with the info of the specified repo and
    appends it to the repositories list in the config dictionary

    :param config: Config dict where the new repo will be added
    :param name: Name of the repository
    :param path: Path inside ~/instance where the repository will be cloned
    :param repo_url: ssh or https URL used to clone the repo
    :param branch: branch of the repo we want to clone
    :return: Config dict with the new repo
    """
    repo_dict = {
        'branch': branch,
        'name': name,
        'path': repo_path,
        'commit': '',
        'depth': 1,
        'repo_url': {
            'origin': repo_url
        }
    }
    config.get('instance').get('repositories').append(repo_dict)
    return config


def build_image(config):
    """ Calls the build helper class with the needed parameters depending if
    a new full stack image, develop image or both will be created.
    If the config dictionary has both, build_image = true and postgres_container = true,
    first it will build a new image with the repos specified in the config and their
    oca dependencies, then that image will be used as base in order to build another one
    with the full stack tools.

    :param config: Configuration object with the format used by deployv.
    :return: dictionary with the new image created or an error.
    """
    build_res = {}
    config.check_config('build_image')
    if not config.version:
        version = config.instance_config.get('version') or utils.version_cid(
            config.instance_config.get('customer_id'))
        if version is None:
            return {'error': ('You need to specify the customer id with the correct format'
                              ' or use the version parameter. Example: customer80 or'
                              ' customersaas-14')}
        config.version = version
    _logger.debug('Starting the build image process with:')
    _logger.debug(json.dumps(config._deploy_config, sort_keys=True, indent=2))
    full_stack = config.container_config.get('full_stack')
    config.working_folder = config.working_folder or config.temp_folder
    if not config.container_config.get('build_image') and not full_stack:
        build_res.update({'error': 'You must use the build_image and/or full_stack parameters'})
        return build_res
    _logger.debug('Building single image')
    build_class = BuildImage(config, full_stack_image=full_stack)
    build_res = build_class.build()
    return build_res
