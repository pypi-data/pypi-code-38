from lbmessaging.services.Common import BaseService


class CVMFSNightliesService(BaseService):
    """
    CVMFS Nightlies installation service
    The exposed exchanges and their methods are:
        - dev_send              mapped to send_command of CvmfsDevExchange
        - dev_receive           mapped to receive_command of CvmfsDevExchange
        - conddb_send           mapped to send_command of CvmfsConDBExchange
        - conddb_receive        mapped to receive_command of CvmfsConDBExchange
        - prod_send             mapped to send_command of CvmfsProdExchange
        - prod_receive          mapped to receive_command of CvmfsProdExchange
        - send_build_ready      mapped to send_build_ready of
                                ContinuousIntegrationExchange
        - receive_build_ready   mapped to receive_build_ready of
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
        super(CVMFSNightliesService, self).__init__(host=host,
                                                    username=username,
                                                    passwd=passwd, port=port,
                                                    vhost=vhost,
                                                    use_ssl=use_ssl)
