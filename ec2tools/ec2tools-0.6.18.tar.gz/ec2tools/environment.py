#!/usr/bin/env python3

import os
import sys
import json
import argparse
import inspect
from botocore.exceptions import ClientError
from pyaws.utils import stdout_message, export_json_object, userchoice_mapping
from pyaws.session import authenticated, boto3_session, parse_profiles
from pyaws.ec2 import get_regions, default_region
from pyaws import Colors
from ec2tools.statics import local_config
from ec2tools import about, logd, __version__

try:
    from pyaws.core.oscodes_unix import exit_codes
except Exception:
    from pyaws.core.oscodes_win import exit_codes    # non-specific os-safe codes

# globals
module = os.path.basename(__file__)
logger = logd.getLogger(__version__)
act = Colors.ORANGE
bd = Colors.BOLD + Colors.WHITE
rst = Colors.RESET
FILE_PATH = local_config['CONFIG']['CONFIG_DIR']
CALLER = 'profileaccount'


def help_menu():
    """
    Summary.

    Displays command line parameter options

    """
    menu = '''
                    ''' + bd + CALLER + rst + ''' help contents

  ''' + bd + '''DESCRIPTION''' + rst + '''

          Profile AWS Account Environment.  Collects Subnets,
          SecurityGroups, and ssh Keypairs for all AWS regions.

  ''' + bd + '''OPTIONS''' + rst + '''

            $ ''' + act + CALLER + rst + '''  --profile <PROFILE> [--outputfile]

                         -p, --profile  <value>
                        [-o, --outputfile ]
                        [-r, --region   <value> ]
                        [-d, --debug     ]
                        [-h, --help      ]

        ''' + bd + '''-p''' + rst + ''', ''' + bd + '''--profile''' + rst + '''  (string):  IAM username or Role corresponding
            to a profile name from local awscli configuration

        ''' + bd + '''-o''' + rst + ''', ''' + bd + '''--outputfile''' + rst + ''' (string):  When parameter present, produces
            a local json file containing metadata gathered about the
            AWS Account designated by --profile during profiling.

        ''' + bd + '''-r''' + rst + ''', ''' + bd + '''--region''' + rst + '''  (string):   Region code designating a specific
            AWS region to profile.  If no region specified, profiles
            all AWS regions in the AWS Account designated by profile
            name provided with --profile.

        ''' + bd + '''-d''' + rst + ''', ''' + bd + '''--debug''' + rst + ''': Debug mode, verbose output.

        ''' + bd + '''-h''' + rst + ''', ''' + bd + '''--help''' + rst + ''': Print this help menu

        ''' + bd + '''-s''' + rst + ''', ''' + bd + '''--show''' + rst + ''' {profiles | ?}:  Display user information

        ''' + bd + '''-V''' + rst + ''', ''' + bd + '''--version''' + rst + ''': Print package version and License information
    '''
    print(menu)
    return True


def is_tty():
    """
    Summary:
        Determines if output is displayed to the screen or redirected
    Returns:
        True if tty terminal | False is redirected, TYPE: bool
    """
    return sys.stdout.isatty()


def get_account_identifier(profile, returnAlias=True):
    """
    Summary:
        Returns account alias
    Args:
        :profile (str): profilename present in local awscli configuration
        :returnAlias (bool): when True (default), returns the account alias if one
         exists.  If False, returns the AWS AccountId number (12 digit integer sequence)
    Returns:
        aws account alias (str) or aws account id number (str)
    """
    client = boto3_session(service='iam', profile=profile)
    alias = client.list_account_aliases()['AccountAliases'][0]
    if alias and returnAlias:
        return alias
    client = boto3_session(service='sts', profile=profile)
    return client.get_caller_identity()['Account']


def profile_subnets(profile):
    """ Profiles all subnets in an account """
    subnets = {}
    for rgn in get_regions():
        try:
            client = boto3_session('ec2', region=rgn, profile=profile)
            r = client.describe_subnets()['Subnets']
            subnets[rgn] = [
                    {
                        x['SubnetId']: {
                                'AvailabilityZone': x['AvailabilityZone'],
                                'CidrBlock': x['CidrBlock'],
                                'State': x['State'],
                                'IpAddresses': 'Public' if x['MapPublicIpOnLaunch'] else 'Private',
                                'VpcId': x['VpcId']
                            }
                    } for x in r
                ]
        except ClientError as e:
            logger.warning(
                '{}: Unable to retrieve subnets for region {}'.format(inspect.stack()[0][3], rgn)
                )
            continue
    return subnets


def profile_securitygroups(profile, region=None):
    """ Profiles securitygroups in an aws account
    THIS IS BROKEN -- ONLY WORKS WHEN GIVEN region,
    LOOPING THRU REGIONS FAILS
    """
    sgs = {}
    regions = [region] or get_regions()

    for rgn in regions:
        try:
            client = boto3_session('ec2', region=rgn, profile=profile)
            r = client.describe_security_groups()['SecurityGroups']
            sgs[rgn] = [
                    {
                        x['GroupId']: {
                            'Description': x['Description'],
                            'GroupName': x['GroupName'],
                            'VpcId': x['VpcId']
                        }
                    } for x in r
                ]
        except ClientError as e:
            stack = inspect.stack()[0][3]
            logger.warning(
                '{}: Unable to retrieve securitygroups for region {}. Error: {}'.format(stack, rgn, e)
                )
            continue
    return sgs


