import os
import time
from fnmatch import fnmatch
from os import getcwd
from os.path import join, splitext, split
from shutil import copyfile

import click
from watchdog.events import FileSystemEventHandler, EVENT_TYPE_MODIFIED, EVENT_TYPE_MOVED, EVENT_TYPE_CREATED
from watchdog.observers import Observer

from kudu.config import ConfigOption
from kudu.defaults import default_pitcher_folders
from kudu.types import PitcherFileType


class PitcherFilePathConverter(object):
    def __init__(self, pfile):
        self.pfile = pfile

    def convert(self, relpath):
        raise NotImplementedError()


class InteractivePathConverter(PitcherFilePathConverter):
    basedir = 'zip'

    def convert(self, relpath):
        dirname = splitext(self.pfile['filename'])[0]
        if fnmatch(relpath, 'thumbnail.png'):
            relpath = dirname + '.png'
        return join(self.basedir, dirname, relpath)


class PresentationPathConverter(InteractivePathConverter):
    basedir = 'slides'

    def convert(self, relpath):
        if fnmatch(relpath, join('iPadOnly', '*')):
            relpath = os.sep.join(split(relpath)[1:])
        return super(PresentationPathConverter, self).convert(relpath)


class InterfacePathConverter(PitcherFilePathConverter):
    def convert(self, relpath):
        if fnmatch(relpath, join('interface', '*')):
            dirname = splitext(self.pfile['filename'])[0]
            relpath = join(dirname, *split(relpath)[1:])
        return relpath


class CopyFilesEventHandler(FileSystemEventHandler):

    def __init__(self, src, dst, converter):
        self.src = src
        self.dst = dst
        self.converter = converter

    def on_any_event(self, event):
        if event.event_type in [EVENT_TYPE_MODIFIED, EVENT_TYPE_MOVED, EVENT_TYPE_CREATED] and not event.is_directory:
            src_path = event.src_path if event.event_type != EVENT_TYPE_MOVED else event.dest_path
            src_relpath = os.path.relpath(src_path)

            dst_relpath = self.converter.convert(src_relpath)
            dst_path = join(self.dst, dst_relpath)
            dst_dirpath = os.path.dirname(dst_path)

            if not os.path.exists(dst_dirpath):
                os.makedirs(dst_dirpath)

            click.echo("Copying file: %s" % src_relpath, nl=False)

            try:
                copyfile(src_path, dst_path)
                click.echo("\rCopying file: %s, done." % src_relpath)
            except (IOError, OSError) as e:
                # File most likely does not exist
                click.echo(e, err=True)

            click.echo("\rCopying file: %s, done." % src_relpath)


def countfiles(top):
    click.echo('Counting files', nl=False)

    count = 0
    for root, dirs, files in os.walk(top):
        count += len(files)
        click.echo('\rCounting files: %d' % count, nl=False)

    click.echo('\rCounting files: %d, done.' % count)
    return count


def copyfiles(src, dst, converter):
    total = countfiles(src)
    curr = 0

    if not os.path.exists(dst):
        os.makedirs(dst, 0755)

    click.echo('Copying files', nl=False)

    for root, dirs, files in os.walk(src):

        for name in files:
            curr += 1
            click.echo('\rCopying files: %d/%d' % (curr, total), nl=False)

            src_path = os.path.join(root, name)
            src_relpath = os.path.relpath(src_path)

            dst_relpath = converter.convert(src_relpath)
            dst_path = join(dst, dst_relpath)
            dst_dirpath = os.path.dirname(dst_path)

            if not os.path.exists(dst_dirpath):
                os.makedirs(dst_dirpath)

            copyfile(join(root, name), dst_path)

    click.echo('\rCopying files: %d/%d, done.' % (curr, total))


def watchfiles(src, dst, converter):
    event_handler = CopyFilesEventHandler(src, dst, converter)
    observer = Observer()
    observer.schedule(event_handler, src, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


@click.command()
@click.option('--file', '-f', 'pfile',
              cls=ConfigOption, config_name='file_id',
              prompt=True, type=PitcherFileType(category=['zip', 'presentation', '']))
@click.option('--pitcher-folders', '-pf',
              cls=ConfigOption, config_name='pitcher_folders',
              prompt=True, default=lambda: default_pitcher_folders(),
              type=click.Path(exists=True, file_okay=False, writable=True))
def link(pfile, pitcher_folders):
    cwd = getcwd()

    if pfile['category'] == 'zip':
        converter = InteractivePathConverter(pfile)
    elif pfile['category'] == 'presentation':
        converter = PresentationPathConverter(pfile)
    elif pfile['category'] == '':
        converter = InterfacePathConverter(pfile)
    else:
        raise NotImplementedError()

    copyfiles(cwd, pitcher_folders, converter)
    watchfiles(cwd, pitcher_folders, converter)
