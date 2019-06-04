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

from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain
from sphinx.domains import ObjType
from sphinx.locale import _
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode

from .pygments_lexer import InmantaLexer


def get_first_statement(stmts):
    out = None
    line = float("inf")
    for stmt in stmts:
        if(stmt.line > 0 and stmt.line < line):
            out = stmt
            line = stmt.line
    return out


class InmantaXRefRole(XRefRole):
    pass


class InmantaObject(ObjectDescription):
    def add_target_and_index(self, name, sig, signode):
        targetname = self.objtype + '-' + name
        if targetname not in self.state.document.ids:
            signode['names'].append(targetname)
            signode['ids'].append(targetname)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)

            objects = self.env.domaindata['inmanta']['objects']
            key = (self.objtype, name)
            if key in objects:
                self.state_machine.reporter.warning('duplicate description of %s %s, ' % (self.objtype, name) +
                                                    'other instance in ' + self.env.doc2path(objects[key]), line=self.lineno)
            objects[key] = self.env.docname
        indextext = self.get_index_text(self.objtype, name)
        if indextext:
            self.indexnode['entries'].append(('single', indextext, targetname, '', None))

    def get_index_text(self, objectname, name):
        return name


class Entity(InmantaObject):
    def handle_signature(self, sig, signode):
        signode += addnodes.desc_annotation("entity", "entity ")
        signode += addnodes.desc_addname(sig, sig)
        return sig


class Attribute(InmantaObject):
    def handle_signature(self, sig, signode):
        signode += addnodes.desc_annotation("attribute", "attribute ")
        typ, name = sig.split(" ")
        default = None
        if "=" in name:
            name, default = name.split("=")

        signode += addnodes.desc_type(typ, typ + " ")

        show_name = name
        if "." in name:
            _, show_name = name.split(".")
        signode += addnodes.desc_addname(name, show_name)

        if default is not None:
            signode += addnodes.desc_type(default, "=" + default)

        return name


class Relation(InmantaObject):
    def handle_signature(self, sig, signode):
        signode += addnodes.desc_annotation("relation", "relation ")
        typ, name, mult = sig.split(" ")
        signode += addnodes.desc_type(typ, typ + " ")

        show_name = name
        if "." in name:
            _, show_name = name.split(".")
        signode += addnodes.desc_addname(name, show_name)

        signode += addnodes.desc_type(mult, " " + mult)
        return name


class Implementation(InmantaObject):
    def handle_signature(self, sig, signode):
        signode += addnodes.desc_annotation("implementation", "implementation ")
        signode += addnodes.desc_addname(sig, sig)
        return sig


class TypeDef(InmantaObject):
    def handle_signature(self, sig, signode):
        signode += addnodes.desc_annotation("typedef", "typedef ")
        signode += addnodes.desc_addname(sig, sig)
        return sig


class InmantaDomain(Domain):
    name = "inmanta"
    label = "inmanta"

    object_types = {
        'module': ObjType(_('module'), 'mod', 'obj'),
        'entity': ObjType(_('entity'), 'func', 'obj'),
        'attribute': ObjType(_('attribute'), 'attr', 'obj'),
        'relation': ObjType(_('relation'), 'attr', 'obj'),
        'implementation': ObjType(_('implementation'), 'attr', 'obj'),
        'typedef': ObjType(_('typedef'), 'attr', 'obj')
    }
    directives = {
        'module': Entity,
        'entity': Entity,
        'attribute': Attribute,
        'relation': Relation,
        'implementation': Implementation,
        'typedef': TypeDef,
    }
    roles = {
        'entity': InmantaXRefRole(),
        'attribute': InmantaXRefRole(),
        'relation': InmantaXRefRole(),
        'implementation': InmantaXRefRole(),
        'typedef': InmantaXRefRole(),
    }
    initial_data = {
        'objects': {},  # fullname -> docname, objtype
    }

    def clear_doc(self, docname):
        for (typ, name), doc in list(self.data['objects'].items()):
            if doc == docname:
                del self.data['objects'][typ, name]

    def merge_domaindata(self, docnames, otherdata):
        # XXX check duplicates
        for (typ, name), doc in otherdata['objects'].items():
            if doc in docnames:
                self.data['objects'][typ, name] = doc

    def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
        objects = self.data['objects']
        for objtype in self.object_types.keys():
            if (objtype, target) in objects:
                return make_refnode(builder, fromdocname, objects[objtype, target], objtype + '-' + target,
                                    contnode, target + ' ' + objtype)

    def resolve_any_xref(self, env, fromdocname, builder, target,
                         node, contnode):
        objects = self.data['objects']
        results = []
        for objtype in self.object_types:
            if (objtype, target) in self.data['objects']:
                results.append(('inmanta:' + self.role_for_objtype(objtype),
                                make_refnode(builder, fromdocname, objects[objtype, target], objtype + '-' + target,
                                             contnode, target + ' ' + objtype)))
        return results

    def get_objects(self):
        for (typ, name), docname in self.data['objects'].items():
            yield name, name, typ, docname, typ + '-' + name, 1


def setup(app):
    app.add_domain(InmantaDomain)
    app.add_lexer("inmanta", InmantaLexer())
