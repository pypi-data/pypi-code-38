"""Gnarwl Forwarder class file."""

import base64


class Forwarder(object):
    """Forwarder class."""

    def __init__(self, update, record):
        """Initialize a person instance."""
        self.record = record
        self.update = update
        self.verbose = update.verbose

        self.username = str(record['username'])
        self.email = '%s@broadinstitute.org' % (self.username)

        self.created = record.get('created')
        self.modified = record.get('modified')

        self.enddate = record.get('enddate')
        self.forward = str(record.get('forward', ''))
        self.sponsor = record.get('sponsor')

        if self.username == 'nagios':
            self.active = 'FALSE'
            self.message = None
            self.password = 'nagios'
            self.first_name = 'Nagios'
            self.last_name = 'Check'
            self.full_name = 'Nagios Check'
        else:
            self.active = 'TRUE'
            self.password = '*'
            self.message = ''
            raw_message = record['message']
            if raw_message:
                self.message = base64.b64decode(raw_message)
            self.get_person()

    def get_person(self):
        """Return a person record if one exists."""
        self.person = self.update.usernames.get(self.username)
        self.first_name = self.username
        self.last_name = self.username
        self.full_name = self.username
        if self.person:
            self.first_name = str(self.person['first_name'])
            self.last_name = str(self.person['last_name'])
            self.full_name = str(self.person['full_name'])

    def to_ldap(self):
        """Return a record for LDAP."""
        record = {
            'cn': [self.username],
            'displayName': [self.full_name],
            'givenName': [self.first_name],
            # 'mail': [self.email],
            'objectClass': [
                'inetOrgPerson',
                'extensibleObject',
                'top',
            ],
            'sn': [self.last_name],
            'uid': [self.username],
            # 'userPassword': [self.password],
            'vacationActive': [self.active],
        }
        # nagios user needs a password
        if self.username == 'nagios':
            record['userPassword'] = [self.password]
        # other users get mail
        else:
            record['mail'] = [self.email]

        if self.message is not None:
            record['vacationInfo'] = [self.message]

        return record
