# coding:utf-8

from atlassian import Jira
from var import config
import logging
import pprint

ATLASSIAN_USER = config.CONFLUENCE_LOGIN
ATLASSIAN_PASSWORD = config.CONFLUENCE_PASSWORD

# logging.basicConfig(level=logging.ERROR)

ul_jira = Jira(
    url="http://jira.ullink.lan",
    username=ATLASSIAN_USER,
    password=ATLASSIAN_PASSWORD)

orc_jira = Jira(
    url="https://jira.orcsoftware.com",
    username=ATLASSIAN_USER,
    password=ATLASSIAN_PASSWORD)


def group_members_stabilisation():
    ul_groups = ul_jira.get_groups(limit=1100).get('groups')

    for group_name in ul_groups:
        group_name = group_name['name']
        print("Start review {}".format(group_name))
        members = get_all_user_from_group(jira=ul_jira, group_name=group_name)
        for member in members:
            username = member.get('key')
            orc_jira.add_user_to_group(username=username, group_name=group_name)


def get_all_user_from_group(jira, group_name):
    limit = 50
    step = 0
    flag = True
    values = []
    while flag:
        groups_members_json = jira.get_all_users_from_group(group=group_name, limit=limit, start=step * limit)
        step += 1
        values += groups_members_json.get('values')
        if len(groups_members_json) == 0 or groups_members_json.get('isLast'):
            flag = False
    return values


def role_stabilization():
    roles = orc_jira.get_all_global_project_roles()
    project_key = 'APP'
    for role in roles:
        role_id = role.get('id')
        values = orc_jira.get_project_actors_for_role_project(project_key, role_id=role_id)
        if len(values) == 0:
            continue
        for role_actor in values:
            if role_actor.get('type') == 'atlassian-group-role-actor':
                if role_actor.get('name') == 'ullink-users':
                    print(role_actor)


def compare_memebership(groupname_1, groupname_2):
    groupname_1_members = []
    groupname_2_members = []
    members = get_all_user_from_group(jira=orc_jira, group_name=groupname_1)
    for member in members:
        username = member.get('key')
        groupname_1_members.append(username)
    members = get_all_user_from_group(jira=orc_jira, group_name=groupname_2)
    for member in members:
        username = member.get('key')
        groupname_2_members.append(username)

    for member in groupname_1_members:
        if member not in groupname_2_members:
            print(member)
            orc_jira.add_user_to_group(member, groupname_2)


def agile_board_iterator():
    pprint.pprint(orc_jira.get_all_agile_boards())


if __name__ == '__main__':
    agile_board_iterator()
    # group_members_stabilisation()
    # compare_memebership("ullink-product", "engineering")
