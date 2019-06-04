# coding=utf-8
from __future__ import print_function
# from ibm_ai_openscale_cli.setup_classes.cloud_foundry import CloudFoundry
from ibm_ai_openscale_cli.setup_classes.resource_controller import ResourceController
from ibm_ai_openscale_cli.setup_classes.setup_ibmcloud_services import SetupIBMCloudServices
from ibm_ai_openscale_cli.setup_classes.token_manager import TokenManager
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger

logger = FastpathLogger(__name__)

class SetupIBMCloudServicesRest(SetupIBMCloudServices):

    def __init__(self, args):
        super().__init__(args)
        self.resourceController = None
        self.cloudFoundry = None
        if self._args.is_icp:
            return
        iam_access_token = None
        if self._args.iam_token:
            iam_access_token = self._args.iam_token
        else:
            iam_access_token = TokenManager(
                apikey=self._args.apikey,
                url=self._args.env_dict['iam_url']
            ).get_token()
        self.resourceController = ResourceController(
            access_token=iam_access_token,
            url=self._args.env_dict['resource_controller_url'],
            resourceGroupUrl=self._args.env_dict['resource_group_url']
        )
        # uaa_access_token = TokenManager(
        #     apikey=self._args.apikey,
        #     url=self._args.env_dict['uaa_url'],
        #     iam_token=False
        # ).get_token()
        # self.cloudFoundry = CloudFoundry(access_token=uaa_access_token)

    def _get_credentials(self, service_display_name, params, is_rc_based, credentials_file=None):
        '''
        Returns the credentials from the specified credentials json file. If not
        then returns the credentials an instance of the specified Service.
        If there is no instance available, a new one is provisioned.
        If there are no existing credentials, new one is created and returned.
        '''
        credentials = None

        if credentials_file is not None:
            credentials = { 'credentials': self.read_credentials_from_file(credentials_file) }
        elif is_rc_based:
            params['resource_group_name'] = self._args.resource_group
            credentials = self.resourceController.get_or_create_instance(**params)
        # elif not is_rc_based:
        #     credentials = self.cloudFoundry.get_or_create_instance(
        #         service_name=params['service_name'],
        #         service_resource_name=params['resource_name'],
        #         service_plan_guid=params['service_plan_guid'],
        #         organization_name=self._args.organization,
        #         space_name=self._args.space
        #     )
        if ('name' in credentials):
            logger.log_info('{0} instance: {1}'.format(service_display_name, credentials['name']))
        return credentials

    def setup_aios(self):
        aiopenscale_params = {}
        aiopenscale_params['resource_name'] = 'openscale-fastpath-instance'
        aiopenscale_params['resource_id'] = '2ad019f3-0fd6-4c25-966d-f3952481a870'
        aiopenscale_params['resource_plan_id'] = '967ba182-c6e0-4adc-92ef-661a822cc1d7' # lite plan
        aiopenscale_params['create_credentials'] = False
        # aiopenscale_params['credentials_role'] = 'Administrator'
        aiopenscale_params['target'] = 'us-south'
        aios_instance = self._get_credentials('Watson OpenScale', aiopenscale_params, True)
        return self._aios_credentials(aios_instance['id'])

    def setup_wml(self):
        service_name = 'Watson Machine Learning'
        logger.log_info('Setting up {} instance'.format(service_name))
        wml_params = {}
        wml_params['resource_name'] = 'wml-fastpath-instance'
        wml_params['resource_id'] = '51c53b72-918f-4869-b834-2d99eb28422a'
        wml_params['resource_plan_id'] = '3f6acf43-ede8-413a-ac69-f8af3bb0cbfe' # lite plan
        wml_params['create_credentials'] = True
        wml_params['target'] = 'us-south'
        return self._get_credentials(service_name, wml_params, True, self._args.wml)['credentials']

    def setup_cos(self):
        service_name = 'IBM Cloud Object Storage'
        logger.log_info('Setting up {} instance'.format(service_name))
        cos_params = {}
        cos_params['resource_name'] = 'cos-fastpath-instance'
        cos_params['resource_id'] = 'dff97f5c-bc5e-4455-b470-411c3edbe49c'
        cos_params['resource_plan_id'] = '2fdf0c08-2d32-4f46-84b5-32e0c92fffd8' # lite plan
        cos_params['create_credentials'] = True
        cos_params['target'] = 'global'
        credentials = self._get_credentials(service_name, cos_params, True, self._args.cos)['credentials']
        if '.test.' in credentials['endpoints'] or '.stage1.' in credentials['endpoints']:
            credentials['iam_oidc_url'] = 'https://iam.stage1.ng.bluemix.net/oidc/token'
            credentials['endpoint_url'] = 'https://s3.us-west.cloud-object-storage.test.appdomain.cloud'
        else:
            credentials['iam_oidc_url'] = 'https://iam.ng.bluemix.net/oidc/token'
            credentials['endpoint_url'] = 'https://s3-api.us-geo.objectstorage.softlayer.net'
        return credentials
