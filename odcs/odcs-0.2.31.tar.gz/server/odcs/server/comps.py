# -*- coding: utf-8 -*-
# Copyright (c) 2017  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

COMPS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE comps PUBLIC "-//Red Hat, Inc.//DTD Comps info//EN" "comps.dtd">
<comps>
  {%- for group in comps.groups %}
  <group>
    <id>{{ group.id }}</id>
    <name>{{ group.name }}</name>
    <description>{{ group.description }}</description>
    <default>{{ group.is_default|lower }}</default>
    <uservisible>{{ group.is_uservisible|lower }}</uservisible>
    <packagelist>
        {%- for package in group.packages %}
        <packagereq
        {%- if package.type %} type="{{ package.type }}"{% endif -%}
        {%- if package.arch %} arch="{{ package.arch }}"{% endif -%}
        {%- if package.requires %} requires="{{ package.requires }}"{% endif -%}
        {%- if package.is_basearchonly %} basearchonly="{{ package.is_basearchonly | lower }}"{% endif -%}
        {%- if false %}{% endif -%}>{{ package.name }}</packagereq>
        {%- endfor %}
    </packagelist>
  </group>
  {%- endfor %}
</comps>

"""

VARIANTS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE variants PUBLIC "-//Red Hat, Inc.//DTD Variants info//EN" "variants2012.dtd">
<variants>
  {%- for variant in product.variants %}
  <variant id="{{ variant.id }}" name="{{ variant.name }}" type="{{ variant.type }}">
    <arches>
      {%- for arch in variant.arches %}
      <arch>{{ arch.name }}</arch>
      {%- endfor %}
    </arches>
    {%- if variant.modules %}
    <modules>
      {%- for module in variant.modules %}
      <module>{{ module.name }}</module>
      {%- endfor %}
    </modules>
    {%- endif %}
    {%- if variant.groups %}
    <groups>
      {%- for group in variant.groups %}
        <group
        {%- if group in variant.default_groups %} default="true"{% endif -%}
        {%- if false %}{% endif %}>{{ group.name }}</group>
      {%- endfor %}
    </groups>
    {%- endif %}
  </variant>
  {%- endfor %}
</variants>

"""


class Arch(object):
    def __init__(self, name):
        self.name = name


class Package(object):
    def __init__(self, name, arch=None, type=None, requires=None, is_basearchonly=False):
        self.name = name
        self.arch = arch
        self.type = type
        self.requires = requires
        self.is_basearchonly = is_basearchonly


class Module(object):
    def __init__(self, name):
        self.name = name


class Group(object):
    def __init__(self, id, name, description, is_default=True, is_uservisible=True):
        self.id = id
        self.name = name
        self.description = description
        self.is_default = is_default
        self.is_uservisible = is_uservisible
        self.packages = []

    def add_package(self, package):
        self.packages.append(package)


class Comps(object):
    def __init__(self):
        self.groups = []

    def add_group(self, group):
        self.groups.append(group)


class Variant(object):
    def __init__(self, id, name, type, source_type):
        self.id = id
        self.name = name
        self.type = type
        self.arches = []
        self.source_type = source_type
        self.groups = []
        self.default_groups = []
        self.modules = []

    def add_arch(self, arch):
        self.arches.append(arch)

    def add_group(self, group, default=True):
        self.groups.append(group)
        if default:
            self.default_groups.append(group)

    def add_module(self, module):
        self.modules.append(module)


class Product(object):
    def __init__(self):
        self.variants = []

    def add_variant(self, variant):
        self.variants.append(variant)
