# coding=utf-8
from ibm_botocore.client import Config
import ibm_boto3
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
import uuid
import time

logger = FastpathLogger(__name__)

BUCKET_NAME_PREFIX = 'openscale-fastpath-bucket-'

class CloudObjectStorage():

    COS_ENDPOINT = "https://s3-api.us-geo.objectstorage.softlayer.net"
    COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"

    def __init__(self, credentials):
        self._cos = ibm_boto3.resource('s3',
                    ibm_api_key_id=credentials['apikey'],
                    ibm_service_instance_id=credentials['resource_instance_id'],
                    ibm_auth_endpoint=CloudObjectStorage.COS_AUTH_ENDPOINT,
                    config=Config(signature_version='oauth'),
                    endpoint_url=CloudObjectStorage.COS_ENDPOINT)

    def _get_existing_buckets(self):
        try:
            logger.log_debug("Retrieving list of existing buckets from IBM Cloud Object Storage ...")
            return self._cos.buckets.all()
        except Exception as e:
            logger.log_exception("Unable to retrieve list buckets: {}".format(str(e)))

    def get_bucket(self):
        buckets = self._get_existing_buckets()
        for bucket in buckets:
            if bucket.name.startswith(BUCKET_NAME_PREFIX):
                logger.log_info("Found bucket: {}".format(bucket.name))
                return bucket
        return None

    def create_bucket(self):
        bucket_name = BUCKET_NAME_PREFIX + str(uuid.uuid4())
        logger.log_info("Creating new bucket: {}".format(bucket_name))
        try:
            return self._cos.Bucket(bucket_name).create()
            logger.log_info("Bucket: {} created!".format(bucket_name))
        except Exception as e:
            logger.log_exception("Unable to create bucket: {}".format(str(e)))

    def delete_item(self, bucket_name, item_name):
        try:
            logger.log_info("Deleting item: {} from bucket: {}".format(item_name, bucket_name))
            self._cos.Object(bucket_name, item_name).delete()
            logger.log_info("Item: {} deleted!".format(item_name))
        except Exception as e:
            logger.log_exception("Unable to delete item: {}".format(str(e)))

    def multi_part_upload(self, bucket_name, item_name, file_path):
        try:
            logger.log_info("Uploading item: {} to bucket: {}".format(item_name, bucket_name))
            # set 5 MB chunks and threadhold to 15 MB
            part_size = 1024 * 1024 * 5
            file_threshold = 1024 * 1024 * 15
            transfer_config = ibm_boto3.s3.transfer.TransferConfig(
                multipart_threshold=file_threshold,
                multipart_chunksize=part_size
            )
            with open(file_path, "rb") as file_data:
                self._cos.Object(bucket_name, item_name).upload_fileobj(
                    Fileobj=file_data,
                    Config=transfer_config
                )
            logger.log_info("Uploaded: {}!".format(item_name))
        except Exception as e:
            logger.log_exception("Unable to upload item: {}".format(str(e)))

    def get_file(self, path):
        (bucket_name, file_name) = path.split('/')
        try:
            start = time.time()
            cos_object = self._cos.Object(bucket_name, file_name).get()
            cos_file = cos_object["Body"].read().decode('utf-8')
            elapsed = time.time() - start
            logger.log_debug('TIMER: cos.Object.get.read.decode {} in {:.3f} seconds'.format(path, elapsed))
        except Exception as e:
            error_msg='Unable to read file from IBM Cloud Object Storage: {}'.format(str(e))
            logger.log_exception(error_msg)
            raise Exception(error_msg)
        return cos_file
