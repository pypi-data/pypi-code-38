"""
Functions to generate KMS Keys policies
"""
from troposphere import (
    Sub
)
from ozone.resolvers.organizations import (
    find_org_in_tree,
    get_ou_accounts,
    get_all_accounts_in_ou_and_sub
)

KEY_POLICY_ALLOW_CLOUDTRAIL_READ = {
    "Sid": "Allow CloudTrail to describe key",
    "Effect": "Allow",
    "Principal": {
        "Service": "cloudtrail.amazonaws.com"
    },
    "Action": "kms:DescribeKey",
    "Resource": "*"
}

def iam_access(iam_users, iam_roles):
    """
    Default KMS Key policy for local account management
    Args:
        iam_users: list() of IAM users matching ^([\x20-\x7E]*)$ local to the account
        iam_roles: list() of IAM roles matching ^([\x20-\x7E]*)$ local to the account
    Returns:
        statement: dict() representing the core key policy
    """
    statement = {
        "Sid": "Allow administration of the key",
        "Effect": "Allow",
        "Principal": {
            "AWS": [
                Sub("arn:aws:iam::${AWS::AccountId}:root")
            ]
        },
        "Action": [
            "kms:*"
        ],
        "Resource": "*"
    }
    if iam_users:
        for user in iam_users:
            statement['Principal']['AWS'].append(
                Sub(f"arn:aws:iam::${{AWS::AccountId}}:user/{user}")
            )
    if iam_roles:
        for role in iam_roles:
            statement['Principal']['AWS'].append(
                Sub(f"arn:aws:iam::${{AWS::AccountId}}:role/{role}")
            )
    return statement


def _cloudtrail_access(accounts_ids):
    """
    Args:
        accounts_ids: List of AWS Account Ids [0-9]{12}
    Returns:
        statemens: list of KMS Policy statements to be added to the Key policy
    """
    trails_arns = []
    accounts_roots = []
    for account_id in accounts_ids:
        accounts_roots.append(f'arn:aws:iam::{account_id}:root')
        trails_arns.append(f'arn:aws:cloudtrail:*:{account_id}:trail/*')
    statements = [
        {
            "Sid": "Allow CloudTrail to encrypt logs",
            "Effect": "Allow",
            "Resource": ["*"],
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": [
                "kms:GenerateDataKey*"
            ],
            "Condition":{
                "StringLike":
                {
                    "kms:EncryptionContext:aws:cloudtrail:arn": trails_arns
                }
            }
        },
        {
            "Sid": "Allow principals in the account to decrypt log files",
            "Effect": "Allow",
            "Principal": {
                "AWS": "*"
            },
            "Action": [
                "kms:Decrypt",
                "kms:ReEncryptFrom"
            ],
            "Resource": "*",
            "Condition": {
                "StringLike": {
                    "kms:EncryptionContext:aws:cloudtrail:arn": trails_arns
                }
            }
        },
        {
            "Sid": "Enable encrypted CloudTrail log read access",
            "Effect": "Allow",
            "Principal": {
                "AWS": accounts_roots
            },
            "Action": "kms:Decrypt",
            "Resource": "*",
            "Condition": {
                "Null": {
                    "kms:EncryptionContext:aws:cloudtrail:arn": "false"
                }
            }
        }
    ]
    return statements


def add_cloudtrail_access(accounts_ids):
    """
    Function to add CloudTrail access the account using a list of Account Ids
    Args:
        accounts_ids: List of account Ids ([0-9]{12})
    """
    return _cloudtrail_access(accounts_ids)


def add_cloudtrail_ou_access(ou_path, use_as_root=False):
    """
    Extends the policy in case CloudTrail is the main user of the KMS Key
    """
    ou_info = find_org_in_tree(ou_path)
    ou_accounts = []
    if use_as_root:
        ou_accounts_list = get_all_accounts_in_ou_and_sub(ou_info['Id'])
    else:
        ou_accounts_list = get_ou_accounts(ou_info['Id'])
    try:
        assert ou_accounts_list
    except AssertionError:
        raise ValueError(f'No accounts found for {ou_path}')

    for account in ou_accounts_list:
        ou_accounts.append(account['Id'])
    return add_cloudtrail_access(ou_accounts)
