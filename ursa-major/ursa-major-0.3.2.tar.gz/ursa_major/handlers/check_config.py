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

import six
import sys
import json

from ursa_major import MBS_BUILD_STATES
from ursa_major.handlers.base import BaseHandler
from ursa_major.logger import log


class CheckConfigHandler(BaseHandler):

    def validate_mandatory_module_config_fields(self, module_config):
        """ Validate a module's mandatory config fields.

        :param module_config: a module config dict
        :return: a generator iterator error messages
        """

        fields = (
            ('name', six.text_type),
            ('stream', six.text_type),
            ('priority', int),
        )

        for field_name, field_type in fields:
            if field_name not in module_config:
                yield ("Missing {} in module config: {}"
                       .format(field_name, module_config))
                continue
            if not isinstance(module_config.get(field_name), field_type):
                yield ("{} should be {} in module config: {}"
                       .format(field_name, field_type, module_config))

    def run(self):
        self.tag_config_file = self.args.tag_config_file
        self.allow_non_ready_module = self.args.allow_non_ready_module

        self.connect_koji()
        self.connect_mbs()

        self.load_tag_config()

        for tag, config in self.tag_config.items():
            log.info("Checking config of tag %s", tag)
            try:
                tag_inheritance = self.koji.get_inheritance_data(tag)
            except Exception as e:
                log.error("Unable to get inheritance data of tag %s: %s", tag, str(e))
                continue

            tag_owners = config.get('owners', None)
            if tag_owners is None or not tag_owners:
                log.warning("Tag %s: missing owners", tag)
            if not isinstance(tag_owners, list):
                log.warning("Tag %s: owners should be a list of emails", tag)

            module_configs = config.get('modules', [])

            if not module_configs:
                log.warning("Tag %s: no module specified", tag)
                continue

            # save modules by priority for checking duplicate priorities
            # exampe: { 100: [module_1, module_2], 200: [module_3]}
            modules_by_priority = {}

            for module_config in module_configs:
                config_string = json.dumps(module_config, indent=2)
                log.debug("Checking config:\n%s", config_string)

                mandatory_field_errors = []
                for error in self.validate_mandatory_module_config_fields(
                        module_config):
                    mandatory_field_errors.append(error)
                    log.error(error)

                if mandatory_field_errors:
                    continue

                if module_config.get('runtime_deps', None) is not None:
                    log.error("'runtime_deps' in module config is deprecated, "
                              "please use 'requires' instead")
                module_priority = module_config.get('priority')
                modules_with_cur_priority = modules_by_priority.setdefault(module_priority, [])
                modules_with_cur_priority.append(module_config.get('name'))
                if len(modules_with_cur_priority) > 1:
                    log.error("More than one module found with same priority '%s' in "
                              "config:\n%s", module_priority, modules_with_cur_priority)

                modules_of_config = self.mbs.get_modules(
                    requires=module_config.get('requires', {}),
                    buildrequires=module_config.get('buildrequires'),
                    name=module_config['name'],
                    stream=module_config['stream'],
                    state=MBS_BUILD_STATES['ready'],
                    page=1,  # we only need the default first page items
                )

                if not (modules_of_config or self.allow_non_ready_module):
                    log.error("Can't find ready modules in MBS with config: %s", module_config)
                    continue

                # checking existing NAME+STREAM modules, don't include criteria
                # of requires or buildrequires, and not limit to ready modules as
                # some old tags may be garbaged
                existing_modules = self.mbs.get_modules(
                    name=module_config['name'],
                    stream=module_config['stream'],
                    state=[MBS_BUILD_STATES['ready'], MBS_BUILD_STATES['garbage']]
                )
                module_tags = [m['koji_tag'] for m in existing_modules]

                non_priorities = [t['priority'] for t in tag_inheritance
                                  if t['name'] not in module_tags]
                if module_config['priority'] in non_priorities:
                    log.error("Module %s has same priority with a tag in tag %s's inheritance",
                              module_config, tag)

        if log.error.counter > 0:
            log.error("Found error(s) in config")
            sys.exit(1)
