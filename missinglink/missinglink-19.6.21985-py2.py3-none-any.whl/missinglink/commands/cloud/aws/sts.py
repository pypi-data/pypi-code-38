import logging
from .base_aws import AwsBase

logger = logging.getLogger('aws.sts')


class Sts(AwsBase):
    def __init__(self, aws_ctx, org):
        super(Sts, self).__init__(aws_ctx, org)
        self.client = AwsBase.client('sts', aws_ctx)

    def whoami(self):
        return self.client.get_caller_identity()
