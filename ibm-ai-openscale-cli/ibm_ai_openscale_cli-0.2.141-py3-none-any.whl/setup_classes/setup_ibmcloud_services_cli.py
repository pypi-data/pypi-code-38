# coding=utf-8
from __future__ import print_function
from ibm_ai_openscale_cli.setup_classes.cloud_foundry_cli import getCFInstanceCredentials
from ibm_ai_openscale_cli.setup_classes.resource_controller_cli import getRCInstanceCredentials
from ibm_ai_openscale_cli.setup_classes.setup_ibmcloud_services import SetupIBMCloudServices
from ibm_ai_openscale_cli.utility_classes.utils import executeCommand
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger

logger = FastpathLogger(__name__)

class SetupIBMCloudServicesCli(SetupIBMCloudServices):

    def __init__(self, args):
        super().__init__(args)
        logger.log_debug('Using IBM Cloud CLI to setup IBM Cloud services')
        executeCommand('bx config --check-version=false')
        executeCommand('bx login --apikey "{}" -a "{}"'.format(self._args.apikey, self._args.env_dict['api']))
        logger.log_debug('Target resource-group "%s"', self._args.resource_group)
        executeCommand('bx target -g "{}"'.format(self._args.resource_group))

    def _get_credentials(self, params, is_rc_based, credentials_file=None):
        '''
        Returns the credentials from the specified credentials json file. If not
        then returns the credentials an instance of the specified Service.
        If there is no instance available, a new one is provisioned.
        If there are no existing credentials, new one is created and returned.
        '''
        logger.log_info('Setting up {} instance'.format(params['service_display_name']))
        credentials = None

        if credentials_file is not None:
            credentials = { 'credentials': self.read_credentials_from_file(credentials_file) }
        elif is_rc_based:
            credentials = getRCInstanceCredentials(params)
        elif not is_rc_based:
            credentials = getCFInstanceCredentials(params)
        return credentials

    def setup_aios(self):
        aiopenscale_params = {}
        aiopenscale_params['service_display_name'] = 'Watson OpenScale'
        aiopenscale_params['service_name'] = 'aiopenscale'
        aiopenscale_params['instance_name'] = 'openscale-fastpath-instance'
        aiopenscale_params['service_plan_name'] = 'lite'
        aiopenscale_params['service_region'] = 'us-south'
        aiopenscale_params['key_name'] = 'openscale-fastpath-credentials'
        aiopenscale_params['key_role'] = 'Editor'
        aios_instance = self._get_credentials(aiopenscale_params, True)
        return self._aios_credentials(aios_instance['source_crn'].split(':')[7])

    def setup_wml(self):
        wml_params = {}
        wml_params['service_display_name'] = 'Watson Machine Learning'
        if self._args.wml is not None:
            return self._get_credentials(wml_params, None, self._args.wml)
        wml_params['service_name'] = 'pm-20'
        wml_params['instance_name'] = 'wml-fastpath-instance'
        wml_params['service_plan_name'] = 'lite'
        wml_params['service_region'] = 'us-south'
        wml_params['key_name'] = 'wml-fastpath-instance-credentials'
        wml_params['key_role'] = 'Writer'
        return self._get_credentials(wml_params, True)['credentials']
