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
"""Library of views use there and there in the interface"""

from cubicweb import tags, view, _
from cubicweb.predicates import match_kwargs, is_instance, score_entity
from cubicweb.view import EntityView
from cubicweb.web.views import baseviews, tabs

from ..xsd import un_camel_case
from ..xsd2uicfg import FIRST_LEVEL_ETYPES
from . import CONTENT_ETYPE, add_subobject_link, dropdown_button


def add_links_from_rtype_roles(entity, rtype_roles, extraurlparams):
    """Return a list of links to be inserted in dropdown button to add subobjects linked to `entity`
    through relations defined in `rtype_roles`, depending on user's permission to add any of them.

    `rtype_roles` is list of 2-uples `(rtype, role)`.
    """
    links = [add_subobject_link(entity, rtype, role, extraurlparams, klass='')
             for rtype, role in rtype_roles]
    return [l for l in links if l]


def display_add_button(w, links, label):
    if links:
        # No links if user cannot add any relation.
        w(dropdown_button(label, links))
        w(tags.div(klass='clearfix'))


class XSDMetaEntityView(EntityView):
    __regid__ = 'seda.xsdmeta'

    def entity_call(self, entity, skip_one_card=False, with_annotation=True):
        cardinality = getattr(entity, 'user_cardinality', '1')
        if cardinality != '1' or not skip_one_card:
            self.w(u' <span class="cardinality">[%s]</span>' % cardinality)
        if with_annotation and getattr(entity, 'user_annotation', None):
            description = entity.printable_value('user_annotation')
            if entity.cw_etype in FIRST_LEVEL_ETYPES:
                # skip first line, already displayed since it's used as title for the entity
                description = '\n'.join(description.splitlines()[1:])
            if description:
                self.w(u' <span class="description text-muted">%s</span>' % description)


class TextEntityAttributeView(EntityView):
    """Attribute view for SEDA relations displaying entity as text (no link to the entity)
    """
    __regid__ = 'seda.reledit.text'
    subvid = 'seda.business'

    def entity_call(self, entity, **kwargs):
        self.w(u'<div>')
        entity.view(self.subvid, w=self.w)
        entity.view('seda.xsdmeta', w=self.w)
        self.w(u'</div>')


class SimpleLinkToEntityAttributeView(TextEntityAttributeView):
    """Attribute view for SEDA relations linking directly to an entity without intermediary entity
    """
    __regid__ = 'seda.reledit.simplelink'
    subvid = 'oneline'


class ComplexLinkEntityAttributeView(EntityView):
    """Attribute view for SEDA relations linking to an entity through an intermediary entity holding
    cardinalities / annotation
    """
    __regid__ = 'seda.reledit.complexlink'

    def entity_call(self, entity):
        rtype = self.cw_extra_kwargs['rtype'].replace('_from', '_to')
        value_rset = entity.related(rtype)
        self.w(u'<div>')
        if value_rset:
            self.w(u'<span class="value">')
            self._cw.view('csv', value_rset, w=self.w)
            self.w(u'</span>')
        else:
            self.wdata(self._cw._('<no value specified>'))
        entity.view('seda.xsdmeta', w=self.w)
        self.w(u'</div>')


def alternative_values(entity, parent_rtype):
    """Display entities under the given alternative `entity`.

    Those are found by introspecting the schema, and skipping the relation from the alternative to
    its parent (`parent_rtype`).
    """
    req = entity._cw
    alternatives = []
    for rschema, _targets, role in entity.e_schema.relation_definitions():
        rtype = rschema.type
        if rtype.startswith('seda_') and rtype != parent_rtype:
            target_rset = entity.related(rtype, role)
            if target_rset:
                alternatives.append(req.view('seda.type_meta', rset=target_rset))
    return (' <b>%s</b> ' % req._(' ALT_I18N ')).join(alternatives)


class AlternativeEntityAttributeView(EntityView):
    """Attribute view for SEDA alternative entities"""
    __regid__ = 'seda.reledit.alternative'

    def entity_call(self, entity):
        alternatives = alternative_values(entity, self.cw_extra_kwargs['rtype'])
        self.w(u'<div class="alternative">')
        if alternatives:
            self.w(alternatives)
        else:
            self.wdata(self._cw._('<no value specified>'))
        entity.view('seda.xsdmeta', w=self.w)
        self.w(u'</div>')


