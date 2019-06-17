from troposphere import (
    Sub
)
from troposphere.kms import (
    Key
)

from .policy import (
    iam_access,
    add_cloudtrail_access,
    add_cloudtrail_ou_access
)

def key_build(**kwargs):
    """
    Args:
      kwargs:
        IamUsers: list of IAM user names to grant admin access to the key
        IamRoles: list of IAM role names to grant admin access to the key
        UseCloudtrail: bool() to define whether or not the key shall be used for CloudTrail
        AccountsIds: list() of account ids representing the accounts using the key for CT
        OrganizationUnitName: str() of the name of the organization unit
                              to lookup accounts for
        UseOrganizationUnitAsRoot: bool() - if True, will lookup all accounts within
                in the OU and in the SubOu to apply it to
    Returns:
        key Key()
    """
    iam_users = []
    iam_roles = []
    if 'IamUsers' in kwargs.keys():
        iam_users = kwargs['IamUsers']
    if 'IamRoles' in kwargs.keys():
        iam_roles = kwargs['IamRoles']

    key_policy = {
        "Version": "2012-10-17",
        "Id": "Key polocy for cloudtrail",
        "Statement": []
    }
    key_policy['Statement'].append(iam_access(iam_users, iam_roles))
    if 'UseCloudTrail' in kwargs.keys():
        if 'AccountsIds' in kwargs.keys():
            key_policy['Statement'] += add_cloudtrail_access(kwargs['AccountsIds'])
        elif 'OrganizationName' in kwargs.keys():
            if ('UseOrganizationUnitAsRoot' in kwargs.keys() and
                kwargs['UseOrganizationUnitAsRoot']):
                key_policy['Statement'] += add_cloudtrail_ou_access(
                    kwargs['OrganizationName'],
                    use_as_root=True
                )
            else:
                key_policy['Statement'] += add_cloudtrail_ou_access(
                    kwargs['OrganizationName']
                )
        else:
            raise KeyError(
                'When using CloudFormation, either AccountsIds or OrganizationName must be set'
            )
    kms_key = Key(
        'KmsKey',
        Description=Sub('KMS Key in ${AWS::Region}'),
        Enabled=True,
        EnableKeyRotation=True,
        KeyPolicy=key_policy
    )
    for key in ['Tags', 'Description', 'Enabled', 'EnableKeyRotation', 'KmsKeyPolicy']:
        if key in kwargs.keys():
            setattr(kms_key, key, kwargs[key])
    if 'Name' in kwargs.keys():
        kms_key.title = kwargs['Name']
    return kms_key
