from orchestrate.core.services.base import Service


class AwsService(Service):
  """
  Base class for all AWS services.
  """
  def __init__(self, services, aws_services):
    super(AwsService, self).__init__(services)
    self.aws_services = aws_services
