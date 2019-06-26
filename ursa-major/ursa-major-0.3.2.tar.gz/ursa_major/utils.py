# -*- coding: utf-8 -*-
# Copyright (c) 2018  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Chenxiong Qi <cqi@redhat.com>
#            Qixiang Wan <qwan@redhat.com>

""" Various utilities """
import os
import re
import gi
gi.require_version('Modulemd', '1.0')  # noqa
from gi.repository import Modulemd

from jinja2 import Environment, PackageLoader
from ursa_major.logger import log


def validate_mail_address(addr):
    """
    Validate e-mail address format.
    """

    mail_pattern = r"^[_a-z0-9-]+(.[_a-z0-9-]+)*@[a-z0-9-]+(.[a-z0-9-]+)*(.[a-z]{2,4})$"
    match = re.match(mail_pattern, addr)
    if match:
        return True

    log.error("E-mail address <%s> is not valid.", addr)
    return False


def jinja2_env(category):
    env = Environment(
        loader=PackageLoader("ursa_major", "templates/" + category)
    )

    def regex_replace(s, find, replace):
        return re.sub(find, replace, s)
    env.filters['regex_replace'] = regex_replace

    return env


def get_env_var(var, raise_if_not_exist=False):
    """
    Get variable value from os environ

    :param raise_if_not_exist: If true, raise ValueError when variable is
        not present in os environ, otherwise return None.
    """
    if var not in os.environ and raise_if_not_exist:
        raise ValueError("ENV variable '{}' does not exist.".format(var))
    return os.environ.get(var, None)


def load_mmd(yaml, is_file=False):
    """ Create Modulemd.Module object from string or file and return. """
    try:
        if is_file:
            mmd = Modulemd.Module().new_from_file(yaml)
        else:
            mmd = Modulemd.Module().new_from_string(yaml)
        # If the modulemd was v1, it will be upgraded to v2
        mmd.upgrade()
    except Exception:
        error = 'Invalid modulemd: {0}'.format(yaml)
        log.error(error)
        raise

    return mmd


def requires_included(mmd_requires, config_requires):
    """Test if requires defined in config is included in module metadata

    :param mmd_requires: a mapping representing either buildrequires or
        requires, which is returned from function ``peek_requires`` and
        ``peek_buildrequires``.
    :type mmd_requires: dict[str, Modulemd.SimpleSet]
    :param dict config_requires: a mapping representing either buildrequires or
        requires defined in config file. This is what to check if it is
        included in ``mmd_requires``.
    :return: True if all requires inside ``config_requires`` are included in
        module metadata. Otherwise, False is returned.
    :rtype: bool
    """
    for req_name, req_streams in config_requires.items():
        if req_name not in mmd_requires:
            return False

        if not isinstance(req_streams, list):
            req_streams = [req_streams]

        neg_reqs = set(s[1:] for s in req_streams if s.startswith('-'))
        pos_reqs = set(s for s in req_streams if not s.startswith('-'))

        streams = set(mmd_requires[req_name].dup())
        if streams & neg_reqs:
            return False
        if pos_reqs and not (streams & pos_reqs):
            return False
    return True


def mmd_has_requires(mmd, requires):
    """
    Check whether a module represent by the mmd has requires.

    :param mmd: Modulemd.Module object
    :param requires: dict of requires, example:
        {'platform': 'f28', 'python3': 'master'}
    """
    deps_list = mmd.peek_dependencies()
    mmd_requires = deps_list[0].peek_requires() if deps_list else {}
    return requires_included(mmd_requires, requires)


def mmd_has_buildrequires(mmd, config_buildrequires):
    """
    Check if a module metadata represented by the mmd has buildrequires.

    :param mmd: a module metadata.
    :type mmd: Modulemd.Module
    :param dict config_buildrequires: a mapping of buildrequires defined in
        config file to match the module metadata, for example:
        ``{'platform': 'f28', 'python3': 'master'}``.
    :return: True if the specified module metadata has the buildrequires
        defined in config.
    :rtype: bool
    """
    deps_list = mmd.peek_dependencies()
    mmd_requires = deps_list[0].peek_buildrequires() if deps_list else {}
    return requires_included(mmd_requires, config_buildrequires)
