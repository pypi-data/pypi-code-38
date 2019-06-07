# coding=utf-8
from ibm_ai_openscale_cli.setup_classes.setup_services import SetupServices
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from ibm_ai_openscale_cli.api_environment import ApiEnvironment

logger = FastpathLogger(__name__)

class SetupIBMCloudPrivateServices(SetupServices):

    def __init__(self, args):
        super().__init__(args)

    def setup_aios(self):
        logger.log_info('Setting up {} instance'.format('Watson OpenScale'))
        aios_icp_credentials = {}
        if self._args.iam_token:
            aios_icp_credentials['iam_token'] = self._args.iam_token
        else:
            aios_icp_credentials['username'] = self._args.username
            aios_icp_credentials['password'] = self._args.password
        aios_icp_credentials['url'] = '{}'.format(self._args.url)
        aios_icp_credentials['hostname'] = ':'.join(self._args.url.split(':')[:2])
        aios_icp_credentials['port'] = self._args.url.split(':')[2]
        return aios_icp_credentials

    def setup_wml(self):
        logger.log_info('Setting up {} instance'.format('Watson Machine Learning'))
        wml_credentials = {}
        if self._args.iam_token:
            wml_credentials['iam_token'] = self._args.iam_token
        else:
            wml_credentials['username'] = self._args.username
            wml_credentials['password'] = self._args.password
        wml_credentials['url'] = ':'.join(self._args.url.split(':')[:2])
        if wml_credentials['url'] == ApiEnvironment().icp_gateway_url:
            wml_credentials['url'] = 'https://wmlproxyservice.zen'
        wml_credentials['instance_id'] = 'icp'
        return wml_credentials

