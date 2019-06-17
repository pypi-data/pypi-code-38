import boto3

def get_kms_key_id_via_alias(alias_name, region=None):
    """
    Returns the Key Id based on the alias name
    """
    if region is None:
        client = boto3.client('kms')
    else:
        client = boto3.client('kms', region_name=region)
    for alias  in client.list_aliases()['Aliases']:
        if alias['AliasName'] == alias_name:
            if 'TargetKeyId' in alias.keys():
                return alias['TargetKeyId']
    return None


def get_kms_key_arn_via_alias(alias_name, region):
    """
    Returns the ARN of the KMS Key based on the alias
    """
    key_id = get_kms_key_id_via_alias(alias_name, region)
    if key_id[0]:
        client = boto3.client('kms', region_name=region)
        return client.describe_key(
            KeyId=key_id[1]
        )['KeyMetadata']['Arn']
    return None

