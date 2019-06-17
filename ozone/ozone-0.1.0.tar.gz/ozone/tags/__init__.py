from troposphere.cloudformation import AWSCustomObject
from troposphere import Tags


class IamRoleTags(AWSCustomObject):
    """
    Class used to call a Lambda function as part of the template to resolve some values"
    """
    resource_type = "Custom::RoleTags"

    props = {
        'ServiceToken': (str, True),
        'RoleName': (str, True),
        'Tags': (Tags, True)
    }
