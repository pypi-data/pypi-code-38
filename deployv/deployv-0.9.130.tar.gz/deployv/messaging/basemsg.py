# coding: utf-8

from os import path
import base64
from datetime import datetime
import uuid
from deployv.helpers import json_helper, utils, configuration_helper
from deployv.base.errors import GracefulExit
import simplejson as json
import time
import logging
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


_logger = logging.getLogger('deployv')
TRIGGER_MAPPINGS = {
    'build_image': 'build_image_trigger',
    'create': 'create_trigger',
    'update_instance': 'update_trigger',
    'restart_instance': 'instance_restart_trigger',
    'restart_container': 'container_restart_trigger',
    'change_passwords': 'change_passwords_trigger',
    'delete_instance': 'destroy_trigger',
    'backupdb': 'backup_trigger',
    'deactivate_backup': 'deactivate_backup_trigger',
    'push_image': 'push_images_trigger',
    'update_production': 'update_prod_trigger',
}


class BaseWorker(object):

    def __init__(self, configuration_object, sender_class, receiver_class, worker_id):
        self.config_obj = configuration_object.config
        self._wid = worker_id
        self.count = 0
        self._config_class = self.config_obj
        self._receiver = receiver_class(configuration_object,
                                        self.config_obj.deployer.get('node_id'))
        self._sender = sender_class(configuration_object, self.config_obj.deployer.get('node_id'))

    def run(self):
        """ This is the start up method
        """
        raise NotImplementedError

    def exit(self):
        """ Exit worker, blocks until worker is finished and dead """
        self.signal_exit()
        while self.is_alive():  # checking `is_alive()` on zombies kills them
            time.sleep(1)

    def kill(self):
        """ This kill immediately the process, should not be used """
        raise NotImplementedError

    def check_message(self, message):
        """ Check if the message is properly formed and can be parsed, if nt a message with the
            error will be generated

        :param message: The message to be checked
        :return: The message object (:class:`~deployv.messaging.messagev.BasicMessage`)
            if no error, else False
        """
        message = json_helper.load_json(message)
        if not isinstance(message, dict):
            return False
        res = BasicMessage(message)
        model_schema = json_helper.build_schema(message.get('res_model'))
        validation = json_helper.validate_schema(message, schema=model_schema)
        validate_cmd = utils.validate_command(message.get('message_body') or {},
                                              self.config_obj.deployer.get('server_type'))
        validate_error = validation.get('error') or validate_cmd.get("error")
        if validate_error:
            res.set_message_body({
                'error': validate_error,
                'command': (message.get('message_body') or {}).get('command'),
            }, message_type='error')
            result = res.build_message()
            self._sender.send_message(result)
            return False
        return res

    def execute_rpc(self, message):
        _logger.info('Executing rpc for message in worker %s', self._wid)
        _logger.debug('%s worker received "%s"', self._wid,
                      json.dumps(message.original_message, sort_keys=True, indent=4))
        if message.receiver_node_id != self.config_obj.deployer.get('node_id'):
            _logger.error('Message in the wrong queue, does not match my wid: %s',
                          self.config_obj.deployer.get('node_id'))
            return False
        self._sender.send_message(message.get_ack_message())
        _logger.debug('Ack sent')
        module = message.message_body.get('module')
        command_name = message.message_body.get('command')
        parameters = message.message_body.get('parameters')
        classes = {'commandv': 'CommandV'}
        if not parameters.get('group_config'):
            parameters.update({'group_config': {}})
        parameters.get('instance', {}).get('config', {}).update({
            'db_owner': self.config_obj.postgres.get('db_user'),
            'db_owner_passwd': self.config_obj.postgres.get('db_password')
        })
        parameters.get('container_config', {}).update({
            'working_folder': self.config_obj.deployer.get('working_folder')
        })
        if not parameters.get('container_config', {}).get('domain'):
            parameters.get('container_config', {}).update({
                'domain': self.config_obj.deployer.get('domain')})
        default_params = {
            'backup_src': self.config_obj.deployer.get('backup_folder'),
            'temp_folder': self.config_obj.deployer.get('temp_folder'),
            'max_instances': self.config_obj.deployer.get('max_instances'),
            'docker_url': self.config_obj.deployer.get('docker_url'),
            'use_nginx': self.config_obj.deployer.get('use_nginx'),
            'nginx_folder': self.config_obj.deployer.get('nginx_folder'),
            'res_id': message.res_id,
            'sender_node_id': message.receiver_node_id,
            'deploy_id': message.deploy_id,
            'receiver_node_id': message.sender_node_id,
            'res_model': message.res_model,
            'model': message.model,
            'user_id': message.user_id,
            'command': 'orchestv.{mo}.{co}'.format(mo=module, co=command_name),
        }
        load_defaults = parameters.get('group_config', {}).get('load_defaults', False)
        for param, value in default_params.items():
            if param not in parameters.get('group_config').keys():
                parameters.get('group_config').update({param: value})
        # Create a new config object for each command instead of using the same for every thread
        command_config = configuration_helper.DeployvConfig(deploy_config=parameters,
                                                            load_defaults=load_defaults)
        command_config.update_configuration(worker_config=self.config_obj.worker_config)
        message_body = {
            'command': command_name,
            'module': module,
        }
        if module == 'commandv':
            module_base = __import__('deployv.base', fromlist=[str(module)])
            module_command = getattr(module_base, module)
            command_obj = getattr(module_command, classes.get(module))(command_config)
            _logger.debug('Parameters: %s',
                          json.dumps(parameters, sort_keys=True, indent=4))
            trigger = TRIGGER_MAPPINGS.get(command_name)
            if not trigger:
                message_body.update({'error': 'Command {cmd} does dot exits in module {module}'
                                    .format(cmd=command_name, module=module)})
                message.set_message_body(message_body, message_type='error')
                response = message.build_message()
                self._sender.send_message(response)
                return
            starting_trigger = getattr(command_obj, trigger)
            try:
                starting_trigger()
            except Exception as error:  # pylint: disable=W0703
                error_msg = utils.get_error_message(error)
                command_obj.sender.send_message(error_msg, log_type='ERROR')
                message_body.update(({'error': error_msg}))
                message.set_message_body(message_body, message_type='error')
                response = message.build_message()
                _logger.debug('Message to send %s',
                              json.dumps(response, sort_keys=True, indent=4))
                self._sender.send_message(response)
                if isinstance(error, (KeyboardInterrupt, GracefulExit)):
                    raise
                _logger.exception(error_msg)
            _logger.info('%s worker done', self._wid)


