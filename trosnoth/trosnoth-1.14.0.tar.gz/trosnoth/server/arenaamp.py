from twisted.protocols import amp


class AlreadyCalled(Exception):
    '''
    Some commands should only be called once.
    '''


class NotYetListening(Exception):
    '''
    This command cannot be called before calling ArenaListening.
    '''


class ArenaListening(amp.Command):
    '''
    Arena -> Auth

    Indicates that the arena process is ready to accept clients.
    '''

    arguments = [
        (b'token', amp.String()),
    ]
    response = []
    errors = {
        AlreadyCalled: b'NOT_ALLOWED'
    }


class RegisterAuthTag(amp.Command):
    '''
    Auth -> Arena

    Registers the given auth token with an authorised user.
    '''

    arguments = [
        (b'username', amp.Unicode()),
        (b'authTag', amp.Integer()),
    ]
    response = []


class ArenaInfoChanged(amp.Command):
    '''
    Arena -> Auth

    Gives info about the arena, to be displayed in the web interface.
    '''

    arguments = [
        (b'status', amp.Unicode(optional=True)),
        (b'players', amp.Integer(optional=True)),
        (b'paused', amp.Boolean(optional=True)),
    ]


class SetArenaInfo(amp.Command):
    '''
    Auth -> Arena

    Instructs the arena to change settings such as pausing game and changing
    ability for teams to shoot or capture zones.
    '''

    arguments = [
        (b'paused', amp.Boolean(optional=True)),
        (b'teamAbilityJSON', amp.Unicode(optional=True)),
        (b'action', amp.Unicode(optional=True)),
    ]


class StartLevel(amp.Command):
    '''
    Auth -> Arena

    Instructs the arena to start the scenario with the given info.
    '''

    arguments = [
        (b'infoJSON', amp.Unicode()),
    ]
