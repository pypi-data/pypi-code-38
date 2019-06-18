# coding: utf-8
from os import path
import logging
import odoorpc
from docker.errors import APIError, NullResource, NotFound
from deployv.base import errors
from deployv.base.extensions_core import EventListenerBase
from deployv.base import postgresv
from deployv.helpers import utils, json_helper
from deployv.instance import instancev

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class TestPsqlConnection(EventListenerBase):

    class Meta:  # pylint: disable=C1001
        """ This EventListener is made to test the connection with postgres before the instance is
        constructed so it is possible to validate the configuration parameters
        """
        name = 'CheckPsqlConnection'
        event = 'before.create.event'

    def execute(self, obj):
        if obj.instance_manager.config.get('full_stack'):
            logger.info("Instance with internal postgres, skipping postgres check")
            return True
        psql_dict = utils.odoo2postgres(obj.instance_manager.db_config)
        logger.debug('Dict: %s', str(psql_dict))
        psql_dict.update({'dbname': 'postgres'})
        try:
            with postgresv.PostgresConnector(psql_dict) as db_test:
                res = db_test.check_config()
                if res:
                    logger.info('PostgreSQL connection test passed')
                else:
                    logger.info('PostgreSQL connection test failed')
        except (KeyboardInterrupt, errors.GracefulExit):
            raise
        except Exception:  # pylint: disable=W0703
            res = False
            logger.error("Could not connect to the database")
        return res


class TestDockerUser(EventListenerBase):

    class Meta:  # pylint: disable=C1001
        """ This EventListener to test if the user is configured to use docker, pull images, etc
        """
        name = 'CheckDockerUser'
        event = 'before.create.event'

    def execute(self, obj):
        # Check if user can use docker
        res = False
        import getpass
        from docker import APIClient as Client
        cli = Client()
        try:
            cli.containers(all=True)
        except (KeyboardInterrupt, errors.GracefulExit):
            raise
        except Exception as error:  # pylint: disable=W0703
            logger.error(('Current user "%s" cannot connect to docker or'
                          ' docker service is down: %s'),
                         getpass.getuser(), str(error))
        else:
            logger.info('Docker connection test passed for user %s',
                        getpass.getuser())
            res = True
        return res


class InstallTestRepo(EventListenerBase):

    class Meta:  # pylint: disable=C1001
        """ This EventListener is made to install the web_environment_ribbon if it is a test or
        dev instance
        """
        name = 'InstallTestRibbon'
        event = 'after.restore.event'

    def execute(self, obj, returned_value):
        instance_type = obj.instance_manager.instance_type
        logger.debug('Instance type: %s', instance_type)
        if instance_type in instancev.INSTALL_RIBBON\
                and returned_value.get('result', False):
            res = True
            if not returned_value.get('result').get('database_name'):
                logger.error('Could not install the web_environment_ribbon, Database not found')
                return False
            elif returned_value.get('result').get('critical'):
                logger.error(returned_value.get('result').get('critical'))
                return False
            else:
                logger.debug('Installing the web_environment_ribbon')
                install = obj.instance_manager.install_module(
                    'web_environment_ribbon_isolated',
                    returned_value.get('result').get('database_name')
                )

            if len(install.get('warnings')) >= 1:
                for warn in install.get('warnings'):
                    if 'invalid module names, ignored: web_environment_ribbon' in warn:
                        logger.warning(
                            'Could not install web_environment_ribbon, module not found'
                        )
                        res = False
                        break
        else:
            res = False
        return res


