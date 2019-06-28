# -*- coding: utf-8 -*-
from builtins import bytes, str
from datetime import datetime, timedelta
from dateutil.parser import isoparse
from dateutil.tz import tzlocal, tzutc
from errno import ENOENT
import math
import os
import shutil
import subprocess

import click
import tabulate

from spell.cli.log import logger


SIZE_SUFFIXES = ["B", "K", "M", "G", "T", "P"]


# TODO(jay): Replace with `shutil.which` when we drop Python 2 support
def is_installed(cmd):
    with open(os.devnull, "w") as f:
        try:
            subprocess.call(cmd, stdout=f, stderr=f)
        except OSError as e:
            if e.errno == ENOENT:
                return False
            raise e
    return True


def with_emoji(emoji, msg, utf8):
    if utf8:
        return u"{} {}".format(emoji, msg)
    return msg


def ellipses(utf8=True):
    return u"…" if utf8 else "..."


def right_arrow(utf8=True):
    return u"→" if utf8 else "->"


def tabulate_rows(rows, headers=None, columns=None, raw=False):
    def extract_attrs(row_objs):
        for row_obj in row_objs:
            yield [getattr(row_obj, col) for col in columns]

    if headers is None:
        headers = ()

    if columns is not None:
        rows = extract_attrs(rows)

    if raw:
        echo_raw(rows)
    else:
        click.echo(tabulate.tabulate(rows,
                                     headers=headers,
                                     tablefmt="plain",
                                     numalign="left"))


# convert_to_local_time is an alternative to prettify_time that returns the input
# timestamp string in a non-relative way, similar to the way that `ls -al` prints
# timestamps in the local timezone of the user
def convert_to_local_time(t, include_seconds=True):
    if isinstance(t, datetime):
        dt = t.replace(tzinfo=tzutc()).astimezone(tzlocal())
    else:
        dt = isoparse(t).astimezone(tzlocal())
    if datetime.now(tzlocal()) - dt < timedelta(days=364):
        format_str = "%b %d %H:%M:%S" if include_seconds else "%b %d %H:%M"
        return dt.strftime(format_str)
    else:
        return dt.strftime("%b %d %Y")


# prettify_time returns a nice human readable representation of a time delta from 'time' to now
# if the default elapsed=False is specified, the return value describes a historical time (e.g., " 2 days ago")
# if elapsed=True, the return value describes an elapsed time (e.g, "2 days")
def prettify_time(time, elapsed=False):
    """prettify a datetime object"""
    now = datetime.now(tzutc())
    if not elapsed and (now - time).days > 14:
        # date for differences of over 2 weeks
        return "{:%Y-%m-%d}".format(time)

    time_str = prettify_timespan(time, now)
    if elapsed:
        return time_str
    return "{} ago".format(time_str)


# prettify_timespan returns a nice human readable representation of a time delta from 'start' to 'end'
def prettify_timespan(start, end):
    """prettify a timedelta object"""
    delta = end - start
    if delta.days > 1:
        # days ago for differences of over a day
        return "{} days".format(delta.days)
    if delta.days > 0:
        return "1 day"
    if delta.seconds > 7200:
        # hours ago for differences of over an hour
        return "{} hours".format(delta.seconds // 3600)
    if delta.seconds > 3600:
        return "1 hour"
    if delta.seconds > 120:
        # minutes ago for differences of over a minute
        return "{} minutes".format(delta.seconds // 60)
    if delta.seconds > 60:
        return "1 minute"
    return "{} seconds".format(delta.seconds)


def prettify_size(size):
    """prettify an int representing file size in bytes"""
    if size < 0:
        raise ValueError("Negative size value {}".format(size))
    if size == 0:
        return "0B"

    order = int(math.log(size, 2) / 10)
    if order == 0:
        return "{}B".format(size)
    if order >= len(SIZE_SUFFIXES):
        raise ValueError("Unparsable size value {}".format(size))
    size_suffix = SIZE_SUFFIXES[order]

    scaled = size / 2**(10.*order)
    if scaled >= 10:
        return "{}{}".format(int(scaled), size_suffix)
    return "{:.1f}{}".format(scaled, size_suffix)


def truncate_string(raw, width, fixed_width=False, utf8=True):
    truncated = False

    s = str(raw)
    split = s.split('\n')
    if len(split) > 1:
        s = split[0]
        truncated = True
    dots = ellipses(utf8)
    if len(s) > width:
        s = s[:width-len(dots)]
        truncated = True
    if truncated:
        s = s + dots
    if fixed_width:
        s = s.ljust(width)
    return s


def echo_raw(data):
    """print rows of data (iterable of iterables) to stdout in CSV form"""
    ts = click.get_text_stream('stdout', encoding='utf-8')
    ts.writelines([','.join(row) + '\n' for row in data])


def remove_path(path, prompt=False):
    """remove file or directory at path"""
    if os.path.isdir(path):
        if prompt:
            click.confirm("Spell will now delete the existing directory {}. Do you wish to continue?".format(path),
                          abort=True)
        logger.info("removing existing directory: {}".format(path))
        shutil.rmtree(path)
    if os.path.isfile(path):
        if prompt:
            click.confirm("Spell will now delete the existing file {}. Do you wish to continue?".format(path),
                          abort=True)
        logger.info("removing existing file: {}".format(path))
        os.remove(path)


def add_known_host(hostname):
    """ If hostname is not in ~/.ssh/known_hosts this function uses ssh-keyscan
    to add it. This allows us to avoid showing the user a yes/no would you like
    to continue connecting prompt, and still provides the safety of strict host
    checking
    """
    with open(os.path.expanduser('~/.ssh/known_hosts'), 'ab+') as f:
        f.seek(0)
        for line in f:
            if line.startswith(bytes(hostname, encoding='utf-8')):
                return
        # Write stderr to devnull to avoid printing extra information returned
        # by ssh-keyscan, i.e. '# git.spell.run:22 SSH...'
        with open(os.devnull, 'w') as devnull:
            key = subprocess.check_output(['ssh-keyscan', '-t', 'ecdsa', hostname], stderr=devnull)
            f.write(key)


def cli_ssh_key_path(config_handler):
    return os.path.join(config_handler.spell_dir, "spell.pem")


def cli_ssh_config_path(config_handler):
    return os.path.join(config_handler.spell_dir, "ssh_config")


def write_ssh_config_file(config_handler):
    with open(cli_ssh_config_path(config_handler), 'w') as f:
        f.write("# empty spell ssh config")


class LazyChoice(click.Choice):
    """ A type similar to click.Choice that loads its choices lazily. It is initialized with a function that
    returns an iterable (probably a generator) for the possible choices. It can optionally be case-sensitive
    or insensitive, and it defaults to case-insensitive
    """

    name = 'lazy_choice'

    def __init__(self, choice_fn, case_sensitive=False):
        self.choice_fn = choice_fn
        super(LazyChoice, self).__init__(self.choice_fn(), case_sensitive=case_sensitive)

    def __getattribute__(self, name):
        # Override any calls to "choices" with the generator
        if name == "choices":
            return self.choice_fn()
        return super(LazyChoice, self).__getattribute__(name)

    def convert(self, value, param, ctx):
        if value is None:
            return None
        for choice in self.choices:
            if self.case_sensitive and value == choice or \
               not self.case_sensitive and value.lower() == choice.lower():
                return choice
        self.fail('invalid choice: {}. (choose from {})'.format(
            value, ', '.join(self.choices)), param, ctx)


class HiddenOption(click.Option):
    """ A subclass of click.Option that hides its existence from help outputs """

    def get_help_record(self, ctx):
        return
