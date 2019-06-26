from googleapiclient import discovery as gcp_client
from google.oauth2 import service_account
from google.auth import compute_engine
import json


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

    def test_credential(self):
        try:
            client = gcp_client.build('compute', 'v1', credentials=self.credentials)
            print(client.instances().list(project='nawaites-panw', zone='us-central1-a').execute())
            return True
        except Exception as e:
            return False
        

    def run(self, runbook_id, resource_details, context=None):
        try:
            runbook = import_module('runbook.' + runbook_id)
            result = runbook.remediate(credentials,resource_details, context)

        except Exception as e:
            raise e