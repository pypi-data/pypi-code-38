# coding: utf-8

"""This class has the algorithms that will be executed by deployvcmd and deployvd, both are
interfaces between the input (files, cmd interface and rabbitmq) and CommandV.

`extend_me <http://pythonhosted.org/extend_me/>`_ is used in the event manager class and the core
command component because it allows an easy app extension without the need of modifying the core
components.

CommandV inherits from `Extensible <http://pythonhosted.org/extend_me/#extensible>`_ base class so
it can be extended in a simple way by just inheriting from CommandV.
"""

import logging
import os
import re
import yaml
import simplejson as json
import base64
from tempfile import mkdtemp
from extend_me import Extensible
from psycopg2 import OperationalError
from datetime import datetime
from docker import APIClient as Client
from docker.errors import APIError, NullResource, NotFound, ContainerError, ImageNotFound
from deployv.base import errors
from deployv.base.extensions_core import events, load_extensions
from deployv.base import postgresv, nginxv
from deployv.helpers import utils, container, database_helper, sender_message, \
    build_helper, json_helper
from deployv.instance import instancev, ODOO_BINARY
from deployv.extensions.checkers import InstallTestRepo
from transitions import State, Machine

logger = logging.getLogger(__name__)  # pylint: disable=C0103

load_extensions()


STATES = [
    'Starting',
    State('Building image'),
    State('Creating container'),
    State('Deactivating database'),
    State('Restoring backup'),
    State('Generating backup'),
    State('Deactivating backup'),
    State('Changing passwords'),
    State('Updating database'),
    State('Destroying instance'),
    State('Pushing images'),
    State('Updating production instance'),
    State('Restarting container'),
    State('Restarting instance'),
    State('Executing final steps'),
    'Done', 'Error'
]


