from atlassian import Jira
from var import config
import logging
import pprint

ATLASSIAN_USER = config.JIRA_LOGIN
ATLASSIAN_PASSWORD = config.JIRA_PASSWORD

logging.basicConfig(level=logging.ERROR)

jira = Jira(
    url=config.JIRA_URL,
    username=ATLASSIAN_USER,
    password=ATLASSIAN_PASSWORD)

# pprint.pprint(jira.get_all_workflows())

# Ger all role ids from Jira
role_ids = []
role_id = 10001
roles = jira.get_all_global_project_roles()
for role in roles:
    if role.get('name') == 'ItivitiUser':
        role_id = role.get('id')


user_role_id = 10000
projects = jira.get_all_projects(included_archived=True)

for project in projects:
    project_key = project.get('key')

    actors = jira.get_project_actors_for_role_project(project_key, role_id)
    if len(actors) > 0:
        for actor in actors:
            if (project.get('projectCategory') or {}).get('name') in ['Archive']:
                if actor.get('type') == 'atlassian-group-role-actor':
                    jira.add_project_actor_in_role(project_key, role_id=str(user_role_id), actor=actor.get('name'), actor_type='group')
                    jira.delete_project_actors(project_key, role_id=role_id, actor=actor.get('name'), actor_type='group')
            else:
                print('Start review project {}'.format(project_key))
                print('\t' + actor.get('displayName') + '\t' + actor.get('type'))
"""
perms = jira.get_all_permissionschemes(expand='user')

for perm in perms:
    pprint.pprint(jira.get_permissionscheme(perm.get('id') , expand='projectRole'))
"""