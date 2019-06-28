# coding: utf8
import config
from atlassian import Jira
from pprint import pprint
import logging

logging.basicConfig(level=logging.ERROR)

""" Login part"""

jira = Jira(
    url=config.JIRA_URL,
    username=config.ATLASSIAN_LOGIN,
    password=config.ATLASSIAN_PASSWORD)


def check_and_into_role(project_key, role_id):
    result = jira.get_project_actors_for_role_project(project_key, role_id)
    if result is None:
        return
    if len(result) == 0:
        return
    entrance = False
    ullink_group = False
    for i in result:
        if i['name'] == 'itiviti' and i['type'] == 'atlassian-group-role-actor':
            entrance = True
        if i['name'] == 'ullink' and i['type'] == 'atlassian-group-role-actor':
            ullink_group = True
    if not entrance and ullink_group:
        pprint(jira.add_project_actor_in_role(project_key, role_id, 'itiviti', 'atlassian-group-role-actor'))


def check_and_into_role_it(project_key, role_id):
    result = jira.get_project_actors_for_role_project(project_key, role_id)
    if result is None:
        return
    if len(result) == 0:
        return
    entrance = False
    itiviti_group = False
    for i in result:
        if i['name'] == 'jira-users' and i['type'] == 'atlassian-group-role-actor':
            itiviti_group = True
        if i['name'] == 'ullink' and i['type'] == 'atlassian-group-role-actor':
            entrance = True
    if not entrance and itiviti_group:
        jira.add_project_actor_in_role(project_key, role_id, 'itiviti', 'atlassian-group-role-actor')
        jira.add_project_actor_in_role(project_key, role_id, 'ullink', 'atlassian-group-role-actor')


all_projects = jira.get_all_projects()
print(all_projects)
"""
for project in all_projects:
    check_and_into_role(project.get('key'), 10744)
    check_and_into_role(project.get('key'), 10743)
    check_and_into_role_it(project.get('key'), 10001)
"""