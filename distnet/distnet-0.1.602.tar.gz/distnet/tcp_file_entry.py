"""
    Manipulate lines in /proc/net/tcp file.
"""


import socket
import network_controller


from hex_manip import ip_from_hex, port_from_hex, int_from_string
from tcp_structs_exceptions import  EntryTCP_FormatError, \
                                    EntryTCP_InitError, \
                                    HostnameNotResolvedError
from tcp_structs import C_STATE


class EntryTCP(object):
    """
        Validated line in TCP file. Supports conversions from hexadecimal.
    """
    def __init__(self, entry_line):

        # entries have fields:
        #   * entry.string      ->  initializer string of EntryTCP constructor
        #   * entry.local_ip    ->  local IP string : re.compile(r'[\.0-9]')
        #   * entry.local_port  ->  local port string : re.compile(r'[0-9]')
        #   * entry.dest_ip     ->  dest IP string : re.compile(r'[\.0-9]')
        #   * entry.dest_port   ->  dest port string : re.compile(r'[0-9]')
        #   * entry.state       ->  0x1 -> 0xB matching C_STATE
        #   * entry.resolved_hostname -> hostname from ns query
        #   * entry.resolved_location -> decision tree result (geoip, whois)


        if not type(entry_line) is str:
            raise EntryTCP_InitError('Entry line must be string. {0}'.format(entry_line), entry_line)

        if entry_line == "":
            raise EntryTCP_FormatError('Entry line must not be null string.', entry_line)

        self.string = entry_line
        if self.string[0] == '\t' or self.string[-1] == '\t' or \
            self.string[0] == ' ' or self.string[-1] == ' ':
            self.string = entry_line.strip('\t ')

        self.local_ip = None
        self.dest_ip = None

        self.local_port = None
        self.dest_port = None

        self.state = None
        self.resolved_hostname = None
        self.resolved_location = None

        self.max_resolve_tries = 2

        issplit = self.string.split(' ')
        ssplit = []

        for item in issplit:
            if item != '':
                ssplit.append(item)

        if len(self.string) < 120:
            raise EntryTCP_FormatError('Line length not recognized as /proc/net format.', "Length was: {0}\n".format(len(self.string)))

        if len(ssplit) < 17:
            raise EntryTCP_FormatError("Columns were less than expected.", 'Number of columns: {0}, with expected: ??\n'.format(len(ssplit)))

        if ssplit[0] == 'sl':
            raise EntryTCP_FormatError("Header line.", "Found header line identifier: {0}\n".format(ssplit[0]))

        #entry_number = ssplit[0]

        """
            See /Documentation for file structure.
            NUMBER  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
        """

        local_addr_field = ssplit[1]
        dest_addr_field = ssplit[2]
        conn_state = ssplit[3]

        s_addr_field = local_addr_field.split(':')
        ip_hex = s_addr_field[0]
        str_port = s_addr_field[1]

        ip_dec = ip_from_hex(ip_hex)
        port = port_from_hex(str_port)

        self.local_ip = ip_dec
        self.local_port = port

        s_addr_field = dest_addr_field.split(':')
        ip_hex = s_addr_field[0]
        str_port = s_addr_field[1]

        ip_dec = ip_from_hex(ip_hex)
        port = port_from_hex(str_port)

        self.dest_ip = ip_dec
        self.dest_port = port

        self.state = conn_state

        #TODO: exceptoins some time
        self.resolved_hostname = self.resolve_hostname()

        try:
            self.resolved_location = self.resolve_country()
        except HostnameNotResolvedError:
            print("Not resolved hostname, so can't check where")


    def resolve_hostname(self):
        resolved_str = None
        if self.max_resolve_tries < 0:
            return
        try:
            resolved_str = network_controller.resolve_hostname(self.dest_ip)
        except socket.gaierror as ge:
            resolved_str = None
        self.resolved_hostname = resolved_str
        self.max_resolve_tries -= 1

    def resolve_country(self):
        if self.resolved_hostname != None:
            self.resolved_location = network_controller.resolve_location(self.resolved_hostname)
        else:
            self.resolve_hostname()
            if self.resolved_hostname == None:
                raise HostnameNotResolvedError('Hostname was not resolved by dns... please retry', str(self.dest_ip))

    def __str__(self):
        rstr = ""
        rstr += "state: " + str(C_STATE.string_from_hex(int_from_string(self.state))) + " \t\t"
        rstr += "from: " + str(self.local_ip) + ":" + str(self.local_port) + " \t\t"
        rstr += "dest: " + str(self.dest_ip) + ":" + str(self.dest_port) + " \t\t"
        rstr += '\n'
        return rstr
