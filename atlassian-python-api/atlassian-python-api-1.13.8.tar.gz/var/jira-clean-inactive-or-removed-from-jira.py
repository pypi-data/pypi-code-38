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
roles = jira.get_all_global_project_roles()
for role in roles:
    role_ids.append(role.get('id'))

projects = jira.get_all_projects(included_archived=True)

for project in projects:
    project_key = project.get('key')
    print('Start review project {}'.format(project_key))
    for role_id in role_ids:
        actors = jira.get_project_actors_for_role_project(project_key, role_id)
        for actor in actors:
            if actor['type'] == 'atlassian-user-role-actor':
                username = actor['name']
                if username is None:
                    continue
                answer = jira.user(username)
                if answer.get('errorMessages') or (not answer.get('active')):
                    print('Removing from project permissions {}'.format(username))
                    jira.delete_project_actors(project_key, role_id=role_id, actor=username, actor_type='user')

# delete inactive users
# jira.delete_project_actors('ENG', role_id='10241', actor='ekaterinas', actor_type='user')
