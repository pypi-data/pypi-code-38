from importlib import import_module
from google.oauth2 import service_account
from google.auth import compute_engine
from . import utils
import json
import traceback


class Client:
    def __init__(self, service_account_json=None):
        # Get credentials from service account JSON key
        if service_account_json is not None:
            try:
                self.credentials = service_account.Credentials.from_service_account_info(
                    service_account_json, scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
            except Exception as e:
                raise Exception("Invalid Service Account JSON.")
        # Get credentials from Compute 
        else:
            try:
                self.credentials = compute_engine.Credentials()
            except Exception as e:
                raise Exception("Cannot obtain credentials from default service account.")
        

    def run(self, runbook_id, resource_details, context=None):
        try:
            runbook = import_module('remediate_gcp.runbook.' + runbook_id)
        except Exception as e:
            return utils.generate_error(f'Runbook {runbook_id} does not exists')


        try:
            result = runbook.remediate(self.credentials,resource_details, context)
        except Exception as e:
            return utils.generate_error(f'Unhandled Error encountered when running runbook {runbook_id}',body=traceback.format_exc())

        return result
