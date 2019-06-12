# Workaround for pyinstaller app to avoid ReactorAlreadyInstalledError
# See https://github.com/kivy/kivy/issues/4182#issuecomment-253159955
import sys
if 'twisted.internet.reactor' in sys.modules:
    del sys.modules['twisted.internet.reactor']

import asyncio
from twisted.internet import asyncioreactor
# Install the asyncio reactor as early as possible
asyncioreactor.install(asyncio.get_event_loop())

import os
from optparse import OptionParser

from trosnoth.run.main import Main
from trosnoth.utils.utils import initLogging


def makeOptionParser():
    parser = OptionParser()
    parser.add_option(
        '-u', '--auth-server', action='store', dest='server',
        help='connect to the given authentication server')
    parser.add_option(
        '-s', '--solo', action='store_const', dest='mode',
        const='solo', default='normal',
        help='run Trosnoth in solo mode.')
    parser.add_option(
        '-i', '--isolate', action='store_const', dest='mode', const='isolate',
        help='run Trosnoth in isolated test mode. Creates client and server '
        'Universe objects, but does not use the network to connect them.')
    parser.add_option(
        '-D', '--delay', action='store', dest='delay', type=float,
        help='implies --isolate. Adds a delay between client and server.')
    parser.add_option(
        '--trosball', action='store_const', dest='mode', const='trosball',
        help='run a solo Trosball game.')
    parser.add_option(
        '-t', '--test', action='store_true', dest='testMode',
        help='run Trosnoth in test mode. This means that players will get 20 '
        'coins each and upgrades will only cost 1 coin.')
    parser.add_option(
        '-b', '--testblock', action='store', dest='mapBlock',
        help='tests the map block with the given filename.')
    parser.add_option(
        '-a', '--aicount', action='store', dest='aiCount',
        help='the number of AIs to include.')
    parser.add_option(
        '-w', '--halfwidth', action='store', dest='halfWidth',
        help='the half map width')
    parser.add_option(
        '-H', '--height', action='store', dest='height', help='the map height')
    parser.add_option(
        '-B', '--block-ratio', action='store', dest='blockRatio', default=0.5,
        type=float, help='the fraction of the map to block off')
    parser.add_option(
        '-m', '--duration', action='store', dest='duration', default=0,
        type=int, help='game duration in minutes')
    parser.add_option(
        '-S', '--stack-teams', action='store_true', dest='stackTeams',
        help='stack all the AI players on one team.')
    parser.add_option(
        '-A', '--aiclass', action='store', dest='aiClass',
        help='the name of the module to import from trosnoth.bots.')
    parser.add_option(
        '--list-ais', action='store_const', dest='mode',
        const='listais', help='list available AI classes and exit')
    parser.add_option(
        '-d', '--debug', action='store_true', dest='debug',
        help='show debug-level messages on console')
    parser.add_option(
        '-p', '--profile', action='store_true', dest='profile',
        help='dump kcachegrind profiling data to trosnoth.log')
    parser.add_option(
        '-r', '--log-reactor-calls', action='store_true',
        dest='log_reactor_calls', help='logs slow reactor calls')
    parser.add_option(
        '-P', '--profile-reactor-calls', action='store_true',
        dest='profile_reactor_calls', help='profiles slow reactor calls')
    parser.add_option(
        '-l', '--log-file', action='store', dest='logFile',
        help='file to write logs to')
    return parser


def listAIs():
    import trosnoth.bots.base
    print('Available AI classes:', file=sys.stderr)
    for name in trosnoth.bots.base.listAIs(showAll=True):
        print('  %s' % (name,), file=sys.stderr)
    return


TESTMODE_AI_COUNT = 7
TESTMODE_HALF_WIDTH = 1
TESTMODE_HEIGHT = 1
BLOCKTEST_HALF_WIDTH = 2
BLOCKTEST_HEIGHT = 1


def processOptions(options, parser):
    if options.server is not None:
        if options.mode != 'normal':
            parser.error('multiple modes specified')
        options.mode = 'auth'

    if options.mode == 'normal' and options.delay:
        options.mode = 'isolate'
    if options.mode == 'normal' and (
            options.testMode or options.mapBlock or
            options.aiCount or options.halfWidth or options.height or
            options.stackTeams or options.aiClass or options.duration):
        options.mode = 'solo'

    if options.aiClass is None:
        options.aiClass = 'ranger'

    if options.mode == 'auth':
        if ':' in options.server:
            host, port = options.server.split(':', 1)
            try:
                port = int(port)
            except ValueError:
                parser.error('%r is not a valid port' % (port,))
        else:
            host = options.server
            port = 6787
        options.host, options.port = host, port
    elif options.mode in ('solo', 'isolate', 'trosball'):
        isolate = options.mode == 'isolate'
        trosball = options.mode == 'trosball'
        options.mode = 'solo'
        if options.mapBlock is None:
            mapBlocks = []
            aiCount = options.aiCount or TESTMODE_AI_COUNT
            halfWidth = options.halfWidth or TESTMODE_HALF_WIDTH
            height = options.height or TESTMODE_HEIGHT
        else:
            mapBlocks = [options.mapBlock]
            aiCount = options.aiCount or 0
            halfWidth = options.halfWidth or BLOCKTEST_HALF_WIDTH
            height = options.height or BLOCKTEST_HEIGHT
        if trosball:
            from trosnoth.levels.trosball import RandomTrosballLevel
            if not options.duration:
                options.duration = 15 * 60
            level = RandomTrosballLevel(
                halfMapWidth=halfWidth, mapHeight=height,
                blockRatio=options.blockRatio, duration=options.duration)
        else:
            level = None
        options.soloArgs = dict(
            isolate=isolate, testMode=options.testMode,
            mapBlocks=mapBlocks, size=(int(halfWidth), int(height)),
            aiCount=int(aiCount),
            stackTeams=options.stackTeams, aiClass=options.aiClass,
            delay=options.delay,
            blockRatio=options.blockRatio,
            duration=options.duration,
            level=level,
        )

    elif options.mode not in ('normal', 'listais'):
        assert False, 'Unknown mode {!r}'.format(options.mode)


def main():
    parser = makeOptionParser()

    options, args = makeOptionParser().parse_args()
    options.replayFile = None
    if len(args) == 1:
        (replayFile,) = args
        if not os.path.exists(replayFile):
            parser.error('Replay file not found: {}'.format(replayFile))
        options.normal = 'replay'
        options.replayFile = replayFile
    elif len(args) > 1:
        parser.error('too many arguments')

    initLogging(options.debug, options.logFile)

    processOptions(options, parser)

    if options.mode == 'listais':
        listAIs()
        return

    if options.mode == 'normal':
        mainObject = Main(showReplay=options.replayFile)
    elif options.mode == 'auth':
        mainObject = Main(serverDetails=(options.host, options.port))
    elif options.mode == 'solo':
        from trosnoth.run import solotest
        mainObject = solotest.Main(**options.soloArgs)
    else:
        assert False, 'Unknown mode'

    if options.log_reactor_calls or options.profile_reactor_calls:
        from trosnoth.utils import twistdebug
        twistdebug.start(profiling=options.profile_reactor_calls)

    if options.profile:
        mainObject.run_with_profiling(twisted=True)
    else:
        mainObject.run_twisted()


if __name__ == '__main__':
    main()
