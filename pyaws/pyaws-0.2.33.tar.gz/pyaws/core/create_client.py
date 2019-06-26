def create_client(service, account=None, role=None):
    """
    Summary:
        Creates the appropriate boto3 client for a particular AWS service
    Args:
        :type service: str
        :param service: name of service at Amazon Web Services (AWS),
            e.g. s3, ec2, etc
        :type credentials: sts credentials object
        :param credentials: authentication credentials to resource in AWS
        :type role: str
        :param role: IAM role designation used to access AWS resources
            in an account
    Returns:
        Boto3 Client Object
    """
    try:
        if role and account:     # create client for a different AWS account
            account_obj = AssumeAWSRole(account, role)
            if account_obj.status.get('STATUS') == 'SUCCESS':
                credentials = account_obj.credentials
                client = boto3.client(
                    service,
                    aws_access_key_id=credentials['AccessKeyId'],
                    aws_secret_access_key=credentials['SecretAccessKey'],
                    aws_session_token=credentials['SessionToken']
                )
            else:
                logger.critical('failed to create client - Error: %s' %
                    str(account_obj.status.get('STATUS')))
                raise ClientError(
                    '%s: Problem creating client using role %s' %
                    (inspect.stack()[0][3], str(role))
                    )
        else:
            return boto3.client(service)    # create client in the current AWS account
    except ClientError as e:
        logger.exception(
            "%s: Problem creating client %s in account %s (Code: %s Message: %s)" %
            (inspect.stack()[0][3], role, account, e.response['Error']['Code'],
            e.response['Error']['Message'])
        )
        raise
    return client
