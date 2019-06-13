import os

from onepanel.utilities.aws_utility import AWSUtility
from onepanel.utilities.gcp_utility import GCPUtility


class CloudStorageUtility:
    @staticmethod
    def get_utility(credentials):
        """
        Use "creds_utility.py" to get the credentials to pass in here.
        :param credentials:
        :return:
        """
        util = None
        cloud_provider = os.getenv('CLOUD_PROVIDER', 'AWS')
        if cloud_provider == 'GCP':
            util = GCPUtility()
        elif cloud_provider == "AWS":
            aws_access_key_id = credentials['data']['AccessKeyID']
            aws_secret_access_key = credentials['data']['SecretAccessKey']
            aws_session_token = credentials['data']['SessionToken']
            util = AWSUtility(aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              aws_session_token=aws_session_token)
        if util is None:
            print("Unable to instantiate cloud provider utility. Contact support.")
            exit(-1)
        return util
