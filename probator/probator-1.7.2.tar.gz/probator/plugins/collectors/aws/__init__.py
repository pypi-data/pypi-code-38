from abc import ABC

from probator import ProbatorError, get_aws_session
from probator.config import dbconfig
from probator.plugins import BaseCollector, CollectorType
from probator.plugins.types.accounts import AWSAccount


class AWSBaseAccountCollector(BaseCollector, ABC):
    name = 'AWS Account Collector'
    ns = 'collector_aws'
    type = CollectorType.AWS_ACCOUNT
    interval = dbconfig.get('interval', ns, 15)

    def __init__(self, account):
        super().__init__()

        if type(account) == str:
            account = AWSAccount.get(account)

        if not isinstance(account, AWSAccount):
            raise ProbatorError(f'The AWS Collector only supports AWS Accounts, got {account.__class__.__name__}')

        self.account = account
        self.session = get_aws_session(self.account)


class AWSBaseRegionCollector(BaseCollector, ABC):
    name = 'AWS Region Collector'
    ns = 'collector_aws'
    type = CollectorType.AWS_REGION
    interval = dbconfig.get('interval', ns, 15)

    def __init__(self, account, region):
        super().__init__()

        if type(account) == str:
            account = AWSAccount.get(account)

        if not isinstance(account, AWSAccount):
            raise ProbatorError(f'The AWS Collector only supports AWS Accounts, got {account.__class__.__name__}')

        self.account = account
        self.region = region
        self.session = get_aws_session(self.account)
