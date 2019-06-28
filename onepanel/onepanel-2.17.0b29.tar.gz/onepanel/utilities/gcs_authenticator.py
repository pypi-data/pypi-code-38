import os

from google.cloud import storage
from onepanel.commands.base import APIViewController


class GCSAuthenticator(APIViewController):
    def __init__(self, conn):
        APIViewController.__init__(self, conn)

    '''
		entity_type is 'datasets' or 'projects'
		entity_uid is 'dataset_uid' or 'project_uid'
	'''

    # todo test this, currently a stub of functionality
    def get_gcs_credentials(self, account_uid='', entity_type='', entity_uid=''):
        if account_uid is '' or entity_type is '' or entity_uid is '':
            return {}  # Empty JSON
        return {"data":"test"}
        # todo implement
        # return self.get('', '/accounts/{account_uid}/{entity_type}/{entity_uid}/credentials/gcs'.format(
        #     account_uid=account_uid,
        #     entity_type=entity_type,
        #     entity_uid=entity_uid
        # ))
