import json

from chibi.command import command
from chibi.atlas import Chibi_atlas
from chibi.snippet.dict import keys_to_snake_case


class Journal_status( Chibi_atlas ):
    pass


def systemctl( option, *services, stdout=True):
    if stdout:
        stdout = 'pipe'
    command_result, error, return_code = command(
        'systemctl', option, '--output=json', *services, stdout=stdout )
    return command_result, error, return_code


def status( *services ):
    command_result, error, return_code = systemctl( 'status', *services )
    pre_parse = command_result.split( '\n' )
    end_of_status = pre_parse.index( '' )

    status = pre_parse[ :end_of_status ]
    pre_messages = pre_parse[ end_of_status:]
    messages = [ json.loads( m ) for m in pre_messages if m ]

    result = Journal_status(
        human=status, messages=messages, properties=show( *services ) )
    return result


def enable( *services ):
    command_result, error, return_code = systemctl( 'enable', *services )
    return command_result, error, return_code


def start( *services ):
    command_result, error, return_code = systemctl( 'start', *services )
    return command_result, error, return_code


def restart( *services ):
    command_result, error, return_code = systemctl( 'restart', *services )
    return command_result, error, return_code


def daemon_reload( *services ):
    command_result, error, return_code = systemctl( 'daemon-reload' )
    return command_result, error, return_code


def show( *service, no_page=True ):
    if no_page:
        service = list( service )
        service.insert( 0, '--no-page' )

    command_result, error, return_code = systemctl( 'show', *service )
    list_of_status = command_result.split( '\n' )

    result = {}
    for status in list_of_status:
        if status:
            s = status.split( '=' )
            result[ s[0].strip() ] = s[1].strip()
    return Chibi_atlas( keys_to_snake_case( result ) )
