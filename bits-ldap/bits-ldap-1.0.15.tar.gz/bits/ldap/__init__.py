"""LDAP class file."""

import json
import ldap


class LDAP(object):
    """LDAP class."""

    # default page size (for Active Directory servers)
    pagesize = 1000

    # Ignore errors related to self-signed certificates
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)

    # Don't follow referrals
    ldap.set_option(ldap.OPT_REFERRALS, 0)

    def __init__(
        self,
        uri,
        bind_dn,
        bind_pw,
        base_dn,
        server_type=None,
        domains=None,
        bitsdb_key=None,
        verbose=False
    ):
        """Initialize an instance."""
        self.base_dn = base_dn
        self.bind_dn = bind_dn
        self.bind_pw = bind_pw
        self.bitsdb_key = bitsdb_key
        self.domains = domains
        self.server_type = server_type
        self.uri = uri
        self.verbose = verbose

        # ldap module
        self.ldapmodule = ldap

        # Initialize the LDAP connection
        self.ldapobject = ldap.initialize(uri)
        if self.verbose:
            print('  Connected to LDAP server: %s' % (uri))

        # set the protocol version to version 3
        self.ldapobject.protocol_version = ldap.VERSION3

        # Bind to LDAP
        self.ldapobject.simple_bind_s(bind_dn, bind_pw)
        if self.verbose:
            print('  Bound to LDAP server as: %s' % (bind_dn))

        # get domains
        self.primary = None
        self.secondary = None
        if self.domains:
            if 'primary' in self.domains:
                self.primary = self.domains['primary']
            if 'secondary' in self.domains:
                self.secondary = self.domains['secondary']

    def get_entries(self, filterstr='(objectClass=*)', attrlist=None):
        """Return LDAP entries as a dict by dn."""
        base = self.base_dn
        scope = ldap.SCOPE_SUBTREE
        results = self.search(base, scope, filterstr, attrlist)
        entries = {}
        for dn, entry in results:
            if not dn:
                continue
            entries[dn] = entry
        return entries

    def get_ous(self):
        """Return a list of OUs."""
        return self.get_entries('(objectClass=organizationalUnit)')

    def search(self, base, scope, filterstr='(objectClass=*)', attrlist=None):
        """Perform an LDAP search."""
        # for ad servers, use simple paged resuls
        if self.server_type == 'ad':
            return self.get_paged_results(base, scope, filterstr, attrlist)

        return self.ldapobject.search_ext_s(
            base=base,
            scope=scope,
            filterstr=filterstr,
            attrlist=attrlist,
            # attrsonly=0,
            # serverctrls=None,
            # clientctrls=None,
            # timeout=-1,
            # sizelimit=0,
        )

    def get_ldap_controls(self, pagesize=None, cookie=''):
        """Return LDAP Controls."""
        # set page size for simple paged results
        if not pagesize:
            pagesize = self.pagesize
        # return controls
        return ldap.controls.SimplePagedResultsControl(
            cookie=cookie,
            criticality=True,
            size=pagesize,
        )

    def get_paged_results(self, base, scope, filterstr, attrlist):
        """Perform a paged search query."""
        items = []

        # define ldap controls for paged results with our pagesize
        lc = self.get_ldap_controls()

        # get all pages of results
        cookie = True
        while cookie:

            # get a page of results
            msgid = self.ldapobject.search_ext(
                base=base,
                scope=scope,
                filterstr=filterstr,
                attrlist=attrlist,
                # attrsonly=0,
                serverctrls=[lc],
                # clientctrls=None,
                # timeout=-1,
                # sizelimit=0,
            )

            # get the details of the query result:
            _, rdata, _, serverctrls = self.ldapobject.result3(msgid)

            # add the results data to the items list
            items.extend(rdata)

            # get the cookie for the next request
            cookie = self.set_cookie(lc, serverctrls)

        return items

    def add_entry(self, dn, new):
        """Add an entry in LDAP."""
        ldif = ldap.modlist.addModlist(new)
        try:
            self.ldapobject.add_s(dn, ldif)
            return True
        except ldap.LDAPError as e:
            print('ERROR adding entry: %s' % (dn))
            print(json.dumps(e.message, indent=2, sort_keys=True))

    def delete_entry(self, dn):
        """Delete an entry in LDAP."""
        try:
            self.ldapobject.delete_s(dn)
            return True
        except ldap.LDAPError as e:
            print('ERROR deleting entry: %s' % (dn))
            print(json.dumps(e.message, indent=2, sort_keys=True))

    def modify_entry(self, dn, current, new):
        """Modify an entry in LDAP."""
        ldif = ldap.modlist.modifyModlist(current, new)
        try:
            self.ldapobject.modify_s(dn, ldif)
            return True
        except ldap.LDAPError as e:
            print('ERROR modifying entry: %s' % (dn))
            print(json.dumps(e.message, indent=2, sort_keys=True))

    def create_ou(self, dn):
        """Create a new ou in LDAP."""
        ou = str(dn).split(',')[0].replace('ou=', '')
        record = {
            'objectClass': [
                'top',
                'organizationalUnit',
            ],
            'ou': [ou],
        }
        self.add_entry(dn, record)

    def set_cookie(self, lc, serverctrls):
        """Return the cookie for the next page of results."""
        # get the cookie from the serverctrls
        cookie = serverctrls[0].cookie

        # update the ldap controls object with the new cookie
        lc.cookie = cookie

        # return the cookie
        return cookie
