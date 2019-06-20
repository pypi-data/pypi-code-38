import boto3
import click
from botocore.exceptions import ClientError  # , NoCredentialsError
from aws_hat.helpers import get_section, set_section

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
AWS_CONFIG_FILE = '~/.aws/config'
AWS_CREDENTIALS_FILE = '~/.aws/credentials'


@click.command(context_settings=CONTEXT_SETTINGS)
# this is the main and mandatory argument which searches
# for the config
# for example: hat role@example -> [profile role@example]
@click.argument(
    'profile-config'
)
# consistent with aws cli --profile can be the target
# for example: aws config --profile example
# will write to [example] in the credentials file
@click.option(
    '--profile',
    default="default",
    envvar='AWS_DEFAULT_PROFILE',
    help="Profile to write to"
)
# default writes the keys to credentials
# you could also print and source them, for example:
# export $(hat role@account -t 123456 -o env)
@click.option(
    '--output',
    '-o',
    default="profile",
    type=click.Choice(['profile', 'env']),
    help="Env output or set profile"
)
@click.option(
    '--force',
    '-f',
    is_flag=True,
    default=False,
    help="Force overwrite the profile."
)
@click.option(
    '--token',
    '-t',
    prompt=True,
    hide_input=True,
    help="The MFA Token code."
)
@click.option(
    '--expiration',
    '-e',
    default=3600,
    envvar='AWS_HAT_EXPIRATION',
    help="Session expiration time (default 3600)"
)
@click.option(
    '--region',
    '-r',
    default='us-east-1',
    envvar='AWS_DEFAULT_REGION',
    help="Specify a region."
)
def default(**kwargs):
    """
    \b
    Examples:
    \b
    $ hat role@account
    $ hat role@account --profile temp
    $ hat role@account --profile temp --force
    $ export $(hat role@account -t 123456 -o env)
    """
    src = get_section(AWS_CONFIG_FILE, "profile " + kwargs['profile_config'])
    if len(src.keys()) == 0:
        print("Profile not found: " + kwargs['profile_config'])
        exit(2)

    if 'region' in src:
        region = src['region']
    else:
        region = kwargs['region']

    # boto must be initiated with the source profile
    sp = get_section('~/.aws/credentials', src['source_profile'])
    sts = boto3.client('sts',
                       aws_access_key_id=sp['aws_access_key_id'],
                       aws_secret_access_key=sp['aws_secret_access_key']
                       )

    # if the user has read permissions on the max session,
    # use the max session timeout
    try:
        iam = boto3.client('iam',
                           aws_access_key_id=sp['aws_access_key_id'],
                           aws_secret_access_key=sp['aws_secret_access_key']
                           )
        role = iam.get_role(
            RoleName="admins"
        )
        kwargs['expiration'] = role['Role']['MaxSessionDuration']
    except Exception as e:
        print(e)

    try:
        response = sts.assume_role(
            RoleArn=src['role_arn'],
            RoleSessionName='session',
            DurationSeconds=kwargs['expiration'],
            SerialNumber=src['mfa_serial'],
            TokenCode=str(kwargs['token'])
        )
    except ClientError as e:
        print("ERROR: {}".format(e))
        exit(1)

    session = {
        'region': region,
        'aws_access_key_id': response['Credentials']['AccessKeyId'],
        'aws_secret_access_key': response['Credentials']['SecretAccessKey'],
        'aws_session_token': response['Credentials']['SessionToken'],
        'expiration': str(response['Credentials']['Expiration'])
    }
    if kwargs['output'] == "env":
        print("AWS_ACCESS_KEY_ID={}".format(session['aws_access_key_id']))
        print("AWS_SECRET_ACCESS_KEY={}".format(
            session['aws_secret_access_key']))
        print("AWS_SESSION_TOKEN={}".format(session['aws_session_token']))
    else:
        # Check if profile already exists
        # if it has an expiration, we assume aws-hat has set this profile
        target = get_section(AWS_CREDENTIALS_FILE, kwargs['profile'])
        profile = kwargs['profile']
        if 'expiration' not in target:
            if len(target.keys()) > 0 and not kwargs['force']:
                print(
                    f'Profile {profile} already used.',
                    'Press enter to proceed or CTRL+C to cancel.'
                )
                input()  # nosec

        set_section(AWS_CREDENTIALS_FILE, kwargs['profile'], session)
        print("Now use: --profile {}".format(kwargs['profile']))


if __name__ == '__main__':
    default()
