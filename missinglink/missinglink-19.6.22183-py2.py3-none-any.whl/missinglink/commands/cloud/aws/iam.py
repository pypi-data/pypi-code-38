import logging
from .base_aws import AwsBase
from .wrappers import handle_not_found

logger = logging.getLogger('aws.sts')


class Iam(AwsBase):
    def __init__(self, aws_ctx, org):
        super(Iam, self).__init__(aws_ctx, org)
        self.client = AwsBase.client('iam', aws_ctx)

    @handle_not_found
    def get_role(self, name):
        return self.client.get_role(RoleName=name)

    def verify_spot_role_exists(self):
        if self.get_role('AWSServiceRoleForEC2Spot'):
            return

        self.client.create_service_linked_role(AWSServiceName='spot.amazonaws.com')
