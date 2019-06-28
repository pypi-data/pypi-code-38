#!/usr/bin/env python3

import argparse
import os
import re
import sys
import json
import inspect
import itertools
from collections import OrderedDict
from botocore.exceptions import ClientError
from pyaws.session import authenticated, boto3_session
from pyaws import Colors
from pyaws.utils import stdout_message, export_json_object
from ec2tools.help_menu import menu_body
from ec2tools import about, logd, __version__

try:
    from pyaws.core.oscodes_unix import exit_codes
except Exception:
    from pyaws.core.oscodes_win import exit_codes    # non-specific os-safe codes

# globals
logger = logd.getLogger(__version__)
DEFAULT_REGION = os.environ['AWS_DEFAULT_REGION']
VALID_FORMATS = ('json', 'text')
VALID_AMI_TYPES = (
        'amazonlinux1', 'amazonlinux2',
        'redhat', 'redhat7.4', 'redhat7.5', 'redhat7.6',
        'ubuntu14.04', 'ubuntu16.04', 'ubuntu16.10', 'ubuntu18.04', 'ubuntu18.10',
        'centos6', 'centos7',
        'windows2012', 'windowsServer2012', 'windows2016', 'windowsServer2016'
    )

# AWS Marketplace Owner IDs
AMAZON = '137112412989'
CENTOS = '679593333241'
REDHAT = '679593333241'
UBUNTU = '099720109477'
MICROSOFT = '801119661308'


def debug_message(response, rgn, mode):
    """
    Prints debug output
    """
    if mode:
        stdout_message(
                message='REGION: %s' % rgn,
                prefix='DBUG',
                severity='WARNING'
            )
        print(json.dumps(response, indent=4))
    return True


def help_menu():
    """
    Displays help menu contents
    """
    print(
        Colors.BOLD + '\n\t\t\t' + 'machineimage' + Colors.RESET +
        ' help contents'
        )
    sys.stdout.write(menu_body + '\n')
    sys.exit(exit_codes['EX_OK']['Code'])


def get_regions(profile):
    """ Return list of all regions """
    try:

        client = boto3_session(service='ec2', profile=profile)

    except ClientError as e:
        logger.exception(
            '%s: Boto error while retrieving regions (%s)' %
            (inspect.stack()[0][3], str(e)))
        raise e
    return [x['RegionName'] for x in client.describe_regions()['Regions']]


