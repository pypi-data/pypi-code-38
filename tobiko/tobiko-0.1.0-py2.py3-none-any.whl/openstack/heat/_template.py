# Copyright 2019 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import collections
import os
import sys

from heatclient.common import template_utils
import yaml

import tobiko


TEMPLATE_SUFFIX = '.yaml'

TEMPLATE_DIRS = list(sys.path)


class HeatTemplate(collections.namedtuple('HeatTemplate',
                                          ['template', 'file', 'files'])):

    _yaml = None

    @classmethod
    def from_dict(cls, template):
        return cls(template=template, file=None, files=None)

    @classmethod
    def from_file(cls, template_file, template_dirs=None):
        if template_dirs or not os.path.isfile(template_file):
            template_dirs = template_dirs or TEMPLATE_DIRS
            template_file = find_heat_template_file(
                template_file=template_file, template_dirs=template_dirs)
        files, template = template_utils.get_template_contents(
            template_file=template_file)
        return cls(file=template_file, files=files, template=template)

    @property
    def yaml(self):
        if not self._yaml:
            self._yaml = yaml.safe_dump(self.template)
        return self._yaml


class HeatTemplateFileFixture(tobiko.SharedFixture):

    template_file = None
    template_dirs = None
    template = None

    def __init__(self, template_file=None, template_dirs=None):
        super(HeatTemplateFileFixture, self).__init__()
        if template_file:
            self.template_file = template_file
        if template_dirs:
            self.template_dirs = template_dirs

    def setup_fixture(self):
        self.setup_template()

    def setup_template(self):
        self.template = HeatTemplate.from_file(
            template_file=self.template_file,
            template_dirs=self.template_dirs)


def heat_template_file(template_file, template_dirs=None):
    return HeatTemplateFileFixture(template_file=template_file,
                                   template_dirs=template_dirs)


def get_heat_template(template_file, template_dirs=None):
    return HeatTemplate.from_file(template_file=template_file,
                                  template_dirs=template_dirs)


def find_heat_template_file(template_file, template_dirs):
    for template_dir in template_dirs:
        template_path = os.path.join(template_dir, template_file)
        if os.path.exists(template_path):
            return template_path

    msg = "Template file {!r} not found in directories {!r}".format(
        template_file, template_dirs)
    raise IOError(msg)
