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
from ursa_major import ModuleConfig, ModuleConfigCmp, MBS_BUILD_STATES
from ursa_major.logger import log


class AddModuleHandler(BaseHandler):
    """Handler to add a module to config file and add its koji tag to inheritance data"""

    def run(self):
        self.dry_run = self.args.dry_run
        self.debug = self.args.debug

        self.force = self.args.force

        self.tag_config_file = self.args.tag_config_file
        self.load_tag_config()

        self.wait_regen_repo = self.args.wait_regen_repo

        # the koji tag we operate against
        self.op_tag = self.args.tag

        tags_to_remove = []
        tag_to_add = None
        inheritance_updated = False

        self.connect_mbs()
        self.connect_koji(dry_run=self.dry_run)
        self.koji.login()

        # By default, if necessary, should update specified tag's
        # inheritance data to add or edit the latest module's tag,
        # and the tag config file should be updated as well.
        to_update_inheritance = True
        to_update_config = True

        if self.args.update_inheritance_only:
            to_update_config = False
            log.warning("Will not update config file because --update-inheritance-only "
                        "is specified, even if the specified module config does not "
                        "exist in tag config file.")
        if self.args.update_config_only:
            to_update_inheritance = False
            log.warning("Will not update tag %s's inheritance data because --update-config-only "
                        "is specified, even if the latest module build's tag does not exists in "
                        "inheritance with specified config", self.op_tag)

        if self.args.module_requires:
            module_requires = dict(self.args.module_requires)
        else:
            module_requires = None

        if self.args.module_buildrequires:
            module_buildrequires = dict(self.args.module_buildrequires)
        else:
            module_buildrequires = None

        input_module_config = ModuleConfig(
            module_config=dict(
                name=self.args.module_name,
                stream=self.args.module_stream,
                priority=self.args.priority,
                requires=module_requires,
                buildrequires=module_buildrequires,
            ))

        # existing tags of specified module from cmdline
        existing_input_module_tags = \
            self.find_module_tags_from_koji_inheritance(self.op_tag, input_module_config)

        if existing_input_module_tags and to_update_inheritance:
            log.info("There are tags exist for the module specified in command line: %s",
                     existing_input_module_tags)
            # Add these existing tags to list, but we may remove the one of
            # latest_module_tag later
            tags_to_remove.extend(existing_input_module_tags)

        # Find out the latest module tag of specified module in MBS
        latest_module_tag = self.find_latest_module_tag(input_module_config)
        if latest_module_tag:
            log.info("Found koji tag %s of the latest module in MBS with module config '%s'",
                     latest_module_tag, input_module_config)

            # in all possible cases, this is the tag we're going to add if needed
            tag_to_add = latest_module_tag

        else:
            log.warning("Can't find any built module in MBS with module config '%s', "
                        "we will not add any new module tag to inheritance data",
                        input_module_config)
            if not self.force:
                log.warning("Will not update inheritance data nor tag config file, consider "
                            "to run with --force to allow updating")
                to_update_inheritance = False
                to_update_config = False

        # find any module exist in config with the same name and stream
        stock_module_config = self.find_module_config(self.op_tag, input_module_config)
        if stock_module_config:
            log.info("Found module config in tag configuration that has same "
                     "name and stream of the specified module: %s",
                     stock_module_config)
        else:
            log.info('No corresponding module config found in tag config file.')

        config_diff = input_module_config.compare(stock_module_config)

        # In all of the cases, we just need to find out the tags to be removed,
        # and then check:
        # 1. if tag_to_add is None:
        #    remove all tags_to_remove
        # 2. if tag_to_add is not None and in tags_to_remove:
        #    (a). if tag's specified priority has same value with the value
        #         in current inheritance data, remove tag_to_add from
        #         tags_to_remove, and then remove tags in tags_to_remove
        #         TODO: or maybe we should do nothing in this case?
        #    (b). if tag's specified priority is different than the value
        #         in current inheritance data, remove tag_to_add from
        #         tags_to_remove, then add tag_to_add (with the specified
        #         priority) and remove tags in tags_to_remove at the same time
        # 3. if tag_to_add is not None and not in tags_to_remove:
        #    remove tags in tags_to_remove and add tag_to_add

        if config_diff == ModuleConfigCmp.NEW:
            log.info("The specified module does not exist in tag config file "
                     "under tag '%s'", self.op_tag)
            # this is a new module in config, check whether the priority exist
            existing_priorities = self.get_module_priorities_in_config(self.op_tag)
            if input_module_config.priority in existing_priorities:
                raise RuntimeError("The specified priority '{}' conflicts with the "
                                   "existing priorities under tag '{}'".format(
                                       input_module_config.priority, self.op_tag))
            # in this case, the possible tags need to remove is the existing_input_tags,
            # which has been added to tags_to_remove before

        elif config_diff == ModuleConfigCmp.DIFFERENT:
            # Module in config changes, it can be a change in requires,
            # buildrequires or priority.

            log.info("A module with same name and stream exists in tag config file "
                     "under tag '%s', but has different configuration", self.op_tag)

            # Check whether the specified priority conflicts with other modules
            existing_priorities = self.get_module_priorities_in_config(self.op_tag)
            if (input_module_config.priority != stock_module_config.priority and
                    input_module_config.priority in existing_priorities):
                raise RuntimeError("The specified priority '{}' conflicts with the "
                                   "existing priorities under tag '{}'".format(
                                       input_module_config.priority, self.op_tag))

            if to_update_inheritance:
                if (input_module_config.requires != stock_module_config.requires or
                        input_module_config.buildrequires != stock_module_config.buildrequires):
                    # module requires changed, we need to remove old tags
                    existing_stock_tags = self.find_module_tags_from_koji_inheritance(
                        self.op_tag, stock_module_config)
                    if existing_stock_tags:
                        log.info("Module config is changed, there are tags of old module "
                                 "exist in inheritance data:\n%s", existing_stock_tags)
                        # Add these tags to remove list
                        tags_to_remove.extend(existing_stock_tags)
                        # we may adding duplicated tags?
                        tags_to_remove = list(set(tags_to_remove))

                # else: module priority changed, that will be handled later,
                # nothing to do here

        elif config_diff == ModuleConfigCmp.SAME:
            log.info("An module exist in tag config file under tag '%s' with the "
                     "same configuration, we will not update anything", self.op_tag)
            to_update_inheritance = False
            to_update_config = False

        if to_update_inheritance:
            if tag_to_add is None and tags_to_remove:
                remove_tags = [{'name': t} for t in tags_to_remove]
                log.info("No module tag to add and going to remove tags:\n%s",
                         tags_to_remove)
                self.koji.update_tag_inheritance(self.op_tag,
                                                 remove_tags=remove_tags)
                inheritance_updated = True

            if tag_to_add is not None:
                if tag_to_add in tags_to_remove:
                    tags_to_remove.remove(tag_to_add)
                    remove_tags = [{'name': t} for t in tags_to_remove]
                    if remove_tags:
                        log.info("Going to remove old tags: %s", tags_to_remove)

                    cur_inheritance = self.koji.get_inheritance_data(self.op_tag)
                    old_tag_data = [d for d in cur_inheritance if d['name'] == tag_to_add].pop()
                    if old_tag_data.get('priority') == input_module_config.priority:
                        # don't need to add the tag since it already exist with
                        # the same priority as specified
                        log.info("The latest module tag %s already exists with same priority "
                                 "as specified, will not add any tag to %s's inheritance data",
                                 tag_to_add, self.op_tag)
                        if remove_tags:
                            self.koji.update_tag_inheritance(self.op_tag,
                                                             remove_tags=remove_tags)
                            inheritance_updated = True
                        # remove list is empty, we don't need to remove any tag
                    else:
                        # latest module tag is in inheritance data, but priority is different,
                        # we need to update the priority
                        log.info("The latest module tag %s exists but with different priority, "
                                 "will update its priority in inheritance", tag_to_add)
                        edit_tags = [{'name': tag_to_add,
                                      'priority': input_module_config.priority}]
                        self.koji.update_tag_inheritance(self.op_tag,
                                                         remove_tags=remove_tags,
                                                         edit_tags=edit_tags)
                        inheritance_updated = True

                # tag_to_add is not in tags_to_remove
                else:
                    add_tags = [{'name': tag_to_add,
                                 'priority': input_module_config.priority}]
                    remove_tags = [{'name': t} for t in tags_to_remove]
                    log.info("Going to add latest module tag: %s", tag_to_add)
                    log.info("Going to remove old tags: %r", tags_to_remove)
                    self.koji.update_tag_inheritance(self.op_tag,
                                                     add_tags=add_tags,
                                                     remove_tags=remove_tags)
                    inheritance_updated = True

        if inheritance_updated:
            if self.koji.is_build_tag(self.op_tag):
                build_tags = [self.op_tag]
            else:
                build_tags = self.koji.find_build_tags(self.op_tag)

            if not build_tags:
                log.warning("No build tag found for %s, not regen any repo", self.op_tag)
            else:
                log.info("Found build tags for %s: %r", self.op_tag, build_tags)
                self.koji.regen_repos(build_tags, wait=self.wait_regen_repo)

        if to_update_config:
            self.add_module_to_config(self.op_tag, input_module_config)

        # Log out from Koji session before leave
        self.koji.logout()

    def get_module_priorities_in_config(self, tag):
        """
        Get all priorities of modules under specified tag in tag config file.

        :param tag: tag name
        """
        config = self.tag_config.get(tag, {})
        modules = config.get('modules', [])
        return [m['priority'] for m in modules]

    def find_latest_module_tag(self, module_config):
        """
        Find the latest ready module which matches the module_config
        in MBS, return its koji_tag, or return None if not found.

        :param module_config: an object of `ModuleConfig`
        :return: tag name or None
        """
        modules = self.mbs.get_modules(
            buildrequires=module_config.buildrequires,
            requires=module_config.requires,
            name=module_config.name,
            stream=module_config.stream,
            state=MBS_BUILD_STATES['ready'],
            page=1)  # we only need the default first page items
        if modules:
            return modules[0]['koji_tag']
        else:
            return None

    def find_module_config(self, tag, module_config):
        """
        Find matched module config under specified tag by name and
        stream in config file

        :param tag: tag name
        :return: object of `ModuleConfig` if found. None otherwise.
        :rtype: ModuleConfig
        """
        tag_config = self.tag_config
        if tag not in tag_config:
            return None
        modules = tag_config[tag].get('modules', [])
        for config in modules:
            if config['name'] == module_config.name and \
                    config['stream'] == module_config.stream:
                return ModuleConfig(config)
        return None

    def add_module_to_config(self, tag, module_config):
        """
        Add the module config to tag config file

        :param tag: tag name, module config will be added under this tag
        :param module_config: an object of `ModuleConfig`
        """
        tag_config = self.tag_config
        config = tag_config.setdefault(tag, {})
        modules = config.setdefault('modules', [])
        module_config_dict = dict(name=module_config.name,
                                  stream=module_config.stream,
                                  priority=module_config.priority)
        if module_config.requires:
            module_config_dict['requires'] = module_config.requires
        if module_config.buildrequires:
            module_config_dict['buildrequires'] = module_config.buildrequires

        modules_with_same_name_stream = [m for m in modules if
                                         m['name'] == module_config.name and
                                         m['stream'] == module_config.stream]

        if len(modules_with_same_name_stream) > 1:
            raise RuntimeError("Unexpected error, found multiple modules in config "
                               "file with same name (%s) and stream (%s)".format(
                                   module_config.name, module_config.stream))

        if len(modules_with_same_name_stream) == 0:
            log.info("Adding module config to tag %s in tag config file:\n%s",
                     tag, module_config_dict)
            modules.append(module_config_dict)

        if len(modules_with_same_name_stream) == 1:
            log.info("Found one existing module config with same name and stream, "
                     "update it with:\n%s", module_config_dict)
            modules.remove(modules_with_same_name_stream[0])
            modules.append(module_config_dict)

        self.write_tag_config()
