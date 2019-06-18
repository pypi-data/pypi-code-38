import pprint

from . import session, settings, authenticate, get_group_events
from ..decorators import MainCommands


@MainCommands(
    ('list', 'List the keys and value in the settings of this module.', []),
    ('get', 'Get a value from the settings of this module.', [
        (['key'], {'help': "The key to get in this module' settings."}),
    ]),
    ('set', 'Set a key to a value.', [
        (['key'], {'help': "The key to set in this module' settings."}),
        (['value'], {'help': "The value of the key to set in this module' settings."})
    ]),
    ('list-groups', 'List the commonly used groups.', []),
    ('add-group', 'Add a group to the list of commonly used groups.', [
        (['group'], {'help': 'The name of the group to add.'})
    ]),
    ('remove-group', 'Remove a group to the list of commonly used groups.', [
        (['group'], {'help': 'The name of the group to delete.'})
    ]),
    ('list-events', 'List the events of a given group.', [
        (['group'], {'help': 'The name of the group to query.'})
    ]),
    ('rsvp', "Reserve a spot at a given group's event.", [
        (['group'], {'help': 'The name of the group to query.'}),
        (['event'], {'help': 'The event number to rsvp to.'})
    ])
)
def main(args):

    # basic settings commands
    if args.command == 'list':
        for key in settings:
            print('{0}: {1}'.format(key, settings[key]))
    elif args.command == 'get':
        if args.key in settings:
            print('{0}: {1}'.format(args.key, settings[args.key]))
    elif args.command == 'set':
        settings[args.key] = args.value
        print('{0}: {1}'.format(args.key, settings[args.key]))

    # done with basic settings commands
    if args.command in ('list', 'get', 'set'):
        return 0

    # module-specific commands
    if args.command == 'list-groups':
        if 'groups' not in settings:
            print('Settings has no key for "groups".')
            return 1
        print('Groups:')
        print('=' * 60)
        for group in settings['groups']:
            print(group)

    # add a group to the common groups
    elif args.command == 'add-group':
        if 'groups' in settings:
            settings['groups'].append(args.group)
        else:
            settings['groups'] = [args.group]

    # remove a group from the common groups
    elif args.command == 'remove-group':
        if 'groups' not in settings:
            print('Settings has no key for "groups".')
            return 1
        settings['groups'].remove(args.group)

    # list the events for a specific group
    elif args.command == 'list-events':
        authenticate()
        events = get_group_events(args.group)
        pprint.pprint(events)

    elif args.command == 'rsvp':
        print('todo: rsvp')


    # write back out the settings if they changed
    if settings.changed:
        settings.write()

    return 0
