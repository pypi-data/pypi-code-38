"""LDAP Update class for Gnarwl."""

from bits.ldap.server import Server


class Gnarwl(Server):
    """Gnarwl LDAP Update class."""

    def prepare_entries(self, ldap):
        """Prepare LDAP entries."""
        self.ldap = ldap
        # forwarders
        if self.verbose:
            print('  Preparing forwarders for Gnarwl LDAP...')
        self.new_entries = self.prepare_forwarders()
        if self.verbose:
            print('  Found %s Gnarwl forwarders' % (len(self.new_entries)))

    def prepare_forwarders(self):
        """Prepare Gnarwl forwarders."""
        forwarders = {}
        for record in self.update.gnarwl_records:
            dn = self.get_gnarwl_dn(record)
            forwarders[dn] = record.to_ldap()
        return forwarders
