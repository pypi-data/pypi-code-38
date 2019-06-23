#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" various useful methods """

import unicodedata
import os.path
import datetime
import subprocess
import time
import sys
import random
import inspect
import textwrap
import functools
from twisted.python import procutils
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)


NO_REPOS_DATA = u"repository data unknown"
repos_cache_dict = None
repos_cache = None


def clean_ustr(ustr):
    """Clean unicode string

    remove special characters from unicode string
    """

    def valid_chars(unicode_source):
        for char in unicode_source:
            if unicodedata.category(char) == "Cc" and char != "\n":
                continue
            yield char

    return "".join(valid_chars(ustr))


def logError(failure_):
    """Genertic errback which log the error as a warning, and re-raise it"""
    log.warning(failure_.value)
    raise failure_


def partial(func, *fixed_args, **fixed_kwargs):
    # FIXME: temporary hack to workaround the fact that inspect.getargspec is not working with functools.partial
    #        making partial unusable with current D-bus module (in addMethod).
    #        Should not be needed anywore once moved to Python 3

    ori_args = inspect.getargspec(func).args
    func = functools.partial(func, *fixed_args, **fixed_kwargs)
    if ori_args[0] == "self":
        del ori_args[0]
    ori_args = ori_args[len(fixed_args) :]
    for kw in fixed_kwargs:
        ori_args.remove(kw)

    exec(
        textwrap.dedent(
            """\
    def method({args}):
        return func({kw_args})
    """
        ).format(
            args=", ".join(ori_args), kw_args=", ".join([a + "=" + a for a in ori_args])
        ),
        locals(),
    )

    return method


def xmpp_date(timestamp=None, with_time=True):
    """Return date according to XEP-0082 specification

    to avoid reveling the timezone, we always return UTC dates
    the string returned by this method is valid with RFC 3339
    @param timestamp(None, float): posix timestamp. If None current time will be used
    @param with_time(bool): if True include the time
    @return(unicode): XEP-0082 formatted date and time
    """
    template_date = u"%Y-%m-%d"
    template_time = u"%H:%M:%SZ"
    template = (
        u"{}T{}".format(template_date, template_time) if with_time else template_date
    )
    return datetime.datetime.utcfromtimestamp(
        time.time() if timestamp is None else timestamp
    ).strftime(template)


def generatePassword(vocabulary=None, size=20):
    """Generate a password with random characters.

    @param vocabulary(iterable): characters to use to create password
    @param size(int): number of characters in the password to generate
    @return (unicode): generated password
    """
    random.seed()
    if vocabulary is None:
        vocabulary = [
            chr(i) for i in range(0x30, 0x3A) + range(0x41, 0x5B) + range(0x61, 0x7B)
        ]
    return u"".join([random.choice(vocabulary) for i in range(15)])


def getRepositoryData(module, as_string=True, is_path=False):
    """Retrieve info on current mecurial repository

    Data is gotten by using the following methods, in order:
        - using "hg" executable
        - looking for a .hg/dirstate in parent directory of module (or in module/.hg if
            is_path is True), and parse dirstate file to get revision
        - checking package version, which should have repository data when we are on a dev version
    @param module(unicode): module to look for (e.g. sat, libervia)
        module can be a path if is_path is True (see below)
    @param as_string(bool): if True return a string, else return a dictionary
    @param is_path(bool): if True "module" is not handled as a module name, but as an
        absolute path to the parent of a ".hg" directory
    @return (unicode, dictionary): retrieved info in a nice string,
        or a dictionary with retrieved data (key is not present if data is not found),
        key can be:
            - node: full revision number (40 bits)
            - branch: branch name
            - date: ISO 8601 format date
            - tag: latest tag used in hierarchie
            - distance: number of commits since the last tag
    """
    global repos_cache_dict
    if as_string:
        global repos_cache
        if repos_cache is not None:
            return repos_cache
    else:
        if repos_cache_dict is not None:
            return repos_cache_dict

    if sys.platform == "android":
        #  FIXME: workaround to avoid trouble on android, need to be fixed properly
        repos_cache = u"Cagou android build"
        return repos_cache

    KEYS = ("node", "node_short", "branch", "date", "tag", "distance")
    ori_cwd = os.getcwd()

    if is_path:
        repos_root = os.path.abspath(module)
    else:
        repos_root = os.path.abspath(os.path.dirname(module.__file__))

    try:
        hg_path = procutils.which("hg")[0]
    except IndexError:
        log.warning(u"Can't find hg executable")
        hg_path = None
        hg_data = {}

    if hg_path is not None:
        os.chdir(repos_root)
        try:
            hg_data_raw = subprocess.check_output(
                [
                    "hg",
                    "log",
                    "-r",
                    "-1",
                    "--template",
                    "{node}\n"
                    "{node|short}\n"
                    "{branch}\n"
                    "{date|isodate}\n"
                    "{latesttag}\n"
                    "{latesttagdistance}",
                ]
            )
        except subprocess.CalledProcessError:
            hg_data = {}
        else:
            hg_data = dict(zip(KEYS, hg_data_raw.split("\n")))
            try:
                hg_data["modified"] = "+" in subprocess.check_output(["hg", "id", "-i"])
            except subprocess.CalledProcessError:
                pass
    else:
        hg_data = {}

    if not hg_data:
        # .hg/dirstate method
        log.debug(u"trying dirstate method")
        if is_path:
            os.chdir(repos_root)
        else:
            os.chdir(os.path.abspath(os.path.dirname(repos_root)))
        try:
            with open(".hg/dirstate") as hg_dirstate:
                hg_data["node"] = hg_dirstate.read(20).encode("hex")
                hg_data["node_short"] = hg_data["node"][:12]
        except IOError:
            log.debug(u"Can't access repository data")

    # we restore original working dir
    os.chdir(ori_cwd)

    if not hg_data:
        log.debug(u"Mercurial not available or working, trying package version")
        try:
            import pkg_resources

            pkg_version = pkg_resources.get_distribution(C.APP_NAME_FILE).version
            version, local_id = pkg_version.split("+", 1)
        except ImportError:
            log.warning("pkg_resources not available, can't get package data")
        except pkg_resources.DistributionNotFound:
            log.warning("can't retrieve package data")
        except ValueError:
            log.info(
                u"no local version id in package: {pkg_version}".format(
                    pkg_version=pkg_version
                )
            )
        else:
            version = version.replace(".dev0", "D")
            if version != C.APP_VERSION:
                log.warning(
                    "Incompatible version ({version}) and pkg_version ({pkg_version})".format(
                        version=C.APP_VERSION, pkg_version=pkg_version
                    )
                )
            else:
                try:
                    hg_node, hg_distance = local_id.split(".")
                except ValueError:
                    log.warning("Version doesn't specify repository data")
                hg_data = {"node_short": hg_node, "distance": hg_distance}

    repos_cache_dict = hg_data

    if as_string:
        if not hg_data:
            repos_cache = NO_REPOS_DATA
        else:
            strings = [u"rev", hg_data["node_short"]]
            try:
                if hg_data["modified"]:
                    strings.append(u"[M]")
            except KeyError:
                pass
            try:
                strings.extend([u"({branch} {date})".format(**hg_data)])
            except KeyError:
                pass
            try:
                strings.extend([u"+{distance}".format(**hg_data)])
            except KeyError:
                pass
            repos_cache = u" ".join(strings)
        return repos_cache
    else:
        return hg_data
