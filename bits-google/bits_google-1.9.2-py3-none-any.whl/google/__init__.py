"""Google class file."""

import argparse
import hashlib
import json
import re
import requests
import string
import sys
import time
from httplib2 import Http
from random import choice

import google.auth
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

# used for auth_stored_credentials
from oauth2client import client, tools
from oauth2client.file import Storage as FileStorage
from oauth2client.service_account import ServiceAccountCredentials

from bits.helpers import chunks

# bits-google model subclasses
from .models import Models

# bits-google service subclasses
from .services.bigquery import BigQuery
from .services.billing import CloudBilling
from .services.budgets import CloudBillingBudgets
from .services.cai import CloudAssetInventory
from .services.calendar import Calendar
from .services.compute import Compute
from .services.crm import CloudResourceManager
from .services.datastore import Datastore
from .services.directory import Directory
from .services.dns import CloudDNS
from .services.drive import Drive
from .services.firestore import Firestore
from .services.gmail import Gmail
from .services.groupssettings import GroupsSettings
from .services.iam import IAM
from .services.iamcredentials import IAMCredentials
from .services.labelmanager import LabelManager
from .services.licensing import Licensing
from .services.people import People
from .services.privatecatalog import PrivateCatalog
from .services.recommender import Recommender
from .services.reports import Reports
from .services.resourcesearch import ResourceSearch
from .services.securitycenter import SecurityCenter
from .services.serviceusage import ServiceUsage
from .services.sheets import Sheets
from .services.sql import SQL
from .services.storage import Storage
from .services.vault import Vault


