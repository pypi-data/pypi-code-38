"""LDAP Update class for Google."""

import re

from bits.ldap.server import Server
from datetime import date, timedelta


class Google(Server):
    """Google LDAP Update class."""

    def get_default_ous(self):
        """Return list of default ous."""
        # add ous to the list of default_ous
        # these ous do not have any ldap users in them but they need to exist for GCDS
        default_ous = []
        for item in [
            # devices
            'ou=Devices',
            'ou=Admin,ou=Devices',
            'ou=Allow Non-Broad Logins,ou=Devices',
            'ou=Unassigned,ou=Devices',
            # people
            'ou=Insecure,ou=People',
        ]:
            default_ous.append('%s,%s' % (item, self.ldap.base_dn))
        return default_ous

    def get_account_dn(self, account):
        """Return the dn for an other account."""
        # set the base ou
        ou = 'ou=Other Accounts,%s' % (self.ldap.base_dn)

        # check for an ou override
        if account.google_ou:
            parts = account.google_ou.split('/')
            for part in parts:
                ou = 'ou=%s,%s' % (part, ou)

        # otherwise, get the type ou
        else:
            type_ou = self.get_account_type_ou(account)
            if type_ou:
                ou = 'ou=%s,%s' % (type_ou, ou)

        # get primary domain
        domain = None
        if 'primary' in self.ldap.domains:
            domain = self.ldap.domains['primary']

        # get primary domain info
        domain_info = {}
        if domain in account.domains:
            domain_info = account.domains[domain]

        # get secure info
        if domain_info.get('secure'):
            ou = 'ou=Secure,%s' % (ou)

        return 'cn=%s,%s' % (account.displayName, ou)

    def get_account_type_ou(self, account):
        """Return the OU based on the type."""
        if account.type == 'saAccount':
            return 'Admins'
        elif account.type == 'externalCollaborator':
            return 'Collaborators'
        elif account.type == 'roleAccount':
            return 'Role Accounts'
        elif account.type == 'sharedAccount':
            return 'Shared Accounts'
        elif account.type == 'testAccount':
            return 'Test Accounts'

    def get_person_dn(self, person):
        """Return the proper DN for a person."""
        # terminated users who are on hold - suspended
        if person.terminated and person.hold:
            ou = 'ou=Hold,%s' % (self.ldap.base_dn)

        # regular terminated users - suspended
        elif person.terminated:
            ou = 'ou=Suspended,%s' % (self.ldap.base_dn)

        # future hires starting beyond the "start" cutoff - suspended
        elif person.start_date > self.start:
            ou = 'ou=Future,%s' % (self.ldap.base_dn)

        # all other people - active
        else:
            ou = 'ou=People,%s' % (self.ldap.base_dn)

            # get trusted tester ou
            if person.trusted_tester and not person.terminated:
                # ou = 'ou=%s,%s' % (person.trusted_tester, ou)
                ou = 'ou=%s,ou=Trusted Testers,%s' % (person.trusted_tester, ou)

            # otherwise, get workday ou
            else:
                # TEMPORARY for testing
                # if 'test.broadinstitute.' in self.ldap.primary:
                #     ou = self.get_workday_orgunit(person, ou)
                ou = self.get_workday_orgunit(person, ou)

        # create dn
        dn = 'uid=%s,%s' % (person.username, ou)

        return str(dn)

    def get_person(self, person, supervisor_dn):
        """Return a person in the correct format."""
        # get username and email from person object
        username = str(person.username)

        # get email from person objects
        email = str(person.email)
        email_username = str(email.replace('@broadinstitute.org', ''))

        # get nicknames
        nicknames = []
        if person.nicknames:
            for nickname in person.nicknames:
                nicknames.append(str(nickname))

        # get primary and secondary domain from ldap object
        primary = self.ldap.domains.get('primary')
        secondary = self.ldap.domains.get('secondary')

        emails = []

        # set primary domian email
        if primary:
            primary = str(primary)

            # get email address based on broad email (may have alias override)
            email = '%s@%s' % (email_username, primary)
            if email not in emails:
                emails.append(email)

            # get primaryEmail
            primaryEmail = '%s@%s' % (username, primary)
            if primaryEmail not in emails:
                emails.append(primaryEmail)

            # get username/nickname emails for primary domain
            emails = self.get_person_domain_emails(username, nicknames, primary, emails)

        # add secondary domain email
        if secondary:
            secondary = str(secondary)

            # get username/nickname emails for primary domain
            emails = self.get_person_domain_emails(username, nicknames, secondary, emails)

        # convert object to ldap record
        ldap_person = person.to_google(supervisor_dn)

        # overwrite email
        ldap_person['description'] = [str(primaryEmail)]
        ldap_person['email'] = [str(email)]
        ldap_person['mail'] = emails

        return ldap_person

    def get_person_domain_emails(self, username, nicknames, domain, emails=[]):
        """Return the list of domain emails for the user."""
        domain = str(domain)
        username = str(username)

        # get username email
        username_email = '%s@%s' % (username, domain)
        if username_email not in emails:
            emails.append(username_email)

        # get nickname emails
        for nickname in nicknames:
            nickname = str(nickname)
            nickname_email = '%s@%s' % (nickname, domain)
            if nickname_email not in emails:
                emails.append(nickname_email)

        return emails

    def get_workday_orgunit(self, person, ou):
        """Get the orgunit for a workday person."""
        # number of org levels to include
        depth = 2
        for org in person.organization[:depth]:
            org = org.replace(',', '')
            ou = 'ou=%s,%s' % (org, ou)
        return ou

    #
    # Assemled all records into a dict of new entries
    #
    def prepare_entries(self, ldap):
        """Prepare LDAP entries."""
        self.ldap = ldap
        self.prepare_entries_from_people()
        self.prepare_entries_from_accounts()
        self.prepare_entries_from_contacts()
        # self.prepare_entries_from_resources()

    def prepare_entries_from_accounts(self):
        """Prepare entries from accounts."""
        if self.verbose:
            print('  Preparing accounts for Google LDAP...')
        self.accounts = self.prepare_accounts()
        if self.verbose:
            print('  Prepared %s accounts for Google LDAP.' % (len(self.accounts)))
        # add contacts
        for dn in self.accounts:
            self.new_entries[dn] = self.accounts[dn]

    def prepare_entries_from_contacts(self):
        """Prepare entries from contacts."""
        if self.verbose:
            print('  Preparing contacts for Google LDAP...')
        self.contacts = self.prepare_contacts()
        if self.verbose:
            print('  Prepared %s contacts for Google LDAP.' % (len(self.contacts)))
        # add contacts
        for dn in self.contacts:
            self.new_entries[dn] = self.contacts[dn]

    def prepare_entries_from_people(self):
        """Prepare entries from people."""
        if self.verbose:
            print('  Preparing people for Google LDAP...')
        self.new_entries = self.prepare_people()
        if self.verbose:
            print('  Prepared %s people for Google LDAP.' % (len(self.new_entries)))

    def prepare_entries_from_resources(self):
        """Prepare entries from resources."""
        if self.verbose:
            print('  Preparing resources for Google LDAP...')
        self.resources = self.prepare_resources()
        if self.verbose:
            print('  Prepared %s resources for Google LDAP.' % (len(self.resources)))
        # add resources
        for dn in self.resources:
            self.new_entries[dn] = self.resources[dn]

    #
    # Prepare actual resources for LDAP
    #
    def prepare_accounts(self):
        """Prepare other accounts from bitsdb."""
        accounts = {}
        for account in self.update.accounts_records:
            # get dn
            dn = self.get_account_dn(account)

            # get emails
            emails = []

            # get primary email
            primary = self.ldap.domains.get('primary')
            primary_info = account.domains.get(primary, {})
            email = primary_info.get('username')
            if email:
                emails.append(str(email))
            else:
                # skip users that have no email
                continue

            # check for sub domains
            subdomain = False
            if '.%s' % (primary) in email:
                subdomain = True

            # check for users with primary email in secondary domain
            secondary_user = False
            if primary not in email:
                secondary_user = True

            # get secondary email
            secondary = self.ldap.domains.get('secondary')
            if email and secondary and not secondary_user and not subdomain:
                # create secondary email by replacing primary domain with secondary
                secondary_email = email.replace(primary, secondary)
                if secondary_email:
                    emails.append(str(secondary_email))

            # create record
            record = {
                'cn': [account.displayName],
                'carLicense': [account.gsuite_license],
                'description': [email],
                'givenName': [account.first_name],
                'co': ['Broad Institute of MIT and Harvard'],
                'mail': emails,
                'o': ['Broad Institute'],
                'objectClass': [
                    'top',
                    'inetOrgPerson',
                    'extensibleObject',
                ],
                'sn': [account.last_name],
            }

            # only add if the account has emails for this domain
            if email and emails:
                accounts[dn] = record

        return accounts

    def prepare_contacts(self):
        """Prepare contact records for Google LDAP."""
        contacts = {}
        for oid in self.update.shared_contacts:
            contact = self.update.shared_contacts[oid]

            # set cn and dn
            cn = str('%s %s' % (contact['first_name'], contact['last_name']))
            ou = str('ou=Contacts,ou=Shared Contacts,%s' % (self.ldap.base_dn))
            dn = str('cn=%s,%s' % (cn, ou))

            # get building info
            building = None
            if 'building' in contact and contact['building']:
                building = self.update.buildings[contact['building']]

            # create record
            record = {
                'cn': [cn],
                'description': [str(contact['email'])],
                'email': [str(contact['email'])],
                'givenName': [str(contact['first_name'])],
                'mail': [str(contact['email'])],
                'o': [str(contact['org'])],
                'objectClass': [
                    'top',
                    'inetOrgPerson',
                    'extensibleObject',
                ],
                'sn': [str(contact['last_name'])],
            }

            # building
            if building:
                record['l'] = [building['city']]
                record['postalCode'] = [building['zip']]
                record['st'] = [building['state']]
                record['street'] = [building['street_address']]

            # telephone
            if contact.get('phone'):
                record['telephoneNumber'] = [str(contact['phone'])]

            # add contact to dictionar
            contacts[dn] = record

        return contacts

    def prepare_people(self):
        """Prepare people records for Google LDAP."""
        # get dates
        date_today = date.today()
        start_date = date_today + timedelta(days=14)
        end_date = date_today - timedelta(days=90)

        # get date strings
        # today = date_today.strftime('%Y-%m-%d')
        self.start = start_date.strftime('%Y-%m-%d')
        self.end = end_date.strftime('%Y-%m-%d')

        people = {}
        for pid in self.update.people_records:
            # get person object
            person = self.update.people_records[pid]

            # skip people who are future hires
            # if person.start_date > self.start:
            #     continue

            # skip people are are past 90 days termination
            if not person.hold and (person.end_date and person.end_date <= self.end):
                continue

            # for broadinstitute.us domains, skip employees
            primary_domain = self.ldap.domains.get('primary')
            if primary_domain and re.search('broadinstitute.us$', primary_domain):
                if person.type in ['Core Member', 'Employee']:
                    continue

            dn = self.get_person_dn(person)
            # get supervisor object
            supervisor_dn = None
            if person.supervisor_id:
                supervisor = self.update.people_records[person.supervisor_id]
                supervisor_dn = self.get_person_dn(supervisor)
            # get person in ldap format
            people[dn] = self.get_person(person, supervisor_dn)
        return people

    def prepare_resources(self):
        """Prepare calendar resources for Google LDAP."""
        resources = {}
        ou = 'ou=Resources,ou=Shared Contacts,%s' % (self.ldap.base_dn)

        # get buildings by code
        buildings = {}
        for bid in self.update.buildings:
            building = self.update.buildings[bid]
            code = building['code'].lower()
            buildings[code] = building

        # create resource records
        for resource in self.update.resources:
            # only include conference rooms

            if 'resourceType' not in resource:
                print('ERROR: No Resource Type: %s' % (resource))
                continue

            if not re.search('Conference Room', resource['resourceType']):
                continue

            # get dn
            dn = 'cn=%s,%s' % (resource['resourceName'], ou)

            # get room and name
            building_room = str(resource['resourceDescription'].split(',')[0])
            room = str(building_room.split('-')[1].strip())
            name = str(resource['resourceName'].split(' (')[0].strip())

            # create record
            record = {
                'cn': [str(resource['resourceName'])],
                'description': [str(resource['resourceDescription'])],
                'email': [str(resource['resourceEmail'])],
                'employeeNumber': [str(resource['resourceId'])],
                'givenName': [name],
                # 'l': ['Cambridge'],
                'objectClass': [
                    'top',
                    'inetOrgPerson',
                    'extensibleObject',
                ],
                # 'postalCode': ['02142'],
                'roomNumber': [room],
                'sn': [str(resource['resourceType'])],
                # 'st': ['MA'],
                # 'street': ['75 Ames Street'],
            }

            # get building
            building_code = resource.get('buildingId')
            if building_code in buildings:
                building = buildings[building_code]
                record['l'] = [building['city']]
                record['postalCode'] = [building['zip']]
                record['st'] = [building['state']]
                record['street'] = [building['street_address']]

            # save record
            resources[dn] = record

        return resources
