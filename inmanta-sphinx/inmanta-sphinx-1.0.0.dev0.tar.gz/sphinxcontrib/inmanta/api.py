"""
    Copyright 2017 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
"""

from collections import defaultdict, OrderedDict
import os
import re
import shutil
import sys
import tempfile

import click

from inmanta import module, compiler, ast
from inmanta.agent import handler
from inmanta.ast.attribute import RelationAttribute
from inmanta.module import Project
from inmanta.plugins import PluginMeta
from inmanta.resources import resource
from sphinx.util import docstrings


ATTRIBUTE_REGEX = re.compile("(?::param|:attribute|:attr) (.*?)(?:(?=:param)|(?=:attribute)|(?=:attr)|\Z)", re.S)
ATTRIBUTE_LINE_REGEX = re.compile("([^\s:]+)(:)?\s(.*?)\Z")
PARAM_REGEX = re.compile(":param|:attribute|:attr")


def format_multiplicity(rel):
    low = rel.low
    high = rel.high

    if low == high:
        return low

    if high is None:
        high = "\*"

    return str(low) + ":" + str(high)


def parse_docstring(docstring):
    """
        Parse a docstring and return its components. Inspired by
        https://github.com/openstack/rally/blob/master/rally/common/plugin/info.py#L31-L79

        :param str docstring: The string/comment to parse in docstring elements
        :returns: {
            "comment": ...,
            "attributes": ...,
        }
    """
    docstring = "\n".join(docstrings.prepare_docstring(docstring))
    comment = docstring
    attributes = {}
    match = PARAM_REGEX.search(docstring)
    if match:
        comment = docstring[:match.start()]

        # process params
        attr_lines = ATTRIBUTE_REGEX.findall(docstring)
        for line in attr_lines:
            line = re.sub("\s+", " ", line.strip())
            match = ATTRIBUTE_LINE_REGEX.search(line)
            if match is None:
                print("Unable to parse line: " + line, file=sys.stderr)
                continue

            items = match.groups()
            attributes[items[0]] = items[2]

    comment_lines = []
    for line in comment.split("\n"):
        line = line.rstrip()
        comment_lines.append(line)

    return {"comment": comment_lines, "attributes": attributes}


