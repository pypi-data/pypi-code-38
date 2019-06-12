"""Google Billing Account class file."""

from bits.progressbar import Progress


class BillingAccount(object):
    """Google BillingAccount class."""

    def __init__(self, google=None):
        """Initialize a Google Billing Account instance."""
        # google class
        self.google = google
        self.billing = google.billing()
        self.verbose = google.verbose

        # billingAccount attributes from Google
        self.name = None
        self.open = None
        self.displayName = None
        self.masterBillingAccount = None

        # additional billingAccount information from Google
        self.budgets = None
        self.iamPolicy = None
        self.organization = None
        self.projects = None

        # contacts
        self.admins = []
        self.approvers = []
        self.owners = []
        self.users = []

        # financial information
        self.budget_start_date = None
        self.budget_end_date = None
        self.cost_object = None
        self.monthly_budget = None
        self.total_budget = None

    def __repr__(self):
        """Human-readable representation."""
        return '%s [%s]' % (self.displayName, self.name.replace('billingAccounts/', ''))

    def list_from_google(self, iamPolicy=False, projects=False):
        """Return a list of Google BillingAccount instances."""
        # get billing accounts from google
        billing_accounts = self.google.billing().get_billing_accounts()

        # create a list for account instances
        accounts = []

        # initialize progress bar
        progress = Progress().start(billing_accounts, verbose=self.verbose)

        # process billing accounts
        for a in billing_accounts:

            # update progress bar
            progress.update()

            # create an account instance
            account = BillingAccount(self.google)

            # assign attributes
            account.name = a['name']
            account.open = a.get('open')
            account.displayName = a['displayName']
            account.masterBillingAccount = a.get('masterBillingAccount')

            # add in iam policy bindings
            if iamPolicy:
                account.refresh_iam_policy()

            # add in projects
            if projects:
                account.refresh_projects()

            # add account to list
            accounts.append(account)

        # finish progress bar
        progress.finish()

        return accounts

    def refresh_iam_policy(self):
        """Refresh the Billing Account iamPolicy bindings list."""
        self.iamPolicy = self.google.billing().get_billing_account_iampolicy(
            self.name
        )

    def refresh_projects(self):
        """Refresh the Billing Account projects list."""
        self.projects = self.google.billing().get_billing_account_projects(
            self.name
        )
