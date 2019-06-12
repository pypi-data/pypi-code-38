"""Google Cloud Billing API."""

import re

from bits.google.services.base import Base
from googleapiclient.discovery import build


class CloudBilling(Base):
    """CloudBilling class."""

    def __init__(self, credentials, api_key):
        """Initialize a class instance."""
        self.billing = build('cloudbilling', 'v1', credentials=credentials)

        # developerKey is needed by services() and skus()
        self.api_key = api_key

    def _get_billing_account_name(self, billingAccount):
        """Return the full name of the billing account."""
        if not re.match('billingAccounts/', billingAccount):
            billingAccount = 'billingAccounts/%s' % (billingAccount)
        return billingAccount

    def _get_project_name(self, project):
        """Return the full name of the project."""
        if not re.match('projects/', project):
            project = 'projects/%s' % (project)
        return project

    def create_billing_subaccount(self, master, displayName=None):
        """Create a new billing subaccount."""
        body = {
            'masterBillingAccount': master,
        }
        if displayName:
            body['displayName'] = displayName
        billingAccounts = self.billing.billingAccounts()
        return billingAccounts.create(body=body).execute()

    def get_billing_account(self, name):
        """Return a billing account."""
        name = self._get_billing_account_name(name)
        billingAccounts = self.billing.billingAccounts()
        return billingAccounts.get(name=name).execute()

    def get_billing_accounts(self):
        """Return list of billing accounts."""
        billingAccounts = self.billing.billingAccounts()
        request = billingAccounts.list()
        return self.get_list_items(billingAccounts, request, 'billingAccounts')

    def get_billing_accounts_dict(self):
        """Return a dict of billing accounts."""
        google_billing_accounts = self.get_billing_accounts()
        billing_accounts = {}
        for b in google_billing_accounts:
            name = b['name']
            billing_accounts[name] = b
        return billing_accounts

    def get_billing_account_projects(self, billingAccount):
        """Return list of projects for a billing account."""
        billingAccount = self._get_billing_account_name(billingAccount)
        params = {
            'name': billingAccount
        }
        projectBillingInfo = self.billing.billingAccounts().projects()
        request = projectBillingInfo.list(**params)
        return self.get_list_items(projectBillingInfo, request, 'projectBillingInfo')

    def get_billing_account_iampolicy(self, resource):
        """Return the billing account's IAM policy bindings."""
        resource = self._get_billing_account_name(resource)
        billingAccounts = self.billing.billingAccounts()
        return billingAccounts.getIamPolicy(resource=resource).execute()

    def set_billing_account_iampolicy(self, resource, body):
        """Update the billing account's IAM policy bindings."""
        resource = self._get_billing_account_name(resource)
        billingAccounts = self.billing.billingAccounts()
        return billingAccounts.setIamPolicy(resource=resource, body=body).execute()

    def get_billing_account_projects_dict(self, billingAccount):
        """Return a dict of projects for a billing account."""
        google_projects = self.get_billing_account_projects(billingAccount)
        projects = {}
        for p in google_projects:
            pid = p['projectId']
            projects[pid] = p
        return projects

    def get_billing_subaccounts(self, master):
        """Return list of billing subaccounts."""
        master = self._get_billing_account_name(master)
        filterString = 'masterBillingAccount=%s' % (master)
        params = {
            'filter': filterString,
        }
        billingAccounts = self.billing.billingAccounts()
        request = billingAccounts.list(**params)
        return self.get_list_items(billingAccounts, request, 'billingAccounts')

    def get_project_billinginfo(self, name):
        """Return billinginfo for a project."""
        name = self._get_project_name(name)
        return self.billing.projects().getBillingInfo(name=name).execute()

    def get_services(self):
        """Return list of servicest."""
        billing = build('cloudbilling', 'v1', developerKey=self.api_key)
        services = billing.services()
        request = services.list()
        return self.get_list_items(services, request, 'services')

    def get_skus(self, parent):
        """Return list of skus."""
        billing = build('cloudbilling', 'v1', developerKey=self.api_key)
        if not re.match('services/', parent):
            parent = 'services/%s' % (parent)
        params = {
            'parent': parent,
        }
        skus = billing.services().skus()
        request = skus.list(**params)
        return self.get_list_items(skus, request, 'skus')

    def update_billing_account(self, name, displayName):
        """Update the display name of a billing account."""
        name = self._get_billing_account_name(name)
        body = {
            'displayName': displayName,
        }
        params = {
            'name': name,
            'body': body,
            'updateMask': 'displayName'
        }
        billingAccounts = self.billing.billingAccounts()
        request = billingAccounts.patch(**params)
        return self.get_list_items(billingAccounts, request, 'billingAccounts')
