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

import json

from ursa_major.koji_service import KojiService
from ursa_major.logger import log
from ursa_major.mbs import MBS
from ursa_major import MBS_BUILD_STATES


class BaseHandler(object):
    def __init__(self, config, *args, **kwargs):
        self.config = config

        # global options
        self.dry_run = False

        self._mbs = None
        self._koji = None

        self.tag_config_file = None
        # Loaded from config file on-demand
        self._tag_config = None

    def set_args(self, args):
        self.args = args

    @property
    def tag_config(self):
        if self._tag_config is None:
            raise RuntimeError("tag_config is not set, call load_tag_config first")
        return self._tag_config

    def load_tag_config(self):
        """ Load config from tag config file into self.tag_config. """
        with open(self.tag_config_file, 'r') as f:
            log.info("Loading tag configuration from %s", self.tag_config_file)
            self._tag_config = json.load(f)

    def write_tag_config(self, config=None):
        """ Write the tag config file with content.

        :param config: a dict of json file, if None, content is self.tag_config
        """
        if config is not None:
            content = config
        else:
            content = self.tag_config

        if self.dry_run:
            log.info('DRYRUN: write tag config to file: %s',
                     json.dumps(content, indent=2, sort_keys=True))
        else:
            with open(self.tag_config_file, 'w') as f:
                json.dump(content, f, indent=4, sort_keys=True, separators=(',', ': '))

    @property
    def koji(self):
        if self._koji is None:
            raise RuntimeError("koji is not set, call connect_koji first")
        return self._koji

    def connect_koji(self, dry_run=False):
        """Setup koji client session."""
        koji_profile = self.config.get('koji', 'profile')
        log.info("Connecting to Koji with profile: %s", koji_profile)
        self._koji = KojiService(koji_profile, dry_run=dry_run)

    @property
    def mbs(self):
        if self._mbs is None:
            raise RuntimeError("MBS is not set, call connect_mbs first")
        return self._mbs

    def connect_mbs(self):
        """Create a MBS intance."""
        mbs_url = self.config.get('mbs', 'server_url')
        log.info("Connecting to MBS with url: %s", mbs_url)
        self._mbs = MBS(mbs_url)

    def find_module_tags_from_koji_inheritance(self, tag, module_config):
        """
        Find koji tags in specified tag's inheritance data that belongs to
        the module of module_config.

        :param str tag: tag name. This tag's parent tags will be retrieved from
            Koji and from which to find out module(s)' tag(s).
        :param module_config: instance of ModuleConfig, whose module build(s)
            will be queried from MBS and find out which module(s)' koji_tag are
            the parent tag of ``tag``.
        :type module_config: :class:`ModuleConfig`
        :return: list of tag name(s) which are parent tag of ``tag``.
        :rtype: list[str]
        """
        tags_from_koji = set(t['name'] for t in self.koji.get_inheritance_data(tag))
        modules = self.mbs.get_modules(
            name=module_config.name,
            stream=module_config.stream,
            state=[MBS_BUILD_STATES['ready'], MBS_BUILD_STATES['garbage']])
        tags_from_mbs = set(module['koji_tag'] for module in modules)
        return list(set(tags_from_koji) & set(tags_from_mbs))
