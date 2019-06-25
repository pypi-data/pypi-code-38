import os
from django.conf import settings

from ievv_opensource.utils.ievvdevrun.runnables import base


class RunnableThread(base.ShellCommandRunnableThread):
    """
    Elasticsearch runnable thread.

    Examples:

        You can just add it to your Django development settings with::

            IEVVTASKS_DEVRUN_RUNNABLES = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.elasticsearch.RunnableThread(
                        configpath='not_for_deploy/elasticsearch.develop.yml')
                )
            }

    """
    default_autorestart_on_crash = True

    def __init__(self, configpath, elasticsearch_executable='elasticsearch', **kwargs):
        self.configpath = configpath
        self.elasticsearch_executable = elasticsearch_executable
        super(RunnableThread, self).__init__(**kwargs)

    def get_logger_name(self):
        return 'ElasticSearch {}'.format(self.configpath)

    def get_command_config(self):
        elasticsearch_version = getattr(settings, 'IEVV_ELASTICSEARCH_MAJOR_VERSION', 1)
        command_config = {
            'executable': self.elasticsearch_executable
        }
        if elasticsearch_version == 1:
            args = ['--config={}'.format(self.configpath)]
            command_config.update({'args': args})
        elif elasticsearch_version == 2:
            args = ['--path.conf={}'.format(self.configpath)]
            command_config.update({'args': args})
        elif elasticsearch_version == 5:
            args = ['-Epath.conf={}'.format(self.configpath)]
            command_config.update({'args': args})
        else:
            raise ValueError('Elasticsearch {} is not supported yet'.format(elasticsearch_version))
            # new_environment = os.environ.copy()
            # new_environment['ES_CONF_PATH'] = self.configpath
            # command_config.update({'_env': new_environment})
        return command_config