def profile_keypairs(profile, region=None):
    keypairs = {}

    regions = [region] or get_regions()

    for rgn in regions:
        try:
            client = boto3_session('ec2', region=rgn, profile=profile)
            keypairs[rgn] = [x['KeyName'] for x in client.describe_key_pairs()['KeyPairs']]
        except ClientError as e:
            logger.warning(
                '{}: Unable to retrieve keypairs for region {}'.format(inspect.stack()[0][3], rgn)
                )
            continue
    return keypairs


def options(parser):
    """
    Summary:
        parse cli parameter options
    Returns:
        TYPE: argparse object, parser argument set
    """
    parser.add_argument("-p", "--profile", nargs='?', default="default",
                              required=False, help="type (default: %(default)s)")
    parser.add_argument("-o", "--outputfile", dest='outputfile', action='store_true', required=False)
    parser.add_argument("-d", "--debug", dest='debug', action='store_true', required=False)
    parser.add_argument("-s", "--show", dest='show', nargs='?', required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    parser.add_argument("-h", "--help", dest='help', action='store_true', required=False)
    return parser.parse_args()


def file_contents(content):
    with open(FILE_PATH + '/' + content) as f1:
        f2 = f1.read()
        f3 = json.loads(f2)
        export_json_object(f3, logging=False)
    return True


def package_version():
    """
    Prints package version and requisite PACKAGE info
    """
    print(about.about_object)
    sys.exit(exit_codes['EX_OK']['Code'])


def precheck(parameters):
    """ Validates user supplied parameters """
    for arg in sys.argv[1:]:
        if arg.startswith('-') or arg.startswith('--'):
            if arg not in (
                '--profile', '-p', '-o', '--outputfile', '-d', '--debug', '-s', '--show',
                '-V', '--version', '-h', '--help'
            ):
                stdout_message(
                    message=f'Unrecognized option ({arg}). Exit',
                    prefix='WARN',
                    severity='warning'
                )
                return False
    return True


def show_information(display):
    """
    Summary:
        Displays information to user
    Returns:
        Success or Failure, TYPE: bool
    """
    def valid(input):
        try:
            if userchoice_mapping(input) is None:
                stdout_message('Please choose a letter associated with one of the choices.', indent=12)
                return False
            elif isinstance(int(input), int) or isinstance(float(input), float):
                stdout_message(message='You must choose a letter', indent=12)
                return False
        except ValueError:
            # valid string
            pass
        return True

    if os.path.exists(FILE_PATH) and display in ('files', 'profiles'):
        files = os.listdir(FILE_PATH)
        profiles = list(filter(lambda x: x.endswith('.profile'), files))
        if profiles:
            # display user menu
            print('\t_______________________________________________________\n')
            print(bd + '\t\t\tLocal AWS Account Profiles' + rst)
            print('\t_______________________________________________________\n')
            for index, file in enumerate(profiles):
                print('\t\t({}):  {}'.format(userchoice_mapping(index + 1), Colors.BRIGHT_PURPLE + file + rst))
            answer = input('\n\tSelect an option to display [quit]:  ')
            # process user input
            if answer:
                if valid(answer):
                    if int(userchoice_mapping(answer)) in range(1, index + 2):
                        return file_contents(profiles[int(userchoice_mapping(answer)) - 1])
                        return True
                    else:
                        # user answer out of selection range
                        stdout_message(
                            message='Please choose a letter associated with one of the choices.',
                            indent=12
                        )
    return False


def init_cli():
    """
    Initializes commandline script
    """
    parser = argparse.ArgumentParser(add_help=False)

    try:

        args = options(parser)

    except Exception as e:
        stdout_message(str(e), 'ERROR')
        sys.exit(exit_codes['EX_OK']['Code'])

    if not precheck(args):
        sys.exit(exit_codes['E_DEPENDENCY']['Code'])

    elif len(sys.argv) == 1:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.help:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.version:
        package_version()

    elif ('--show' in sys.argv or '-s' in sys.argv) and args.show is None:
        stdout_message('You must specify a value when using the --show option. Example: \
        \n\n\t\t$  %s  --show profiles' % (act + CALLER + rst))

    elif args.show:
        return show_information(args.show)

    elif args.profile:
        if authenticated(profile=parse_profiles(args.profile)):

            container = {}
            default_outputfile = get_account_identifier(parse_profiles(args.profile)) + '.profile'
            region = default_region(args.profile)

            # add aws account identifiers
            container['AccountId'] = get_account_identifier(parse_profiles(args.profile), returnAlias=False)
            container['AccountAlias'] = get_account_identifier(parse_profiles(args.profile))

            # profile the account
            r_subnets = profile_subnets(profile=parse_profiles(args.profile))
            r_sgs = profile_securitygroups(profile=parse_profiles(args.profile))
            r_keypairs = profile_keypairs(profile=parse_profiles(args.profile))

            # assemble profile data into single json schema
            if r_subnets and r_sgs and r_keypairs:

                try:
                    for region in get_regions():
                        temp = {}
                        temp['Subnets'] = r_subnets[region]
                        temp['SecurityGroups'] = r_sgs[region]
                        temp['KeyPairs'] = r_keypairs[region]
                        container[region] = temp
                except KeyError as e:
                    raise e

                if args.outputfile:
                    export_json_object(container, FILE_PATH + '/' + default_outputfile)
                elif is_tty():
                    export_json_object(container, logging=False)
                    stdout_message('AWS Account profile complete')
        return True

    else:
        stdout_message('Unrecognized option. Exit')
    return False


if __name__ == '__main__':
    sys.exit(init_cli())