class TestContainer(EventListenerBase):

    class Meta:  # pylint: disable=C1001
        """ This EventListener is made to test if the container is running and the instance is up,
        at this point we cannot assume that there is a database because is just a post event for
        :meth:`deployv.base.commandv.CommandV.create` method and such method does not create
        database
        """
        name = 'CheckContainer'
        event = 'after.create.event'

    def execute(self, obj, returned_value):
        if obj.instance_manager.docker_id is None:
            return False
        cid = obj.instance_manager.docker_id
        inspected = self.inspect(obj)
        if not inspected:
            return False
        if not inspected.get('State').get('Running'):
            logger.error('The container %s is not runnig', cid)
            return False
        # Check if odoo instance is running
        res = obj.instance_manager.exec_cmd('supervisorctl status odoo')
        if u'RUNNING' not in res:
            logger.error('Odoo instance is not running in container %s', cid)
        else:
            logger.info(
                'Supervisord in container %s reported the instance is running', cid)
        port_binds = obj.instance_manager.basic_info.get('ports').get('8069')
        if not isinstance(port_binds, list):
            host = obj.instance_manager.config.get('domain')
            res = self.test_connection(host, port_binds)
            return res
        for bind in port_binds:
            parts = bind.split(':')
            host = parts[0]
            port = parts[1]
            res = self.test_connection(host, int(port))
            if res:
                return res

    def inspect(self, obj):
        try:
            inspected = obj.instance_manager.inspect()
        except NotFound:
            logger.exception('The provided id/name does not exists')
            return
        except NullResource as error:
            logger.exception('Container is not running: %s',
                             utils.get_error_message(error))
            return
        except errors.NoSuchContainer as error:
            logger.exception('Container does not exists: %s', utils.get_error_message(error))
            return
        return inspected

    def test_connection(self, host, port):
        try:
            odoo = odoorpc.ODOO(host, port=port)
            odoo.db.list()
        except (KeyboardInterrupt, errors.GracefulExit):
            raise
        except Exception as error:  # pylint: disable=W0703
            logger.error('Could not connect to the instance using %s:%s', host, port)
            logger.error(str(error))
            res = False
        else:
            logger.info('Connected to the instance via %s:%s', host, port)
            res = True
        return res


class TestBranches(EventListenerBase):

    class Meta:  # pylint: disable=C1001
        """ This EventListener makes sure that the branches and commits cloned into the new
        instance are the ones specified in branchesv
        """
        name = 'CheckBranches'
        event = 'after.create.event'

    def execute(self, obj, returned_value):
        if returned_value.get('error'):
            return False
        try:
            pre_path = path.join(obj.instance_manager.temp_folder, 'branches.json')
        except APIError as error:
            logger.exception('Could not connect to the instance: %s', error.explanation)
            return False
        except errors.NotRunning as error:
            logger.exception('Container is not running: %s',
                             utils.get_error_message(error))
            return False
        except errors.NoSuchContainer as error:
            logger.exception('Container does not exists: %s', utils.get_error_message(error))
            return False

        try:
            pre_branches = json_helper.load_json(pre_path)
        except IOError as error:
            logger.warn(utils.get_error_message(error))
            logger.warn('Maybe no branches was provided in the config (this is not an error)')
            return True
        home = obj.instance_manager.config.get('env_vars').get('odoo_home')
        instance_dir = path.join(home, 'instance/')
        post_path = path.join('/tmp', 'post_process.json')
        try:
            obj.instance_manager.exec_cmd('branchesv save -p {i} -f {p}'.format(i=instance_dir,
                                                                                p=post_path))
        except errors.NotRunning as error:
            logger.exception('Could not load the branches: %s',
                             utils.get_error_message(error))
            return False
        post_branches = json_helper.load_json(
            path.join(
                obj.instance_manager.temp_folder,
                'post_process.json'
            ))
        for value in pre_branches:
            if not value['commit']:
                url_dict = value['repo_url']
                url = url_dict.get('origin')
                cmd = ('git ls-remote {remote} HEAD'.format(remote=url))
                result = obj.instance_manager.exec_cmd(cmd)
                latest = result.split()
                value['commit'] = latest[0].strip()
            if value not in post_branches:
                logger.info('Repository not cloned: %s', value['name'])
            else:
                logger.info('Repository %s successfully cloned', value['name'])
