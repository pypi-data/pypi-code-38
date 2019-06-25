"""Jira class file."""

# import base64
import csv
import datetime
# import json
import requests

from jira.client import JIRA


class Jira(object):
    """Jira class."""

    def __init__(
        self,
        username,
        password,
        server='https://company.atlassian.net',
        verbose=False,
    ):
        """Initialize a JIRA class instance."""
        self.jira_server = server
        self.jira_username = username
        self.jira_password = password

        self.verbose = verbose

        self.base_url = self.jira_server
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        # authenticate
        if username and password:
            if self.verbose:
                print('Connecting to JIRA v3...')
            self.connect_v3()

    def connect_v3(self):
        """Connect to JIRA."""
        self.auth = (self.jira_username, self.jira_password)

    #
    # Group Members
    #
    def get_group_members(self, group, includeInactiveUsers=False):
        """Return a list of members in a group."""
        url = '%s/rest/api/3/group/member' % (self.base_url)
        params = {
            'groupname': group,
            'includeInactiveUsers': includeInactiveUsers,
            'maxResults': 1000,
        }
        response = requests.get(url, auth=self.auth, params=params).json()
        members = response.get('values', [])

        while not response['isLast']:
            nextPage = response['nextPage']
            response = requests.get(nextPage, auth=self.auth).json()
            members.extend(response.get('values', []))

        return members

    def get_group_members_dict(self, group, includeInactiveUsers=False):
        """Return a list of emails of members in a group."""
        members = self.get_group_members(group, includeInactiveUsers)
        emails = {}
        for m in members:
            email = m['emailAddress']
            emails[email] = m
        return emails

    #
    # Groups
    #
    def get_groups(self):
        """Return a list of JIRA Group names."""
        url = '%s/rest/api/3/groups/picker' % (self.base_url)
        params = {
            'maxResults': 1000,
        }
        response = requests.get(url, auth=self.auth, params=params).json()
        groups = response['groups']
        total = response['total']
        if len(groups) < total:
            print('WARNING: %s' % (response['header']))
        return groups

    def get_groups_dict(self):
        """Return a dict of JIRA Groups."""
        groups = {}
        for group in self.get_groups():
            name = group['name']
            groups[name] = group
        return groups

    def get_groups_with_members(self):
        """Return na list of JIRA Groups."""
        groups_dict = self.get_groups_dict()
        for name in groups_dict:
            group = groups_dict[name]
            members = self.get_group_members(name)
            group['members'] = members
            yield group

    #
    # Update Groups
    #
    def add_user_to_group(self, accountId, groupname):
        """Add a user to a JIRA Group."""
        url = '%s/rest/api/3/group/user' % (self.base_url)
        body = {
            'accountId': accountId,
        }
        params = {
            'groupname': groupname,
        }
        return requests.post(url, auth=self.auth, json=body, params=params)

    def remove_user_from_group(self, accountId, groupname):
        """Remove a user from a JIRA Group."""
        url = '%s/rest/api/3/group/user' % (self.base_url)
        params = {
            'accountId': accountId,
            'groupname': groupname,
        }
        return requests.delete(url, auth=self.auth, params=params)

    def get_members_to_add(self, current, members):
        """Return a list of members to add to a group."""
        add = []
        for email in members:
            if email not in current:
                users = self.get_users(email)
                if len(users) == 1:
                    add.append(users[0])
        return add

    def get_members_to_remove(self, current, members):
        """Return a list of members to remove from a group."""
        remove = []
        for email in current:
            if email not in members:
                remove.append(current[email])
        return remove

    def update_group_members(self, group, google_members):
        """Update the members of a group to match provided members list."""
        current = self.get_group_members_dict(group)
        add = self.get_members_to_add(current, google_members)
        remove = self.get_members_to_remove(current, google_members)

        if add:
            print('    Adding members:')
            for user in sorted(add, key=lambda x: x['emailAddress']):
                accountId = user['accountId']
                print('      + %s' % (user['emailAddress']))
                self.add_user_to_group(accountId, group)

        if remove:
            print('    Removing members:')
            for user in sorted(remove, key=lambda x: x['emailAddress']):
                accountId = user['accountId']
                print('      - %s' % (user['emailAddress']))
                self.remove_user_from_group(accountId, group)

    def _get_google_group_member_emails(self, members, users):
        """Return a list of emails for Google Group Members."""
        emails = []
        for m in members:
            uid = m['id']
            email = m['email']
            if uid not in users:
                print('ERROR: Google User not found: %s [%s]' % (email, uid))
                continue
            user = users[uid]
            email = user['primaryEmail']
            emails.append(email)
        return emails

    def update_groups(self, auth, groups):
        """Update JIRA Groups."""
        g = auth.google()
        g.auth_service_account(g.scopes, g.subject)

        # get Google Users
        if auth.verbose:
            print('Getting Google Users...')
        fields = 'nextPageToken,users(id,primaryEmail,name/fullName)'
        users = g.directory().get_users_dict(fields=fields)
        if auth.verbose:
            print('Found %s Google Users' % (len(users)))

        # process all group updates
        for group in sorted(groups, key=lambda x: x.lower()):
            email = groups[group]

            # get google group members emails
            google_members = self._get_google_group_member_emails(
                g.directory().get_derived_members(email),
                users
            )

            print('Updating Group: %s [%s]' % (group, email))
            self.update_group_members(group, google_members)

    #
    # Projects
    #
    def get_projects(self):
        """Return a list of JIRA Group projects."""
        maxResults = 1000
        params = {'maxResults': maxResults}
        url = '%s/rest/api/3/project/search' % (self.base_url)

        projects = []

        response = requests.get(url, auth=self.auth, params=params)
        results = response.json()
        projects.extend(results.get('values', []))

        while len(results) == maxResults:
            params['startAt'] = len(projects)
            response = requests.get(url, auth=self.auth, params=params)
            results = response.json()
            projects.extend(results.get('values', []))

        return projects

    def get_projects_dict(self):
        """Return a dict of JIRA Group projects."""
        projects = {}
        for p in self.get_projects():
            projects[p.key] = p.raw
        return projects

    #
    # Users
    #
    def get_user(self, accountId, applicationRoles=False, groups=False):
        """Return a JIRA user."""
        url = '%s/rest/api/3/user' % (self.base_url)

        expand = []
        if applicationRoles:
            expand.append('applicationRoles')
        if groups:
            expand.append('groups')

        params = {
            'accountId': accountId,
            'expand': ','.join(expand),
        }

        return requests.get(url, auth=self.auth, params=params).json()

    def get_users(
        self,
        # query='',
        # accountId=None,
        startAt=0,
        maxResults=1000,
        # includeActive=True,
        # includeInactive=False,
    ):
        """Return a list of all users."""
        url = '%s/rest/api/3/users/search' % (self.base_url)

        params = {
            # 'query': query,
            # 'accountId': accountId,
            'startAt': startAt,
            'maxResults': maxResults,
            # 'includeActive': includeActive,
            # 'includeInactive': includeInactive,
        }

        users = []

        response = requests.get(url, auth=self.auth, params=params)
        results = response.json()
        users.extend(results)

        while len(results) == maxResults:
            params['startAt'] = len(users)
            response = requests.get(url, auth=self.auth, params=params)
            results = response.json()
            users.extend(results)

        return users

    def get_users_csv(
        self,
        auth,
        bucket='broad-jira-users',
        filename='export-users.csv',
    ):
        """Return a list of account dictionaries from a CSV file."""
        g = auth.google()
        g.auth_service_account(g.scopes)
        media = g.storage().get_object_media(bucket, filename)
        lines = media.getvalue().decode().split('\n')

        users = []
        for user in list(csv.DictReader(lines)):
            user = dict(user)

            # accountId
            user['accountId'] = user['id']
            del user['id']

            # active, Confluence, Jira Software
            for key in ['active', 'Confluence', 'Jira Software']:
                if user[key] == 'Yes':
                    user[key] = True
                else:
                    user[key] = False

            # created
            if 'Before' in user['created']:
                user['created'] = user['created'].replace('Before ', '')
            created = datetime.datetime.strptime(user['created'], '%d %b %Y')
            user['created'] = str(created.date())

            # emailAddress
            user['emailAddress'] = user['email']
            del user['email']

            # full_name
            user['displayName'] = user['full_name']
            del user['full_name']

            # last active dates
            for key in [
                "Last active in Confluence",
                "Last active in Jira",
                "Last active in Opsgenie",
                "Last active in Statuspage",
                "Last active in Stride",
            ]:
                if 'Never logged in' in user[key]:
                    user[key] = None
                elif 'Not active in the last 180 days':
                    user[key] = '1 Jan 1970'
                elif 'Before' in user[key]:
                    user[key] = user[key].replace('Before ', '')
                if user[key]:
                    time = datetime.datetime.strptime(user[key], '%d %b %Y')
                    user[key] = str(time.date())

            users.append(user)

        return users

    def get_users_csv_dict(
        self,
        auth,
        bucket='broad-jira-users',
        filename='export-users.csv',
    ):
        """Return a dict of account dictionaries from a CSV file."""
        users = {}
        for user in self.get_users_csv(auth, bucket, filename):
            uid = user['accountId']
            users[uid] = user
        return users

    def get_users_dict(
        self,
        # query='',
        startAt=0,
        maxResults=1000,
        # includeActive=True,
        # includeInactive=False,
        key='emailAddress',
    ):
        """Return a list of all users."""
        all_users = self.get_users(
            # query,
            startAt=startAt,
            maxResults=maxResults,
            # includeActive=includeActive,
            # includeInactive=includeInactive
        )

        # convert to dict
        users = {}
        for u in all_users:
            k = u[key]
            users[k] = u
        return users
