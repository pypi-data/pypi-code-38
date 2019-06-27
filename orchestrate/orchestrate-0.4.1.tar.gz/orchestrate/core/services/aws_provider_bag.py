from orchestrate.core.autoscaling.service import AwsAutoScalingService
from orchestrate.core.cloudformation.service import AwsCloudFormationService
from orchestrate.core.ec2.service import AwsEc2Service
from orchestrate.core.ecr.service import AwsEcrService
from orchestrate.core.eks.service import AwsEksService
from orchestrate.core.iam.service import AwsIamService
from orchestrate.core.services.bag import ServiceBag
from orchestrate.core.sts.service import AwsStsService


class AwsProviderServiceBag(ServiceBag):
  def __init__(self, orchestrate_services, aws_access_key_id, aws_secret_access_key):
    self.orchestrate_services = orchestrate_services
    self._aws_access_key_id = aws_access_key_id
    self._aws_secret_access_key = aws_secret_access_key
    super(AwsProviderServiceBag, self).__init__()

  @property
  def aws_access_key_id(self):
    return self._aws_access_key_id

  @property
  def aws_secret_access_key(self):
    return self._aws_secret_access_key

  def _create_services(self):
    super(AwsProviderServiceBag, self)._create_services()
    options = dict(
      aws_access_key_id=self.aws_access_key_id,
      aws_secret_access_key=self.aws_secret_access_key,
    )
    self.autoscaling_service = AwsAutoScalingService(self.orchestrate_services, self, **options)
    self.cloudformation_service = AwsCloudFormationService(self.orchestrate_services, self, **options)
    self.ec2_service = AwsEc2Service(self.orchestrate_services, self, **options)
    self.ecr_service = AwsEcrService(self.orchestrate_services, self, **options)
    self.eks_service = AwsEksService(self.orchestrate_services, self, **options)
    self.iam_service = AwsIamService(self.orchestrate_services, self, **options)
    self.sts_service = AwsStsService(self.orchestrate_services, self, **options)
