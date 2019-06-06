from boto3.session import Session


__all__ = [
    'create_session',
    'ssm_client',
]


def create_session():
    """
    A handy helper function that will create the
    boto session using our waddle-level settings
    """
    from waddle import settings
    session = Session(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
        profile_name=settings.aws_profile,
    )
    return session


def ssm_client():
    session = create_session()
    return session.client('ssm')
