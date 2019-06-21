"""LDAP Update class for ServiceNow."""

from bits.ldap.server import Server


class ServiceNow(Server):
    """ServiceNow LDAP Update class."""

    def get_person(self, person, supervisor_dn):
        """Return a person in the correct format."""
        return person.to_servicenow(supervisor_dn)
