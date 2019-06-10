from chibi.atlas import Chibi_atlas
from chibi.snippet import regex
from chibi.snippet.iter import chunk_each
import re


class Interface( Chibi_atlas ):
    def up( self ):
        raise NotImplementedError

    def down( self ):
        raise NotImplementedError


class Network( Chibi_atlas ):

    @classmethod
    def load_from_string( cls, s ):
        split = s.split( '\n' )
        interfaces_raw = chunk_each(
            split, lambda x: regex.test( r'^\d+:', x  ) )

        result = cls()
        for interface_raw in interfaces_raw:
            interface_raw = "\n".join( interface_raw )
            interface_name = re.search(
                r"^.*: (?P<interface>\w+.+):",
                interface_raw ).groupdict()[ 'interface' ]
            interface = Interface()
            result[ interface_name ] = interface

            interface.ip_v4 = re.search(
                r"inet\s*(?P<ip_v4>\d+.\d+.\d+.\d+/\d+)",
                interface_raw, re.MULTILINE )
            if interface.ip_v4:
                interface.ip_v4 = interface.ip_v4.groupdict()[ 'ip_v4' ]

        return result


class Wireless( Network ):
    pass