class BusinessValueEntityView(EntityView):
    """Entity view that will display value of the attribute specified by `value_attr` on the
    entity's class
    """
    __regid__ = 'seda.business'
    no_value_msg = _('<no value specified>')

    def entity_call(self, entity):
        value = self.entity_value(entity)
        if value:
            self.w(u'<span class="value">')
            self.w(value)
            self.w(u'</span>')
        else:
            self.wdata(self._cw._(self.no_value_msg))

    def entity_value(self, entity):
        if entity.value_attr:
            value = entity.printable_value(entity.value_attr)
        else:
            value = None
        return value


class BusinessValueConceptEntityView(BusinessValueEntityView):
    """Specific business value view for concept entity: simply display the concept's label as text.
    """
    __select__ = is_instance('Concept')

    def entity_value(self, entity):
        return entity.label()


class BusinessValueLinkEntityView(BusinessValueEntityView):
    """Similar to seda.business but value is enclosed in a link if some value is specified."""
    __abstract__ = True

    def entity_value(self, entity):
        value = super(BusinessValueLinkEntityView, self).entity_value(entity)
        if value:
            value = tags.a(value, href=entity.absolute_url())
        return value


class BusinessValueReferenceEntityView(BusinessValueEntityView):
    """Similar to seda.business but value is enclosed in a link if some value is specified."""
    __select__ = is_instance(*FIRST_LEVEL_ETYPES)

    def entity_value(self, entity):
        value = entity.dc_title()
        return tags.a(value, href=entity.absolute_url())


class TypeAndMetaEntityView(EntityView):
    """Glue entity's type, seda.business and seda.xsdmeta views together, for use within alternative
    """
    __regid__ = 'seda.type_meta'

    def entity_call(self, entity):
        self.w(entity.dc_type() + u' ')
        entity.view('seda.business', w=self.w)
        entity.view('seda.xsdmeta', w=self.w, skip_one_card=True)


class ListItemView(EntityView):
    """Extended 'oneline' view for entities related to an AuthorityRecord, including link to remove
    the relation.
    """
    __regid__ = 'seda.listitem'
    __select__ = EntityView.__select__ & match_kwargs('parent', 'tabid')

    def entity_call(self, entity, parent, tabid, edit=True, delete=True):
        entity.view('seda.listitem.content', w=self.w)
        if entity.cw_has_perm('update'):
            self._cw.add_js(('cubicweb.ajax.js', 'cubes.seda.js'))
            editurlparams = {
                '__redirectpath': parent.rest_path(),
                '__redirectparams': 'tab=' + tabid
            }
            if edit or delete:
                self.w(u'<div class="pull-right">')
                if edit:
                    self.w(tags.a(title=self._cw.__('edit'), klass='icon-pencil',
                                  href=entity.absolute_url(vid='edition', **editurlparams)))
                if delete:
                    self.w(tags.a(title=self._cw.__('delete'), klass='icon-trash',
                                  href=entity.absolute_url(vid='deleteconf', **editurlparams)))
                self.w(u'</div>')


class ListItemContentView(EntityView):
    """Glue seda.business and seda.xsdmeta views together, for use within list."""
    __regid__ = 'seda.listitem.content'

    def entity_call(self, entity):
        entity.view('seda.business', w=self.w)
        entity.view('seda.xsdmeta', w=self.w, skip_one_card=True)


class PrimaryTabWithoutBoxes(tabs.PrimaryTab):
    """Abstract base class for tabs which rely on the primary view logic but don't want side boxes.
    """
    __abstract__ = True
    __regid__ = None  # we don't want 'primary'

    def is_primary(self):
        return False

    def content_navigation_components(self, context):
        pass


class SubObjectsTab(tabs.TabsMixin, EntityView):
    """Base class for tabs with a 'add' button and one or more list of subobjects, driven by the
    `rtype_role_targets` class attribute
    """
    rtype_role_targets = None
    subvid = 'seda.listitem'

    @property
    def tabid(self):
        return self.__regid__

    def entity_call(self, entity):
        self.display_add_button(entity)
        self.display_subobjects_list(entity)

    def display_add_button(self, entity):
        rtype_roles = [(rtype, role) for rtype, role, _ in self.rtype_role_targets]
        links = add_links_from_rtype_roles(entity, rtype_roles, self.url_params(entity))
        display_add_button(self.w, links, self._cw.__('add'))

    def display_subobjects_list(self, entity):
        for rtype, role, target in self.rtype_role_targets:
            rset = entity.related(rtype, role)
            if rset:
                if target is not None:
                    self.w('<h2>%s</h2>' % self._cw.__(target + '_plural'))
                self._cw.view('list', rset=rset, parent=self.parent(entity), w=self.w,
                              subvid=self.subvid, tabid=self.tabid)

    def url_params(self, entity):
        return {'__redirectparams': 'tab=' + self.tabid}

    def parent(self, entity):
        return entity


