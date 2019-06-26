#!/usr/bin/env python

import sys
import json
import argparse
import boto3

# -- functions  ----------------------------------------------------------------


def get_regions():
    """Summary

    Returns:
        TYPE: Description
    """
    client = boto3.client('ec2')
    region_response = client.describe_regions()
    regions = [region['RegionName'] for region in region_response['Regions']]
    return regions


def remove_tags(id_list, tag_list):
    """
    Deletes tags on resource ids provided as parameter
    """
    pass


def clean_list(list):
    """ cleans a list of all extraneous characters """
    clean_list = []
    try:
        for element in list:
            clean_list.append(element.strip())
    except Exception:
        return -1
    return clean_list


def remove_duplicates(list):
    """
    Removes duplicate dict in a list of dict by enforcing unique keys
    """

    clean_list, key_list = [], []

    try:
        for dict in list:
            if dict['Key'] not in key_list:
                clean_list.append(dict)
                key_list.append(dict['Key'])

    except KeyError:
        # dedup list of items, not dict
        for item in list:
            if clean_list:
                if item not in clean_list:
                    clean_list.append(item)
            else:
                clean_list.append(item)
        return clean_list
    except Exception:
        return -1
    return clean_list


def remove_restricted(list):
    """
    Remove restricted Amazon tags from list of tags
    """

    clean_list = []

    try:
        for dict in list:
            if 'aws' not in dict['Key']:
                clean_list.append(dict)
    except Exception:
        return -1
    return clean_list


# -- MAIN ----------------------------------------------------------------------

# global vars
global DBUGMODE
global REGION
global PREFIX
PREFIX = 'gcreds-'      # temporary credential prefix in local awscli config
global PROFILE

# parse options setup
parser = argparse.ArgumentParser(description='Required parameters:')
parser.add_argument('-a','--accts', dest='file', action='store',
                    help='Profile name from local awscli config')
parser.add_argument('-c','--convert', action='store_true',
                    help='optional flag required to execute tag conversion')
args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(0)

if args.convert:
    DBUGMODE = False
else:
    DBUGMODE = True

try:
    fileobj1 = open(args.file)
    accounts = fileobj1.readlines()
    print("\nContents of accounts list: ")
    for acct in accounts:
        print(acct.strip())
    print("Length of accounts list: " + str(len(accounts)))

except IOError as e:
    print('File passed as parameter cannot be opened')
except Exception:
    print("Unexpected error:", sys.exc_info()[0])
    raise

# clean lists
accounts = clean_list(accounts)

# list iam users for each account
for PROFILE in accounts:
    #
    TMPPROFILE = PREFIX + PROFILE
    #
    regions = get_regions()
    change_record = []      # list to track number of resources for which config updated
    regions = ['eu-west-1']
    for region in regions:
        session = boto3.Session(profile_name=TMPPROFILE, region_name=region)
        #base = AWSEC2_resource(PROFILE, REGION)
        ec2 = session.resource('ec2')
        base = ec2.instances.all()
        # the following used if converting for one or more specific instances:
        #ids = ['i-bc816f59']
        #base = ec2.instances.filter(InstanceIds=ids)

        ct = 0
        for instance in base:
            ct += 1
        print('\n---------------------------------------------------------------------------------')
        print('\n ' + str(ct) + ' instances found for account [' + str(PROFILE) +
            '] in region [' + str(region) + ']\n')
        print('---------------------------------------------------------------------------------\n')

        for instance in base:
            # initialize tag lists
            delete_tags = []        # k,v pairs (tags) to be deleted
            tags = instance.tags    # k,v pairs (pre-conversion tags on instance)

            # calc columns
            col_width = 0
            for t in tags:
                tag_width = len(t['Key']) + 2
                if tag_width > col_width:
                    col_width = tag_width
            #print('col_width is: ' + str(col_width))
            col_width = 30

            print('\nEC2 INSTANCE ID [' + str(instance.id) + '] ----------------------------\n')
            print('\n\tExisting tag set:\n')
            tags.sort()
            for t in tags:
                s1 = 'Key: ' + str(t['Key'])
                s2 = 'Value: ' + str(t['Value'])
                # print in 2 columns
                print '{0:30}  {1}'.format(s1, s2)
            print('\n')

            # remove restricted tags before we attempt to convert and reapply
            tags = remove_restricted(tags)

            # convert tag keys
            for t in tags:
                if t.get('MPC-SN-NAME'):
                    delete_tags.append(t)
                    tags.remove(t)
                    #change_record.append(instance.id)

                elif 'CreationDate' in t['Key']:
                    d = t.copy()
                    delete_tags.append(d)
                    t['Key'] = 'MPC-AWS-CREATIONDATE'
                    #change_record.append(instance.id)

                elif 'BillGroup' in t['Key']:
                    d = t.copy()
                    delete_tags.append(d)
                    t['Key'] = 'MPC-AWS-BILLGROUP'
                    #change_record.append(instance.id)

                elif t['Key'] == 'TAG-BACKUP':
                    d = t.copy()
                    delete_tags.append(d)
                    t['Key'] = 'MPC-AWS-BACKUP'
                    #change_record.append(instance.id)

            # output results
            print('\n\tConverted tag set to be applied (aws* restricted tags omitted):\n')
            tags = remove_duplicates(tags)
            change_record = remove_duplicates(change_record)
            tags.sort()
            for t in tags:
                s1 = 'Key: ' + str(t['Key'])
                s2 = 'Value: ' + str(t['Value'])
                # print in 2 columns
                print '{0:30}  {1}'.format(s1, s2)
            print('\n')

            print('\n\tTags to be deleted:\n')
            delete_tags.sort()
            for t in delete_tags:
                s1 = 'Key: ' + str(t['Key'])
                s2 = 'Value: ' + str(t['Value'])
                # print in 2 columns
                print '{0:30}  {1}'.format(s1, s2)
            print('\n')

            if DBUGMODE == False:
                # apply new converted tags
                response_create = instance.create_tags(Tags=tags)
                print('\nresponse_create is:')
                print(str(response_create) + '\n')
                if delete_tags:
                    # WARNING: calling instance.delete_tags() with empty tag list
                    #          results in deletion of ALL pre-existing tags, must ensure
                    #          contains at least 1 tag before calling delete method
                    response_delete = instance.delete_tags(Tags=delete_tags)
                    print('\nresponse_delete is:')
                    print(str(response_delete) + '\n')

        if DBUGMODE == True:
            print('\n-------------------------------------')
            print(' Converted tags not applied. DBUGMODE')
            print('-------------------------------------\n')
        # footer
    print('\n---------------------------------------------------------------------------------')
    print('Summary:\nUpdated config for ' + str(len(change_record)) +
          ' resources in account ' + str(PROFILE))
    print('---------------------------------------------------------------------------------\n')
# <-- end -->
exit (0)
