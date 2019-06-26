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

import copy
import json
import traceback

from ursa_major import ModuleConfig
from ursa_major.handlers.base import BaseHandler
from ursa_major.logger import log
from ursa_major.mail import MailAPI
from ursa_major.utils import get_env_var, mmd_has_requires, mmd_has_buildrequires


class ModuleInfo(object):
    def __init__(self):
        fields = ('build_id', 'koji_tag', 'mmd',
                  'name', 'stream', 'version', 'context',
                  'requires', 'buildrequires')
        for field in fields:
            setattr(self, field, None)

    @classmethod
    def from_mbs_message(cls, mbs, message):
        """
        Create an instance from mbs state change message.

        :param message: message in dict format
        :param mbs: MBS instance
        :return: an instance of ModuleInfo
        """
        modinfo = cls()
        modinfo.koji_tag = message['koji_tag']
        modinfo.build_id = message['id']

        mmd = mbs.get_module_mmd(modinfo.build_id)
        modinfo.mmd = mmd
        modinfo.name = mmd.peek_name()
        modinfo.stream = mmd.peek_stream()
        modinfo.version = str(mmd.peek_version())
        modinfo.context = mmd.peek_context()

        deps_list = mmd.peek_dependencies()
        requires = deps_list[0].peek_requires() if deps_list else {}
        buildrequires = deps_list[0].peek_buildrequires() if deps_list else {}
        modinfo.requires = {name: stream.dup() for
                            name, stream in requires.items()}
        modinfo.buildrequires = {name: stream.dup() for
                                 name, stream in buildrequires.items()}

        return modinfo

    @property
    def nsvc(self):
        return "{}:{}:{}:{}".format(
               self.name, self.stream, self.version, self.context)

    @property
    def short_info(self):
        return {
            'build_id': self.build_id,
            'koji_tag': self.koji_tag,
            'nsvc': self.nsvc,
            'requires': self.requires,
        }


class AddTagHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super(AddTagHandler, self).__init__(*args, **kwargs)
        self.send_mail = False
        self.wait_regen_repo = False

    @staticmethod
    def get_module_config(module_configs, modinfo):
        """
        Get the module config from configs which matches the module represented
        by the modinfo.

        :param module_configs: a list of module config
        :type module_configs: list[dict]
        :param modinfo: instance of ModuleInfo
        :type modinfo: :class:`ModuleInfo`
        :return: the matched module config. None is returned if no module
            config matches the module metadata.
        :rtype: dict
        :raises RuntimeError: if more than one module configs match the
            specified module metadata.
        """
        matched = []
        for config in module_configs:
            name = config['name']
            stream = config['stream']
            if not (name == modinfo.name and stream == modinfo.stream):
                continue
            dep_requires = config.get('buildrequires')
            if dep_requires and not mmd_has_buildrequires(modinfo.mmd, dep_requires):
                continue
            requires = config.get('requires', {})
            if requires and not mmd_has_requires(modinfo.mmd, requires):
                continue
            matched.append(config)

        if len(matched) == 0:
            return None
        if len(matched) > 1:
            error = ("Multiple config items match with module <{}>, unable to "
                     "determine which item we should use: {!s}".format(
                         modinfo.nsvc, matched))
            log.error(error)
            raise RuntimeError(error)
        return matched[0]

    def add_module_to_tag(self, tag, modinfo, module_config):
        """
        Add koji tag of module represent by modinfo to specified tag's
        inheritance data, config options are in module_config.

        Note: while adding module tag to inheritance, we remove old tags
        of the module as well. We do it in one call to avoid race
        condition.

        :param tag: tag name
        :param modinfo: ModuleInfo instance
        :param module_config: a module config object.
        :type module_config: :class:`ModuleConfig`
        :return: a tuple of (added_tags, removed_tags)
        :rtype: tuple[list[str], list[str]]
        """
        old_tags = self.find_module_tags_from_koji_inheritance(tag, module_config)

        # if this is a tag already exists, we will try to update it
        if modinfo.koji_tag in old_tags:
            old_tags.remove(modinfo.koji_tag)

        add_tag_info = {
            'name': modinfo.koji_tag,
            'priority': module_config.priority
        }

        self.koji.login()
        added_tags, removed_tags = self.koji.update_tag_inheritance(
            tag,
            add_tags=[add_tag_info],
            remove_tags=[{'name': name} for name in old_tags]
        )

        # regen repo for build tags only when inheritance data is updated
        if added_tags or removed_tags:
            if self.koji.is_build_tag(tag):
                build_tags = [tag]
            else:
                build_tags = self.koji.find_build_tags(tag)

            if not build_tags:
                log.warning("No build tag found for %s, not regen any repo", tag)
            else:
                log.info("Found build tags for '%s': %r", tag, build_tags)
                self.koji.regen_repos(build_tags, wait=self.wait_regen_repo)

        return added_tags, removed_tags

    def run(self):
        try:
            ci_message_string = get_env_var(self.args.module_from_env,
                                            raise_if_not_exist=True)
            ci_message = json.loads(ci_message_string)
            log.info('Received MBS state change message:\n%s',
                     json.dumps(ci_message, indent=2, sort_keys=True))

        except Exception as e:
            error = "Fail to load '{!s}' from os environ: {!s}".format(self.args.module_from_env, e)
            log.error(error)
            raise RuntimeError(error)

        if ci_message.get('state_name', None) != 'ready':
            log.info("MBS build state is not 'ready', skipping")
            return

        self.dry_run = self.args.dry_run
        self.send_mail = self.args.send_mail
        self.tag_config_file = self.args.tag_config_file
        self.wait_regen_repo = self.args.wait_regen_repo

        self.load_tag_config()

        if self.send_mail:
            if not self.config.has_section('mail'):
                log.error("Sending mail is enabled, but config doesn't contain mail settings")
                raise RuntimeError("Missing mail settings")
            mail_config = dict(self.config.items('mail'))
            self.mail_api = MailAPI(mail_config)
            self.mail_data = {'build_url': get_env_var('BUILD_URL')}

        self.connect_koji(dry_run=self.dry_run)
        self.connect_mbs()

        modinfo = ModuleInfo.from_mbs_message(self.mbs, ci_message)
        if self.send_mail:
            self.mail_data['module'] = modinfo.short_info

        errors = []
        for tag, tag_config in self.tag_config.items():
            tag_owners = tag_config.get('owners', [])
            if not tag_owners:
                log.warning("Sending mail is enabled, but no owners set for tag %s, "
                            "will not send mail", tag)

            conf_modules = tag_config.get('modules', [])
            try:
                module_config = self.get_module_config(conf_modules, modinfo)
                if module_config is None:
                    log.info("Module %s is not listed in tag %s, skipping this tag.",
                             modinfo.nsvc, tag)
                    continue

                # the module we're handling matches config of this tag
                added_tags, removed_tags = self.add_module_to_tag(
                    tag, modinfo, ModuleConfig(module_config))

                if self.dry_run or not tag_owners:
                    continue

                if (added_tags or removed_tags) and self.send_mail and tag_owners:
                    # send tag update success mail
                    mail_subject = 'Tag {} is updated'.format(tag)
                    content = copy.deepcopy(self.mail_data)
                    content['tag'] = tag
                    content['added_tags'] = added_tags
                    content['removed_tags'] = removed_tags
                    log.info("Sending mail to %r with content:\n%r", str(tag_owners), content)
                    self.mail_api.send_mail('add-tag.txt', tag_owners,
                                            subject=mail_subject, data=content)

            except Exception as e:
                error = ("Error while adding module <{!s}> to tag <{}>: "
                         "{!s}".format(modinfo.nsvc, tag, e))
                errors.append(error)
                log.error(error)

                if self.dry_run or not tag_owners:
                    continue

                if self.send_mail and tag_owners:
                    mail_subject = "Failed to update tag {}".format(tag)
                    content = copy.deepcopy(self.mail_data)
                    content['tag'] = tag
                    content['traceback'] = traceback.format_exc()
                    log.info("Sending mail to %r with data:\n%r", tag_owners, content)
                    self.mail_api.send_mail('add-tag-error.txt', tag_owners,
                                            subject=mail_subject, data=content)

        if errors:
            raise RuntimeError("Errors: {!s}".format(errors))
