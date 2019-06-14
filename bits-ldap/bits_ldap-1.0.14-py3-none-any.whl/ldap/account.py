"""Account class file."""


class Account(object):
    """Account class."""

    def __init__(self, update, account):
        """Initialize an other account instance."""
        # get basic information
        self.description = account.get('description')
        self.first_name = account.get('first_name')
        self.last_name = account.get('last_name')
        self.name = account.get('name')
        self.type = account.get('type')

        # get full name
        self.full_name = '%s %s' % (self.first_name, self.last_name)

        # get displayName
        if self.description:
            self.displayName = str(self.description.strip())
        elif self.name:
            self.displayName = str(self.name.strip())
        else:
            self.displayName = str(self.full_name.strip())

        # get names
        names = self.displayName.split(' ')
        if names < 2:
            names.append('Account')
        # first/last
        self.first_name = str(names[0])
        self.last_name = str(' '.join(names[1:]))

        # google information
        self.google_license = account.get('google_license')
        self.google_ou = account.get('google_ou')

        # broadinstitute.org
        self.google_secure = account.get('google_secure')
        self.google_username = account.get('google_username')
        # test.broadinstitute.org
        self.google_test_secure = account.get('google_test_secure')
        self.google_test_username = account.get('google_test_username')
        # broadinstitute.us
        self.google_us_secure = account.get('google_us_secure')
        self.google_us_username = account.get('google_us_username')
        # test.broadinstitute.us
        self.google_us_test_secure = account.get('google_us_test_secure')
        self.google_us_test_username = account.get('google_us_test_username')

        # gsuite license
        self.gsuite_license = 'Google-Apps-Lite'
        if self.google_license == 'Enterprise':
            self.gsuite_license = 'Google-Apps-Enterprise'

        # domains
        self.domains = {}

        # broadinstitute.org
        if self.google_username:
            self.domains['broadinstitute.org'] = {
                'username': str(self.google_username),
                'secure': self.google_secure,
            }
        if self.google_test_username:
            self.domains['test.broadinstitute.org'] = {
                'username': str(self.google_test_username),
                'secure': self.google_test_secure,
            }
        if self.google_us_username:
            self.domains['broadinstitute.us'] = {
                'username': str(self.google_us_username),
                'secure': self.google_us_secure,
            }
        if self.google_us_test_username:
            self.domains['test.broadinstitute.us'] = {
                'username': str(self.google_us_test_username),
                'secure': self.google_us_test_username,
            }
