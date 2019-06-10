import logging
import os


class CloudCredentialsHandler(object):

    def __init__(self, kw):
        self.kwargs = kw

    def _validate_key_and_bind_path_if_present(self, key, relative_path):
        src_path = os.path.join(os.path.expanduser('~'), relative_path)
        target_path = os.path.join('/root', relative_path)
        if not self.kwargs.get(key, True):  # not pop-ing as we might call it twice and lose users decline
            logging.debug('%s is set to false, skipping %s ', key, src_path)
            return {}

        if not os.path.exists(src_path):
            logging.debug('%s path %s not found', key, src_path)
            return {}

        logging.info('%s linking %s to dockers %s', key, src_path, target_path)
        return {src_path: target_path}

    def _local_aws_mount(self):
        return self._validate_key_and_bind_path_if_present('link_aws', '.aws')

    def _local_gcp_mount(self):
        return self._validate_key_and_bind_path_if_present('link_gcp', '.config/gcloud')

    def _local_azure_mount(self):
        return self._validate_key_and_bind_path_if_present('link_azure', '.azure')

    def _local_aws_env(self):
        if not self.kwargs.get('env_aws', True):
            return {}

        res = {k: v for k, v in os.environ.items() if k.startswith('AWS_')}
        logging.info('AWS environment variables passed to docker: %s', list(res.keys()))
        return res

    def update_cred_volumes(self):
        volumes = {}
        volumes.update(self._local_aws_mount())
        volumes.update(self._local_gcp_mount())
        volumes.update(self._local_azure_mount())
        return volumes

    def update_cred_env(self):
        env = {}
        env.update(self._local_aws_env())

        return env

    @classmethod
    def command_extend_from_iter(cls, command, arg_name, iter_):
        for itm in iter_:
            command.append('--%s' % arg_name)
            if isinstance(itm, (tuple, list)):
                command.extend(itm)
            else:
                command.append(str(itm))

    def extend_command_with_creds(self, command):
        env = self.update_cred_env()
        volumes = self.update_cred_volumes()

        self.command_extend_from_iter(command, 'env', env.items())
        self.command_extend_from_iter(command, 'mount', sorted(volumes.items()))
