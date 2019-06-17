#!/usr/bin/env python
"""
Scripts to get specific values for AWS Organization Units
"""

import boto3


def get_root():
    """
    Returns:
        the root account Info. There is only one value possible
    """
    client = boto3.client('organizations')
    return client.list_roots()['Roots'][0]


def get_ou_by_name(ou_name, parent_id):
    """
    Args:
        ou_name: name of the OU
        parent_id: Id of the parent for that OU
    Returns:
        Tuple(Bool, Dict) bool to determined if the call worked
    """
    client = boto3.client('organizations')
    res = client.list_organizational_units_for_parent(
        ParentId=parent_id
    )
    for ou_info in res['OrganizationalUnits']:
        if ou_info['Name'] == ou_name:
            return ou_info
    return None


def lookup_org_by_id(org_id):
    """
    Args:
        org_id: OU Id
    Returns:
        Dict() with the info of the OU
    """
    client = boto3.client('organizations')
    return client.describe_organizational_unit(OrganizationalUnitId=org_id)['OrganizationalUnit']


def get_all_accounts_in_ou_and_sub(parent_id, ous_list=None, accounts_list=None):
    """
    Args:
        parent_id: ID of the parent to lookup from
        accounts_list: only used for recursion
        next_token: only used for recursion
    Returns:
        accounts_list: list() of all the accounts in the OU and Sub OUs
    """
    if accounts_list is None:
        accounts_list = []
    if ous_list is None:
        ous_list = []
    accounts_list += get_ou_accounts(parent_id)
    ous_list += get_ou_sub_ous(parent_id)
    if ous_list:
        item = ous_list[0]
        ous_list.pop(0)
        return get_all_accounts_in_ou_and_sub(item['Id'], ous_list, accounts_list)
    return accounts_list


def find_org_in_tree(ou_path, parent_ou=None, separator='/'):
    """
    Args:
        ou_path: full path to the ou using
    Returns:
        dictionary containing Id, Name and Arn of the OU
    Raises:
        ValueError() in case nothing was found
    """
    if not ou_path.startswith('/') and parent_ou is None:
        ou_path = '/' + ou_path
    client = boto3.client('organizations')
    if ((ou_path.find(separator) < 0 and parent_ou is None) or
        ou_path == '/root' or
        ou_path == separator):
        return get_root()

    if (ou_path.find(separator) >= 0 and
        ou_path.startswith(separator) and
        parent_ou is None):
        child = ou_path.split(separator, 1)[-1]
        parent_ou = get_root()
        return find_org_in_tree(child, parent_ou)

    if ou_path.find(separator) > 0 and parent_ou is not None:
        new_parent = ou_path.split(separator, 1)[0]
        new_child = ou_path.split(separator, 1)[-1]
        children = client.list_children(
            ParentId=parent_ou['Id'],
            ChildType='ORGANIZATIONAL_UNIT'
        )['Children']

        for child in children:
            the_ou = None
            ou_info = lookup_org_by_id(child['Id'])
            if new_parent == ou_info['Name']:
                return find_org_in_tree(new_child, ou_info)

    if ou_path.find(separator) < 0 and parent_ou is not None:
        children = client.list_children(
            ParentId=parent_ou['Id'],
            ChildType='ORGANIZATIONAL_UNIT'
        )['Children']
        for child in children:
            ou_info = lookup_org_by_id(child['Id'])
            if ou_path == ou_info['Name']:
                return ou_info
    raise ValueError(f'Could not find the ou {ou_path}')


def get_ou_sub_ous(parent_id, ous_list=None, next_token=None):
    """
    Args:
        parent_id: ID of the parent to lookup from
        accounts_list: only used for recursion
        next_token: only used for recursion
    Returns:
        accounts_list: list() of all the accounts in the OU and Sub OUs
    """
    client = boto3.client('organizations')
    if ous_list is None:
        ous_list = []
    if isinstance(next_token, str):
        ous_r = client.list_children(
            ParentId=parent_id, ChildType="ORGANIZATIONAL_UNIT", NextToken=next_token
        )
    else:
        ous_r = client.list_children(
            ParentId=parent_id, ChildType="ORGANIZATIONAL_UNIT")
    for ou_child in ous_r['Children']:
        ous_list.append(ou_child)
    if 'NextToken' in ous_r.keys():
        return get_ou_sub_ous(parent_id, ous_list, next_token)
    return ous_list


def get_ou_accounts(parent_id, accounts_list=None, next_token=None):
    """
    Args:
        parent_id: string that represents the Id of the parent OU
        accounts_list: list of accounts from a previous call due to the recursive
        next_token: the token for the call in case a recursive occurs
    Returns:
        list of dict() with the information of the accounts in the OU
    """
    if accounts_list is None:
        accounts_list = []
    client = boto3.client('organizations')
    if isinstance(next_token, str):
        res = client.list_accounts_for_parent(
            ParentId=parent_id,
            NextToken=next_token
        )
    else:
        res = client.list_accounts_for_parent(
            ParentId=parent_id,
        )
    accounts_list += res['Accounts']
    if 'NextToken' in res.keys():
        return get_ou_accounts(parent_id, accounts_list, res['NextToken'])
    return accounts_list


def get_ou_accounts_by_ou_name(ou_name, accounts_list=None, parent=None):
    """
    Returns the account of an OU by itsname
    Args:
        ou_name: name of the OU
        accounts_list: list of accounts from a previous call due to the recursive
        next_token: the token for the call in case a recursive occurs
    Returns:
        list of dict() with the information of the accounts in the OU
    """
    if accounts_list is None:
        accounts_list = []
    if parent is None:
        parent = get_root()['Id']
    try:
        ou_info = get_ou_by_name(ou_name, parent)
        parent = ou_info['Id']
    except:
        raise ValueError(f'Failed to retrieve the organization unit of name {ou_name}')

    return get_ou_accounts(parent)


if __name__ == '__main__':
    SEARCH_OU = 'platform'
    OUS = get_all_accounts_in_ou_and_sub(find_org_in_tree('productone/prod')['Id'])
    for acct in OUS:
        print(acct['Name'])
