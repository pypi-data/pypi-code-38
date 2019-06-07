# coding=utf-8
from __future__ import print_function
import json
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from ibm_ai_openscale_cli.enums import MLEngineType
from ibm_ai_openscale_cli.setup_classes.setup_ibmcloud_services_cli import SetupIBMCloudServicesCli
from ibm_ai_openscale_cli.setup_classes.setup_ibmcloud_services_rest import SetupIBMCloudServicesRest
from ibm_ai_openscale_cli.setup_classes.setup_ibmcloudprivate_services import SetupIBMCloudPrivateServices

logger = FastpathLogger(__name__)

class Credentials:

    def __init__(self, args):
        self._args = args
        self._services = None
        self._ml_engine_credentials = None
        self._database_credentials = None
        self._openscale_credentials = None
        self._cos_credentials = None
        self._run_once = True
        if self._args.is_icp:
            self._services = SetupIBMCloudPrivateServices(self._args)
        else:
            if self._args.bx:
                self._services = SetupIBMCloudServicesCli(self._args)
            else:
                self._services = SetupIBMCloudServicesRest(self._args)

    def get_openscale_credentials(self):
        if not self._openscale_credentials:
            self._openscale_credentials = self._services.setup_aios()
        return self._openscale_credentials

    def get_ml_engine_credentials(self):
        if not self._ml_engine_credentials:
            if self._args.ml_engine_type is MLEngineType.WML:
                if self._args.wml_json:
                    self._ml_engine_credentials = json.loads(self._args.wml_json)
                else:
                    self._ml_engine_credentials = self._services.setup_wml()
            elif self._args.ml_engine_type is MLEngineType.AZUREML:
                if self._args.azure_json:
                    self._ml_engine_credentials = json.loads(self._args.azure_json)
                else:
                    self._ml_engine_credentials = self._services.read_credentials_from_file(self._args.azure)
            elif self._args.ml_engine_type is MLEngineType.SPSS:
                if self._args.spss_json:
                    self._ml_engine_credentials = json.loads(self._args.spss_json)
                else:
                    self._ml_engine_credentials = self._services.read_credentials_from_file(self._args.spss)
            elif self._args.ml_engine_type is MLEngineType.CUSTOM:
                if self._args.custom_json:
                    self._ml_engine_credentials = json.loads(self._args.custom_json)
                else:
                    self._ml_engine_credentials = self._services.read_credentials_from_file(self._args.custom)
            elif self._args.ml_engine_type is MLEngineType.SAGEMAKER:
                if self._args.aws_json:
                    self._ml_engine_credentials = json.loads(self._args.aws_json)
                else:
                    self._ml_engine_credentials = self._services.read_credentials_from_file(self._args.aws)
        return self._ml_engine_credentials

    def get_database_credentials(self):
        if not self._database_credentials and self._run_once:
            # compose
            postgres_credentials = self._services.setup_postgres_database()
            if postgres_credentials is not None:
                self._database_credentials = postgres_credentials
            # icd
            if not self._database_credentials:
                icd_credentials = self._services.setup_icd_database()
                if icd_credentials is not None:
                    self._database_credentials = icd_credentials
            # db2
            if not self._database_credentials:
                db2_credentials = self._services.setup_db2_database()
                if db2_credentials is not None:
                    self._database_credentials = db2_credentials
            self._run_once = False
        return self._database_credentials

    def get_cos_credentials(self):
        if not self._cos_credentials:
            self._cos_credentials = self._services.setup_cos()
        return self._cos_credentials
