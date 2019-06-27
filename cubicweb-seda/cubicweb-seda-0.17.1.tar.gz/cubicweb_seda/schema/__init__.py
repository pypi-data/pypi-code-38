# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-seda schema"""

from yams.buildobjs import RelationType, RelationDefinition
from yams.buildobjs import String

from cubicweb import _
from cubicweb.schema import ERQLExpression, RRQLExpression, RQLConstraint

from cubicweb_skos import schema as skos

from .xsd2yams import MULTIPLE_CHILDREN

_('1')
_('0..1')
_('0..n')
_('1..n')


def seda_profile_element(cardinalities=None, default_cardinality=None, annotable=True):
    """Class decorator adding attributes to configure a SEDA field.
    """
    def decorator(cls):
        if cardinalities and len(cardinalities) > 1:
            cls.add_relation(String(required=True, vocabulary=cardinalities,
                                    default=default_cardinality,
                                    internationalizable=True),
                             name='user_cardinality')
        if annotable:
            required = cls.__name__ in ('SEDAArchiveUnit',
                                        'SEDABinaryDataObject', 'SEDAPhysicalDataObject')
            if required:
                description = _('the first line will be used to display this '
                                'entity within the user interface')
            else:
                description = None
            cls.add_relation(String(fulltextindexed=True,
                                    required=required, description=description),
                             name='user_annotation')
        return cls
    return decorator


class scheme_relation_type(RelationDefinition):
    """Special relation from a concept scheme to a relation type, that may be used to restrict
    possible concept of a particular relation without depending on the scheme's name or other kind
    of ambiguous reference mecanism.
    """
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': ('managers',),
                       'delete': ('managers',)}
    subject = 'ConceptScheme'
    object = 'CWRType'
    cardinality = '**'


class scheme_entity_type(RelationDefinition):
    """Special relation from a concept scheme to an entity type, when one add to constraint on a
    particular subject of a relation type (see `scheme_relation_type`).
    """
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': ('managers',),
                       'delete': ('managers',)}
    subject = 'ConceptScheme'
    object = 'CWEType'
    cardinality = '*?'


class seda_keyword_reference_to_scheme(RelationDefinition):
    subject = 'SEDAKeywordReference'
    object = 'ConceptScheme'
    cardinality = '?*'
    inlined = True


class file_category(RelationDefinition):
    subject = 'SEDABinaryDataObject'
    object = 'Concept'
    cardinality = '**'
    constraints = [
        RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "file_category"'),
    ]


class ordering(RelationDefinition):
    subject = tuple([etype for etype, _ in MULTIPLE_CHILDREN])
    object = 'Int'
    cardinality = '?1'


class container(RelationType):
    inlined = False


class _clone_of(RelationDefinition):
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': ('managers', 'users',),
                       'delete': ()}
    name = 'clone_of'
    cardinality = '?*'
    inlined = True


class clone_of_archive_transfer(_clone_of):
    subject = 'SEDAArchiveTransfer'
    object = 'SEDAArchiveTransfer'


class clone_of_archive_unit(_clone_of):
    subject = 'SEDAArchiveUnit'
    object = 'SEDAArchiveUnit'


class title(RelationDefinition):
    subject = 'SEDAArchiveTransfer'
    object = 'String'
    description = _('title for this profile, not used in the generated schema')
    cardinality = '11'
    fulltextindexed = True


class simplified_profile(RelationDefinition):
    subject = 'SEDAArchiveTransfer'
    object = 'Boolean'
    default = False
    description = _('simplified profiles are compatible with older version of SEDA, but have not '
                    'the full SEDA 2 expressivness')
    cardinality = '11'


class code_keyword_type(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', RRQLExpression('U has_update_permission S')),
        'delete': ('managers', RRQLExpression('U has_update_permission S')),
    }
    subject = 'ConceptScheme'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    description = _('SEDA code keyword type for this scheme')
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type RT, '
                                 'RT name "seda_keyword_type_to"')]


class compat_list(RelationDefinition):
    __permissions__ = {'read': ('managers', 'users', 'guests',),
                       'add': (),
                       'update': ()}
    subject = 'SEDAArchiveTransfer'
    object = 'String'
    description = _("names of format in which the profile may be exported (e.g. 'SEDA 2, SEDA 1')")


language_code = skos.Label.get_relation('language_code')
language_code.constraints[0].max = 7


def post_build_callback(schema):
    from cubicweb_seda import seda_profile_container_def, iter_all_rdefs

    container_etypes = ('SEDAArchiveTransfer', 'SEDAArchiveUnit')
    for etype, parent_rdefs in seda_profile_container_def(schema):
        # add relation to the container from every entity type within the compound graph
        for container_etype in container_etypes:
            # special case for SEDAArchiveUnit's cardinality as it may be both
            # contained and container
            container_rdef = RelationDefinition(
                etype, 'container', container_etype,
                cardinality='?*' if etype == 'SEDAArchiveUnit' else '1*',
                __permissions__={'add': (),
                                 'delete': (),
                                 'read': ('managers', 'users', 'guests')})
            schema.add_relation_def(container_rdef)
        eschema = schema[etype]
        # set permissions on entity types from the compound graph according to permission on the
        # container entity
        for action in ('update', 'delete'):
            eschema.set_action_permissions(
                action, (ERQLExpression('U has_{action}_permission C, '
                                        'X container C'.format(action=action)),)
            )
    for action in ('update', 'delete'):
        schema['SEDAArchiveUnit'].set_action_permissions(
            action, (ERQLExpression('U has_{action}_permission C, '
                                    'X container C'.format(action=action)),
                     ERQLExpression('NOT EXISTS(X container C), U in_group G, '
                                    'G name IN ("managers", "users")')))
    # set permissions on all relation defs related to the compound graph according to permission on
    # the container entity
    for rdef, role in iter_all_rdefs(schema, 'SEDAArchiveTransfer'):
        if role == 'subject':
            target_etype, var = rdef.subject, 'S'
        else:
            target_etype, var = rdef.object, 'O'
        rrql_exprs = []
        if target_etype == 'SEDAArchiveUnit':
            rrql_exprs.append('U has_update_permission {0}, NOT EXISTS({0} container C)'
                              .format(var, var))
            rrql_exprs.append('U has_update_permission C, {0} container C'.format(var))

        else:
            if target_etype == 'SEDAArchiveTransfer':
                rrql_exprs.append('U has_update_permission {0}'.format(var))
            else:
                rrql_exprs.append('U has_update_permission C, {0} container C'.format(var))
        permissions = [RRQLExpression(expr) for expr in rrql_exprs]
        for action in ('add', 'delete'):
            rdef.set_action_permissions(action, permissions)
