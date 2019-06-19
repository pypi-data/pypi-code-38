from lbmessaging.services.Common import BaseService
import os

class LbCIService(BaseService):
    """
    LHCb continuous integration messaging service
    The exposed exchanges and their methods are:

        - send_build_ready      mapped to send_build_ready of
                                ContinuousIntegrationExchange
        - consume_build_ready   mapped to consume_build_ready of
                                ContinuousIntegrationExchange
        - receive_build_ready   mapped to receive_build_ready of
                                ContinuousIntegrationExchange
        - send_envkit_ready     mapped to send_envkit_ready of
                                ContinuousIntegrationExchange
        - consume_envkit_ready  mapped to consume_envkit_ready of
                                ContinuousIntegrationExchange
        - receive_envkit_ready  mapped to receive_envkit_ready of
                                ContinuousIntegrationExchange
    """
    def __init__(self, host=None, username=None, passwd=None, port=5671,
                 vhost='/lhcb', use_ssl=True):
        """
        :param host: the RabbitMQ server hostname
        :param username: the RabbitMQ server username
        :param passwd: the RabbitMQ server password
        :param port: the RabbitMQ server port
        :param vhost: the RabbitMQ virtual host that should be used in the
                      connection
        :param use_ssl: if True, an encrypted connection is created, plain text
                        otherwise
        """
        super(LbCIService, self).__init__(host=host, username=username,
                                          passwd=passwd, port=port,
                                          vhost=vhost, use_ssl=use_ssl)

    @staticmethod
    def getEnvKitUrl(flavour, platform, version, url=None,
                     reponame='lhcbdev.cern.ch'):
        if url:
            return url
        base = {
            'lhcb.cern.ch': 'lbenv-prod-kit',
        }.get(reponame, 'lbenv-kit')
        return "http://lhcb-rpm.web.cern.ch/lhcb-rpm/%ss/" \
               "%s.%s.%s.%s.tar.bz2" % (base, base, flavour, platform, version)

    @staticmethod
    def getEnvKitPrefix(flavour, platform, reponame='lhcbdev.cern.ch'):
        env_kit_top_dir = {
            'lhcb.cern.ch': '/cvmfs/lhcb.cern.ch/lib/var/lib/LbEnv',
        }.get(reponame, '/cvmfs/lhcbdev.cern.ch/new-msr/var/lib/LbEnv')
        path = os.path.normpath(
            os.path.join(env_kit_top_dir, flavour, platform))
        if not path.startswith(env_kit_top_dir):
            raise ValueError("Trying to compute a path outside the top "
                             "directory for envkit: %s" % path)
        return path + os.path.sep
