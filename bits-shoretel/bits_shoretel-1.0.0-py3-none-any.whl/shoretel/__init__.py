"""Shoretel class file."""

from bits.mysql import MySQL


class Shoretel(MySQL):
    """Shoretel class."""

    def __init__(
        self,
        server,
        user,
        password,
        port=4308,
        db='shoreware',
        cdr_port=4309,
        cdr_db='shorewarecdr',
        verbose=False
    ):
        """Initialize an Shoretel class instance."""
        MySQL.__init__(self, server, port, user, password, db, verbose)

        # connect to cdr database
        self.cdr = MySQL(
            server=server,
            port=cdr_port,
            user=user,
            password=password,
            db=cdr_db,
        )

    # def get_calls(self):
    #     """Return a list of Shoretel calls."""
    #     return self.cdr.get_table('`call`')

    def get_calls_stats_by_extension(self):
        """Return a dict of call statistics by extension."""
        query = """SELECT
                count(*) AS count,
                Extension as extension,
                t.Name as type
            FROM `call` c
            LEFT JOIN `calltype` t
                ON t.CallType = c.CallType
            GROUP BY Extension, t.Name
            ORDER BY count DESC;"""

        cur = self.cdr.create_dictcursor()
        cur.execute(query)
        stats = {}
        for row in cur:
            ext = row['extension']
            call_type = row['type']
            count = row['count']
            if ext not in stats:
                stats[ext] = {}
            stats[ext][call_type] = count
        return stats

    def get_phones(self):
        """Return a dictionary of phones in Shoretel."""
        cur = self.create_dictcursor()
        query = """SELECT guiloginname,
                tabaddresses.FirstName, tabaddresses.LastName, tabAddresses.EmailAddress,
                ports.JackNumber, ports.PortId,
                users.AddressID, users.UserDN
            FROM Users
            LEFT JOIN tabaddresses ON tabaddresses.AddressID = users.AddressID
            LEFT JOIN ports ON ports.CurrentDN = users.UserDN;"""
        cur.execute(query)
        self.phones = {}
        for p in cur:
            extension = p['UserDN']
            self.phones[extension] = p
        return self.phones

    def get_ports(self):
        """Return a list of Shoretel ports."""
        return self.get_table('ports')

    def get_ports_dict(self, key='PortID'):
        """Return a dict of Shoretel ports."""
        ports = {}
        for p in self.get_ports():
            k = p.get(key)
            if k:
                ports[k] = p
        return ports

    def get_tabaddresses(self):
        """Return a list of Shoretel tabaddresses."""
        return self.get_table('tabaddresses')

    def get_tabaddresses_dict(self, key='AddressID'):
        """Return a dict of Shoretel tabaddresses."""
        tabaddresses = {}
        for u in self.get_tabaddresses():
            k = u.get(key)
            if k:
                tabaddresses[k] = u
        return tabaddresses

    def get_users(self):
        """Return a list of Shoretel users."""
        return self.get_table('users')

    def get_users_dict(self, key='UserDN'):
        """Return a dict of Shoretel users."""
        users = {}
        for u in self.get_users():
            k = u.get(key)
            if k:
                users[k] = u
        return users

    def update_email(self, addressid, email):
        """Update the EmailAddress in shoretel."""
        if not addressid:
            return
        cur = self.db.cursor()
        querystring = 'UPDATE tabaddresses SET EmailAddress = %s WHERE AddressID = %s;'
        queryfields = [email, addressid]
        cur.execute(querystring, queryfields)
        self.db.commit()
        cur.close()
        return True

    def update_first_name(self, addressid, first_name):
        """Update the FirstName in shoretel."""
        if not addressid:
            return
        cur = self.db.cursor()
        querystring = 'UPDATE tabaddresses SET FirstName = %s WHERE AddressID = %s;'
        queryfields = [first_name, addressid]
        cur.execute(querystring, queryfields)
        self.db.commit()
        cur.close()
        return True

    def update_last_name(self, addressid, last_name):
        """Update the LastName in shoretel."""
        if not addressid:
            return
        cur = self.db.cursor()
        querystring = 'UPDATE tabaddresses SET LastName = %s WHERE AddressID = %s;'
        queryfields = [last_name, addressid]
        cur.execute(querystring, queryfields)
        self.db.commit()
        cur.close()
        return True

    def update_port(self, portid, location):
        """Update the port location in shoretel."""
        if not portid:
            return
        cur = self.db.cursor()
        jack = 'NULL'
        if location:
            jack = '%s' % (location)
        querystring = 'UPDATE ports SET JackNumber = %s WHERE PortId = %s;'
        queryfields = [jack, portid]
        cur.execute(querystring, queryfields)
        self.db.commit()
        cur.close()
        return True