def amazonlinux1(profile, region=None, detailed=False, debug=False):
    """
    Return latest current amazonlinux v1 AMI for each region
    Args:
        :profile (str): profile_name
        :region (str): if supplied as parameter, only the ami for the single
        region specified is returned
    Returns:
        amis, TYPE: list:  container for metadata dict for most current instance in region
    """
    amis, metadata = {}, {}
    if region:
        regions = [region]
    else:
        regions = get_regions(profile=profile)

    # retrieve ami for each region in list
    for region in regions:
        try:
            client = boto3_session(service='ec2', region=region, profile=profile)
            r = client.describe_images(
                Owners=['amazon'],
                Filters=[
                    {
                        'Name': 'name',
                        'Values': [
                            'amzn-ami-hvm-2018.??.?.2018????-x86_64-gp2'
                        ]
                    }
                ])

            # need to find ami with latest date returned
            debug_message(r, region, debug)
            newest = newest_ami(r['Images'])
            metadata[region] = newest
            amis[region] = newest.get('ImageId', 'unavailable')
        except ClientError as e:
            logger.exception(
                '%s: Boto error while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            continue
        except Exception as e:
            logger.exception(
                '%s: Unknown Exception occured while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            raise e
    if detailed:
        return metadata
    return amis


def amazonlinux2(profile, region=None, detailed=False, debug=False):
    """
    Return latest current amazonlinux v2 AMI for each region
    Args:
        :profile (str): profile_name
        :region (str): if supplied as parameter, only the ami for the single
        region specified is returned
    Returns:
        amis, TYPE: list:  container for metadata dict for most current instance in region
    """
    amis, metadata = {}, {}
    if region:
        regions = [region]
    else:
        regions = get_regions(profile=profile)

    # retrieve ami for each region in list
    for region in regions:
        try:
            if not profile:
                profile = 'default'
            client = boto3_session(service='ec2', region=region, profile=profile)

            r = client.describe_images(
                Owners=['amazon'],
                Filters=[
                    {
                        'Name': 'name',
                        'Values': [
                            'amzn2-ami-hvm-????.??.?.2018????.?-x86_64-gp2',
                            'amzn2-ami-hvm-????.??.?.2018????-x86_64-gp2'
                        ]
                    }
                ])

            # need to find ami with latest date returned
            debug_message(r, region, debug)
            newest = newest_ami(r['Images'])
            metadata[region] = newest
            amis[region] = newest.get('ImageId', 'unavailable')
        except ClientError as e:
            logger.exception(
                '%s: Boto error while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            continue
        except Exception as e:
            logger.exception(
                '%s: Unknown Exception occured while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            raise e
    if detailed:
        return metadata
    return amis


def centos(profile, os, region=None, detailed=False, debug=False):
    """
    Return latest current Redhat AMI for each region
    Args:
        :profile (str): profile_name
        :region (str): if supplied as parameter, only the ami for the single
        region specified is returned
    Returns:
        amis, TYPE: list:  container for metadata dict for most current instance in region
    """
    amis, metadata = {}, {}
    if region:
        regions = [region]
    else:
        regions = get_regions(profile=profile)
    # retrieve ami for each region in list
    for region in regions:
        try:
            client = boto3_session(service='ec2', region=region, profile=profile)
            r = client.describe_images(
                Owners=[CENTOS],
                Filters=[
                    {
                        'Name': 'name',
                        'Values': [
                            'CentOS*%s x86_64*' % os
                        ]
                    }
                ])

            # need to find ami with latest date returned
            debug_message(r, region, debug)
            newest = newest_ami(r['Images'])
            metadata[region] = newest
            amis[region] = newest.get('ImageId', 'unavailable')
        except ClientError as e:
            logger.exception(
                '%s: Boto error while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            continue
        except Exception as e:
            logger.exception(
                '%s: Unknown Exception occured while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            raise e
    if detailed:
        return metadata
    return amis


def redhat(profile, os, region=None, detailed=False, debug=False):
    """
    Return latest current Redhat AMI for each region
    Args:
        :profile (str): profile_name
        :region (str): if supplied as parameter, only the ami for the single
        region specified is returned
    Returns:
        amis, TYPE: list:  container for metadata dict for most current instance in region
    """
    amis, metadata = {}, {}
    if region:
        regions = [region]
    else:
        regions = get_regions(profile=profile)
    # retrieve ami for each region in list
    for region in regions:
        try:
            client = boto3_session(service='ec2', region=region, profile=profile)
            r = client.describe_images(
                Owners=['309956199498'],
                Filters=[
                    {
                        'Name': 'name',
                        'Values': [
                            'RHEL-%s*GA*' % os
                        ]
                    }
                ])

            # need to find ami with latest date returned
            debug_message(r, region, debug)
            newest = newest_ami(r['Images'])
            metadata[region] = newest
            amis[region] = newest.get('ImageId', 'unavailable')
        except ClientError as e:
            logger.exception(
                '%s: Boto error while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            continue
        except Exception as e:
            logger.exception(
                '%s: Unknown Exception occured while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            raise e
    if detailed:
        return metadata
    return amis


def ubuntu(profile, os, region=None, detailed=False, debug=False):
    """
    Return latest current ubuntu AMI for each region
    Args:
        :profile (str): profile_name
        :region (str): if supplied as parameter, only the ami for the single
        region specified is returned
    Returns:
        amis, TYPE: list:  container for metadata dict for most current instance in region
    """
    amis, metadata = {}, {}
    if region:
        regions = [region]
    else:
        regions = get_regions(profile=profile)
    # retrieve ami for each region in list
    for region in regions:
        try:
            client = boto3_session(service='ec2', region=region, profile=profile)
            r = client.describe_images(
                Owners=[UBUNTU],
                Filters=[
                    {
                        'Name': 'name',
                        'Values': [
                            'ubuntu/images/hvm-ssd/*%s*' % os
                        ]
                    }
                ])

            # need to find ami with latest date returned
            debug_message(r, region, debug)
            newest = newest_ami(r['Images'])
            metadata[region] = newest
            amis[region] = newest.get('ImageId', 'unavailable')
        except ClientError as e:
            logger.exception(
                '%s: Boto error while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            continue
        except Exception as e:
            logger.exception(
                '%s: Unknown Exception occured while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            raise e
    if detailed:
        return metadata
    return amis


def windows(profile, os, region=None, detailed=False, debug=False):
    """
    Return latest current Microsoft Windows Server AMI for each region
    Args:
        :profile (str): profile_name
        :region (str): if supplied as parameter, only the ami for the single
        region specified is returned
    Returns:
        amis, TYPE: list:  container for metadata dict for most current instance in region

        "Name": "Windows_Server-2016-English-Full-Base-2018.07.11"

    """
    if os == '2012':
        filter_criteria = 'Windows_Server-%s-R2*English*Base*' % os
    else:
        filter_criteria = 'Windows_Server*%s*English*Base*' % os

    amis, metadata = {}, {}
    if region:
        regions = [region]
    else:
        regions = get_regions(profile=profile)
    # retrieve ami for each region in list
    for region in regions:
        try:
            client = boto3_session(service='ec2', region=region, profile=profile)
            r = client.describe_images(
                Owners=[MICROSOFT],
                Filters=[
                    {
                        'Name': 'name',
                        'Values': [
                            filter_criteria
                        ]
                    }
                ])

            # need to find ami with latest date returned
            debug_message(r, region, debug)
            newest = newest_ami(r['Images'])
            metadata[region] = newest
            amis[region] = newest.get('ImageId', 'unavailable')
        except ClientError as e:
            logger.exception(
                '%s: Boto error while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            continue
        except Exception as e:
            logger.exception(
                '%s: Unknown Exception occured while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            raise e
    if detailed:
        return metadata
    return amis


def is_tty():
    """
    Summary:
        Determines if output is displayed to the screen or redirected
    Returns:
        True if tty terminal | False is redirected, TYPE: bool
    """
    return sys.stdout.isatty()


def os_version(imageType):
    """
    Returns the version when provided redhat AMI type
    """
    return ''.join(re.split('(\d+)', imageType)[1:])


def format_text(json_object, file=None):
    """
    Summary:
        Formats json object into text format
    Args:
        :json_object (json):  object with json schema
    Returns:
        text object | empty string upon failure
    """

    block = ''

    try:
        for k, v in json_object.items():
            # format k,v depending if writing to the screen (tty) or fs
            if is_tty() and file is None:
                key = Colors.BOLD + Colors.BLUE + str(k) + Colors.RESET
                value = Colors.GOLD3 + str(v) + Colors.RESET
            else:
                key = str(k)
                value = str(v)
            row = '%s \t%s\n' % (key, value)
            block += row
    except KeyError as e:
        logger.exception(
            '%s: json_object does not appear to be json structure. Error (%s)' %
            (inspect.stack()[0][3], str(e))
            )
        return ''
    return block.strip()


def main(profile, imagetype, format, details, debug, filename='', rgn=None):
    """
    Summary:
        Calls appropriate module function to identify the latest current amazon machine
        image for the specified OS type
    Returns:
        json (dict) | text (str)
    """
    try:
        if imagetype.startswith('amazonlinux1'):
            latest = amazonlinux1(
                        profile=profile,
                        region=rgn,
                        detailed=details,
                        debug=debug
                    )

        elif imagetype.startswith('amazonlinux2'):
            latest = amazonlinux2(
                        profile=profile,
                        region=rgn,
                        detailed=details,
                        debug=debug
                    )

        elif imagetype.startswith('centos'):
            latest = centos(
                        profile=profile,
                        os=os_version(imagetype),
                        region=rgn,
                        detailed=details,
                        debug=debug
                    )

        elif imagetype.startswith('redhat'):
            latest = redhat(
                        profile=profile,
                        os=os_version(imagetype),
                        region=rgn,
                        detailed=details,
                        debug=debug
                    )

        elif imagetype.startswith('ubuntu'):
            latest = ubuntu(
                        profile=profile,
                        os=os_version(imagetype),
                        region=rgn,
                        detailed=details,
                        debug=debug
                    )

        elif imagetype.startswith('windows'):
            latest = windows(
                        profile=profile,
                        os=os_version(imagetype),
                        region=rgn,
                        detailed=details,
                        debug=debug
                    )

        # return appropriate response format
        if format == 'json' and not filename:
            if is_tty():
                r = export_json_object(dict_obj=latest, logging=False)
            else:
                print(json.dumps(latest, indent=4))
                return True

        elif format == 'json' and filename:
            r = export_json_object(dict_obj=latest, filename=filename)

        elif format == 'text' and not filename:
            print(format_text(latest))
            return True

        elif format == 'text' and filename:
            r = write_to_file(text=format_text(latest, filename), file=filename)

    except Exception as e:
        logger.exception(
            '%s: Unknown problem retrieving data from AWS (%s)' %
            (inspect.stack()[0][3], str(e)))
        return False
    return r


def options(parser, help_menu=False):
    """
    Summary:
        parse cli parameter options
    Returns:
        TYPE: argparse object, parser argument set
    """
    parser.add_argument("-p", "--profile", nargs='?', default="default", required=False, help="type (default: %(default)s)")
    parser.add_argument("-i", "--image", nargs='?', type=str, choices=VALID_AMI_TYPES, required=False)
    parser.add_argument("-d", "--details", dest='details', default=False, action='store_true', required=False)
    parser.add_argument("-r", "--region", nargs='?', type=str, required=False)
    parser.add_argument("-f", "--format", nargs='?', default='json', type=str, choices=VALID_FORMATS, required=False)
    parser.add_argument("-n", "--filename", nargs='?', default='', type=str, required=False)
    parser.add_argument("-D", "--debug", dest='debug', default=False, action='store_true', required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    parser.add_argument("-h", "--help", dest='help', action='store_true', required=False)
    return parser.parse_args()


def newest_ami(image_list):
    """
    Summary:
        Returns metadata for the most recent amazon machine image returned
        for a region from boto3
    """
    if image_list:
        return sorted(image_list, key=lambda k: k['CreationDate'])[-1]
    return {}


def package_version():
    """
    Prints package version and requisite PACKAGE info
    """
    print(about.about_object)
    sys.exit(exit_codes['EX_OK']['Code'])


def unwrap_dict(doc):
    def unwrap_results(doc, name=None):
        out = []
        if 'someKey' in doc:
            return [name, doc['test-case']] if isinstance(doc['test-case'], list) else [name, [doc['test-case']]]
        if isinstance(doc, list):
            out.extend(itertools.chain(*[unwrap_results(x, name) for x in doc]))
        elif isinstance(doc, dict):
            out.extend(itertools.chain(*[unwrap_results(x, name) for x in doc.values()]))
        return out

    result = unwrap_results(doc)
    return OrderedDict(zip(result[::2], result[1::2]))


def write_to_file(text, file):
    """ Writes text object to the local filesystem """
    try:
        with open(file, 'w') as f1:
            f1.write(text)
    except OSError as e:
        logger.exception(
            '%s: Problem writing %s to local filesystem' %
            (inspect.stack()[0][3], file))
        return False
    return True


def init_cli():
    """ Collect parameters and call main """
    try:
        parser = argparse.ArgumentParser(add_help=False)
        args = options(parser)
    except Exception as e:
        help_menu()
        stdout_message(str(e), 'ERROR')
        sys.exit(exit_codes['E_MISC']['Code'])

    if args.debug:
        stdout_message(message='profile is: %s' % args.profile, prefix='DBUG', severity='WARNING')
        stdout_message(message='image type: %s' % args.image, prefix='DBUG', severity='WARNING')
        stdout_message(message='format: %s' % args.format, prefix='DBUG', severity='WARNING')
        stdout_message(message='filename: %s' % args.filename, prefix='DBUG', severity='WARNING')
        stdout_message(message='debug flag: %s' % str(args.debug), prefix='DBUG', severity='WARNING')

    if len(sys.argv) == 1:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.help:
        help_menu()

    elif args.version:
        package_version()

    elif authenticated(profile=args.profile):
        # execute ami operation
        if args.image and args.region:
            if args.region in get_regions(args.profile):
                main(
                        profile=args.profile, imagetype=args.image,
                        format=args.format, filename=args.filename,
                        rgn=args.region, details=args.details, debug=args.debug
                    )
            else:
                stdout_message(
                        'Invalid AWS region code %s. Region must be one of:' %
                        (Colors.RED + args.region + Colors.RESET),
                        prefix='WARN',
                        severity='WARNING'
                    )
                for region in get_regions(args.profile):
                    print('\t\t' + region)
                print('\n')
                sys.exit(exit_codes['E_BADARG']['Code'])

        elif args.image and not args.region:
            main(
                    profile=args.profile, imagetype=args.image,
                    format=args.format, filename=args.filename,
                    details=args.details, debug=args.debug
                )
        else:
            stdout_message(
                    f'Image type must be one of: {VALID_AMI_TYPES}',
                    prefix='INFO'
                )
            sys.exit(exit_codes['E_DEPENDENCY']['Code'])
    else:
        stdout_message(
            'Authenication Failed to AWS Account for user %s' % args.profile,
            prefix='AUTH',
            severity='WARNING'
            )
        sys.exit(exit_codes['E_AUTHFAIL']['Code'])

    failure = """ : Check of runtime parameters failed for unknown reason.
    Please ensure local awscli is configured. Then run keyconfig to
    configure keyup runtime parameters.   Exiting. Code: """
    logger.warning(failure + 'Exit. Code: %s' % sys.exit(exit_codes['E_MISC']['Code']))
    print(failure)
