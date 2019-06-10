import xmltodict
from chibi.command import command
from chibi.atlas import Chibi_atlas
from chibi.snippet.dict import hate_ordered_dict, remove_xml_notatation
from chibi.snippet.xml import guaranteed_list


def nmap( *args, stdout=True ):
    if stdout:
        stdout = 'pipe'
    command_result, error, return_code = command(
        'nmap', '-oX', '-', *args, stdout=stdout )
    result = xmltodict.parse( command_result )
    result = hate_ordered_dict( result )
    result = remove_xml_notatation( result )
    result = guaranteed_list( result, 'host' )
    return Chibi_atlas( result )