class DocModule(object):
    def doc_compile(self, module_dir, name, import_list):
        curdir = os.getcwd()
        main_cf = "\n".join(["import " + i for i in import_list])
        try:
            project_dir = tempfile.mkdtemp()
            with open(os.path.join(project_dir, "main.cf"), "w+") as fd:
                fd.write(main_cf)

            with open(os.path.join(project_dir, "project.yml"), "w+") as fd:
                fd.write("""name: docgen
description: Project to generate docs
repo: %s
modulepath: %s
    """ % (module_dir, module_dir))

            project = Project(project_dir)
            project.use_virtual_env()
            Project.set(project)
            project.verify()
            project.load()
            _, root_ns = compiler.do_compile()

            
            module_ns = root_ns.get_child(name)

            doc_ns = [ns for ns in module_ns.children(recursive=True)]
            doc_ns.append(module_ns)


            modules = {}
            for ns in doc_ns:
                modules[ns.get_full_name()] = ns.defines_types

            lines = []

            types = defaultdict(OrderedDict)
            for module in sorted(modules.keys()):
                for type_name in sorted(modules[module].keys()):
                    type_obj = modules[module][type_name]
                    if isinstance(type_obj, ast.entity.Entity):
                        full_name = type_obj.get_full_name()
                        types["entity"][full_name] = type_obj

                    elif isinstance(type_obj, ast.entity.Implementation):
                        full_name = type_obj.get_full_name()
                        types["implementation"][full_name] = type_obj

                    elif isinstance(type_obj, ast.type.ConstraintType):
                        types["typedef"][type_name] = type_obj

                    elif isinstance(type(type_obj), PluginMeta):
                        types["plugin"][type_name] = type_obj

                    else:
                        print(type(type_obj))

            if len(types["typedef"]) > 0:
                lines.extend(self.emit_heading("Typedefs", "-"))
                for obj in types["typedef"].values():
                    lines.extend(self.emit_typedef(obj))
                lines.append("")

            if len(types["entity"]) > 0:
                lines.extend(self.emit_heading("Entities", "-"))
                for obj in types["entity"].values():
                    lines.extend(self.emit_entity(obj))

            if len(types["implementation"]) > 0:
                lines.extend(self.emit_heading("Implementations", "-"))
                for obj in types["implementation"].values():
                    lines.extend(self.emit_implementation(obj))

            if len(types["plugin"]) > 0:
                lines.extend(self.emit_heading("Plugins", "-"))
                for plugin in types["plugin"].values():
                    lines.extend(self.emit_plugin(plugin))

            res_list = sorted([res for res in resource._resources.items() if res[0][:len(name)] == name], key=lambda x: x[0])
            if len(res_list) > 0:
                lines.extend(self.emit_heading("Resources", "-"))
                for res, (cls, opt) in res_list:
                    lines.extend(self.emit_resource(res, cls, opt))

            h = []
            for entity, handlers in handler.Commander.get_handlers().items():
                for handler_name, cls in handlers.items():
                    if cls.__module__.startswith("inmanta_plugins." + name):
                        h.extend(self.emit_handler(entity, handler_name, cls))

            if len(h) > 0:
                lines.extend(self.emit_heading("Handlers", "-"))
                lines.extend(h)

            return lines
        finally:
            os.chdir(curdir)
            shutil.rmtree(project_dir)

        return []

    def emit_handler(self, entity, name, cls):
        mod = cls.__module__[len("inmanta_plugins."):]
        lines = [".. py:class:: %s.%s" % (mod, cls.__name__), ""]
        if cls.__doc__ is not None:
            lines.extend(self.prep_docstring(cls.__doc__, 1))
            lines.append("")

        lines.append(" * Handler name ``%s``" % name)
        lines.append(" * Handler for entity :inmanta:Entity:`%s`" % entity)
        lines.append("")
        return lines

    def emit_resource(self, name, cls, opt):
        mod = cls.__module__[len("inmanta_plugins."):]
        lines = [".. py:class:: %s.%s" % (mod, cls.__name__), ""]
        if cls.__doc__ is not None:
            lines.extend(self.prep_docstring(cls.__doc__, 1))
            lines.append("")

        lines.append(" * Resource for entity :inmanta:Entity:`%s`" % name)
        lines.append(" * Id attribute ``%s``" % opt["name"])
        lines.append(" * Agent name ``%s``" % opt["agent"])

        handlers = []
        for cls in handler.Commander.get_handlers()[name].values():
            mod = cls.__module__[len("inmanta_plugins."):]
            handlers.append(":py:class:`%s.%s`" % (mod, cls.__name__))
        lines.append(" * Handlers " + ", ".join(handlers))
        lines.append("")
        return lines

    def emit_plugin(self, instance):
        lines = [".. py:function:: %s.%s" % (str(instance.ns), instance.get_signature()), ""]
        if instance.__class__.__function__.__doc__ is not None:
            docstring = ["   " + x for x in docstrings.prepare_docstring(instance.__class__.__function__.__doc__)]
            lines.extend(docstring)
            lines.append("")
        return lines

    def emit_heading(self, heading, char):
        """emit a sphinx heading/section  underlined by char """
        return [heading, char * len(heading), ""]

    def prep_docstring(self, docstr, indent_level=0):
        return [("   " * indent_level) + x for x in docstrings.prepare_docstring(docstr)]

    def emit_attributes(self, entity, attributes):
        all_attributes = [entity.get_attribute(name) for name in list(entity._attributes.keys())]
        relations = [x for x in all_attributes if isinstance(x, RelationAttribute)]
        others = [x for x in all_attributes if not isinstance(x, RelationAttribute)]

        defaults = entity.get_default_values()
        lines = []

        for attr in others:
            name = attr.get_name()

            attr_line = "   .. inmanta:attribute:: {1} {2}.{0}".format(attr.get_name(), attr.get_type().type_string(),
                                                                       entity.get_full_name())
            if attr.get_name() in defaults:
                attr_line += "=" + str(defaults[attr.get_name()])
            lines.append(attr_line)
            lines.append("")
            if name in attributes:
                lines.append("      " + attributes[name])

            lines.append("")

        for attr in relations:
            lines.append("   .. inmanta:relation:: {} {}.{} [{}]".format(attr.get_type(), entity.get_full_name(),
                                                                         attr.get_name(), format_multiplicity(attr)))
            if attr.comment is not None:
                lines.append("")
                lines.extend(self.prep_docstring(attr.comment, 2))

            lines.append("")
            if attr.end is not None:
                otherend = attr.end.get_entity().get_full_name() + "." + attr.end.get_name()
                lines.append("      other end: :inmanta:relation:`{0} [{1}]<{0}>`".format(otherend,
                                                                                          format_multiplicity(attr.end)))
                lines.append("")

        if len(entity.implementations) > 0:
            lines.append("   The following implementations are defined for this entity:")
            lines.append("")
            for impl in entity.implementations:
                lines.append("      * :inmanta:implementation:`%s`" % impl.get_full_name())

            lines.append("")

        if len(entity.implements) > 0:
            lines.append("   The following implements statements select implementations for this entity:")
            lines.append("")
            for impl in entity.implements:
                lines.append("      * " + ", ".join([":inmanta:implementation:`%s`" % x.get_full_name()
                                                     for x in impl.implementations]))

                constraint_str = impl.constraint.pretty_print()
                if constraint_str != "True":
                    lines.append("        constraint ``%s``" % constraint_str)

            lines.append("")

        return lines

    def emit_implementation(self, impl):
        lines = []
        lines.append(".. inmanta:implementation:: {0}::{1}".format(impl.namespace.get_full_name(), impl.name))
        if impl.comment is not None:
            lines.append("")
            lines.extend(self.prep_docstring(impl.comment, 2))
        lines.append("")

        return lines

    def emit_entity(self, entity):
        lines = []
        lines.append(".. inmanta:entity:: " + entity.get_full_name())
        lines.append("")

        if len(entity.parent_entities) > 0:
            lines.append("   Parents: %s" % ", ".join([":inmanta:entity:`%s`" % x.get_full_name()
                                                       for x in entity.parent_entities]))
        lines.append("")

        attributes = {}
        if(entity.comment):
            result = parse_docstring(entity.comment)
            lines.extend(["   " + x for x in result["comment"]])
            lines.append("")
            attributes = result["attributes"]

        lines.extend(self.emit_attributes(entity, attributes))
        lines.append("")

        return lines

    def emit_typedef(self, typedef):
        lines = []
        lines.append(".. inmanta:typedef:: {0}".format(typedef.type_string()))
        lines.append("")
        lines.append("   * Base type ``{0}``".format(typedef.basetype.type_string()))
        lines.append("   * Type constraint ``{0}``".format(typedef.expression.pretty_print()))
        lines.append("")
        return lines

    def emit_intro(self, module, source_repo):
        lines = self.emit_heading("Module " + module._meta["name"], "=")

        if "description" in module._meta:
            lines.append(module._meta["description"])
            lines.append("")

        lines.append(" * License: " + module._meta["license"])
        lines.append(" * Version: " + str(module._meta["version"]))
        if "author" in module._meta:
            lines.append(" * Author: " + module._meta["author"])

        if "compiler_version" in module._meta:
            lines.append(" * This module requires compiler version %s or higher" % module._meta["compiler_version"])

        if source_repo is not None:
            lines.append(" * Upstream project: " + source_repo)

        lines.append("")
        return lines

    def _get_modules(self, module_path):
        if os.path.exists(module_path) and module.Module.is_valid_module(module_path):
            mod = module.Module(None, module_path)
            return mod, mod.get_all_submodules()
        return None, None

    def run(self, module_repo, module, extra_modules, source_repo):
        module_path = os.path.join(module_repo, module)
        mod, submodules = self._get_modules(module_path)

        for name in extra_modules:
            module_path = os.path.join(module_repo, name)
            _, m = self._get_modules(module_path)
            if m is not None:
                submodules.extend(m)

        lines = self.emit_intro(mod, source_repo)
        lines.extend(self.doc_compile(module_repo, module, submodules))
        return "\n".join(lines)


@click.command()
@click.option("--module_repo", help="The repo where all modules are stored (local file)", required=True)
@click.option("--module", help="The module to generate api docs for", required=True)
@click.option("--extra-modules", "-m", help="Extra modules that should be loaded to render the docs", multiple=True)
@click.option("--source-repo", help="The repo where the upstream source is located.")
@click.option("--file", "-f", help="Save the generated result here.", required=True)
def generate_api_doc(module_repo, module, extra_modules, source_repo, file):
    """
        Generate API documentation for module
    """
    module_repo=os.path.abspath(module_repo)
    doc = DocModule()
    content = doc.run(module_repo, module, extra_modules, source_repo)

    with open(file, "w+") as fd:
        fd.write(content)


if __name__ == "__main__":
    generate_api_doc()
