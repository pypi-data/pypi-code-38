"""Google admin directory SDK."""

import re

from bits.google.services.base import Base
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession


class Directory(Base):
    """Directory class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.admin = build('admin', 'directory_v1', credentials=credentials)
        self.customer_id = 'C00q9u7iu'
        self.credentials = credentials

    #
    # Chrome Devices
    #
    def get_chromeosdevices(self):
        """Return list of domain chromeosdevices."""
        chromeosdevices = self.admin.chromeosdevices()
        request = chromeosdevices.list(customerId=self.customer_id)
        return self.get_list_items(chromeosdevices, request, 'chromeosdevices')

    def patch_chromeosdevice(self, deviceId, body):
        """Update a chromeosdevice."""
        params = {
            'customerId': self.customer_id,
            'deviceId': deviceId,
            'body': body,
        }
        return self.admin.chromeosdevices().patch(**params).execute()

    #
    # Customers
    #
    # def get_customer(self):

    #
    # Groups
    #
    def create_group(self, email, name, description=None):
        """Create a group."""
        body = {
            "name": name,
            "description": description,
            "email": email,
        }
        return self.admin.groups().insert(body=body).execute()

    def delete_group(self, groupKey):
        """Create a group."""
        return self.admin.groups().delete(groupKey=groupKey).execute()

    def get_group(self, email):
        """Add a group member."""
        return self.admin.groups().get(groupKey=email).execute()

    def get_groups(
            self,
            customer='my_customer',
            fields=None,
            userKey=None,
            verbose=False,
    ):
        """Return list of domain groups."""
        params = {
            'fields': fields
        }
        if not userKey:
            params['customer'] = customer
        else:
            params['domain'] = 'broadinstitute.org'
            params['userKey'] = userKey
        groups = self.admin.groups()
        request = groups.list(**params)
        return self.get_list_items(groups, request, 'groups')

    def get_groups_dict(
            self,
            customer='my_customer',
            userKey=None,
            key='email',
            verbose=False,
    ):
        """Return a dict of Google groups."""
        google_groups = self.get_groups(
            customer=customer,
            userKey=userKey,
            verbose=verbose,
        )
        groups = {}
        for g in google_groups:
            gid = g[key]
            groups[gid] = g
        return groups

    def get_user_groups(self, userKey):
        """Return a list of groups for a given user."""
        if not re.search('@', userKey):
            userKey = '%s@broadinstitute.org' % (userKey)

        # get user to retrieve primaryEmail
        user = self.get_user(userKey)
        primaryEmail = user['primaryEmail']

        # create qury
        query = 'memberkey=%s' % (primaryEmail)

        # return user groups
        return self.query_groups(query)

    def query_groups(self, query):
        """Return the results of a group query."""
        params = {
            'customer': self.customer_id,
            'query': query,
        }
        groups = self.admin.groups()
        request = groups.list(**params)
        return self.get_list_items(groups, request, 'groups')

    #
    # Members
    #
    def add_member(self, groupKey, email, role='MEMBER'):
        """Add a group member."""
        params = {
            'groupKey': groupKey,
            'body': {
                'email': email,
                'role': role,
            },
        }
        return self.admin.members().insert(**params).execute()

    def get_member(self, groupKey, memberKey):
        """Return a group member."""
        params = {
            'groupKey': groupKey,
            'memberKey': memberKey,
        }
        return self.admin.members().get(**params).execute()

    def get_members(self, groupKey):
        """Return list of group members."""
        members = self.admin.members()
        request = members.list(groupKey=groupKey)
        return self.get_list_items(members, request, 'members')

    def get_derived_members(self, groupKey):
        """Return the derived members of a group."""
        params = {
            'groupKey': groupKey,
            'includeDerivedMembership': 'true',
        }
        members = self.admin.members()
        request = members.list(**params)
        return self.get_list_items(members, request, 'members')

    def get_members_recursively(self, group):
        """Return a list of group members including subgroup members."""
        members = []
        group_members = self.get_members(group)
        for m in group_members:
            if m['type'] == 'GROUP':
                email = m['email']
                sub_members = self.get_members_recursively(email)
                members += sub_members
            else:
                members.append(m)
        return members

    def group_has_member(self, groupKey, memberKey):
        """Check if group has member."""
        params = {
            'groupKey': groupKey,
            'memberKey': memberKey,
        }
        return self.admin.members().hasMember(**params).execute().get('isMember')

    def remove_member(self, groupKey, memberKey):
        """Remove a group member."""
        params = {
            'groupKey': groupKey,
            'memberKey': memberKey,
        }
        return self.admin.members().delete(**params).execute()

    #
    # Organizational Units
    #
    def get_orgunits(self):
        """Return list of domain orgunits."""
        params = {
            'customerId': self.customer_id,
            'type': 'all',
        }
        orgunits_list = self.admin.orgunits().list(**params)
        return orgunits_list.execute().get('organizationUnits', [])

    #
    # Resource Calendars
    #
    def create_resource_calendar(self, customer, body):
        """Insert a calendar resource."""
        calendars = self.admin.resources().calendars()
        return calendars.insert(customer=customer, body=body).execute()

    def get_resource_calendar(self, customer, calendarId):
        """Insert a calendar resource."""
        calendars = self.admin.resources().calendars()
        return calendars.get(customer=customer, calendarResourceId=calendarId).execute()

    def get_resource_calendars(self, query=None):
        """Return list of domain calendars."""
        calendars = self.admin.resources().calendars()
        params = {
            'customer': 'my_customer',
            'query': query,
        }
        request = calendars.list(**params)
        return self.get_list_items(calendars, request, 'items')

    def get_resource_calendars_dict(self):
        """Return a dict of Google resource calendars."""
        google_resources = self.get_resource_calendars()
        resources = {}
        for r in google_resources:
            rid = r['resourceId']
            resources[rid] = r
        return resources

    #
    # Roles
    #
    def get_roles(self, customer='my_customer'):
        """Return a list of roles for the customer."""
        return self.admin.roles().list(customer=customer).execute().get('items', [])

    #
    # Role Assignments
    #
    def get_role_assignments(self, customer='my_customer'):
        """Return a list of role assignments for the customer."""
        return self.admin.roleAssignments().list(customer=customer).execute().get('items', [])

    #
    # tokens
    #
    def get_tokens(self, user):
        """Get all tokens for a user."""
        return self.admin.tokens().list(userKey=user).execute().get('items', [])

    #
    # users
    #
    def change_password(
            self,
            userKey,
            password,
            hashFunction,
            ):
        """Change a user's password."""
        try:
            user = self.get_user(userKey)
        except Exception:
            return
        if not user:
            print('ERROR: No such user: %s' % (userKey))
            return
        user['password'] = password
        user['hashFunction'] = hashFunction
        params = {
            'userKey': userKey,
            'body': user,
        }
        return self.admin.users().update(**params).execute()

    def create_user(self, body):
        """Create a user."""
        return self.admin.users().insert(body=body).execute()

    def delete_user(self, userKey):
        """Create a user."""
        return self.admin.users().delete(userKey=userKey).execute()

    def get_user(self, user, fields=None):
        """Return a user."""
        params = {
            'userKey': user,
            'fields': fields,
        }
        return self.admin.users().get(**params).execute()

    def get_users(
            self,
            fields=None,
            projection='basic',
            query=None,
            verbose=False
    ):
        """Return list of domain users."""
        params = {
            'customer': 'my_customer',
            'fields': fields,
            'maxResults': 500,
            'projection': projection,
            'query': query,
        }
        users = self.admin.users()
        request = users.list(**params)

        google_users = []
        while request is not None:
            users_list = request.execute()
            google_users += users_list.get('users', [])
            request = users.list_next(request, users_list)
        return google_users

    def get_users_dict(
            self,
            fields=None,
            key='id',
            projection='basic',
            query=None,
            verbose=False
    ):
        """Return a dict of Google users."""
        google_users = self.get_users(
            fields=fields,
            projection=projection,
            query=query,
            verbose=verbose
        )
        users = {}
        for u in google_users:
            uid = u[key]
            users[uid] = u
        return users

    def patch_user(self, userKey, body={}):
        """Patch a Google User."""
        params = {
            'userKey': userKey,
            'body': body,
        }
        return self.admin.users().patch(**params).execute()

    def suspend_user(self, userKey):
        """Suspend a Google user."""
        try:
            user = self.get_user(userKey)
        except Exception:
            return
        if user.get('suspended'):
            return
        user['suspended'] = True
        params = {
            'userKey': userKey,
            'body': user,
        }
        try:
            return self.admin.users().update(**params).execute()
        except Exception as e:
            print(e)
            return None

    def unsuspend_user(self, userKey):
        """Suspend a Google user."""
        try:
            user = self.get_user(userKey)
        except Exception:
            return
        if not user.get('suspended'):
            return
        user['suspended'] = False
        params = {
            'userKey': userKey,
            'body': user,
        }
        try:
            return self.admin.users().update(**params).execute()
        except Exception as e:
            print(e)
            return None

    def update_user(self, userKey, body={}):
        """Update a Google User."""
        params = {
            'userKey': userKey,
            'body': body,
        }
        return self.admin.users().update(**params).execute()
