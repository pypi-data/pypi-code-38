import asyncio
import itertools
import logging.config
import os
import sys
from pathlib import Path

from . import (
    __version__, commands, config, controler, get_main_loop, process,
    set_main_widget_policy, utils)

#


async def register_branch_colors(loop):
    screen = loop.screen
    widget = loop.widget
    colors = itertools.cycle([
        color for color in config.PALETTE
        if (color[0]
            and color[0].startswith('branch.')
            and not color[0].endswith('.focus'))])
    focused = itertools.cycle([
        color for color in config.PALETTE
        if (color[0]
            and color[0].startswith('branch.')
            and color[0].endswith('.focus'))])
    cmd = ('--color', 'debug', 'branches', '--closed')
    async for line in process.hg(*cmd):
        name = config.COLOR_REGEXP.search(line).groups()[1]
        name = 'branch.' + name
        screen.register_palette_entry(name, *next(colors)[1:])
        screen.register_palette_entry(name + '.focus', *next(focused)[1:])
        widget._invalidate()
        loop.draw_screen()


async def register_topic_colors(loop):
    screen = loop.screen
    widget = loop.widget
    colors = itertools.cycle([
        color for color in config.PALETTE
        if (color[0]
            and color[0].startswith('topic.')
            and not color[0].endswith('.focus'))])
    focused = itertools.cycle([
        color for color in config.PALETTE
        if (color[0]
            and color[0].startswith('topic.')
            and color[0].endswith('.focus'))])
    cmd = ('--color', 'debug', 'topic')
    try:
        async for line in process.hg(*cmd):
            matching = config.TOPIC_NAME_REGEXP.search(line)
            if not matching:
                # Topic outputs has changed ? or Topic is not installed ?
                # This is a optional feature, just ignore it
                continue
            name = matching.groups()[0]
            name = 'topic.' + name
            screen.register_palette_entry(name, *next(colors)[1:])
            screen.register_palette_entry(name + '.focus', *next(focused)[1:])
            widget._invalidate()
            loop.draw_screen()
    except OSError:
        # Topic is not installed ?
        # This is a optional feature, just ignore it
        pass


async def activate_notify(callback, *, loop=None):
    """Activate Inotify (File System Events)."""
    try:
        import aionotify
    except ImportError:
        return
    loop = loop or asyncio.get_event_loop()
    path = (await commands.get_rootpath())
    watcher = aionotify.Watcher()
    watcher.watch(alias='logs', path=str(path / '.hg'),
                  flags=aionotify.Flags.MODIFY | aionotify.Flags.CREATE | aionotify.Flags.DELETE)
    await watcher.setup(loop)
    try:
        while True:
            await watcher.get_event()
            callback()
    finally:
        watcher.close()


def run(rev=None, debug=False, inotify=False):
    ctrl = controler.maincontroler(rev=rev)
    ctrl.ensure()
    set_main_widget_policy(ctrl.get_widget)
    loop = get_main_loop()
    loop._unhandled_input = ctrl.unhandled_input
    if debug:
        debug_mode(loop)
    utils.ensure_one(register_branch_colors).ensure(loop)
    utils.ensure_one(register_topic_colors).ensure(loop)
    if inotify:
        utils.ensure_one(activate_notify).ensure(ctrl.ensure)
    loop.run()


def parse_args():
    import argparse
    hgpath = os.environ.get('LAIRUCREM_HG')
    if not hgpath:
        hgpath = Path('/usr/bin/hg')
        hgpath = str(hgpath) if hgpath.exists() else 'hg'
    parser = argparse.ArgumentParser(description=globals()['__doc__'])
    parser.add_argument('--rev', '-r',
                        help='show the specified revision set',
                        default=None)
    parser.add_argument('--debug',
                        help='enable debug mode',
                        default=False, action='store_true')
    parser.add_argument('--with-hg', metavar='PATH',
                        default=hgpath,
                        help=('hg script path. Can be set using the '
                              '`LAIRUCREM_HG` environment variable. '
                              '[%(default)r]'))
    parser.add_argument('--curses', default=False, action='store_true',
                        help='Force to use curses interface')
    parser.add_argument('--log-path', default=None, type=Path, metavar='PATH',
                        help='Enable logging into the given file')
    parser.add_argument('-K', '--key-bindings', default='default,mouse',
                        type=lambda val: [s.strip().lower() for s in val.split(',')],
                        help=('coma-separated ordered keybindings. '
                              'Choose from {0}. [%(default)s]'.format(
                                  ', '.join(config.KEYBINDINGS_SETTERS))))
    parser.add_argument('--force-ascii', default=False, action='store_true',
                        help='Force ascii chars in decoration')
    parser.add_argument('--disable-inotify', default=False, action='store_true',
                        help='disable automatic refresh data on repository modification.'
                        'Requires aionotify (https://github.com/rbarrois/aionotify)')
    parser.add_argument('--version', action='store_true',
                        help='show version')
    return parser.parse_args()


def debug_mode(mainloop):
    from lairucrem.utils import monkeypatch
    try:
        from IPython.core.debugger import Pdb
    except ImportError:
        from pdb import set_trace, Pdb
    ctx = []

    @monkeypatch(Pdb, 'do_c')
    @monkeypatch(Pdb, 'do_cont')
    @monkeypatch(Pdb)
    def do_continue(self, arg):
        if ctx:
            ctx.pop()
            mainloop.start()
        self.set_continue()
        return 1

    def _set_trace():
        try:
            mainloop.stop()
            ctx.append(True)
        except Exception:
            pass
        set_trace()


def setup_logging(logpath):
    if logpath:
        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
            'handlers': {
                'file': {
                    'class': 'logging.FileHandler',
                    'filename': logpath,
                    'level': logging.DEBUG,
                }
            },
            'loggers': {
                os.getcwd(): {
                    'handlers': ['file'],
                }
            }
        })
    config.logger = logging.getLogger(os.getcwd())


def apply_keybindings(maps):
    for name in maps:
        config.KEYBINDINGS_SETTERS[name]()


def force_ascii_decoration():
    config.GRAPHNODETEMPLATE = config.GRAPHNODETEMPLATE_ASCII
    config.BORDERS = config.BORDERS_ASCII


def show_version_and_exit():
    print(__version__)
    sys.exit(0)


def main():
    opts = parse_args()
    if opts.version:
        show_version_and_exit()
    setup_logging(opts.log_path)
    config.DEBUG = opts.debug
    if opts.with_hg is not None:
        config._HGPATH = opts.with_hg
    if opts.curses:
        config.SCREEN = 'curses'
    if opts.force_ascii:
        force_ascii_decoration()
    if opts.key_bindings:
        apply_keybindings(opts.key_bindings)
    run(rev=opts.rev, debug=opts.debug, inotify=not opts.disable_inotify)


if __name__ == '__main__':
    main()
