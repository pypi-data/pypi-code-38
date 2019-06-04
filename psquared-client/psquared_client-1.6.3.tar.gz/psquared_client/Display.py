#
# Module: Display
#
# Description: Displays the ET created from the response of a PSquared server in a readable manner.
#

from __future__ import print_function

PADDING = len('  1970-01-01T00:00:000000-00:00 SUBMITTED ')

def configurations(application):
    """Displays all the configurations contained in an application document

    Keyword arguments:
    application -- the application document whose configurations should be displayed.
    """

    c = application.findall('configurations/configuration')
    print('Currently active configurations:')
    for config in c:
         if None == config.find('description') or None == config.find('description').text:
             descriptionToUse = ""
         else:
             descriptionToUse = ': ' + config.find('description').text
         print("  " + config.find('name').text + descriptionToUse)
    print()


def versions(configuration):
    """Displays all the versions of a named configuration

    Keyword arguments:
    configuration -- the configuration document that should be displayed.
    """

    v = configuration.find('default-version')
    if None == v or None == v.text:
        defaultUrl = None
        defaultNote = ''
    else:
        defaultUrl = v.text
        defaultNote = " (* indicates the default version)"
    v = configuration.findall('known-versions/known-version')
    print('Currently active version for configuration "' + configuration.find('name').text + '"' + defaultNote)
    for vers in v:
        if defaultUrl == vers.find('uri').text:
            header = "* "
        else:
            header = "  "
        if None == vers.find('description') or None == vers.find('description').text:
            descriptionToUse = ""
        else:
            descriptionToUse = ': ' + vers.find('description').text
        print(header + vers.find('name').text + descriptionToUse)
    print()


def entry(e, name = None, max = 0, changed = False):
    """Displays the entry to a Realized State.
    """

    if None == name:
        label = ''
    else:
        label = name + ' ' * (max - len(name)) + ' : '
    if None == changed:
        status = 'C    '
    else:
        status = '    '
    header = status + label + e.find('completed').text + ' ' + e.find('state').text
    message = e.find('message')
    if None == message or None == message.text:
        messageToUse = ''
    else:
        messageToUse = message.text.replace('\n', '\n' + ' ' * (PADDING) )
    print(header +  ' ' * (PADDING + (max + 3) - len(header)) + messageToUse)


def info(name, version, report, items = None, note = None):
    """Displays the set of Realized States.

    Arguments:
    name    -- the name of the configuration whose command URL should be returned.
    version -- the version of the named configuration whose command URL should be returned.
    report  -- the report document that should be displayed.
    items   -- the sequence of items to display.
    note    -- the alternate node to be printed (default None).
    """

    states = report.findall('realized-state')
    if None == items:

        # This is the case when there was no set of items explicitly requested.
        if 0 == len(states):
            print('There are no items to report on for version "' + version + '" of configuration "' + name + '"')
            return
        print('Results for version "' + version + '" of configuration "' + name + '"')
        names = report.findall('realized-state/item')
        max = 0
        for n in names:
            name = n.text
            if len(name) > max:
                max = len(name)
        for state in states:
            entry(state.find('entry'), state.find('item').text, max)
        return

    if 0 == len(items):
        print('There are no items to report on for version "' + version + '" of configuration "' + name + '"')
        return

    index = 0
    if index == len(states):
        state = None
    else:
        state = states[index]
    for item in items:
        if None != state and item == state.find('item').text:
            if None == note:
                print('Current state of of "' + item + '" with version "' + version + '" of configuration "' + name + '"')
            else:
                print(note)
            entry(state.find('entry'), changed = (None == state.find('unchanged')))
            print
            index += 1
            if index == len(states):
                state = None
            else:
                state = states[index]
        else:
            print('There has been no processing of "' + item + '" with version "' + version + '" of configuration "' + name + '"')
            print()


def histories(configuration, version, report, items):
    """Displays the set of Histories.
    """

    histories = report.findall('history')
    index = 0
    if index == len(histories):
        history = None
    else:
        history = histories[index]
    for item in items:
        if None != history and item == history.find('current-state/item').text:
            print('History of "' + item + '" with version "' + version + '" of configuration "' + configuration + '"')
            entries=history.findall('.//entry')
            entries.reverse()
            for e in entries:
                entry(e)
            print
            index += 1
            if index == len(histories):
                history = None
            else:
                history = histories[index]
        else:
            print('There is no History of "' + item + '" with version "' + version + '" of configuration "' + configuration + '"')
            print()
