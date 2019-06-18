# coding: utf-8

import logging
import os
from jinja2 import Environment, FileSystemLoader
try:
    from xmlrpc import client as xmlrpcclient
except ImportError:
    import xmlrpclib as xmlrpcclient


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class NginxV(object):
    """Wrapper class around supervisor to manage nginx service and site config files.

    :param nginx_working_dir: The path where nginx will store config, logs and pid file.
    :type nginx_working_dir: str
    :param process_name: Process name inside supervisor config file. By default is 'nginx'.
    :type process_name: str
    :param supervisor_url: Url used to stablish communication with supervisor.
        By default is 'unix:///var/run/supervisor.sock'.
    :type supervisor_url: str
    """

    def __init__(self,
                 nginx_working_dir,
                 process_name='nginx',
                 supervisor_url='unix:///var/run/supervisor.sock'):
        self._supervisor_url = supervisor_url
        self._supervisor_server = xmlrpcclient.Server('http://127.0.0.1:9001/RPC2')
        self._process_name = process_name
        self._working_dir = os.path.expanduser(nginx_working_dir)
        logger.debug('Nginx work folder: %s', self._working_dir)
        if not os.path.exists(self._working_dir):
            logger.debug('Creating nginx working path')
            os.mkdir(self._working_dir)

    def restart(self):
        """Restarts the nginx process.

        Generally is only needed when the templates are updated.

        :return: If succeeded or not.
        :rtype: bool
        """
        logger.debug('Sending the HUP signal to nginx')
        res = self._supervisor_server.supervisor.signalProcess(
            self._process_name, 'HUP'
        )
        return res

    def update_sites(self, sites):
        """Updates the sites files with the given options.

        :param sites: Domains and ports in the following format:

            .. code-block:: python

                [
                    {
                        'url': 'sub_domain',
                        'port': instance_port,
                        'lp_port': instance_longpolling_port,
                        'logs': 'path to the instance log'
                    },
                    {
                        'url': 'sub_domain_2',
                        'port': instance_port_2,
                        'lp_port': instalce_longpolling_port_2,
                        'logs': 'path to the instance log'
                    },
                ]

        :type sites: list
        """
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates/')
        logger.debug('Searching for the nginx template in: %s', path)
        env = Environment(loader=FileSystemLoader(path))
        template = env.get_template('nginx_sites.jinja')
        values = {
            'sites': sites,
            'working_dir': self._working_dir
        }
        nginx_config = template.render(values)
        logger.debug('Saving generated config to %s', self._working_dir)
        with open(os.path.join(self._working_dir, 'nginx.conf'), 'w') as config:
            config.write(nginx_config)
