import ldap


class DirectoryActions:
    """
    Class containing methods to work with an LDAP server to perform login actions and resolve details about users.
    """

    def __init__(self, conf_data):
        """
        Constructor.
        :param conf_data: dictionary containing configuration data for the app
        """
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        self.conf_data = conf_data

    def login(self, employeeid, password):
        """
        Perform login operation against an LDAP connection.
        :param employeeid: employee ID of user trying to log in
        :param password: password of user trying to log in
        :return: either details of user or False on failure
        """
        con = ldap.initialize(self.conf_data['LDAP_CONN_INFO']['server'])
        dn = self.conf_data['LDAP_CONN_INFO']['dn_base'] % employeeid
        try:
            con.simple_bind_s(dn, password)
            return DirectoryActions.get_userdetails(con, employeeid)
        except ldap.LDAPError as error_message:
            print(error_message)
            # return "Failed login on bind: dn=%s, pass=%s, error_message=%s" % (dn, password, error_message)
            return False

    def service_account_login(self):
        """
        Log into the LDAP server using a service account, which will allow us to search instead of only log in.
        :return: LDAP connection object or False on failure
        """
        con = ldap.initialize(self.conf_data['LDAP_CONN_INFO']['server'])
        try:
            con.simple_bind_s(self.conf_data['LDAP_SERVICE_ACCOUNT']['dn'],
                              self.conf_data['LDAP_SERVICE_ACCOUNT']['password'])
            return con
        except ldap.LDAPError as error_message:
            print(error_message)
            return False

    @staticmethod
    def search(con, search_term):
        """
        Generic search method against an LDAP connection.
        :param con: LDAP server connection object
        :param search_term: search term
        :return: dictionary of LDAP search results
        """
        base = ''
        scope = ldap.SCOPE_SUBTREE
        retrieve_attributes = None
        result_set = []
        timeout = 0
        try:
            result_id = con.search(base, scope, search_term, retrieve_attributes)
            while True:
                result_type, result_data = con.result(result_id, timeout)
                if result_data is []:
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        result_set.append(result_data)
            if len(result_set) == 0:
                print("Empty result set: search-term=%s" % search_term)
                # return "Empty result set: search-term=%s" % search_term
                return False
            return result_set[0][0][1]
        except ldap.LDAPError as error_message:
            print(error_message)
            # return error_message
            return False

    @staticmethod
    def get_userdetails(con, employeeid):
        """
        Get details about the user with the specified employee ID.
        :param con: LDAP server connection object
        :param employeeid: user employee ID
        :return: dictionary with user details or false on failure
        """
        dir_result = DirectoryActions.search(con, "cn=%s" % employeeid)
        if not dir_result:
            return False
        if dir_result['employeeStatus'][0] != 'Active':
            return False
        return dir_result