class BasicMessage(object):
    """ Basic unit of communication that will be used for remote communications, you need at least
    specify the sender, receiver and a message body (command, error, status, etc)::

        >>> message = basemsg.BasicMessage()
        >>> message.sender_node_id = 'me01'
        >>> message.receiver_node_id = 'you01'
        >>> res = message.build_message()

    The :func:`~deployv.base.messagev.BasicMessage.build_message` method generates the proper
    message according to the defines schema for the communication (check test_messagev.py
    in the tests folder)

    """

    def __init__(self, message=None):
        envelope = {
            'version': '0.1',
            'message_id': str(uuid.uuid1()),
            'res_id': None,
            'deploy_id': None,
            'orchest_pipe_id': None,
            'sender_node_id': None,
            'receiver_node_id': None,
            'timestamp': None,
            'response_to': None,
            'message_body': dict(),
            'res_model': None,
            'model': None,
            'user_id': None
        }
        self.__dict__ = envelope.copy()
        self._envelope = envelope.copy()
        self._files = list()
        self._message_types = ['error', 'result', 'parameters']
        if message is None:
            self._original_message = None
        elif isinstance(message, str):
            self._original_message = json.loads(message)
        elif isinstance(message, dict):
            self._original_message = message.copy()
        else:
            raise TypeError('Message is in a unsupported type {}'.format(type(message)))
        if self._original_message is not None:
            for key in envelope:
                setattr(self, key, self._original_message.get(key))

    @property
    def original_message(self):
        return self._original_message

    def attach_file(self, file_name, mime_type=None):
        assert path.isfile(file_name)
        self._files.append((file_name, mime_type))

    def set_message_body(self, message_body, message_type):
        """ Define the message body to be send

        :param message_body: Message body according to the documentation
        :param message_type: Error, ack, response or parameters
        :return: None
        """
        if message_type not in self._message_types:
            raise ValueError('Message type must be one of: {}'.format(str(self._message_types)))
        self.message_body = message_body

    def set_command(self, module_command, parameters):
        """ Helper method to create the message for a command

        :param module_command: Execute the command from the specified module.
            Must be in the format module.command
        :param parameters: The parameters that will be passed to the command in a dict
        :return: None
        """
        assert len(module_command.split('.')) == 2
        assert isinstance(parameters, dict)
        res = {
            'module': module_command.split('.')[0],
            'command': module_command.split('.')[1],
            'parameters': parameters
        }
        self.message_body = res

    def build_message(self):
        """ Builds the message with the provided properties in the class and according to the type

        :return: The formatted message in a dict
        """
        res = dict()
        attachments = list()
        for key in self._envelope:
            res.update({key: getattr(self, key)})
        res.update({
            'timestamp': datetime.utcnow().isoformat()})
        for fname in self._files:
            with open(fname(0)) as fname_descriptor:
                coded_file = utils.decode(base64.b64encode(utils.encode(fname_descriptor.read())))
            attachments.append({
                'file_name': path.basename(fname(0)),
                'file': coded_file,
                'type': fname(1)
            })
        if self._original_message:
            res.update({
                'receiver_node_id': self._original_message.get('sender_node_id'),
                'sender_node_id':  self._original_message.get('receiver_node_id'),
                'res_model': (self._original_message.get('res_model') or
                              self._original_message.get('model'))
            })
        if res.get('message_body').get('error', False) and attachments:
            res.get('message_body').get('error').update({'attachments': attachments})
        elif res.get('message_body').get('result', False) and attachments:
            res.get('message_body').get('result').update({'attachments': attachments})
        return res

    def get_ack_message(self, send_to=None):
        """ When a message is provided in the constructor this method generates an ack response
        with the proper parameters

        :param send_to: message route if none is provided will use default
                        passed to the class constructor
        :return: The ack message
        """
        if self._original_message is None:
            res = self.build_message()
        else:
            res = self._original_message.copy()
        res.update({
            'receiver_node_id': res.get('receiver_node_id'),
            'sender_node_id':  res.get('sender_node_id') if send_to is None else send_to,
            'res_model': res.get('res_model'),
            'model': res.get('model'),
            'res_id': res.get('res_id'),
            'deploy_id': res.get('deploy_id'),
            'timestamp': self.timestamp,
            'response_to': res.get('message_id'),
            'message_id': str(uuid.uuid1()),
            'message_body': {
                'module': res.get('message_body').get('module'),
                'command': res.get('message_body').get('command'),
                'ack': {
                    'message': 'Message received'
                }
            }
        })
        return BasicMessage(message=res)

    def get_message_str(self):
        """ A simple helper method that returns the message as a str but being sure that it will
        be safe for rabbitmq

        :return: The string representing the message
        """
        return json.dumps(self.build_message(),
                          ensure_ascii=True,
                          check_circular=True,
                          encoding='utf-8')

    def __repr__(self):
        return self.get_message_str()


class BaseFileConfig(object):
    def __init__(self, config_file, result=False):
        assert path.isfile(config_file)
        self.config = ConfigParser()
        self._result = result
