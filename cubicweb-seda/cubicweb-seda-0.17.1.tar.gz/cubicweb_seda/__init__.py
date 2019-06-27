# copyright 2016-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-seda application package

Data Exchange Standard for Archival
"""

from cubicweb_compound import skip_rtypes_set, structure_def, CompositeGraph


# control of compound graph by adding etype / rtype to the corresponding set below
GRAPH_SKIP_ETYPES = set()
GRAPH_SKIP_RTYPES = set(['container', 'clone_of'])


def seda_profile_container_def(schema):
    """Define container for SEDAArchiveTransfer, as a list of (etype, parent_rdefs)."""
    return structure_def(schema, 'SEDAArchiveTransfer',
                         skipetypes=GRAPH_SKIP_ETYPES, skiprtypes=GRAPH_SKIP_RTYPES).items()


def _iter_external_rdefs(eschema, skip_rtypes):
    """Return an iterator on (rdef, role) of external relations from entity schema (i.e.
    non-composite relations).
    """
    for rschema, targets, role in eschema.relation_definitions():
        if rschema in skip_rtypes:
            continue
        for target_etype in targets:
            rdef = eschema.rdef(rschema, role, target_etype)
            if rdef.composite:
                continue
            yield rdef, role


def iter_all_rdefs(schema, container_etype):
    """Return an iterator on (rdef, role) of all relations of the compound graph starting from the
    given entity type, both internal (composite) and external (non-composite).
    """
    graph = CompositeGraph(schema, skipetypes=GRAPH_SKIP_ETYPES, skiprtypes=GRAPH_SKIP_RTYPES)
    skip_external_rtypes = skip_rtypes_set(GRAPH_SKIP_RTYPES)
    stack = [container_etype]
    visited = set(stack)
    while stack:
        etype = stack.pop()
        for (rtype, role), targets in graph.child_relations(etype):
            rschema = schema.rschema(rtype)
            for target in targets:
                if role == 'subject':
                    rdef = rschema.rdefs[(etype, target)]
                else:
                    rdef = rschema.rdefs[(target, etype)]
                yield rdef, role

                if target not in visited:
                    visited.add(target)
                    stack.append(target)
        for rdef, role in _iter_external_rdefs(schema[etype], skip_external_rtypes):
            yield rdef, role
