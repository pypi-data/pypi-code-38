from __future__ import print_function
from swimlane_platform.lib import ArgsConfigQuestions, names, DockerComposeFileManager, Configuration, \
    read_dict, write_dict, PyMongoManager, BaseWithLog, info_function_start_finish, debug_function_args, \
    debug_function_return
from os import path, makedirs, environ
import re
from OpenSSL import crypto
from shutil import copy2
from typing import Dict
from swimlane_platform.questions_groups import logging_questions


class EnableSsl(BaseWithLog):

    def __init__(self, args):
        # type: (Configuration) -> EnableSsl
        super(EnableSsl, self).__init__(args)
        self.install_dir = names.INSTALL_DIR
        self.env_root = path.join(self.install_dir, names.SECRETS_SUB_FOLDER)
        self.secrets = path.join(self.install_dir, names.SECRETS_SUB_FOLDER)
        self.py_mongo_manager = PyMongoManager(self.logger)

    @info_function_start_finish('Enable SSL for MongoDB')
    def run(self):
        # type: () -> None
        """
        Runs modifications to environment to enable additional settings for SSL
        """
        if not path.exists(self.secrets):
            makedirs(self.secrets)
        if self.args.selfsigned:
            self._env_modify(False)
            cert = self._generate_certificates()
            self._set_secret_source_docker_compose(cert)
        else:
            self._env_modify(True)
            url = self._get_certificate_url(self.args.certificate)
            copy2(self.args.certificate, self.secrets)
            self._add_alias_to_docker_compose(url)
            self._set_secret_source_docker_compose(self.args.certificate)
            self._env_change_server_name(url)
        self._set_mongodb_command()

    @debug_function_args
    def _env_modify(self, verify_certificate):
        # type: (bool) -> None
        self._env_modify_file(names.API_ENV_FILE, verify_certificate)
        self._env_modify_file(names.TASKS_ENV_FILE, verify_certificate)

    @debug_function_args
    def _env_modify_file(self, file_name, verify_certificate):
        # type: (str, bool) -> None
        api_env_file = path.abspath(path.join(self.env_root, file_name))
        api_env = read_dict(api_env_file)
        self._env_enable_mongo_ssl(api_env, 'SwimlaneConnectionString', verify_certificate)
        self._env_enable_mongo_ssl(api_env, 'HistoryConnectionString', verify_certificate)
        write_dict(api_env_file, api_env)

    @debug_function_args
    def _add_alias_to_docker_compose(self, certificate_url):
        # type: (str) -> None
        docker_compose = DockerComposeFileManager(self.logger, path.join(self.install_dir, 'docker-compose.yml'))
        alias_path = ['services', names.SW_MONGO, 'networks', 'internal_network', 'aliases']
        docker_compose.append_or_create_list(certificate_url, *alias_path)
        docker_compose.save()

    @debug_function_args
    def _set_secret_source_docker_compose(self, host_cert_path):
        # type: (str) -> None
        _, file_name = path.split(host_cert_path)
        install_cert_path = path.join(self.secrets, file_name)
        docker_compose = DockerComposeFileManager(self.logger, path.join(self.install_dir, 'docker-compose.yml'))
        alias_path = ['secrets', 'mongodb.pem',  'file']
        docker_compose.set(install_cert_path, *alias_path)
        docker_compose.append_or_create_list('mongodb.pem', 'services', names.SW_MONGO, 'secrets')
        docker_compose.save()

    @debug_function_args
    def _env_enable_mongo_ssl(self, api_env, conn_name_part, verify_certificate):
        # type: (Dict[str, str], str, bool) -> None
        regex = '.*{name}'.format(name=conn_name_part)
        for key, value in api_env.items():
            if re.match(regex, key):
                mongo_settings = self.py_mongo_manager.parse_mongo_uri(value)
                options = mongo_settings['options']
                options['ssl'] = str(True).lower()
                options['sslVerifyCertificate'] = str(verify_certificate).lower()
                api_env[key] = self.py_mongo_manager.get_mongo_uri(mongo_settings)

    @debug_function_return
    @debug_function_args
    def _generate_certificates(self, one_file=True):
        # type: (bool) -> str
        file_template = path.join(self.secrets, 'mongodb.{ext}')
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 1024)
        cert = crypto.X509()
        cert.get_subject().C = "US"
        cert.get_subject().ST = "Colorado"
        cert.get_subject().L = "Lousville"
        cert.get_subject().OU = "Swimlane Inc"
        cert.get_subject().CN = 'sw_mongo'
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha1')
        if one_file:
            pem_file = file_template.format(ext='pem')
            open(pem_file, "w").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
            open(pem_file, "a").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
            return pem_file
        else:
            open(file_template.format(ext='key'), "w").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
            open(file_template.format(ext='crt'), "w").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
            return file_template.format(ext='crt')

    @debug_function_return
    @debug_function_args
    def _get_certificate_url(self, certificate_location):
        # type: (str) -> str
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(certificate_location, 'rt').read())
        return cert.get_subject().CN

    @debug_function_args
    def _env_change_server_name(self, url):
        # type: (str) -> None
        for file_name in [names.API_ENV_FILE, names.TASKS_ENV_FILE]:
            env_file = path.abspath(path.join(self.env_root, file_name))
            env = read_dict(env_file)
            connection_names = ['SwimlaneConnectionString', 'HistoryConnectionString']
            for regex in ['.*{name}'.format(name=name) for name in connection_names]:
                for key, value in env.items():
                    if re.match(regex, key):
                        connection = self.py_mongo_manager.parse_mongo_uri(value)
                        new_node_list = []
                        for _, port in connection['nodelist']:
                            new_node_list.append((url, port))
                        connection['nodelist'] = new_node_list
                        env[key] = self.py_mongo_manager.get_mongo_uri(connection)
            write_dict(env_file, env)

    def _set_mongodb_command(self):
        docker_compose = DockerComposeFileManager(self.logger, path.join(self.install_dir, 'docker-compose.yml'))
        command = '--sslMode requireSSL --sslPEMKeyFile /run/secrets/mongodb.pem'
        docker_compose.set(command, 'services', names.SW_MONGO, 'command')
        docker_compose.save()


def run(parent_config=None):
    # type: (Dict[str, str]) -> None
    """
    The script run method, that can be called by other script or from file run method.
    :param parent_config: Additional configuration information collected by parent script.
    """
    questions = [
        {
            'type': 'confirm',
            'message': 'Do you want to use a self-signed certificate for SSL connections to MongoDB? If not, you must provide your own certificate in .pem format.',
            'name': 'selfsigned',
            'default': True
        },
        {
            'type': 'input',
            'name': 'certificate',
            'message': 'Specify the full path to your .pem format certificate.',
            'when': lambda a: not a['selfsigned']
        }
    ]
    questions.extend(logging_questions)
    config = ArgsConfigQuestions(parent_config)
    config.collect(questions)
    enable_ssl = EnableSsl(config.to_arguments())
    enable_ssl.run()
