"""Google Cloud Resource Manager class."""

import sys

from bits.google.services.base import Base
from googleapiclient.discovery import build


class CloudResourceManager(Base):
    """CloudResourceManager class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.crm = build('cloudresourcemanager', 'v1', credentials=credentials)
        self.crm2 = build('cloudresourcemanager', 'v2', credentials=credentials)

    def create_folder(self, parent, name):
        """Return a response from folder creation."""
        params = {
            'parent': parent,
            'body': {
                'displayName': name,
            },
        }
        return self.crm2.folders().create(**params).execute()

    def get_folder_iampolicy(self, resource):
        """Return the iamPolicy for an organization."""
        params = {
            'body': {},
            'resource': resource,
        }
        return self.crm2.folders().getIamPolicy(**params).execute()

    def get_folders(self, parent, recursive=False):
        """Return a list of folders under a parent."""
        if not recursive:
            return self.crm2.folders().list(parent=parent).execute().get('folders', [])

        # get parent folders
        folders = self.get_folders(parent)

        # now deal with the children
        for f in sorted(folders, key=lambda x: x['displayName']):
            name = f['name']
            folders += self.get_folders(name, recursive)

        return folders

    def get_folders_dict(self, parent, recursive=False):
        """Return a dict of domain folders."""
        google_folders = self.get_folders(parent, recursive)
        folders = {}
        for f in google_folders:
            name = f['name']
            folders[name] = f
        return folders

    def get_folders_iampolicy(self, parent):
        """Return a dict of folders with the iam policy added."""
        folders = self.get_folders_dict(parent)
        for p in sorted(folders):
            iam_policy = self.get_folder_iampolicy(p)
            folders[p]['iam_policy'] = iam_policy
        return folders

    def search_folders(self, query=None):
        """Return a list of folder search results."""
        body = {
            'query': query,
            'pageToken': None,
        }

        # get first page of folders
        response = self.crm2.folders().search(body=body).execute()
        folders = response.get('folders', [])
        nextPageToken = response.get('nextPageToken')

        # see if we have more pages
        while nextPageToken:
            body['pageToken'] = nextPageToken

            # get next page of folders
            response = self.crm.folders().search(body=body).execute()
            folders += response.get('folders', [])
            nextPageToken = response.get('nextPageToken')

        return folders

    def get_operation(self, name):
        """Return an operation resource."""
        return self.crm.operations().get(name=name).execute()

    def get_organization(self, name):
        """Return an organization resource."""
        return self.crm.organizations().get(name=name).execute()

    def get_organization_folders(self, parent):
        """Return all folders and subfolders for an organization."""
        org_folders = self.get_folders_iampolicy(parent)
        all_folders = {}
        for folder in org_folders:
            all_folders[folder] = org_folders[folder]
            sub_folders = self.get_organization_folders(folder)
            all_folders.update(sub_folders)
        return all_folders

    def get_organization_iampolicy(self, resource):
        """Return the iamPolicy for an organization."""
        params = {
            'body': {},
            'resource': resource,
        }
        return self.crm.organizations().getIamPolicy(**params).execute()

    def get_organizations(self):
        """Return list of GCP organizations."""
        response = self.crm.organizations().search(body={}).execute()
        return response.get('organizations', [])

    def get_organizations_dict(self):
        """Return a dict of organizations."""
        google_organizations = self.get_organizations()
        organizations = {}
        for o in google_organizations:
            name = o['name']
            organizations[name] = o
        return organizations

    def get_organizations_folders(self):
        """Return a dict of all orgs and their folders."""
        orgs = self.get_organizations()
        folders = {}
        for o in orgs:
            org = o['name']
            org_folders = self.get_organization_folders(org)
            for f in org_folders:
                folders[f] = org_folders[f]
        return folders

    def get_organizations_iampolicy(self):
        """Return a dict of organizations with the iam policy added."""
        organizations = self.get_organizations_dict()
        for o in sorted(organizations):
            iam_policy = self.get_organization_iampolicy(o)
            organizations[o]['iam_policy'] = iam_policy
        return organizations

    def get_project_iampolicy(self, resource):
        """Return the iamPolicy for an organization."""
        params = {
            'body': {},
            'resource': resource,
        }
        return self.crm.projects().getIamPolicy(**params).execute()

    def get_project(self, projectId):
        """Return a project."""
        return self.crm.projects().get(projectId=projectId).execute()

    def get_project_ancestry(self, projectId):
        """Return a project."""
        return self.crm.projects().getAncestry(
            projectId=projectId, body={}
        ).execute().get('ancestor', [])

    def get_projects(self, filter=None):
        """Return list of projects."""
        params = {
            'filter': filter,
        }
        projects = self.crm.projects()
        request = projects.list(**params)
        return self.get_list_items(projects, request, 'projects')

    def get_projects_dict(self):
        """Return a dict of domain projects."""
        google_projects = self.get_projects()
        projects = {}
        for p in google_projects:
            pid = p['projectId']
            projects[pid] = p
        return projects

    def get_projects_iampolicy(self, verbose=False):
        """Return a dict of projects with the iam policy added."""
        projects = self.get_projects_dict()
        for p in sorted(projects):
            try:
                iam_policy = self.get_project_iampolicy(p)
            except Exception as e:
                print >> sys.stderr, 'ERROR retrieving IAM policy for: %s' % (
                    p
                )
                print >> sys.stderr, e
            projects[p]['iam_policy'] = iam_policy
        return projects

    def update_project(self, projectId, body):
        """Update the information for a project."""
        return self.crm.projects().update(projectId=projectId, body=body).execute()