class CommandV(Extensible):
    """ Class that contains the main methods of each command

    :param config: Configuration dictionary. See :class:`~deployv.base.instancev.InstanceV`.
    :type config: dict
    :param instance_class: Class for the instance manager object.
    :type instance_class: class
    """

    def __init__(self, config_obj, instance_class=None):
        self.__config = config_obj
        self._domains = None
        self.sender = sender_message.SenderMessage(self.__config)
        transitions_path = os.path.join(
            os.path.dirname(__file__), '../config', 'transitions.json')
        transitions = json_helper.load_json(transitions_path)
        self.process = Machine(model=self, states=STATES, transitions=transitions,
                               initial='Starting')
        self._update_done = False
        self._need_revert = False
        if self.__config.instance_config:
            prefix = container.generate_prefix(self.__config)
            self.__config.prefix = prefix and prefix.lower()
        if instance_class:
            self.__instance_manager = instance_class(self.__config)
        else:
            self.__instance_manager = instancev.InstanceV(self.__config, timeout=3000)

    @property
    def instance_manager(self):
        return self.__instance_manager

    def deactivating_database(self):
        """Transitions condition used to take the process setps required to
        deactivate a database. This method only returns True if the
        deactivate command is called or if the `deactivating_database`
        parameter is specified in the config json > group_config dictionary.
        """
        return self.__config.deactivating_database

    def pushing_images(self):
        """Transitions condition used to finish the process after pushing
        the images. This condition was only added in order to keep the
        posibility to create a `push` command.
        """
        return self.__config.pushing_images

    def create_database(self):
        """Transitions condition used to add the `restore` command to
        the process. This method returns the value stored in the
        config json > instance > restore_db key.
        """
        return self.__config.instance_config.get('restore_db')

    def need_revert(self):
        """Transitions condition used to go to the `Create container` state
        if an error occurs, only used during the `update_production` command
        to revert the changes if an error occurs when the production databases
        are updated.
        """
        return self._need_revert

    def deactivate_required(self):
        """Transitions condition used to add the `deactivate` step to the
        process. This method only returns True if the
        config json > instance > instance_type key is any of `updates`,
        `develop`, or `test`.
        """
        instance_type = self.__config.instance_config.get('instance_type')
        if instance_type in instancev.DEACTIVATE:
            return True
        return False

    def update_required(self):
        """Transitions condition used to add the `update` step to the process.
        This method only returns True if the
        config json > instance > instance_type key is `updates` or `develop`.
        """
        if self._update_done:
            return False
        instance_type = self.__config.instance_config.get('instance_type')
        if instance_type in instancev.UPDATE or self.__config.container_config.get('keep_db'):
            InstallTestRepo.event = 'after.updatedb.event'
            return True
        return False

    def deactivating_backup(self):
        """Transitions condition used to take the process setps required to
        deactivate a backup. This method only returns True if the
        deactivate_backup command is called or if the `deactivating_backup`
        key is specified in the config json > group_config dictionary.
        """
        return self.__config.deactivating_backup

    def build_image_required(self):
        """Transitons condition used to add the `build_image` step to
        the process. This only returns True if either the `build_image` or
        `full_stack` keys in config json > container_config are True.
        """
        cfg = self.__config.container_config
        return cfg.get('build_image') or cfg.get('full_stack')

    def skip_push(self):
        """Transitions condition used to skip the `push_images` step during
        the process in order to avoid pushing the full stack images, this is
        also used to willingly skip the push during a process. The condition
        is True if the config json > container_config > `full_stack` or the
        config json > group_config > skip_push keys are True.
        """
        return self.__config.container_config.get('full_stack') or self.__config.skip_push

    def create_container(self):
        """Transitions condition used to add the `create container` step to
        the process. This method only returns True if the `create` command
        is called or if the config json > group_config > create_container key
        is True.
        """
        return self.__config.create_container

    def updating_instance(self):
        """Transitions condition used to take the process steps required to
        update an instance from orchest.
        """
        return self.__config.updating_instance

    def _can_add_new(self):
        """As we have a limited amount of resources in each node we need to check if the running
        instances count is less than the allowed to run a new one.

        :returns: If the count of running instances is lower than the allowed max.
        :rtype: bool
        """
        containers = self.instance_manager.cli.containers()
        max_instances = self.__config.deployer.get('max_instances')
        if not max_instances:
            return True
        count = 0
        for container_info in containers:
            for name in container_info.get('Names'):
                if re.match(r'/([\w\d\_\-]+)_odoo$', name):
                    count += 1
                    break
        logger.debug('Instance count %s/%s', count, max_instances)
        return count < max_instances

    def build_image(self):
        """Builds a new image using the configuration in the json
        and returns the name of the image built as well as the first 10
        characters of it's sha.

        :return: Dictionary with the `image_name` and `image_sha` keys
        """
        res = {'command': 'build_image'}
        self.sender.send_message('Building image.')
        self.__config.check_config('build_image')
        self.instance_manager.add_extra_repos()
        build_res = build_helper.build_image(self.__config)
        logger.debug('Build res %s', res)
        res.update(build_res)
        if res.get('error'):
            self.sender.send_message(msg=res.get('error'), body=res, log_type='ERROR')
            self.error_trigger()
            return res
        self.sender.send_message('Image {} built.'.format(
            res.get('result').get('image_name')))
        base_img = self.__config.container_config.get('customer_image')
        tag_img = '{img}:{tag}'.format(
            img=base_img, tag=res['result'].get('image_sha'))
        if not isinstance(self.__config.container_config.get('push_image'), list):
            self.__config.container_config.update({'push_image': []})
        instance_type = self.__config.instance_config.get('instance_type')
        self.__config.container_config.get('push_image').append({
            'tag': res['result'].get('image_sha'), 'base': base_img,
            'image': res.get('result').get('image_name'),
            'tag_latest': True if instance_type == 'updates' else False})
        self.__config.container_config.update({
            'image_name': (tag_img if not self.skip_push() else
                           res.get('result').get('image_name'))
        })
        self.build_done_trigger()
        return res

    @utils.traceback_docker_error
    @events
    def create(self):
        """Creates an Odoo dockerized instance with the provided configuration.

        :returns: A response in json format containing the info dict returned
            by :func:`~deployv.base.dockerv.DockerV.basic_info`.
        :rtype: dict
        """
        res = {'command': 'create', 'result': {},
               'attachments': list()}
        self.sender.send_message('Creating instance.')
        self.__config.check_config('create')
        if not self._can_add_new():
            logger.info('Max instance count reached (%s allowed)',
                        self.__config.deployer.get('max_instances'))
            res.update({'error': 'Reached max instance count for this node ({} allowed)'
                       .format(self.__config.deployer.get('max_instances'))})
            self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
            self.error_trigger()
            return res
        self.instance_manager.add_extra_repos()
        try:
            info = self.instance_manager.start_odoo_container()
        except (KeyboardInterrupt, errors.GracefulExit):
            raise
        except Exception as error:  # pylint: disable=W0703
            logger.exception('Could not start container')
            res.update({'error': utils.get_error_message(error)})
            self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
            self.error_trigger()
            return res
        if info.get('error'):
            res.update({'error': info.get('error')})
            self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
            self.error_trigger()
            return res
        if info and self.__config.instance_config.get('ssh_key'):
            self.instance_manager.deploy_key()
            self.instance_manager.check_keys()
        self.sender.send_message('Configuring instance.')
        res_build = self.instance_manager.build_instance()
        if self.__config.container_config.get('full_stack'):
            self.instance_manager.remove_key()
        if not res_build[0]:
            res.update({'error': res_build[1]})
            self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
            self.error_trigger()
            return res
        self.sender.send_message('Instance configured.')
        post_branch = os.path.join(self.instance_manager.temp_folder, 'post_process.json')
        res.get('attachments').append(
            {
                'file_name': os.path.basename(post_branch),
                'file': utils.generate_attachment(post_branch),
                'type': 'application/json'
            }
        )
        if info:
            res.get('result').update(info)
            if self.__config.deployer:
                logger.debug('Use nginx config: %s',
                             self.__config.deployer.get('use_nginx', False))
                if self.__config.deployer.get('use_nginx', False):
                    logger.debug('Using nginx')
                    self._domains = self.update_nginx()
                    nginx_url = self._get_nginx_url(info.get('name')[:-5].replace('_', '-'))
                    res['result'].update({
                        'nginx_url': "http://{url}".format(url=nginx_url),
                        'instance_log': '{url}/logs/odoo_stdout.log'.format(url=nginx_url)
                    })
        if not self.create_database():
            self.instance_manager.start_instance()
        res.update({'instance_revert': self._need_revert})
        self.sender.send_message('Instance created', body=res)
        self.create_done_trigger()
        return res

    def _get_nginx_url(self, name):
        nginx_url = None
        for domain in self._domains:
            if domain.get('domain').startswith(name):
                nginx_url = "{domain}.{server}".format(
                    domain=domain.get('domain'), server=self.__config.deployer.get('domain'))
                break
        logger.debug('Updating url : %s', nginx_url)
        return nginx_url

    def deactivate(self, database=False):
        database = database or self.__config.instance_config.get('config', {}).get('db_name')
        self.sender.send_message('Deactivating database {}.'.format(database))
        self.__config.check_config('deactivate')
        db_config = self.instance_manager.db_config.copy()
        db_config.update({
            'nginx_url': self.instance_manager.config.get('nginx_url'),
            'use_mailhog': self.__config.instance_config.get("use_mailhog")})
        extras_sql = self.instance_manager.extras_deactivate()
        instancev.deactivate_database(db_config, database, extras_sql=extras_sql)
        new_admin = self.__config.instance_config.get('config').get('admin', False)
        if new_admin:
            db_config.update({'db_name': database})
            cfg = utils.odoo2postgres(db_config)
            with postgresv.PostgresConnector(cfg) as conn:
                admin_users = conn.execute(
                    "select id from ir_model_data where name in"
                    " ('user_root', 'user_admin');")
            admin_id = 2 if len(admin_users) > 1 else 1
            instancev.InstanceV.change_password(
                admin_id, new_admin, database, db_config)
        self.sender.send_message('Database {} deactivated.'.format(database))
        self.deactivate_done_trigger()

    @utils.traceback_docker_error
    def post_process(self):
        """Command in charge of performing the steps required after deploying an instance
        like generating the cloc report.

        :returns: dict with the results or the errors
        """
        self.sender.send_message('Executing final steps.')
        res = {'command': 'post_process'}
        post_process = ['cloc_report', 'list_packages']
        if self.__config.instance_config.get('original_database'):
            post_process.append('compare_databases')
        for command in post_process:
            if not hasattr(self, command):
                msg = 'Command {} does not exist, skipping from the post process'.format(command)
                logger.error(msg)
                self.sender.send_message(msg, log_type='ERROR')
                continue
            cmd_method = getattr(self, command)
            cmd_res = cmd_method()
            if 'error' in cmd_res.keys():
                res.update({'error': cmd_res.get('error')})
                self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
                self.error_trigger()
                return res
            cmd_res.pop('command', False)
            res.update({command: cmd_res})
        res.update({'instance_revert': self._need_revert})
        self.sender.send_message('Steps executed', body=res)
        self.done_trigger()
        return res

    def cloc_report(self):
        """This method generates a report by the cloc command the number of lines of code that has
        an instance and stores it in yaml format to be added as an attachment.

        :returns: a list of the dictionary that has the output of the cloc command in yaml format
            to be added as an attachment.
        :rtype: dict
        """
        res = {'command': 'cloc_report', 'attachments': list()}
        command_exists = self.__instance_manager.exec_cmd("which cloc")
        if not command_exists:
            res.update({
                'result': 'CLOC is not installed in the container, report not generated'
            })
            return res
        odoo_home = self.__instance_manager.\
            config.get('env_vars').get('odoo_home')
        module = os.path.join(odoo_home, 'instance')
        command_cloc = "cloc --yaml {module}".format(module=module)
        execute_cloc = self.__instance_manager.exec_cmd(command_cloc)
        body_content = execute_cloc.split('\n---')
        res.get('attachments').append(
            {
                "file_name": "cloc_report",
                "file": utils.decode(base64.b64encode(utils.encode(json.dumps(
                    yaml.load(body_content[1]), indent=4
                )))),
                "type": 'application/json'
            }
        )
        res.update({'result': 'CLOC report successfully generated'})
        return res

    def list_packages(self):
        """This method dumps a list of packages installed inside the container with `apt` and `pip`.
        """
        res = {
            'command': 'list_packages',
            'packages': self.__instance_manager.get_container_packages()
        }
        return res

    @utils.traceback_docker_error
    @events
    def restore(self):
        """Restores a backup from a file or folder. If a folder is provided, searches the best
        match for the given configuration. Database name is an optional parameter.

        The return value is a dict as follows::

            {
                'command': 'command executed',
                'result':
                {
                    'backup': 'backup file used to restore the database',
                    'database_name': 'the database name created with the corresponding backup'
                }
            }

        In case of any error::

            {
                'command': 'command executed',
                'error': 'error message'
            }

        :param backup_src: Backup source, can be a folder or a backup file.
        :type backup_src: str
        :param database_name: Database name to restore. If None, is generated automatically.
        :type database_name: str
        :param deactivate: Force db deactivation ignoring the instance type.
        :type deactivate: bool
        :returns: A json object with the result or error generated. If any result is generated the
            result key will have the backup used and the database name.
        :rtype: dict
        """
        self.sender.send_message('Creating database')
        self.__config.check_config('restore')
        res = {'command': 'restore', 'result': {}}
        database_name = self.__config.instance_config.get('config').get('db_name')
        restore_from = self.__config.instance_config.get('restore_db_from')
        if restore_from:
            msg = 'Copying database from: {}.'.format(restore_from.get('container_name'))
            self.sender.send_message(msg)
            logger.info(msg)
            commandv = CommandV({'container_config': {
                'container_name': restore_from.get('container_name'),
            }})
            backup_res = commandv.backup(False, restore_from.get('db_name'), cformat=False)
            if backup_res.get('error'):
                res.update({'error': backup_res.get('error')})
                self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
                self.error_trigger()
                return res
            self.__config.backup_src = backup_res.get('result').get('tmp_dir')
        if not self.__config.backup_src:
            result = self.create_db_demo()
            res.update(result)
            self.sender.send_message(body=res)
            self.restore_done_trigger()
            return res
        try:
            self.sender.send_message('Restoring a backup in the database "{}".'
                                     .format(database_name))
            restore_res = self.__instance_manager.restore_database(
                database_name, self.__config.backup_src)
            res.update(restore_res)
        except (OperationalError, EOFError, AttributeError) as error:
            logger.exception(error)
            res.update({'error': utils.get_error_message(error)})
        if res.get('error', False):
            self.sender.send_message(msg=res.get('error'), body=res, log_type='ERROR')
            self.error_trigger()
            return res
        if self.__config.instance_config.get('instance_type') == 'updates':
            original_db = self.instance_manager.clone_db(database_name)
            self.__config.instance_config.update({'original_database': original_db})
            res.get('result').update({'original_database': original_db})
        self.__instance_manager.start_instance()
        logger.debug('restore_res: %s', str(restore_res))
        if restore_from:
            utils.clean_files(self.__config.backup_src)
        user = self.instance_manager.get_odoo_users(database_name, user_id=1)
        res.get('result').update({'user_admin': (user and user[0] or {}).get("login")})
        params = {'database.generated_at': restore_res["result"].get('create_date'),
                  'database.type': self.instance_manager.instance_type}
        self.instance_manager.set_parameters(database_name, params)
        self.sender.send_message(msg='Database "{}" created.'.format(database_name), body=res)
        self.restore_done_trigger()
        return res

    def _attach_file(self, msg, file_name, file_type):
        res = msg
        if not res.get('attachments', False):
            res.update({'attachments': list()})
        res.get('attachments').append(
            {
                'file_name': os.path.basename(file_name),
                'file': utils.generate_attachment(file_name),
                'type': file_type
            }
        )
        return res

    def _install_module(self, db_name):
        install_res = self.__instance_manager.install_module(
            self.__config.instance_config.get('install_module'),
            db_name
        )
        return install_res

    @events
    def backup(self):
        res = {'command': 'backup'}
        self.__config.check_config('backup')
        database_name = self.__config.instance_config.get('config').get('db_name')
        prefix = self.__config.prefix
        bkp_dir = self.__config.backup_src or os.getcwd()
        try:
            bkp = self.__instance_manager.generate_backup(
                database_name, bkp_dir, cformat=self.__config.cformat,
                reason=self.__config.reason, tmp_dir=self.__config.temp_folder, prefix=prefix)
        except errors.DumpError as error:
            logger.exception('Backup could not be generated')
            res.update({'error': 'Could not generate the backup: {0}'
                       .format(utils.get_error_message(error))})
            self.sender.send_message(msg=res['error'], body=res, log_type='ERROR')
            self.error_trigger()
            return res
        if bkp:
            res.update({'result': bkp})
            logger.info("Backup generated: %s", bkp)
        else:
            res.update({'error': 'Could not generate the backup'})
            logger.error(res['error'])
        self.sender.send_message(body=res)
        self.done_trigger()
        return res

    def deactivate_backup(self):
        self.__config.check_config('deactivate_backup')
        db_config = self.__config.instance_config.get('config')
        prefix = self.__config.prefix
        admin_password = db_config.get('admin')
        if not db_config.get('db_host') or utils.is_docker_ip(db_config.get('db_host')):
            db_config.update({'db_host': 'localhost'})
        working_dir = mkdtemp(dir=self.__config.temp_folder, prefix='deployv_')
        db_helper_class = database_helper.DatabaseHelper.get_helper(use_template=False)
        db_helper = db_helper_class(utils.odoo2postgres(db_config))
        candidate = db_helper.search_candidate(self.__config.backup_src, prefix)
        prefix = '{prefix}_deactivated'.format(prefix=prefix)
        db_name = utils.generate_dbname({}, candidate[1], prefix)
        postgres = postgresv.PostgresShell(utils.odoo2postgres(db_config))
        logger.info('Restoring backup to be deactivated')
        postgres.drop(db_name)
        try:
            dest_dir = utils.decompress_files(candidate[1], working_dir)
        except (EOFError, IOError) as error:
            error_msg = utils.get_error_message(error)
            logger.error(error_msg)
            utils.clean_files(working_dir)
            return False
        restore_res = db_helper.create_database(
            dest_dir, db_name.lower(), db_config.get('db_user'), db_config.get('db_password'),
            jobs=self.__config.jobs)
        if not restore_res[0]:
            logger.error(restore_res[1])
            return False
        logger.info('Deactivating database')
        instancev.deactivate_database(db_config, db_name)
        instancev.InstanceV.change_password('1', admin_password, db_name, db_config)
        dump_path = 'database_dump.sql' if not self.__config.jobs else 'database_dump'
        dump_path = os.path.join(working_dir, dump_path)
        logger.info('Generating deactivated backup')
        postgres.dump(db_name, dump_path, jobs=self.__config.jobs)
        backup_name = utils.generate_backup_name(db_name)
        files2backup = [dump_path]
        files = os.listdir(dest_dir)
        for element in files:
            if any([self.__config.no_fs and element == "filestore",
                    element in ['database_dump.sql', 'database_dump']]):
                continue
            full_path = os.path.join(dest_dir, element)
            files2backup.append(full_path)
        logger.info('Generating backup with the files %s', ', '.join(files2backup))
        backup = utils.compress_files(
            backup_name, files2backup, dest_folder=self.__config.store_path,
            cformat=self.__config.cformat)
        postgres.drop(db_name)
        utils.clean_files(working_dir)
        if self.__config.upload:
            utils.upload_file(backup, self.__config.upload)
            logger.info('File uploded to %s', self.__config.upload)
        if self.__config.remove:
            os.remove(backup)
        logger.info('Deactivated backup generated: %s', backup)
        self.done_trigger()
        return backup

    def change_passwords(self):
        """Generates a random password for each one of the users in an instance.
        """
        res = {'command': 'change_passwords'}
        results = {}
        db_name = self.__config.instance_config.get('config').get('db_name')
        self.sender.send_message('Changing passwords of the database "{}".'.format(db_name))
        try:
            users = self.instance_manager.get_odoo_users(db_name)
        except OperationalError as error:
            error_msg = ("Failed to change the users passwords: {0}"
                         .format(error.message))
            res.update({'error': error_msg})
            self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
            self.error_trigger()
            return res
        for user in users:
            if user.get('login') not in ['public', 'portaltemplate']:
                password = utils.random_string(10)
                result = instancev.InstanceV.change_password(user.get('id'), password, db_name,
                                                             self.instance_manager.db_config)
                if result.get('error'):
                    res.update(result)
                    self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
                    self.error_trigger()
                    return res
                results.update({user.get('login'): password})
        res.update({'result': results})
        self.sender.send_message(msg='Passwords changed.', body=res)
        self.done_trigger()
        return res

    def compare_databases(self):
        res = {'command': 'compare_databases'}
        original_db = self.__config.instance_config.get('original_database')
        updated_db = self.__config.instance_config.get('config').get('db_name')
        self.sender.send_message('Comparing the databases "{}" with "{}".'.format(
            original_db, updated_db))
        # Get all the data
        try:
            original_translations = self.instance_manager.get_translations(original_db)
            updated_translations = self.instance_manager.get_translations(updated_db)
            original_menus = self.instance_manager.get_menus(original_db)
            updated_menus = self.instance_manager.get_menus(updated_db)
            original_views = self.instance_manager.get_views(original_db)
            updated_views = self.instance_manager.get_views(updated_db)
            original_fields = self.instance_manager.get_fields(original_db)
            updated_fields = self.instance_manager.get_fields(updated_db)
        except OperationalError as error:
            res.update({'error': 'Failed to compare the databases: {err}'.format(
                err=error.message)})
            self._drop_dbs([original_db])
            self.sender.send_message(res.get('error'), log_type='ERROR')
            return res
        # Compare the data
        translations_diff = self.instance_manager.compare_translations(
            original_translations, updated_translations)
        menus_diff = self.instance_manager.compare_menus(
            original_menus, updated_menus, original_db, updated_db)
        views_diff = self.instance_manager.compare_views(original_views, updated_views)
        fields_diff = self.instance_manager.compare_fields(original_fields, updated_fields)
        res.update({'result': {'translations': translations_diff,
                               'menus': menus_diff,
                               'views': views_diff,
                               'fields': fields_diff}})
        self._drop_dbs([original_db])
        self.sender.send_message('Compared the databases "{}" with "{}".'.format(
            original_db, updated_db))
        return res

    @utils.traceback_docker_error
    @events
    def updatedb(self, db_name=False):
        """Updates an instance (branches and database) and returns the json with a summary of the
        operation.

        :param database_name: Database name to be updated.
        :type database_name: str
        :returns: The result from :meth:`deployv.instance.instancev.run_and_log`.
        :rtype: dict
        """
        db_name = db_name or self.__config.instance_config.get('config').get('db_name')
        self.sender.send_message('Updating database "{}".'.format(db_name))
        self.__config.check_config('updatedb')
        update_modules = self.__config.instance_config.get('update_module', ["all"])
        if not isinstance(update_modules, list):
            update_modules = update_modules.split(",")
        res = {'command': 'updatedb'}
        try:
            self.__instance_manager.stop_instance()
        except APIError as error:
            error_msg = utils.get_error_message(error)
            logger.exception('Could not update database %s: %s', db_name, error_msg)
            res.update({'error': error_msg})
            self.sender.send_message(error_msg, body=res, log_type='ERROR')
            self.error_trigger()
            return res
        retry = 0
        res.update({"attachments": [], "result": {"update_logs": []}})
        for module in update_modules:
            while retry <= 1:
                res_update = self.__instance_manager.update_db(module, db_name)
                if res_update.get('errors'):
                    if retry < 1:
                        logger.info(
                            'Some error shown in the update log, updating again')
                        retry = retry + 1
                    else:
                        logger.error('The instance was not updated properly, check logfile: %s',
                                     res_update.get('log_file'))
                        res['result']['update_logs'].append(res_update)
                        break
                else:
                    res['result']['update_logs'].append(res_update)
                    break
        self.__instance_manager.start_instance()
        for log in res["result"]["update_logs"]:
            res["attachments"].append(
                {
                    'file_name': os.path.basename(log["log_file"]),
                    'file': utils.generate_attachment(log["log_file"]),
                    'type': 'text/plain'
                })
        res['result'].update({'database_name': db_name})
        install_module = self.__config.instance_config.get('install_module')
        if install_module:
            self.sender.send_message('Installing module(s): {}.'.format(', '.join(install_module)))
            install_res = self.__instance_manager.install_module(install_module, db_name)
            res['result'].update({
                'install_module': install_res
            })
            if not res.get('attachments', False):
                res.update({'attachments': list()})
            res.get('attachments').append(
                {
                    'file_name': os.path.basename(install_res.get('log_file')),
                    'file': utils.generate_attachment(install_res.get('log_file')),
                    'type': 'text/plain'
                }
            )
        if self.updating_instance() and not self.skip_push():
            image = self.__config.container_config.get('image_name')
            expr = r'(?P<url>[^/]*)/(?P<repo>.*):(?P<tag>.*)'
            match = re.match(expr, image)
            if not match:
                res.update({'error': ("Unable to push the updated image: Bad format in"
                                      " image name {img}").format(img=image)})
                self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
                self.error_trigger()
                return res
            res.get('result').update({'image': image})
            tag = match.groupdict().get('tag')
            instance_type = self.__config.instance_config.get('instance_type')
            self.__config.container_config.get('push_image').append({
                'tag': tag, 'base': self.__config.container_config.get('customer_image'),
                'tag_latest': True if instance_type == 'updates' else False})
        self._update_done = True
        self.sender.send_message('Database "{}" updated.'.format(db_name), body=res)
        self.update_done_trigger()
        return res

    @utils.traceback_docker_error
    @events
    def update_branches(self):
        """Updates repos in the given instance.

        :return: Returns the operation result in the json format, additionally will attach the
            current instance status with the commits, repos and branches. See
            :mod:`~deployv.helpers.branches` for more info about the format.
        :rtype: dict
        """
        self.sender.send_message('Updating branches.')
        res = {'command': 'update_branches'}
        if self.__config.instance_config.get('ssh_key'):
            self.__instance_manager.deploy_key()
            self.__instance_manager.check_keys()
        res_build = self.__instance_manager.build_instance()
        if self.__config.container_config.get('full_stack'):
            self.instance_manager.remove_key()
        if not res_build[0]:
            res.update({
                'error': 'Could not generate instance with the given branches: {}'
                         .format(res_build[1])
            })
            self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
            self.error_trigger()
            return res
        install_log = self.__instance_manager.install_deps()
        logger.info(install_log)
        if install_log:
            res.update(install_log)
        self.__instance_manager.stop_instance()
        if not res.get('attachments', False):
            res.update({'attachments': list()})
        post_branch = os.path.join(self.__instance_manager.temp_folder, 'post_process.json')
        res.get('attachments').append(
            {
                'file_name': os.path.basename(post_branch),
                'file': utils.generate_attachment(post_branch),
                'type': 'application/json'
            }
        )
        res.update({'result': 'Branches updated'})
        self.sender.send_message('Branches updated.', body=res)
        return res

    def _stop_instance(self):
        try:
            self.__instance_manager.stop_instance()
        except NotFound as error:
            logger.debug('Error message %s', utils.get_error_message(error))
            utils.get_error_message(error)
            return 'Instance already deleted'
        except NullResource as error:
            if "image or container param is undefined" in error.message:
                return 'Instance already deleted or misspelled name'
        return True

    def _drop_dbs(self, dbs_to_delete):
        db_owner = self.__config.instance_config.get('config').get('db_owner')
        db_owner_passwd = self.__config.instance_config.get('config').get('db_owner_passwd')
        psql_dict = utils.odoo2postgres(self.__instance_manager.db_config)
        psql_dict.update({"owner": db_owner, "owner_password": db_owner_passwd})
        error_msgs = ["Connection refused", "password authentication failed"]
        try:
            psql_shell = postgresv.PostgresShell(psql_dict)
        except OperationalError as error:
            if any([msg in error.message for msg in error_msgs]):
                return
            raise
        res = []
        for db_name in dbs_to_delete:
            logger.debug('Dropping %s database', db_name)
            psql_shell.drop(db_name, force=True)
            res.append('Dropped %s database' % db_name)
        return res

    @events
    def delete_instance(self):
        """Delete an instance and database from the node.  If it does not exists or was already
        deleted, will indicate it in the message.

        :returns: A json object with the result or error generated. The result key will contain the
            generated result message, if any.
        :rtype: dict
        """
        self.sender.send_message('Deleting container(s).')
        logger.info('Deleting container(s)')
        res = {'command': 'delete_instance'}
        result = []
        try:
            self.instance_manager.clean_volumes()
        except (NullResource, errors.NotRunning, errors.CommandError) as error:
            allowed_errors = ['image or container param is undefined', 'is not running',
                              'Container does not exist']
            error_msg = utils.get_error_message(error)
            if any([allowed_error in error_msg for allowed_error in allowed_errors]):
                logger.error(
                    'Could not clean the container\'s volumes, container not found or not running'
                )
            else:
                res.update({'error': utils.get_error_message(error)})
                self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
                self.error_trigger()
                return res
        try:
            config = self.instance_manager.config
            self.instance_manager.remove_container(config.get('container_name'))
            result.append('Instance {} deleted'.format(config.get('container_name')))
            if config.get('postgres_container_name'):
                self.instance_manager.remove_container(config.get('postgres_container_name'))
                result.append('Instance {} deleted'.format(config.get('postgres_container_name')))
            if self.__instance_manager.instance_type == "develop":
                remove_img = self.instance_manager.remove_image(config.get('image_name'))
                result += remove_img
            if not config.get('keep_db'):
                db_name = self.__config.instance_config.get('config').get('db_name')
                res_dropdb = self._drop_dbs([db_name])
                result.extend(res_dropdb)
            res.update({
                'result': result
            })
            if self.__config.deployer.get('use_nginx'):
                self.update_nginx()
        except (KeyboardInterrupt, errors.GracefulExit):
            raise
        except Exception as error:  # pylint: disable=W0703
            logger.exception('Could not remove container')
            if "No such container or id: None" in utils.get_error_message(error):
                res.update({'result': 'Instance already deleted or misspelled name'})
            else:
                res.update({'error': utils.get_error_message(error)})
            self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
            self.error_trigger()
            return res
        self.sender.send_message('Container(s) deleted.', body=res)
        self.destroy_done_trigger()
        return res

    def get_containers(self):
        """Gets the containers list that are currently executing, which names match the
        regex: '^/([tiu][0-9]+_[a-z]+[0-9]+)_odoo', for example: 't111_cust80_odoo'.

        :return: Containers (as dict) with the domain and mapping ports.
        :rtype: list
        """
        cli = Client()
        containers = cli.containers()
        res = list()
        logger.debug('Geting containes names')
        regex = r'/([\w\d\_\-]+)_odoo$'
        for container_info in containers:
            for name in container_info.get('Names'):
                logger.debug('Name : %s', name)
                domain = re.match(regex, name)
                if not domain:
                    continue
                domain = domain.group(1).replace('_', '-')
                inspected = self.instance_manager.inspect(container_info.get('Id'))
                envs = inspected.get('Config').get('Env')
                envs = container.parse_env_vars(envs)
                if envs.get('instance_type') != 'develop':
                    continue
                ports_info = container.get_ports_dict(inspected)
                res.append({
                    'domain': domain,
                    'port': ports_info.get('8069'),
                    'lp_port': ports_info.get('8072'),
                    'logs': os.path.join(
                            os.path.expanduser(
                                    self.__config.container_config.get('working_folder')
                            ),
                            inspected.get('Name')[1:])
                })
                break
        return res

    @events
    def update_nginx(self):
        """Updates nginx config file to match running containers. If any are stopped or removed,
        they will be removed from nginx config.

        :return: Containers config. See :meth:`deployv.base.commandv.get_containers`.
        :rtype: dict
        """
        containers_config = self.get_containers()
        nginx_manager = nginxv.NginxV(self.__config.deployer.get('nginx_folder'))
        nginx_manager.update_sites(containers_config)
        nginx_manager.restart()
        return containers_config

    @events
    def push_image(self):
        res = {
            'command': 'push_image',
            'result': {},
            'attachments': [],
        }
        if self.skip_push():
            self.push_images_done_trigger()
            return res
        manager = self.__instance_manager
        images = self.__config.container_config.get('push_image')
        self.sender.send_message('Pushing images.')
        if not images:
            res.update({
                'error': ("No images to updload were specified. Please specify"
                          " at least one in container_config > push_image")})
            self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
            self.error_trigger()
            return res
        pushed_imgs = []
        for img in images:
            local_image = img.get('image') or pushed_imgs and pushed_imgs[-1]
            if not local_image:
                push_result = manager.commit_and_push(img.get('base'), img.get('tag'))
            else:
                push_result = manager.tag_and_push(local_image, img.get('base'), img.get('tag'))
            if push_result.get('error'):
                res.update({'error': push_result.get('error')})
                self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
                self.error_trigger()
                return res
            push_details = push_result.get('result').get('push_result').get('log')
            res.get('attachments').append({
                'file_name': 'push_image_{tag}.json'.format(tag=img.get('tag')),
                'file': base64.b64encode(utils.encode(json.dumps(push_details, indent=4))),
                'type': 'application/json',
            })
            instance_type = self.__config.instance_config.get('instance_type')
            pushed_imgs.append({'name': push_result.get('result').get('tagged_image'),
                                'tag_latest': img.get('tag_latest'),
                                'tag_dev': True if instance_type == 'develop' else False})
        res['result'].update({'images': pushed_imgs})
        self.sender.send_message('Images pushed.', body=res)
        self.push_images_done_trigger()
        return res

    def create_db_demo(self):
        """ This method creates an empty database.

        :return: The name of the database
        :rtype: str
        """
        res = {'result': {}}
        self.sender.send_message('Creating a clean database')
        self._stop_instance()
        db_name = self.__config.instance_config.get('config').get('db_name')
        self._drop_dbs([db_name])
        if self.__config.instance_config.get('config').get('db_name'):
            db_name = self.__config.instance_config.get('config').get('db_name')
        else:
            db_name = utils.generate_dbname(self.__config, False, self.__config.prefix)
        db_config = self.instance_manager.db_config
        postgres = postgresv.PostgresShell(utils.odoo2postgres(db_config))
        postgres.create(db_name)
        create_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        postgres.create_extension_unaccent(db_name)
        self.instance_manager.update_db('all', db_name)
        res.get('result').update({'database_name': db_name, 'create_date': create_date})
        params = {'database.generated_at': create_date,
                  'database.type': self.instance_manager.instance_type}
        self.instance_manager.set_parameters(db_name, params)
        self.sender.send_message('Database "{db}" created'.format(db=db_name))
        return res

    def _check_free_space(self):
        """ Checks if there is enough free space in the paths where the compressed and the
        decompressed backups will be stored.

        :return: dictionary with the `error` key if an error ocurred or empty if there is
        enough space
        :rtype: dict
        """
        res = {}
        decompressed = utils.parse_backup_size(self.__config.decompressed_backup_size)
        compressed = utils.parse_backup_size(self.__config.compressed_backup_size)
        if decompressed['size_unit'] != compressed['size_unit']:
            converted_compressed = utils.byte_converter(self.__config.compressed_backup_size,
                                                        to_unit=decompressed['size_unit'])
            compressed = utils.parse_backup_size(converted_compressed)
        if self.__config.temp_folder == self.__config.backup_src:
            expected_size_value = compressed['size_value'] + decompressed['size_value']
            expected_size = '{value}{unit}'.format(value=expected_size_value,
                                                   unit=decompressed['size_unit'])
            if not utils.verify_free_disk_space(expected_size, self.__config.backup_src):
                res.update({'error': 'Not enough disk space available in {directory}.'.format(
                    directory=self.__config.backup_src)})
            return res
        if not utils.verify_free_disk_space(self.__config.decompressed_backup_size,
                                            self.__config.temp_folder):
            res.update({'error': 'Not enough disk space available in {directory}.'.format(
                directory=self.__config.temp_folder)})
        elif not utils.verify_free_disk_space(self.__config.compressed_backup_size,
                                              self.__config.backup_src):
            res.update({'error': 'Not enough disk space available in {directory}.'.format(
                directory=self.__config.backup_src)})
        return res

    def _check_update_production_requirements(self):
        res = {'command': 'update_production', 'result': {}}
        # Check images
        images_data = [
            {
                'image_name': self.__config.container_config.get('image_name'),
                'image_size': self.__config.image_size
            }
        ]
        if self.__config.maintenance_page:
            images_data.append(self.__config.maintenance_page)
        images_path = utils.get_images_path()
        logger.info('Cheking disk space required for the images')
        for image in images_data:
            name = image.get('image_name')
            if not image.get('image_size'):
                logger.warning(
                    'No expected image size was provided for the image %s,'
                    ' skipping this check', name)
            elif not utils.verify_free_disk_space(image.get('image_size'), images_path):
                msg = ('There is not enough space in disk for the image {image_name}.'
                       ' Required space: {image_size}'.format(**image))
                res.update({'error': msg})
                self.sender.send_message(msg, body=res, log_type='ERROR')
                return False
            logger.info('Pulling image "%s"', name)
            self.sender.send_message('Pulling image {}'.format(name))
            try:
                self.instance_manager.pull(name)
            except (errors.NoSuchImage, APIError, ImageNotFound):
                msg = 'Image "{img}" doesn\'t exist'.format(img=name)
                res.update({'error': msg})
                self.sender.send_message(msg, body=res, log_type='ERROR')
                return False
        # Check postgres config
        db_config = self.instance_manager.db_config
        db_config.update({'db_name': self.__config.instance_config.get('config').get('db_name')})
        with postgresv.PostgresConnector(utils.odoo2postgres(db_config)) as conn:
            db_conn = conn.check_config()
        if not db_conn:
            msg = 'Failed to connect to the database'
            res.update({'error': msg})
            self.sender.send_message(msg, body=res, log_type='ERROR')
            return False
        logger.debug('Postgres config check successful')
        # Check free space
        free_space = self._check_free_space()
        if free_space.get('error'):
            res.update({'error': free_space.get('error')})
            self.sender.send_message(free_space['error'], body=res, log_type='ERROR')
            return False
        logger.debug('Space check successful')
        # Check working folder
        working_folder = self.instance_manager.config.get("working_folder")
        if not os.path.isdir(os.path.expanduser(working_folder)):
            msg = 'The {folder} working folder does not exist.'.format(folder=working_folder)
            res.update({'error': msg})
            self.sender.send_message(msg, body=res, log_type='ERROR')
            return False
        logger.debug('Working folder check successful')
        return True

    def update_production(self):
        """Updates a production instance.

        The process is as follows:

            1. The free disk space is checked to see if there is enough to generate the backups.
            2. The production container is committed as the stable one, and pushed to the repo.
            3. The backup is generated (but not compressed).
            4. The current production container is destroyed.
            5. The modules are updated in the database using the updates image.
            6. The new production container is started.
            7. The backup is compressed inside the backup folder.

        :param backup_src: Where the backup is going to be saved at the end.
        :param expected_backup_size: The size of the expected backup, so it can be checked.
        :param odoo_version: The Odoo version
        :param status_checks: How many times it will check when a process needs to be ensured.
        :param cformat: The format to use to compress the backup (bz2, gz).
        :param tmp_dir: Temporary directory to store the backup.
        :param prefix: Prefix for the backup name.
        :param reason: Reason for the backup name.

        :type backup_src: str
        :type expected_backup_size: str
        :type odoo_version: str
        :type status_checks: int
        :type cformat: str
        :type tmp_dir: str
        :type prefix: str
        :type reason: str
        """
        self.sender.send_message('Updating Production instance.')
        res = {'command': 'update_production', 'result': {}}
        self.__config.check_config('update_production')
        image = self.__config.container_config.get('image_name')
        container_info = self.instance_manager.basic_info
        container_name = container_info.get('name')
        env = self.__instance_manager.docker_env
        instance_config = self.__config.instance_config
        db_config = self.instance_manager.db_config
        db_config.update({'db_name': instance_config.get('config').get('db_name')})
        pg_shell = postgresv.PostgresShell(utils.odoo2postgres(db_config))
        pg_shell.terminate_sessions(
            db_config['db_name'], instance_config.get('config').get('db_owner'),
            instance_config.get('config').get('db_owner_passwd'))
        backup_result = self._production_backup(
            container_name, self.__config.status_checks, self.__config.temp_folder,
            self.__config.instance_config.get('customer_id') or self.__config.prefix,
            self.__config.reason or 'preupdate')
        if backup_result.get('error'):
            res.update({'error': backup_result.get('error')})
            self.sender.send_message(msg=res.get('error'), body=res, log_type='ERROR')
            self.error_trigger()
            return res
        logger.debug('Backup result: %s', json.dumps(backup_result, indent=2))
        start_result = self._production_update_and_start(
            image, container_name, self.__config.status_checks,
            env, self.__config.odoo_version)
        if start_result.get('error'):
            res.update(start_result)
            self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
            self.__config.container_config.update({'image_name': self.__config.previous_image})
            self._need_revert = True
            self.error_trigger()
            return res
        tag_result = self._production_commit_and_tag_stable()
        if tag_result.get('error'):
            res.update({'error': tag_result.get('error')})
            self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
            self.error_trigger()
            return res
        logger.debug('Commit and tag stable result: %s', json.dumps(tag_result, indent=2))
        stable_image = tag_result.get('result').get('stable_image')
        res['result'].update({
            'stable_image': stable_image,
            'tagged_image': tag_result.get('result').get('tagged_image'),
            'modules': start_result.get('result').get('modules'),
            'update_logs': start_result.get('result').get('update_logs'),
            'result_type': 'pre-backup'
        })
        odoo_user = self.__config.container_config.get('env_vars').get('odoo_user')
        odoo_home = os.path.join(self.__config.container_config.get('env_vars').get('odoo_home'),
                                 'instance')
        path_branches = os.path.join(self.instance_manager.temp_folder, 'branches_product.json')
        self.__instance_manager.exec_cmd(
            'su {user} -c "branchesv save -p {home} -f /tmp/branches_product.json"'
            .format(user=odoo_user, home=odoo_home)
        )
        start_result.get('attachments').append({
            'file_name': os.path.basename(path_branches),
            'file': utils.generate_attachment(path_branches),
            'type': 'application/json'
        })
        res.update({'attachments': start_result.get('attachments')})
        logger.debug('Update and start result: %s', json.dumps(start_result, indent=2))
        full_res = res.copy()
        self.sender.send_message(body=res)
        backup = backup_result.get('result').get('backup')
        compress_result = self._production_compress_backup(
            container_name, backup['files'], backup['name'],
            self.__config.backup_src or os.getcwd(), self.__config.cformat, backup['tmp_dir'])
        if compress_result.get('error'):
            res.update({'error': compress_result.get('error')})
            self.sender.send_message(res.get('error'), body=res, log_type='ERROR')
            self.error_trigger()
            return res
        logger.debug('Compress result: %s', json.dumps(compress_result, indent=2))
        # Done
        backup_name = compress_result.get('result')
        logger.info('Production instance successfully updated')
        full_res['result'].update({
            'backup': backup_name,
            'backup_size': utils.get_size(backup_name),
            'result_type': 'post-backup'
        })
        full_res.update({'attachments': start_result.get('attachments')})
        self.sender.send_message('Production instance successfully updated', body=res)
        self.done_trigger()
        return res

    def _production_commit_and_tag_stable(self):
        """Commits the production container as stable and with the current date, and
        pushes the generated images to the repository.

        (This method shouldn't be called directly, instead use: `update_production`.)
        """
        res = {'result': {}}
        # Commit container and push image
        manager = self.__instance_manager
        image_name = self.__config.container_config.get('image_name')
        image_repo = image_name.split(':')[0]
        image_tag = utils.get_strtime()
        self.sender.send_message('Pushing image {}:{}'.format(image_name, image_tag))
        commit_result = manager.commit_and_push(image_repo, image_tag)
        if commit_result.get('error'):
            res.update({'error': commit_result.get('error')})
            return res
        # Tag updates as stable and push
        self.sender.send_message('Pushing scheduled image {} as stable'.format(image_name))
        tag_result = manager.tag_and_push(image_name, image_repo, tag='stable')
        if tag_result.get('error'):
            res.update({'error': tag_result.get('error')})
        res['result'].update({
            'container_info': commit_result.get('result').get('container_info'),
            'tagged_image': commit_result.get('result').get('tagged_image'),
            'updates_image': image_name,
            'stable_image': tag_result.get('result').get('tagged_image'),
        })
        return res

    def _production_backup(self, container_name, status_checks,
                           tmp_dir, prefix, reason):
        """Backups the production instance and destroys its current container.

        (This method shouldn't be called directly, instead use: `update_production`.)

        :param container_name: The production container name.
        :param status_checks: How many times it will check if the instance was
            successfully stopped.
        :param tmp_dir: The temporary directory where the backup is to be generated.
        :param prefix: The prefix for the backup name.
        :param reason: The reason for the backup name.

        :type container_name: str
        :type status_checks: int
        :type tmp_dir: str
        :type prefix: str
        :type reason: str
        """
        manager = self.__instance_manager
        res = {'result': {}}
        # Stop instance
        logger.info('Stopping instance in "%s"', container_name)
        self.sender.send_message('Stopping instance in "{}"'.format(container_name))
        stopped = manager.ensure_instance_status(ensure_running=False, max_tries=status_checks)
        if not stopped:
            res.update({'error': 'Couldn\'t stop instance in "{container}"'.format(
                container=container_name
            )})
            return res
        # Dump backup
        db_name = self.__config.instance_config.get('config', {}).get('db_name')
        info_msg = 'Generating backup for "{}" with DB "{}"'.format(container_name, db_name)
        self.sender.send_message(info_msg)
        logger.info(info_msg)
        backup = manager.generate_backup(
            db_name, cformat=False, reason=reason, tmp_dir=tmp_dir, prefix=prefix)
        self.sender.send_message('Temporary backup generated in "{}"'.format(
            backup.get('tmp_dir')))
        logger.info('Temporary backup generated in "%s"', backup.get('tmp_dir'))
        res['result'].update({
            'backup': backup
        })
        return res

    def _production_update_and_start(self, stable_image, container_name,
                                     status_checks, env, odoo_version):
        """Updates the production database using the updates image and starts the new production
        container.

        (This method shouldn't be called directly, instead use: `update_production`.)

        :param stable_image: The image that is going to be used to update and create the
            new container.
        :param container_name: The name for the production container.
        :param status_checks: How many times it will check if the production instance was
            successfully started.
        :param env: The environment variables for the old instance.
        :param odoo_version: The Odoo version for the instance.

        :type stable_image: str
        :type container_name: str
        :type status_checks: int
        :type env: dict
        :type odoo_version: str
        """
        manager = self.__instance_manager
        config = self.__config
        res = {'result': {'update_logs': []}, 'attachments': []}
        # Remove container
        logger.info('Removing container "%s"', container_name)
        manager.remove_container()
        # start maintenance page's container
        maintenance_container = False
        if config.maintenance_page:
            maintenance_container = manager.start_maintenance_page_container()
        # Update modules
        db_config = config.instance_config.get('config') or {}
        odoo_bin = ODOO_BINARY[odoo_version or env.get('version')]
        modules = config.instance_config.get('update_module')
        container_cfg = config.container_config
        working_folder = os.path.join(container_cfg.get("working_folder"), container_name)
        volumes = container_cfg.get('volumes')
        binded_volumes = container.generate_binds(volumes, working_folder)
        container_options = {
            'user': 'odoo',
            'volumes': binded_volumes,
            'remove': True,
        }
        base_command = (
            '{odoo} -c {rc} -d {db_name} -u {{module}} --logfile {{log}} --stop-after-init '
            '-r {db_user} -w {db_password} --db_host {db_host} --db_port {db_port}'.format(
                odoo=os.path.join('/home/odoo/instance/odoo', odoo_bin),
                rc='/home/odoo/.openerp_serverrc', **db_config))
        msg = 'Updating modules "{mod}" in "{db}" using "{img}" with options "{ops}"'.format(
            mod=", ".join(modules), db=db_config.get('db_name'), img=stable_image,
            ops=container_options)
        logger.info(msg)
        self.sender.send_message(msg)
        for module in modules:
            for attempt in range(2):
                log_file = 'update_{mod}_{date}.log'.format(mod=module, date=utils.get_strtime())
                log_path = os.path.join('/tmp/deployvlogs', log_file)
                local_path = os.path.expanduser(os.path.join(working_folder, log_path.strip('/')))
                command = base_command.format(module=module, log=log_path)
                self.sender.send_message('Updating "{}"'.format(module))
                logger.info('Updating "%s"', module)
                try:
                    manager.cli2.containers.run(stable_image, command, **container_options)
                except ContainerError as error:
                    res.update({'error': 'Error updating "{mod}": {err}'.format(
                        mod=module, err=str(error))})
                    parsed_log = self._parse_update_production_log(local_path, module)
                    summary = parsed_log.get('summary')
                    if summary:
                        res['result']['update_logs'].append(summary)
                        res['attachments'].append(parsed_log.get('attachment'))
                    # Remove maintenance container
                    if maintenance_container:
                        manager.remove_container(maintenance_container)
                    return res
                logger.info('Log was saved to "%s"', local_path)
                parsed_log = self._parse_update_production_log(local_path, module)
                if parsed_log.get('error') and not parsed_log.get('summary'):
                    # Return the error message if the log file couldn't be generated
                    res.update(parsed_log)
                    # Remove maintenance container
                    if maintenance_container:
                        manager.remove_container(maintenance_container)
                    return res
                summary = parsed_log.get('summary')
                if parsed_log.get('error'):
                    if attempt:
                        res.update({'error': parsed_log.get('error')})
                        res['result']['update_logs'].append(summary)
                        res['attachments'].append(parsed_log.get('attachment'))
                        # Remove maintenance container
                        if maintenance_container:
                            manager.remove_container(maintenance_container)
                        return res
                    logger.info('Trying again')
                    continue
                res['result']['update_logs'].append(summary)
                res['attachments'].append(parsed_log.get('attachment'))
                break
        # Remove maintenance container
        if maintenance_container:
            manager.remove_container(maintenance_container)
        # Create container
        self.sender.send_message('Starting container and instance in "{}"'.format(container_name))
        logger.info('Starting container and instance in "%s"', container_name)
        manager.start_odoo_container()
        # Start instance
        logger.info('Waiting for Odoo to start in "%s"', container_name)
        started = manager.ensure_instance_status(ensure_running=True, max_tries=status_checks)
        if not started:
            res.update({'error': 'Instance not running in "{container}"'.format(
                container=container_name
            )})
            return res
        res['result'].update({
            'modules': modules,
            'container_name': container_name,
        })
        return res

    def _production_compress_backup(self, container_name, files, name, directory, cformat, tmp):
        """Compresses the production backup.

        (This method shouldn't be called directly, instead use: `update_production`.)

        :param container_name: The container name.
        :param files: The files to be compressed.
        :param name: The name for the backup file.
        :param directory: Where the backup will be saved.
        :param cformat: The format for the backup.
        :param tmp: The temporal directory where the backup was generated.

        :type container_name: str
        :type files: list
        :type name: str
        :type directory: str
        :type cformat: str
        :type tmp: str
        """
        manager = self.__instance_manager
        res = {'result': {}}
        # Compress backup
        self.sender.send_message('Compressing backup for "{}" in "{}"'.format(
            container_name, directory))
        logger.info('Compressing backup for "%s" in "%s"', container_name, directory)
        try:
            result_file = manager.compress_files(files, name, directory, cformat)
        except IOError as error:
            res.update({'error': 'Failed to generate backup: {err}'.format(err=str(error))})
            return res
        self.sender.send_message('Backup generated in "{}"'.format(result_file))
        logger.info('Backup generated in "%s"', result_file)
        utils.clean_files(tmp)
        res.update({'result': result_file})
        return res

    def _parse_update_production_log(self, log_path, module):
        res = {}
        try:
            with open(log_path) as log_file:
                summary = utils.resume_log(log_file)
        except IOError as error:
            res.update({'error': 'Could not open log "{log}": {err}'.format(
                log=log_path, err=utils.get_error_message(error))
            })
            return res
        for log_type, log_num in sorted(summary.items(), key=lambda log: log[0]):
            logger.info('+-- %s %s', log_type.replace('_', ' ').title(), len(log_num))
        summary.update({'log_file': log_path})
        if summary.get('errors') or summary.get('critical'):
            update_error = 'An error ocurred while updating "{mod}"'.format(mod=module)
            res.update({'error': update_error})
            logger.error(update_error)
        res.update({
            'summary': summary,
            'attachment': {
                'file_name': os.path.basename(log_path),
                'file': utils.generate_attachment(log_path),
                'type': 'text/plain'
            }
        })
        return res

    def restart_instance(self):
        """Restarts the odoo inside the container and checks if an error
        occurred or if it started successfully.
        """
        res = {'command': 'restart_instance'}
        self.sender.send_message('Restarting instance')
        restart_res = self.instance_manager.restart_instance()
        # Add anything returned by the restart_instance() method to the result key, despite
        # if it was an error or not, so orchest won't move the deploy to the error state
        res.update({'result': restart_res.get('result') or restart_res.get('error')})
        log_type = 'error' in restart_res.keys() and 'ERROR' or 'INFO'
        self.sender.send_message(body=res, msg=res.get('result'), log_type=log_type)
        return res

    def restart_container(self):
        """Restarts the docker container and checks if it started properly
        """
        res = {'command': 'restart_container'}
        self.sender.send_message('Restarting container')
        restart_res = self.instance_manager.restart_container()
        results = {
            True: 'Instance successfully restarted',
            False: ('Failed to restart the container, it may be because it'
                    ' does not exist or it took too long to start')
        }
        res.update({'result': restart_res, 'msg': results.get(restart_res)})
        self.sender.send_message(res.get('msg'), res, restart_res and 'INFO' or 'ERROR')
        return res
