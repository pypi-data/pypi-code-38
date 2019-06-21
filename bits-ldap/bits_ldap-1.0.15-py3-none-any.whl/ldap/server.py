"""LDAP Update Base class for any server type."""

import re


class Server(object):
    """LDAP Server Update class."""

    def __init__(self, update):
        """Initialize a server class instance."""
        self.update = update
        self.verbose = update.verbose

        # ldap class
        self.ldap = None

        # entries from the ldap server
        self.entries = None

        # new entries to be compared
        self.new_entries = None

    #
    # Organization Units
    #
    def add_ous(self):
        """Add any missing ous."""
        # get all ous
        ous = self.get_ous()

        # create missing ous
        for ou in sorted(ous, key=lambda x: len(x)):
            if ou not in self.entries:
                print('    + OU: %s' % (ou))
                # add ou
                self.ldap.create_ou(ou)

        return ous

    def delete_ous(self):
        """Delete any unneeded ous."""
        # get all ous
        ous = self.get_ous(self.entries)
        new_ous = self.get_ous()

        # delete missing ous
        for ou in sorted(ous, key=lambda x: len(x), reverse=True):
            if ou not in new_ous:
                print('    - OU: %s' % (ou))
                # delete ou
                self.ldap.delete_entry(ou)

        return ous

    def get_default_ous(self):
        """Return a list of default ous."""
        return []

    def get_entries_ous(self, entries):
        """Return a list of ous used by all the entries."""
        ous = []
        for dn in entries:
            parent = self.get_ou_parent(dn)
            if re.match('ou=', parent) and parent not in ous:
                ous.append(parent)
        return ous

    def get_entries_to_add(self):
        """Return a list of dns to add."""
        add = []
        for dn in sorted(self.new_entries):
            if dn not in self.entries:
                add.append(dn)
        return add

    def get_entries_to_delete(self):
        """Return a list of dns to delete."""
        delete = []
        for dn in sorted(self.entries):
            if dn not in self.new_entries:
                if not re.match(r'dc=|ou=', dn):
                    delete.append(dn)
        return delete

    def get_entries_to_update(self):
        """Return a list of dns to update."""
        update = []
        for dn in sorted(self.new_entries):
            if dn not in self.entries:
                continue

            # get entries
            entry = self.entries[dn]
            new_entry = self.new_entries[dn]

            # sort mail emails
            # for e in [entry, new_entry]:
            #     for key in ['mail', 'objectClass']:
            #         if key in e and e[key]:
            #             e[key] = sorted(e[key])

            # compare entries
            if entry != new_entry:

                # create update data
                data = {
                    'dn': dn,
                    'entry': entry,
                    'new_entry': new_entry,
                }

                # add data to list
                update.append(data)

        return update

    def get_gnarwl_dn(self, record):
        """Return the proper DN for a gnarwl record."""
        if record.username == 'nagios':
            ou = 'ou=users,%s' % (self.ldap.base_dn)
        else:
            ou = 'ou=people,%s' % (self.ldap.base_dn)
        return 'uid=%s,%s' % (record.username, ou)

    def get_ou_parent(self, ou):
        """Return the parent of an ou."""
        return ','.join(ou.split(',')[1:])

    def get_ou_parents(self, ou):
        """Return the parents of an ou."""
        parents = []

        # return if the ou is not an ou
        if not re.match('ou=', ou):
            return parents

        # get the direct parent of this ou
        parent = self.get_ou_parent(ou)

        # check if the parent is an ou
        if re.match('ou=', parent):
            parents.append(parent)
            # get parents of this ou - commented out recursive call
            # parents.extend(self.get_ou_parents(parent))
        return parents

    def get_ous(self, entries=None):
        """Return a list of all ous."""
        if not entries:
            entries = self.new_entries
        # get default ous from class
        ous = self.get_default_ous()
        # add in ous from each DN in our entries
        ous.extend(self.get_entries_ous(entries))
        # add in any ous that just contain other ous but no records
        ous.extend(self.get_parent_ous(ous))
        # do it once more for good measure (to avoid a recursive call)
        ous.extend(self.get_parent_ous(ous))
        return list(set(ous))

    def get_parent_ous(self, ous):
        """Return a list of ous that are parents of the given ous."""
        parents = []
        for ou in sorted(ous):
            parents.extend(self.get_ou_parents(ou))
        return parents

    def get_person(self, person, supervisor_dn):
        """Return a person in the correct format."""
        return person.to_ldap(supervisor_dn)

    def get_person_dn(self, person):
        """Return the proper DN for a person."""
        return 'uid=%s,ou=people,%s' % (
                person.username,
                self.ldap.base_dn
            )

    def perform_updates(self, server):
        """Peform LDAP updates for a server."""
        if self.verbose:
            print('  Getting entries from LDAP...')
        self.entries = self.ldap.get_entries()
        if self.verbose:
            print('  Retrieved %s entries from LDAP' % (len(self.entries)))

        # display info about entries
        print('  Entries: %s current, %s new' % (
            len(self.entries),
            len(self.new_entries),
        ))

        # add any ous that are missing
        self.add_ous()

        # get entries to add/delete/update
        add = self.get_entries_to_add()
        delete = self.get_entries_to_delete()
        update = self.get_entries_to_update()

        # display info about diff
        print('  Diff: add %s, delete %s, update %s' % (
            len(add),
            len(delete),
            len(update),
        ))

        # perform updates
        self.delete_entries(delete)
        self.add_entries(add)
        self.update_entries(update)

        # delete any ous we no longer need
        self.delete_ous()

    def add_entries(self, add):
        """Add entries to LDAP."""
        if not add:
            return
        for dn in sorted(add):
            print('    + %s' % (dn))
            # add entry
            entry = self.new_entries[dn]
            self.ldap.add_entry(dn, entry)

    def delete_entries(self, delete):
        """Delete entries from LDAP."""
        if not delete:
            return
        for dn in sorted(delete):
            print('    - %s' % (dn))
            # delete entry
            self.ldap.delete_entry(dn)

    def update_entries(self, update):
        """Update entries in LDAP."""
        if not update:
            return

        for item in sorted(update, key=lambda x: x['dn']):
            # get update data
            dn = item['dn']
            entry = item['entry']
            new_entry = item['new_entry']

            # get a list of all keys from both entries
            keys = list(set(sorted(entry) + sorted(new_entry)))

            # create output list
            output = []

            # for key in the account, look for changes
            for key in sorted(keys):

                # get key values
                o = entry.get(key)
                n = new_entry.get(key)

                # order of emails in "mail" doesn't actually matter
                # if key == 'mail':
                #     o = sorted(o)
                #     n = sorted(n)

                # check for changes
                if o != n:
                    output.append('      %s: %s -> %s' % (key, o, n))

            if output:
                # display output
                print('    * %s:' % (dn))
                print('\n'.join(output))

                # update entry
                self.ldap.modify_entry(dn, entry, new_entry)

                # alternate method uses delete, add
                # self.ldap.delete_entry(dn)
                # self.ldap.add_entry(dn, new_entry)

    def prepare_entries(self, ldap):
        """Prepare LDAP entries."""
        self.ldap = ldap
        if self.verbose:
            print('  Preparing entries for LDAP...')
        self.new_entries = self.prepare_people()
        if self.verbose:
            print('  Prepared %s entries for LDAP.' % (len(self.new_entries)))

    def prepare_people(self):
        """Prepare people records for LDAP."""
        people = {}
        for pid in self.update.people_records:
            # get person object
            person = self.update.people_records[pid]
            dn = self.get_person_dn(person)
            # get supervisor object
            supervisor_dn = None
            if person.supervisor_id:
                supervisor = self.update.people_records[person.supervisor_id]
                supervisor_dn = self.get_person_dn(supervisor)
            # get person in ldap format
            people[dn] = self.get_person(person, supervisor_dn)
        return people
