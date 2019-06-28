import boto3
import botocore

class efsClient:
    __access_key_id = None

    __secret_access_key = None

    __session_token = None

    __efs_endpoint = None

    def __init__(self, efs_config):
        self.__access_key_id = efs_config['credentials']['accessKeyId']
        self.__secret_access_key = efs_config['credentials']['secretAccessKey']
        self.__efs_endpoint = efs_config['efsAddress']
        self.__session_token = efs_config['credentials']['sessionToken']
        self.__client = self.init()

    def init(self):
        config = boto3.session.Config(s3={'addressing_style': 'path'})
        client = boto3.client(service_name="s3",
                      region_name="eleme",
                      aws_access_key_id=self.__access_key_id,
                      aws_secret_access_key=self.__secret_access_key,
                      endpoint_url=self.__efs_endpoint,
                      aws_session_token=self.__session_token,
                      use_ssl=False,
                      config=config,
        )
        return client

    def put_object(self, key, bucket_name, file):
        try:
            res = self.__client.put_object(Bucket=bucket_name,Key=key,Body=file)
            print "Successfully uploaded data with key %s, versionID: %s" % (key,res["VersionId"])
        except botocore.exceptions.ClientError as e:
            print "Failed to upload data to %s/%s, %s" % (bucket_name,key,e)

        return res["VersionId"]    
