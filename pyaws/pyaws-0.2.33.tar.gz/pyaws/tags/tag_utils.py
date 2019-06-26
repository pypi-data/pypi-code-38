"""
pyaws.tags:  Tag Utilities
"""
import json
import inspect
from pygments import highlight, lexers, formatters
from functools import reduce
import boto3
from botocore.exceptions import ClientError
from pyaws.session import authenticated, boto3_session
from pyaws import logger
from pyaws import __version__

try:
    from pyaws.core.oscodes_unix import exit_codes
except Exception:
    from pyaws.core.oscodes_win import exit_codes    # non-specific os-safe codes


def create_taglist(dict):
    """
    Summary:
        Transforms tag dictionary back into a properly formatted tag list
    Returns:
        tags, TYPE: list
    """
    tags = []
    for k, v in dict.items():
        temp = {}
        temp['Key'] = k
        temp['Value'] = v
        tags.append(temp)
    return tags


def create_tagdict(tags):
    """
    Summary.
        Converts tag list to tag dict
    Args:
        :tags (list): k,v
         pair
        {
            [
                'Key': k1,
                'Value': v1
            ]
        }
    Returns:
        :tags (dict): {k1: v1, k2: v2}
        
    """
    return {x['Key']: x['Value'] for x in tags}


def delete_tags(resourceIds, region, tags):
    """ Removes tags from an EC2 resource """
    client = boto3_session('ec2', region)
    try:
        for resourceid in resourceIds:
            response = client.delete_tags(
                Resources=[resourceid],
                Tags=tags
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                logger.info('Existing Tags deleted from vol id %s' % resourceid)
                return True
            else:
                logger.warning('Problem deleting existing tags from vol id %s' % resourceid)
                return False
    except ClientError as e:
        logger.critical(
            "%s: Problem apply tags to ec2 instances (Code: %s Message: %s)" %
            (inspect.stack()[0][3], e.response['Error']['Code'], e.response['Error']['Message']))
        return False


def divide_tags(tag_list, *args):
    """
    Summary:
        Identifys a specific tag in tag_list by Key.  When found,
        creates a new tag list containing tags with keys provided in *args.
        tag_list is returned without matching tags
    Args:
        tag_list (list): tag list starting reference
        matching (list): tags which have keys matching any of *args
        residual (list): tag_list after any matching tags are removed
    RETURNS
        TYPE: matching tag list, residual tag list
    """
    matching = []
    residual = {x['Key']: x['Value'] for x in tag_list.copy()}
    tag_dict = {x['Key']: x['Value'] for x in tag_list}
    for key in args:
        for k,v in tag_dict.items():
            try:
                if key == k:
                    matching.append({'Key': k, 'Value': v})
                else:
                    residual.pop(key)
            except KeyError:
                continue
    return matching, [{'Key': k, 'Value': v} for k,v in residual.items()]


def exclude_tags(tag_list, *args):
    """
        - Filters a tag set by Exclusion
        - variable tag keys given as parameters, tag keys corresponding to args
          are excluded

    RETURNS
        TYPE: list
    """
    clean = tag_list.copy()

    for tag in tag_list:
        for arg in args:
            if arg == tag['Key']:
                clean.remove(tag)
    return clean


def extract_tag(tag_list, key):
    """
    Summary:
        Search tag list for prescence of tag matching key parameter
    Returns:
        tag, TYPE: list
    """
    if {x['Key']: x['Value'] for x in tag_list}.get(key):
        return list(filter(lambda x: x['Key'] == key, tag_list))[0]
    return []


def include_tags(tag_list, *args):
    """
        - Filters a tag set by Inclusion
        - variable tag keys given as parameters, tag keys corresponding to args
          are excluded

    RETURNS
        TYPE: list
    """
    targets = []

    for tag in tag_list:
        for arg in args:
            if arg == tag['Key']:
                targets.append(tag)
    return targets


def filter_tags(tag_list, *args):
    """DEPRECATED
        - Filters a tag set by exclusion
        - variable tag keys given as parameters, tag keys corresponding to args
          are excluded

    RETURNS
        TYPE: list
    """
    clean = tag_list.copy()

    for tag in tag_list:
        for arg in args:
            if arg == tag['Key']:
                clean.remove(tag)
    return clean


def json_tags(resource_list, tag_list, mode=''):
    """
        - Prints tag keys, values applied to resources
        - output: cloudwatch logs
        - mode:  INFO, DBUG, or UNKN (unknown or not provided)
    """
    if mode == 0:
        mode_text = 'DBUG'
    else:
        mode_text = 'INFO'

    try:
        for resource in resource_list:
            if mode == 0:
                logger.debug('DBUGMODE enabled - Print tags found on resource %s:' % str(resource))
            else:
                logger.info('Tags found resource %s:' % str(resource))
            print(json.dumps(tag_list, indent=4, sort_keys=True))
    except Exception as e:
        logger.critical(
            "%s: problem printing tag keys or values to cw logs: %s" %
            (inspect.stack()[0][3], str(e)))
        return False
    return True


def pretty_print_tags(tag_list):
    """ prints json tags with syntax highlighting """
    json_str = json.dumps(tag_list, indent=4, sort_keys=True)
    print(highlight(
        json_str, lexers.JsonLexer(), formatters.TerminalFormatter()
        ))
    print('\n')
    return True


def print_tags(resource_list, tag_list, mode=''):
    """
        - Prints tag keys, values applied to resources
        - output: cloudwatch logs
        - mode:  INFO, DBUG, or UNKN (unknown or not provided)
    """
    if mode == 0:
        mode_text = 'DBUG'
    else:
        mode_text = 'INFO'

    try:
        for resource in resource_list:
            logger.info('Tags successfully applied to resource: ' + str(resource))
            ct = 0
            for t in tag_list:
                logger.info('tag' + str(ct) + ': ' + str(t['Key']) + ' : ' + str(t['Value']))
                ct += 1
        if mode == 0:
            logger.debug('DBUGMODE = True, No tags applied')

    except Exception as e:
        logger.critical(
            "%s: problem printing tag keys or values to cw logs: %s" %
            (inspect.stack()[0][3], str(e)))
        return 1
    return 0


def remove_duplicates(alist):
    """
    Removes duplicate dict in a list of dict by enforcing unique keys
    """

    clean_list, key_list = [], []

    try:
        for dict in alist:
            if dict['Key'] not in key_list:
                clean_list.append(dict)
                key_list.append(dict['Key'])
    except KeyError:
        # dedup list of items, not dict
        return list(reduce(lambda r, x: r + [x] if x not in r else r, alist, []))
    except Exception as e:
        raise e
    return clean_list


def remove_restricted(list):
    """
    Remove restricted (system) Amazon tags from list of tags
    """

    clean_list = []

    try:
        for dict in list:
            if 'aws' not in dict['Key']:
                clean_list.append(dict)
    except Exception:
        return -1
    return clean_list


def remove_bykeys(tag_list, *keys):
    """
    Summary:
        Removes tags from a tag list for specified keys
    Returns:
        tags (list)
    """
    tag_dict = {x['Key']: x['Value'] for x in tag_list}
    for key in keys:
        if key in tag_dict:
            tag_dict.pop(key)
    return [{'Key': k, 'Value': v} for k,v in tag_dict.items()]


def select_tags(tag_list, key_list):
    """
    Return selected tags from a list of many tags given a tag key
    """
    select_list = []
    # select tags by keys in key_list
    for tag in tag_list:
        for key in key_list:
            if key == tag['Key']:
                select_list.append(tag)
    # ensure only tag-appropriate k,v pairs in list
    clean = [{'Key': x['Key'], 'Value': x['Value']} for x in select_list]
    return clean


def valid_tags(tag_list, invalid):
    """
    Summary:
        checks tags for invalid chars
    Args:
        tag_list (list): starting list of tags
        invalid (list): list of illegal characters that should not be present in keys in tag_list
    Returns:
        Success | Failure, TYPE: bool
    """
    for tag in tag_list:
        for char in invalid:
            if char in tag['Key']:
                return False
    return True