class Google(object):
    """Google class definition."""

    def __init__(
        self,
        access_token=None,
        api_key=None,
        app_name=None,
        client_scopes=None,
        client_secrets_file='client_secrets.json',
        credentials_file='credentials.json',
        gsuite_licenses={},
        private_key_password='notasecret',
        redirect_uri='urn:ietf:wg:oauth:2.0:oob',
        scopes=[],
        service_account_email=None,
        service_account_file='service_account.json',
        subject=None,
        verbose=False,
    ):
        """Initialize a class instance."""
        # token authentication
        self.access_token = access_token

        # developer key authentication
        self.api_key = api_key

        # client secrets oauth2 authentication flow
        self.app_name = app_name
        self.client_secrets_file = client_secrets_file
        self.client_scopes = client_scopes
        self.credentials_file = credentials_file
        self.redirect_uri = redirect_uri

        # service account scopes
        self.scopes = scopes

        # service account authentication (json/p12)
        self.service_account_file = service_account_file
        self.subject = subject

        # service account authentication (p12)
        self.private_key_password = private_key_password
        self.service_account_email = service_account_email

        # enable verbose output
        self.verbose = verbose

        # authorized credentials
        self.credentials = None
        self.http = None

        # project ID
        self.project_id = None

        # collections
        self.google_people = None
        self.groups = None
        self.projects = None
        self.users = None

        # G Suite licenses
        self.gsuite_licenses = gsuite_licenses

    #
    # Authentication functions
    #
    def auth_google_credentials(self, scopes=None):
        """Authorize application default credentials."""
        credentials, project_id = google.auth.default(scopes=scopes)
        self.credentials = credentials
        self.project_id = project_id
        return credentials

    def auth_service_account_json(self, scopes, subject=None):
        """Authorize service account json file."""
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file
        )
        if scopes:
            credentials = credentials.with_scopes(scopes)
        if subject:
            credentials = credentials.with_subject(subject)
        # store credentials
        self.credentials = credentials
        return credentials

    def auth_service_account_p12(self, scopes, subject=None):
        """Authorize service account p12 file."""
        # need to remove support for p12 accounts because of dependency
        # on oauth2client
        credentials = ServiceAccountCredentials.from_p12_keyfile(
            self.service_account_email,
            self.service_account_file,
            self.private_key_password,
            scopes,
        )
        if subject:
            credentials = credentials.create_scoped(subject)
        # store credentials
        self.credentials = credentials
        return credentials

    def auth_service_account(self, scopes=[], subject=None):
        """Authorize service account."""
        if not scopes:
            scopes = self.scopes
        if isinstance(scopes, str):
            scopes = [scopes]
        # need to remove support for p12 in a future version because
        # of dependency on oauth2client
        if re.search('.p12$', self.service_account_file):
            return self.auth_service_account_p12(scopes, subject)
        elif re.search('.json$', self.service_account_file):
            return self.auth_service_account_json(scopes, subject)

    def auth_stored_credentials(self, scopes=[]):
        """Authorize stored credentials."""
        # this has a dependency on oauth2client
        if not scopes:
            scopes = self.client_scopes
        try:
            parser = argparse.ArgumentParser(parents=[tools.argparser])
            parser.add_argument('args', nargs=argparse.REMAINDER)
            flags = parser.parse_args()
            flags.noauth_local_webserver = True
        except ImportError:
            flags = None
        # retrieve stored credentials, if they exist
        store = FileStorage(self.credentials_file)
        credentials = store.get()
        # create stored credentials
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(
                self.client_secrets_file,
                scopes,
            )
            flow.user_agent = self.app_name
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            if self.verbose:
                print('Saved credentials to %s' % (self.credentials_file))
        # authorize an Http instance
        self.http = credentials.authorize(Http())
        # store credentials
        self.credentials = credentials
        return credentials

    def get_auth_token(self, credentials):
        """Return an auth token from Google credentials."""
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token

    #
    # Models class
    #
    def models(self):
        """Return the Models class."""
        return Models(self)

    #
    # Sub-class functions for Services
    #
    def bigquery(self):
        """Return the BigQuery class."""
        return BigQuery(self.credentials)

    def billing(self):
        """Return the CloudBilling class."""
        return CloudBilling(self.credentials, self.api_key)

    def budgets(self):
        """Return the CloudBillingBudgets class."""
        return CloudBillingBudgets(self.credentials)

    def cai(self):
        """Return the CloudAssetInventory class."""
        return CloudAssetInventory(self.credentials)

    def calendar(self):
        """Return the Calendar class."""
        return Calendar(self.credentials)

    def compute(self):
        """Return the Compute class."""
        return Compute(self.credentials)

    def crm(self):
        """Return the CloudResourceManager class."""
        return CloudResourceManager(self.credentials)

    def datastore(self, project):
        """Return the Datastore class."""
        return Datastore(project, self.credentials)

    def directory(self):
        """Return the Directory class."""
        return Directory(self.credentials)

    def dns(self):
        """Return the CloudDNS class."""
        return CloudDNS(self.credentials)

    def drive(self):
        """Return the Drive class."""
        return Drive(self.credentials)

    def firestore(self, project):
        """Return the Firestore class."""
        return Firestore(project, self.credentials)

    def gmail(self):
        """Return the Gmail class."""
        return Gmail(self.credentials)

    def groupssettings(self):
        """Return the GroupsSettings class."""
        return GroupsSettings(self.credentials)

    def iam(self):
        """Return the IAM class."""
        return IAM(self.credentials)

    def iamcredentials(self):
        """Return the IAMCredentials class."""
        return IAMCredentials(self.credentials)

    def labelmanager(self):
        """Return the LabelManager class."""
        return LabelManager(self.credentials, self.api_key)

    def licensing(self):
        """Return the Licensing class."""
        return Licensing(self.http, self.gsuite_licenses)

    def people(self):
        """Return the People class."""
        return People(self.credentials)

    def privatecatalog(self):
        """Return the PrivateCatalog class."""
        return PrivateCatalog(self.credentials, self.api_key)

    def recommender(self):
        """Return the Recommender class."""
        return Recommender(self.credentials)

    def reports(self):
        """Return the Reports class."""
        return Reports(self.credentials)

    def resourcesearch(self):
        """Return the ResourceSearch class."""
        return ResourceSearch(self.credentials)

    def sheets(self):
        """Return the Sheets class."""
        return Sheets(self.credentials)

    def securitycenter(self):
        """Return the SecurityCenter class."""
        return SecurityCenter(self.credentials)

    def serviceusage(self):
        """Return the ServiceUsage class."""
        return ServiceUsage(self.credentials)

    def sql(self):
        """Return the SQL class."""
        return SQL(self.credentials)

    def storage(self):
        """Return the Storage class."""
        return Storage(self.credentials)

    def vault(self):
        """Return the Vault class."""
        return Vault(self.credentials)

    #
    # Adding in all additional "Helper" functions
    #
    #
    # Helper Functions
    #
    def check_billing_labels(self, projects, projects2, billing_accounts):
        """Check and update the billingaccount labels on projects."""
        for projectId in sorted(projects):
            p = projects[projectId]
            # skip deleted projects
            if p['lifecycleState'] == 'DELETE_REQUESTED':
                continue
            # get project labels
            labels = projects2.get(projectId, {}).get('labels', {})
            # get billing label
            billing_label = labels.get('billing')
            # get billing account
            billing_account = p.get('billing_account')
            if billing_account:
                billing_account = '%s' % (
                    billing_account.replace('billingAccounts/', '').lower(),
                )

            # check labels
            if billing_label != billing_account:
                print('   * Updating billing label for %s: %s -> %s' % (
                    projectId,
                    billing_label,
                    billing_account,
                ))

                # get project
                # project = self.crm().get_project(projectId)
                if projectId not in projects2:
                    print('ERROR: Project not found in current list: %s' % (projectId))
                    continue
                project = projects2[projectId]
                # print(json.dumps(project, indent=2, sort_keys=True))

                # see if we're adding/updating a label
                if billing_account:
                    # add labels
                    if 'labels' not in project:
                        project['labels'] = {}
                    # update label
                    project['labels']['billing'] = billing_account

                # otherwise we're deleting the cost_object label
                else:
                    if 'labels' in project:
                        if 'billing' in project['labels']:
                            del project['labels']['billing']

                # update project
                self.crm().update_project(projectId, project)

    def check_costobject_labels(self, projects, projects2, billing_accounts):
        """Check and update the cost object labels on projects."""
        for projectId in sorted(projects):
            p = projects[projectId]
            # skip deleted projects
            if p['lifecycleState'] == 'DELETE_REQUESTED':
                continue
            # get project labels
            labels = projects2.get(projectId, {}).get('labels', {})
            # get cost object label
            costobject = labels.get('costobject')
            # get billing account
            billingaccount = p.get('billing_account')

            billing_co = None
            # check if billing account exists
            if billingaccount:
                # check for broad billing account
                if billingaccount in billing_accounts:
                    account = billing_accounts[billingaccount]
                    displayName = account['displayName']
                    if re.match('Broad Institute - [0-9]{7}$', displayName):
                        billing_co = 'broad-%s' % (
                            displayName.replace('Broad Institute - ', '')
                        )
                    else:
                        billing_co = 'broad-split'

            # check labels
            if costobject != billing_co:
                print('   * Updating costobject label for %s: %s -> %s' % (
                    projectId,
                    costobject,
                    billing_co,
                ))

                # get project
                # project = self.crm().get_project(projectId)
                project = projects2[projectId]
                # print(json.dumps(project, indent=2, sort_keys=True))

                # see if we're adding/updating a label
                if billing_co:
                    # add labels
                    if 'labels' not in project:
                        project['labels'] = {}
                    # update label
                    project['labels']['costobject'] = billing_co

                # otherwise we're deleting the cost_object label
                else:
                    if 'labels' in project:
                        if 'costobject' in project['labels']:
                            del project['labels']['costobject']

                # update project
                self.crm().update_project(projectId, project)

    def check_project_folders(self, projects, projects2, folders, billing_accounts):
        """Check the folder that each project is in."""
        foldernames = {}
        for folder in sorted(folders, key=lambda x: folders[x]['displayName']):
            f = folders[folder]
            # a = f['ancestry']
            displayName = f['displayName']
            if displayName in foldernames:
                print('Duplicate folder name: %s [%s]' % (displayName, folder))
                continue
            foldernames[displayName] = f

        createfolders = []

        for projectId in sorted(projects):
            p = projects[projectId]
            # parent = p['parent']
            if projectId not in projects2:
                # print('ERROR: Project not in projects2: %s' % (projectId))
                continue
            parent = projects2[projectId]['parent']
            state = p['lifecycleState']

            # skip deleted projects
            if state == 'DELETE_REQUESTED':
                continue

            broad_orgid = '548622027621'
            broad_orgname = 'organizations/%s' % (broad_orgid)

            # get appropriate parent folder for the project
            foldername = None

            broad_billing = False
            # check broad billing account projects
            if 'broad_billing_account' in p:
                billingAccount = p['broad_billing_account']
                account = billing_accounts[billingAccount]
                billingAccountName = account['displayName']

                # check for cost object in billing account name
                if re.match('Broad Institute - ', billingAccountName):
                    foldername = billingAccountName.replace('Institute ', '')
                    broad_billing = foldername

            # check projects with a non-broad billing account
            elif 'billing_account' in p and broad_orgname in p['ancestry']:
                foldername = 'Non-Broad Billing'
                billingAccount = p['billing_account']
                if billingAccount not in billing_accounts:
                    print('  * Project in %s has non-Broad billing: %s' % (
                        projectId,
                        billingAccount.replace('billingAccounts/', ''),
                    ))

            # check projects with no billing account
            else:
                foldername = 'No Billing'

            # check if anything needs to move
            folder = None
            move = False

            # check for projects in broadinstitute root
            if parent['id'] == broad_orgid:
                print('  * Project in broadinstitute.org top-level: %s' % (projectId))
                move = True

            # check if we need to create any folders
            if foldername not in foldernames:
                if foldername and foldername not in createfolders:
                    createfolders.append(foldername)
            else:
                folder = foldernames[foldername]['name']

            # check for co projects with the wrong parent
            if folder and broad_orgname in p['ancestry'] and broad_billing:
                if folder not in p['ancestry']:
                    current_parent = '%ss/%s' % (
                        parent['type'],
                        parent['id'],
                    )
                    current_foldername = broad_orgname
                    if parent['type'] == 'folder':
                        current_foldername = folders.get(current_parent, {}).get('displayName')

                    if current_foldername != foldername:
                        print('  * Project with wrong parent: %s [%s -> %s]' % (
                            projectId,
                            current_foldername,
                            foldername
                        ))
                        move = True

            if move and folder:
                print('    - Moving project %s to folder %s' % (projectId, foldername))
                p = projects2[projectId]
                p['parent'] = {
                    'id': folder.replace('folders/', ''),
                    'type': 'folder',
                }
                self.crm().update_project(projectId, p)

        # see what folders we need to create
        if createfolders:
            print('\n  Billing Accounts without Folders:')
        for name in sorted(createfolders):
            print('  * %s' % (name))

    def getBillingAccounts(self, projects=False, iampolicy=False):
        """Return a dict of billing accounts."""
        self.auth_service_account(self.scopes, self.subject)
        billing_accounts = self.billing().get_billing_accounts_dict()

        if projects or iampolicy:
            # progress = Progress().start(billing_accounts, self.verbose)
            for name in billing_accounts:
                # progress.update()

                # get billing account projects
                if projects:
                    try:
                        plist = self.billing().get_billing_account_projects(
                            name,
                        )
                    except HttpError as err:
                        if err.resp.status in [403]:
                            plist = []
                        else:
                            raise
                    billing_accounts[name]['projects'] = plist

                # get billing account iampolicy
                if iampolicy:
                    try:
                        policy = self.billing().get_billing_account_iampolicy(
                            name,
                        )
                    except HttpError as err:
                        if err.resp.status in [403]:
                            policy = []
                        else:
                            raise
                    billing_accounts[name]['iam_policy'] = policy

            # progress.finish()

        return billing_accounts

    def getBillingAccountProjects(self, name):
        """Return a list of projects associated with a billing account."""
        return self.billing().get_billing_account_projects(name)

    def getCalendar(self, calendarId):
        """Return a calendar."""
        return self.calendar().get_calendar(calendarId)

    def getCalendarEvents(
        self,
        calendarId,
        showDeleted=False,
        singleEvents=False,
        timeMin=None,
        timeMax=None,
        timeZone=None,
    ):
        """Return a list of events from a calendar."""
        params = {
            'calendarId': calendarId,
            'showDeleted': showDeleted,
            'singleEvents': singleEvents,
            'timeMin': timeMin,
            'timeMax': timeMax,
            'timeZone': timeZone,
        }
        return self.calendar().get_calendar_events_list(**params)

    def getAllCalendars(self):
        """Return a dict of all calendars."""
        if not self.users:
            print('Getting users...')
            self.users = self.getUsers()
        # progress = Progress().start(self.users, verbose=self.verbose)
        calendars = {}
        for uid in sorted(
                self.users,
                key=lambda x: self.users[x]['primaryEmail']
        ):
            # progress.update()
            user = self.users[uid]
            # skip suspended users
            if user['suspended']:
                continue
            email = user['primaryEmail']
            self.auth_service_account(self.scopes, email)
            try:
                user_calendars = self.calendar().get_calendar_list()
            except Exception:
                user_calendars = []
            for c in user_calendars:
                cid = c['id']
                if cid not in calendars:
                    calendars[cid] = c
        # progress.finish()
        return calendars

    def getAllServiceAccounts(self):
        """Return a dict of all service accounts."""
        if not self.projects:
            print('Getting projects...')
            self.projects = self.getProjects()
        # progress = Progress().start(self.projects, verbose=self.verbose)
        service_accounts = {}
        for p in sorted(self.projects):
            # progress.update()
            project = self.projects[p]
            # skip deleted projects
            if project['lifecycleState'] == 'DELETE_REQUESTED':
                continue
            accounts = self.iam().get_service_accounts_dict(p)
            service_accounts.update(accounts)
        # progress.finish()
        return service_accounts

    def getEmailForwardingSettings(self):
        """Return dict of all user email forwarding settings."""
        if not self.users:
            print('Getting users...')
            self.users = self.getUsers()
        # progress = Progress().start(self.users, verbose=self.verbose)
        settings = {}
        for uid in self.users:
            # progress.update()
            user = self.users[uid]
            if user['suspended']:
                continue
            email = user['primaryEmail']
            self.auth_service_account(self.scopes, email)
            try:
                settings[email] = self.gmail().get_auto_forwarding_settings(
                    email,
                )
            except Exception:
                continue
        # progress.finish()
        return settings

    #
    # drive
    #
    def addDriveFileToFolder(self, userKey, fileId, folderId):
        """Add a drive file to a folder."""
        self.auth_service_account(self.scopes, userKey)
        return self.drive().add_parents(fileId, folderId)

    def changeDriveFileOwner(self, userKey, fileId, owner):
        """Change the owner of a drive file."""
        self.auth_service_account(self.scopes, userKey)
        return self.drive().change_owner(fileId, owner)

    def createDriveFolder(self, userKey, folder):
        """Create a drive folder."""
        self.auth_service_account(self.scopes, userKey)
        return self.drive().create_folder(folder)

    def getDriveAbout(self, userKey, fields=None):
        """Return the Google Drive About information for a user."""
        self.auth_service_account(self.scopes, userKey)
        return self.drive().get_about(fields)

    def getDriveFiles(self, userKey, fields=None, orderBy=None, q=None):
        """Get the list of files for a user query."""
        self.auth_service_account(self.scopes, userKey)
        return self.drive().get_files(fields, orderBy, q)

    #
    # groups
    #
    def createGroup(self, groupKey, name, description=None):
        """Create a Google group."""
        self.auth_service_account(self.scopes, self.subject)
        return self.directory().create_group(
            groupKey,
            name,
            description,
        )

    def deleteGroup(self, groupKey):
        """Delete a Google group."""
        self.auth_service_account(self.scopes, self.subject)
        return self.directory().delete_group(
            groupKey,
        )

    def getGroup(self, groupKey):
        """Return a group member."""
        self.auth_service_account(self.scopes, self.subject)
        group = self.directory().get_group(groupKey)
        members = self.directory().get_members(groupKey)
        if group and members:
            group['members'] = members
        return group

    def getGroups(self, memberKey=None):
        """Return a dict of all groups."""
        self.auth_service_account(self.scopes, self.subject)
        self.groups = self.directory().get_groups_dict(userKey=memberKey)
        return self.groups

    def getGroupsByMember(self, groups, users):
        """Return a dict of group members and their groups."""
        groups_by_member = {}

        # assemble an array of all google users' primary email
        all_user_emails = []
        for uid in users:
            user = users[uid]
            all_user_emails.append(user['primaryEmail'])

        for group in sorted(groups):
            g = groups[group]
            if 'members' in g:
                members = g['members']
                if not members:
                    continue
                for m in members:

                    # check for * membership
                    if 'email' not in m:
                        emails = all_user_emails

                    # otherwise just one person
                    else:
                        emails = [m['email'].lower()]

                    # add email(s) to groups_by_member
                    for email in emails:
                        if email in groups_by_member:
                            groups_by_member[email]['groups'].append(group)
                        else:
                            groups_by_member[email] = {
                                'email': email,
                                'groups': [group]
                            }

        return groups_by_member

    #
    # groupssettings
    #
    def getAllGroupsSettings(self):
        """Return all the settings for all groups."""
        self.auth_service_account(self.scopes, self.subject)
        groups = self.directory().get_groups_dict()
        groups_settings = {}
        # if self.verbose:
        #     progress = Progress().start(groups, verbose=self.verbose)
        for groupKey in sorted(groups):
            # if self.verbose:
            #     progress.update()
            try:
                group_settings = self.groupssettings().get_group_settings(
                    groupKey,
                )
                groups_settings[groupKey] = group_settings
            except Exception as e:
                group_settings = {}
                print('ERROR: Failed to get settings for %s.' % (groupKey))
                print(e)
        # if self.verbose:
        #     progress.finish()

        return groups_settings

    def getGroupSettings(self, groupKey):
        """Return the settings for a Google Group."""
        self.auth_service_account(self.scopes, self.subject)
        return self.groupssettings().get_group_settings(groupKey)

    def updateGroupSettings(self, groupKey, settings):
        """Update the settings for a Google Group."""
        self.auth_service_account(self.scopes, self.subject)
        return self.groupssettings().update_group_settings(
            groupKey,
            settings,
        )

    #
    # members
    #
    def addMember(self, groupKey, memberKey):
        """Add a group member."""
        self.auth_service_account(self.scopes, self.subject)
        return self.directory().add_member(groupKey, memberKey)

    def addOwner(self, groupKey, memberKey):
        """Add a group owner."""
        self.auth_service_account(self.scopes, self.subject)
        return self.directory().add_member(
            groupKey,
            memberKey,
            role='OWNER',
        )

    def getMember(self, groupKey, memberKey):
        """Return a group member."""
        self.auth_service_account(self.scopes, self.subject)
        return self.directory().get_member(groupKey, memberKey)

    def getMembers(self, groupKey):
        """Return members of a group."""
        self.auth_service_account(self.scopes, self.subject)
        return self.directory().get_members(groupKey)

    def removeFromGroups(self, userKey):
        """Remove a user from Google Groups."""
        self.auth_service_account(self.scopes, self.subject)
        groups = self.directory().get_groups_dict(
            userKey=userKey,
            verbose=self.verbose,
        )
        success = []
        for groupKey in groups:
            try:
                self.directory().remove_member(
                    groupKey,
                    userKey,
                )
                success.append(groupKey)
                print('      - Unsubscribed from group: %s' % (groupKey))
            except Exception as e:
                print >> sys.stderr, e

        return success

    def removeMember(self, groupKey, memberKey):
        """Return a group member."""
        self.auth_service_account(self.scopes, self.subject)
        try:
            return self.directory().remove_member(groupKey, memberKey)
        except Exception as e:
            print(e)
            return None

    def subscribeToGroups(self, userKey, groups):
        """Remove a user from Google Groups."""
        self.auth_service_account(self.scopes, self.subject)
        success = []
        for groupKey in groups:
            try:
                self.directory().add_member(
                    groupKey,
                    userKey,
                )
                success.append(groupKey)
                print('      + Subscribed to group: %s' % (groupKey))
            except Exception as e:
                print >> sys.stderr, e

        return success

    def _get_group_members(self, group):
        """Return the members of the group."""
        members = []
        for m in group['members']:
            members.append(m['email'].lower())
        return members

    def _get_group_owners(self, group):
        """Return the owners of the group."""
        owners = []
        for m in group['members']:
            if m['role'] == 'OWNER':
                owners.append(m['email'].lower())
        return owners

    def _get_members_to_add(self, members, membersList):
        """Return the members to add to the group."""
        add = []
        for email in membersList:
            if email and email.lower() not in [x.lower() for x in members]:
                add.append(email)
        return add

    def _get_members_to_remove(self, members, membersList):
        """Return the members to remove from the group."""
        remove = []
        for email in members:
            if email and email.lower() not in [x.lower() for x in membersList]:
                remove.append(email)
        return remove

    def _add_members(self, groupKey, add):
        """Add members to a group."""
        for email in sorted(add):
            try:
                self.addMember(groupKey, email)
                print('   + %s' % (email))
            except Exception as e:
                print('   ! error adding %s' % (email))
                print(e)

    def _remove_members(self, groupKey, remove, owners, deleteOwners):
        """Remove members from a group."""
        for email in sorted(remove):
            if email not in owners or (email in owners and deleteOwners):
                self.removeMember(groupKey, email)
                print('   - %s' % (email))
            else:
                print('   o %s (not deleted - OWNER)' % (email))

    def updateGroupMembers(
            self,
            groupKey,
            membersList,
            delete=False,
            deleteOwners=False
    ):
        """Update the members of a Google Group."""
        group = self.getGroup(groupKey)

        if not group:
            print('ERROR group not found: %s' % (groupKey))
            return group

        if 'members' not in group or not group['members']:
            print('ERROR no members retrieved for group: %s' % (groupKey))
            return group

        # get members and owners
        members = self._get_group_members(group)
        owners = self._get_group_owners(group)

        # get members to add and remove
        add = self._get_members_to_add(members, membersList)
        remove = self._get_members_to_remove(members, membersList)

        # check if we need to make any updates
        if add or (remove and delete):
            print('Updating group: %s' % (groupKey))

        # remove members
        if remove and delete:
            print('  Removing members...')
            self._remove_members(groupKey, remove, owners, deleteOwners)

        # add members
        if add:
            print('  Adding members...')
            self._add_members(groupKey, add)

    #
    # people
    #
    def getPeople(self, credentials=None):
        """Return a dict of all people."""
        if not credentials:
            self.auth_service_account(self.scopes, self.subject)
        else:
            self.credentials = credentials
        if not self.users:
            print('Getting users...')
            self.users = self.directory().get_users_dict(
                query="isSuspended=false"
            )
        user_chunks = list(chunks(list(self.users), 50))
        fields = [
            'addresses',
            'ageRanges',
            'biographies',
            'birthdays',
            'braggingRights',
            'coverPhotos',
            'emailAddresses',
            'events',
            'genders',
            'imClients',
            'interests',
            'locales',
            'memberships',
            'metadata',
            'names',
            'nicknames',
            'occupations',
            'organizations',
            'phoneNumbers',
            'photos',
            'relations',
            'relationshipInterests',
            'relationshipStatuses',
            'residences',
            'sipAddresses',
            'skills',
            'taglines',
            'urls',
            'userDefined',
        ]
        personFields = ','.join(fields)
        # progress = Progress().start(user_chunks, verbose=self.verbose)
        self.google_people = {}
        for chunk in user_chunks:
            # progress.update()
            batch = []
            for uid in chunk:
                batch.append('people/%s' % (uid))
            responses = self.people().get_batch(
                batch,
                personFields,
            ).get('responses', [])
            for r in responses:
                uid = r['requestedResourceName'].replace('people/', '')
                if 'person' in r:
                    self.google_people[uid] = r['person']
        # progress.finish()
        return self.google_people

    #
    # projects
    #
    def getProjects(self):
        """Return a dict of all projects with iam policy."""
        self.auth_service_account(self.scopes, self.subject)
        self.projects = self.crm().get_projects_iampolicy(
            verbose=self.verbose,
        )
        return self.projects

    #
    # users
    #
    def changePassword(self, userKey, password=None):
        """Change a user's password."""
        self.auth_service_account(self.scopes, self.subject)

        # generate a random password
        if not password:
            length = 16
            characters = string.ascii_letters + string.digits
            password = ''.join(choice(characters) for _ in range(length))

        # generate a md5 of the password
        md5 = hashlib.md5(password).hexdigest()

        # update the user with the new password
        return self.directory().change_password(
            userKey,
            md5,
            'MD5',
        )

    def createUser(self, user, password, show_error=True):
        """Create a user."""
        self.auth_service_account(self.scopes, self.subject)
        body = {
            'name': {
                'fullName': user.get('full_name'),
                'givenName': user.get('first_name'),
                'familyName': user.get('last_name'),
            },
            'password': password,
            'primaryEmail': user.get('username_email'),
            'suspended': True,
        }
        try:
            return self.directory().create_user(body)
        except Exception:
            if show_error:
                print('ERROR creating user')
            return None

    def deleteUser(self, username, show_error=True):
        """Delete a user."""
        self.auth_service_account(self.scopes, self.subject)
        try:
            return self.directory().delete_user(username)
        except Exception:
            if show_error:
                print('ERROR deleting user: %s' % (username))
            return None

    def getUser(self, username, show_error=True):
        """Return a user."""
        self.auth_service_account(self.scopes, self.subject)
        try:
            return self.directory().get_user(username)
        except Exception:
            if show_error:
                print('ERROR getting user: %s' % (username))
            return None

    def getUsers(self, fields=None, query=None):
        """Update users dict from Google and return."""
        self.auth_service_account(self.scopes, self.subject)
        self.users = self.directory().get_users_dict(
            fields=fields,
            query=query,
            verbose=self.verbose,
        )
        return self.users

    def patchUser(self, username, body={}):
        """Patch a user."""
        self.auth_service_account(self.scopes, self.subject)
        return self.directory().patch_user(username, body)

    def suspendUser(self, username):
        """Suspend a user."""
        self.auth_service_account(self.scopes, self.subject)
        return self.directory().suspend_user(username)

    def unsuspendUser(self, username):
        """Unsuspend a user."""
        self.auth_service_account(self.scopes, self.subject)
        return self.directory().unsuspend_user(username)

    class Bitsdb(object):
        """GitHub subclass for BITSdb API."""

        def __init__(self):
            """Initialize a class instance."""

        def billingaccount(self, g):
            """Return a google#billingaccount for BITSdb API."""
            status = 'closed'
            if g.get('open', False):
                status = 'open'

            name = g['name'].replace('billingAccounts/', '')

            cost_object = None
            if re.match('Broad Institute - [0-9]{7}(|-[0-9]{7})', g['displayName']):
                cost_object = g['displayName'].replace('Broad Institute - ', '')

            bitsdb = {
                'kind': 'google#billingaccount',
                'id': name,
                'name': name,
                'display_name': g['displayName'],
                'status': status,
                'cost_object': cost_object,
            }
            return bitsdb

        def group(self, g):
            """Return a google#group for BITSdb API."""
            bitsdb = {
                'kind': 'google#group',
                'id': g['id'],
                # 'etag': g['etag'],
                'email': g['email'],
                'name': g['name'],
                'directMembersCount': g['directMembersCount'],
                'description': g['description'],
            }
            return bitsdb

        def user(self, g):
            """Return a google#user for BITSdb API."""
            bitsdb = {
                'kind': 'google#user',
                'id': g['id'],
                # 'etag': g['etag'],
                'primaryEmail': g['primaryEmail'],
            }
            return bitsdb

        def prep(self, collection, data):
            """Return data prepared for BITSdb API."""
            bitsdb = {}
            for oid in sorted(data):
                s = data[oid]
                k = str(oid)
                if collection == 'groups':
                    bitsdb[k] = self.group(s)
                elif collection == 'billingaccounts':
                    bitsdb[k] = self.billingaccount(s)
                elif collection == 'users':
                    bitsdb[k] = self.user(s)
                else:
                    print('ERROR: Unknown collection "%s"' % (collection))
            return bitsdb
