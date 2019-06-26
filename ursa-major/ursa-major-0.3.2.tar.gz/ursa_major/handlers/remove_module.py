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

from ursa_major.handlers.base import BaseHandler
from ursa_major.logger import log


class RemoveModuleHandler(BaseHandler):
    def run(self):
        self.dry_run = self.args.dry_run

        self.tag = self.args.tag
        self.module_name = self.args.module_name
        self.module_stream = self.args.module_stream
        self.module_requires = {}
        if self.args.module_requires is not None:
            self.module_requires = dict(self.args.module_requires)
        if self.args.module_buildrequires is not None:
            self.module_buildrequires = dict(self.args.module_buildrequires)
        else:
            self.module_buildrequires = {}
        self.tag_config_file = self.args.tag_config_file
        self.not_update_config = self.args.not_update_config

        self.connect_koji()
        self.connect_mbs()

        self.load_tag_config()
        if self.tag not in self.tag_config.keys():
            log.warning("Tag %s is not present in tag config file %s",
                        self.tag, self.tag_config_file)

        try:
            tag_inheritance = self.koji.get_inheritance_data(self.tag)
        except Exception as e:
            raise RuntimeError("Unable to get inheritance data of tag {}:\n"
                               "{!s}".format(self.tag, e))

        inheritance_tags = [t['name'] for t in tag_inheritance]

        log.info("Querying modules of '%s:%s' from MBS with requires: %r and "
                 "buildrequires: %r",
                 self.module_name, self.module_stream, self.module_requires,
                 self.module_buildrequires)

        modules = self.mbs.get_modules(
            name=self.module_name,
            stream=self.module_stream,
            requires=self.module_requires,
            buildrequires=self.module_buildrequires)

        module_tags = [m['koji_tag'] for m in modules]
        match_tags = list(set(inheritance_tags) & set(module_tags))
        if match_tags:
            log.info("Found matched module tags under %s: %r", self.tag, match_tags)
            self.koji.remove_tags_from_inheritance(self.tag, match_tags)
        else:
            log.info("No match tag found in tag %s's inheritance data", self.tag)

        if self.not_update_config:
            log.info("Not update config is specified, not update config")
            return

        if self.tag not in self.tag_config.keys():
            log.info("Tag config file doesn't contain tag %s, not update config file",
                     self.tag)
            return

        module_configs = self.tag_config[self.tag].get('modules', [])

        found_config = None
        for config in module_configs:
            if all((
                self.module_name == config['name'],
                self.module_stream == config['stream'],

                # NOTE: we only find config that matches module_requires exactly
                self.module_requires == config.get('requires', {}),
                # Same as requires
                self.module_buildrequires == config.get('buildrequires', {})
            )):
                found_config = config
                break

        if found_config is None:
            log.info("Doesn't find match config under tag %s, not update config file",
                     self.tag)
        else:
            module_configs.remove(found_config)
            log.info("Updating tag config file to remove module:\n%r", found_config)
            self.write_tag_config()