# references views #################################################################################

def typed_reference_origin(entity):
    """Given a typed reference (eg. SEDAIsVersionOf, SEDAReplaces, etc), return a value to display
    its type and origin (archive unit defining it).
    """
    up_to_content_rtype = 'seda_{}'.format(un_camel_case(entity.cw_etype[4:]))
    content = entity.related(up_to_content_rtype).one()
    archive_unit = content.cw_adapt_to('ITreeBase').parent()
    return'{} ({})'.format(archive_unit.view('incontext'), entity.dc_type())


class ArchiveUnitRefIdOutOfContextView(baseviews.OutOfContextView):
    """Custom outofcontext view for proper display of SEDAArchiveUnitRefId from in boxes"""
    __select__ = is_instance('SEDAArchiveUnitRefId')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        parent = entity.cw_adapt_to('IContained').parent
        if parent.cw_etype == 'SEDAAltArchiveUnitArchiveUnitRefId':
            parent.view('incontext', w=self.w)
        else:
            parent_parent_rtype = 'seda_{}'.format(un_camel_case(parent.cw_etype[4:]))
            parent_parent = parent.related(parent_parent_rtype, 'object').one()
            self.w(typed_reference_origin(parent_parent))


class ArchiveUnitRefIdBusinessValueLinkEntityView(BusinessValueLinkEntityView):
    __select__ = is_instance('SEDAArchiveUnitRefId')

    def entity_value(self, entity):
        if entity.seda_archive_unit_ref_id_to:
            archiveunit = entity.seda_archive_unit_ref_id_to[0]
            return archiveunit.view('oneline')
        return None


def is_main_data_object_reference(reference):
    """Return True if the given SEDADataObjectReference is a 'main' reference from an archive unit
    to a data object (not a qualified reference, eg IsVersionOf, IsPartOf, Reference, etc.).
    """
    parent = reference.seda_data_object_reference[0]
    return parent.cw_etype == CONTENT_ETYPE


class MainDataObjectReferenceBusinessValueLinkEntityView(BusinessValueLinkEntityView):
    __select__ = (is_instance('SEDADataObjectReference')
                  & score_entity(lambda x: is_main_data_object_reference(x)))

    def entity_call(self, entity):
        do_rset = entity.related('seda_data_object_reference_id', 'subject')
        if do_rset:
            do_rset.one().view(self.__regid__, w=self.w)
        else:
            super(MainDataObjectReferenceBusinessValueLinkEntityView, self).entity_call(entity)


class OtherDataObjectReferenceBusinessValueLinkEntityView(BusinessValueLinkEntityView):
    __select__ = (is_instance('SEDADataObjectReference')
                  & score_entity(lambda x: not is_main_data_object_reference(x)))

    def entity_value(self, entity):
        if entity.seda_data_object_reference_id:
            dataobject = entity.seda_data_object_reference_id[0]
            return dataobject.view('oneline')
        return None


class ObjectReferencepArchiveUnitEntityView(view.EntityView):

    __regid__ = 'seda.object-ref.archive-unit'
    __select__ = is_instance('SEDADataObjectReference')

    def entity_call(self, entity):
        au_seq = entity.seda_data_object_reference[0]
        if au_seq.cw_etype == CONTENT_ETYPE:
            au_choice = au_seq.reverse_seda_seq_alt_archive_unit_archive_unit_ref_id_management[0]
            target = au_choice.reverse_seda_alt_archive_unit_archive_unit_ref_id[0]
        else:
            rtype = 'seda_{}'.format(un_camel_case(au_seq.cw_etype[4:]))
            target = au_seq.related(rtype, 'object').one()
        target.view('listitem', w=self.w)


class ReferenceListItemView(view.EntityView):
    __regid__ = 'listitem'
    # additional match_kwargs because we don't want to be selected by SubObjectsTab based list
    __select__ = is_instance('SEDAIsVersionOf', 'SEDAReplaces', 'SEDARequires', 'SEDAIsPartOf',
                             'SEDAReferences') & ~match_kwargs('tabid')

    def entity_call(self, entity):
        self.w(typed_reference_origin(entity))
