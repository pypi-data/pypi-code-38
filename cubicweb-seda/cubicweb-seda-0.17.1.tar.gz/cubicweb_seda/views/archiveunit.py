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
"""cubicweb-seda views for ArchiveUnit"""

from six import text_type

from logilab.mtconverter import xml_escape
from logilab.common.registry import objectify_predicate
from logilab.common.decorators import monkeypatch

from cubicweb import tags, _
from cubicweb.predicates import is_instance, match_form_params, specified_etype_implements
from cubicweb.view import EntityView
from cubicweb.web.views import autoform, baseviews, tabs, uicfg

from cubicweb_compound import views as compound
from cubes.relationwidget import views as rwdg

from ..xsd import un_camel_case
from ..entities import (is_full_seda2_profile, full_seda2_profile,
                        simplified_profile, parent_and_container)
from ..entities.itree import parent_archive_unit
from . import (CONTENT_ETYPE, add_subobject_link,
               rtags_from_xsd_element, rtags_from_rtype_role_targets, has_rel_perm)
from . import clone, viewlib, widgets
from . import uicfg as sedauicfg  # noqa - ensure those rules are defined first


def add_links_with_custom_arguments(seq, rtype, role, extraurlparams, sub_unit_types):
    """Return a list of links to be inserted in dropdown button to add subobjects through `rtype`
    and `role` but with an extra argument in url params, given through the `param_defs` list of
    3-uple defining argument's (name, value, link label).
    """
    _ = seq._cw._
    links = []
    urlparams = extraurlparams.copy()
    for argument, value, label in sub_unit_types:
        urlparams[argument] = value
        link = add_subobject_link(seq, rtype, role, urlparams,
                                  msg=_(label), klass='')
        if link:
            links.append(link)
    return links


@objectify_predicate
def is_archive_unit_ref(cls, req, rset=None, entity=None, **kwargs):
    """Return 1 if a unit_type value is specified in kwargs or in form parameters, and its value is
    'unit_ref'
    """
    try:
        # first check for unit_type specified in form params
        unit_type = req.form['unit_type']
        return int(unit_type == 'unit_ref')
    except KeyError:
        # if it's not, look if we're in the context of a archive unit or its first level choice
        if entity is None:
            assert rset is not None, \
                ('is_archive_unit_ref can only be used in the context of a SEDAArchiveUnit '
                 'or SEDAAltArchiveUnitArchiveUnitRefId entity, but no context entity specified')
            entity = rset.get_entity(0, 0)
        if entity.cw_etype == 'SEDAArchiveUnit':
            entity = entity.first_level_choice
        elif entity.cw_etype == 'SEDAArchiveUnitRefId':
            if not entity.seda_archive_unit_ref_id_from:
                return 0  # other kind of reference
            entity = entity.seda_archive_unit_ref_id_from[0]
            if entity.cw_etype != 'SEDAAltArchiveUnitArchiveUnitRefId':
                return 0  # other kind of reference
        assert entity.cw_etype == 'SEDAAltArchiveUnitArchiveUnitRefId', \
            ('is_archive_unit_ref can only be used in the context of a SEDAArchiveUnit, '
             'SEDAArchiveUnitRefId or SEDAAltArchiveUnitArchiveUnitRefId entity, not %s' % entity)
        return 0 if entity.content_sequence else 1


@objectify_predicate
def is_simple_keyword(cls, req, rset=None, entity=None, **kwargs):
    """Return 1 if a keyword_type value is specified in kwargs or in form parameters, and its value is
    'simple_keyword', or if given entity is not linked to a keyword reference.
    """
    try:
        # first check for unit_type specified in form params
        unit_type = req.form['keyword_type']
        return int(unit_type == 'simple_keyword')
    except KeyError:
        if entity is not None and not entity.reverse_seda_keyword_reference_from:
            return 1
        return 0


@objectify_predicate
def typed_reference(cls, req, entity=None, **kwargs):
    """Return positive score for content's typed data object references (IsPartOf, VersionOf, etc.),
    not those starting directly from archive unit.
    """
    # code below don't handle properly the case where entity isn't yet created while rtype isn't
    # specified (e.g. because it's an inlined form). To avoid false positive, we've to also ensure
    # we're within a full seda 2 profile (typed references aren't allowed in simplified profiles)
    if not is_full_seda2_profile(entity, kwargs.get('rset')):
        return 0
    if entity is None or not entity.has_eid():
        try:
            rtype, eid, role = req.form['__linkto'].split(':')
        except KeyError:
            pass
        else:
            if rtype == 'seda_data_object_reference':
                entity = req.entity_from_eid(eid)
            else:
                return 0
    else:
        entity = entity.seda_data_object_reference[0]
    if entity is not None and entity.cw_etype == CONTENT_ETYPE:
        return 0
    return 1


afs = uicfg.autoform_section
affk = uicfg.autoform_field_kwargs
pvs = uicfg.primaryview_section
pvdc = uicfg.primaryview_display_ctrl
rec = uicfg.reledit_ctrl


def unit_ref_vocabulary(form, field):
    """Form vocabulary function for archive unit references, necessary to get parent container while
    the entity is being created.
    """
    req = form._cw
    parent, container = parent_and_container(form.edited_entity)
    assert container is not None
    rset = req.execute('Any X, XUA ORDERBY XUA WHERE '
                       'X is SEDAArchiveUnit, X user_annotation XUA, X container R, R eid %(root)s',
                       {'root': container.eid})
    return [(entity.dc_title(), str(entity.eid)) for entity in rset.entities()]


affk.tag_subject_of(('SEDAArchiveUnitRefId', 'seda_archive_unit_ref_id_to', '*'),
                    {'choices': unit_ref_vocabulary})


def do_ref_vocabulary(form, field):
    """Form vocabulary function for data object references, necessary to get parent container while
    the entity is being created.
    """
    req = form._cw
    parent, container = parent_and_container(form.edited_entity)
    assert container is not None
    rset = req.execute('Any X, XUA ORDERBY XUA WHERE '
                       'X is IN(SEDABinaryDataObject, SEDAPhysicalDataObject), '
                       'X user_annotation XUA, X container R, R eid %(root)s',
                       {'root': container.eid})
    return [(entity.dc_title(), str(entity.eid)) for entity in rset.entities()]


for rtype in ('seda_data_object_reference_id', 'seda_target'):
    affk.tag_subject_of(('*', rtype, '*'), {'choices': do_ref_vocabulary})


pvs.tag_subject_of(
    ('SEDAArchiveUnit', 'seda_alt_archive_unit_archive_unit_ref_id', '*'),
    'hidden')


class SkipIBreadCrumbsAdapter(compound.IContainedBreadcrumbsAdapter):
    """IBreadCrumbsAdapter for entities which should not appears in breadcrumb, we want to go back to
    the parent
    """
    __select__ = is_instance('SEDAAltArchiveUnitArchiveUnitRefId',
                             CONTENT_ETYPE)

    def breadcrumbs(self, view=None, recurs=None):
        parent = self.parent_entity()
        adapter = parent.cw_adapt_to('IBreadCrumbs')
        return adapter.breadcrumbs(view, recurs)


class SkipInContextView(baseviews.InContextView):
    """Custom incontext view, for use in title of creation form, among others"""
    __select__ = is_instance('SEDAAltArchiveUnitArchiveUnitRefId',
                             CONTENT_ETYPE)

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        parent_archive_unit(entity).view('incontext', w=self.w)


class ArchiveUnitSubObjectsTab(viewlib.SubObjectsTab):
    """Abstract subobjects tab specific to archive unit to handle subentities below choice>sequence
    child transparently.
    """

    __abstract__ = True
    __select__ = is_instance('SEDAArchiveUnit') & ~is_archive_unit_ref()

    def entity_call(self, entity):
        seq = entity.first_level_choice.content_sequence
        self.display_add_button(seq)
        self.display_subobjects_list(seq)

    def url_params(self, entity):
        archive_unit = parent_archive_unit(entity)
        return {'__redirectparams': 'tab=' + self.__regid__,
                '__redirectpath': archive_unit.rest_path()}

    def parent(self, entity):
        return parent_archive_unit(entity)


class ArchiveUnitContentTab(tabs.TabsMixin, EntityView):
    """Base class for tabs whose content is generated by redirecting to a view on archive unit's
    content.
    """

    __abstract__ = True
    __select__ = ArchiveUnitSubObjectsTab.__select__
    content_vid = None  # set in concrete class

    def entity_call(self, entity):
        seq = entity.first_level_choice.content_sequence
        seq.view(self.content_vid, w=self.w)


class ContentSubObjectsView(viewlib.SubObjectsTab):
    """Base class to display subobjects of archive unit's content as if they were directly linked
    to it.
    """

    __abstract__ = True
    __select__ = is_instance(CONTENT_ETYPE)
    tabid = None  # set in concrete class

    def url_params(self, entity):
        params = super(ContentSubObjectsView, self).url_params(entity)
        params['__redirectpath'] = self.parent(entity).rest_path()
        return params

    def parent(self, entity):
        return (entity
                .reverse_seda_seq_alt_archive_unit_archive_unit_ref_id_management[0]
                .reverse_seda_alt_archive_unit_archive_unit_ref_id[0])


class ArchiveUnitTabbedPrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('SEDAArchiveUnit')

    tabs = [
        'main_tab',
        _('seda_management_tab'),
        _('seda_archive_units_tab'),
        _('seda_data_objects_tab'),
        # Content tabs
        _('seda_identification_tab'),
        _('seda_dates_tab'),
        _('seda_gps_tab'),
        _('seda_services_tab'),
        _('seda_agents_tab'),
        _('seda_coverage_tab'),
        _('seda_indexation_tab'),
        _('seda_relations_tab'),
        _('seda_events_tab'),
        _('seda_history_tab'),

    ]

    def entity_call(self, entity, **kwargs):
        super(ArchiveUnitTabbedPrimaryView, self).entity_call(entity, **kwargs)
        rwdg.bootstrap_dialog(self.w, self._cw._, clone._import_div_id(entity))


# main tab for archive unit reference ##########################################

au_ref_pvs = pvs.derive(__name__,
                        is_instance('SEDAArchiveUnit') & is_archive_unit_ref())
au_ref_pvs.tag_subject_of(
    ('SEDAArchiveUnit', 'seda_alt_archive_unit_archive_unit_ref_id', '*'),
    'attributes')
rec.tag_subject_of(('SEDAArchiveUnit', 'seda_alt_archive_unit_archive_unit_ref_id', '*'),
                   {'rvid': 'seda.reledit.simplelink',
                    'novalue_label': ' '})


class RefArchiveUnitSimpleLinkToEntityAttributeView(EntityView):
    __regid__ = 'seda.reledit.simplelink'
    __select__ = is_instance('SEDAAltArchiveUnitArchiveUnitRefId') & is_archive_unit_ref()

    def entity_call(self, entity):
        entity.reference.view('seda.reledit.complexlink',
                              initargs={'rtype': 'seda_archive_unit_ref_id_from'},
                              w=self.w)


# management tab ###############################################################

class ArchiveUnitManagementTab(viewlib.PrimaryTabWithoutBoxes):
    """Display management information about an archive unit."""

    __regid__ = 'seda_management_tab'
    __select__ = is_instance('SEDAArchiveUnit') & ~is_archive_unit_ref()

    rtype_role_targets = [
        ('seda_storage_rule', 'object', None),
        ('seda_appraisal_rule', 'object', None),
        ('seda_access_rule', 'object', None),
        ('seda_dissemination_rule', 'object', None),
        ('seda_reuse_rule', 'object', None),
        ('seda_classification_rule', 'object', None),
        ('seda_need_authorization', 'object', None),
    ]
    rsection, display_ctrl = rtags_from_rtype_role_targets(
        CONTENT_ETYPE, rtype_role_targets
    )

    def entity_call(self, entity, **kwargs):
        seq = entity.first_level_choice.content_sequence
        super(ArchiveUnitManagementTab, self).entity_call(seq, **kwargs)


class SimplifiedArchiveUnitManagementTab(ArchiveUnitManagementTab):
    __select__ = ArchiveUnitManagementTab.__select__ & simplified_profile()

    rtype_role_targets = [
        ('seda_appraisal_rule', 'object', None),
        ('seda_access_rule', 'object', None),
    ]
    rsection, display_ctrl = rtags_from_rtype_role_targets(
        CONTENT_ETYPE, rtype_role_targets
    )


# identification tab ###########################################################

class ArchiveUnitIdentificationTab(ArchiveUnitContentTab):
    """Display identification information about a full seda2 archive unit."""

    __regid__ = 'seda_identification_tab'
    __select__ = ArchiveUnitContentTab.__select__ & full_seda2_profile()
    content_vid = 'seda_content_identification'


class ContentIdentificationView(viewlib.PrimaryTabWithoutBoxes):
    """Display identification information about an archive unit content."""

    __regid__ = 'seda_content_identification'
    __select__ = is_instance(CONTENT_ETYPE)

    rtype_role_targets = [
        ('seda_source', 'object', None),
        ('seda_file_plan_position', 'object', None),
        ('seda_system_id', 'object', None),
        ('seda_originating_system_id', 'object', None),
        ('seda_archival_agency_archive_unit_identifier', 'object', None),
        ('seda_originating_agency_archive_unit_identifier', 'object', None),
        ('seda_transferring_agency_archive_unit_identifier', 'object', None),
    ]
    rsection, display_ctrl = rtags_from_rtype_role_targets(CONTENT_ETYPE, rtype_role_targets)


# dates tab ####################################################################

class ArchiveUnitDatesTab(ArchiveUnitContentTab):
    """Display dates information about a full seda2 archive unit."""

    __regid__ = 'seda_dates_tab'
    __select__ = ArchiveUnitContentTab.__select__ & full_seda2_profile()
    content_vid = 'seda_content_dates'


class ContentDatesView(viewlib.PrimaryTabWithoutBoxes):
    """Display dates information about an archive unit content."""

    __regid__ = 'seda_content_dates'
    __select__ = is_instance(CONTENT_ETYPE)

    rtype_role_targets = [
        ('seda_created_date', 'object', None),
        ('seda_transacted_date', 'object', None),
        ('seda_acquired_date', 'object', None),
        ('seda_sent_date', 'object', None),
        ('seda_received_date', 'object', None),
        ('seda_registered_date', 'object', None),
        ('seda_start_date', 'object', None),
        ('seda_end_date', 'object', None),
    ]
    rsection, display_ctrl = rtags_from_rtype_role_targets(CONTENT_ETYPE, rtype_role_targets)


# GPS tab ######################################################################

class ArchiveUnitGPSTab(ArchiveUnitContentTab):
    """Display GPS information about a full seda2 archive unit."""

    __regid__ = 'seda_gps_tab'
    __select__ = ArchiveUnitContentTab.__select__ & full_seda2_profile()
    content_vid = 'seda_content_gps'


class ContentGPSView(viewlib.PrimaryTabWithoutBoxes):
    """Display GPS information about an archive unit content."""

    __regid__ = 'seda_content_gps'
    __select__ = is_instance(CONTENT_ETYPE)

    rsection, display_ctrl = rtags_from_xsd_element(CONTENT_ETYPE, 'Gps')


# services tab #################################################################

class ArchiveUnitServicesTab(ArchiveUnitContentTab):
    """Display services related to a full seda2 archive unit."""

    __regid__ = 'seda_services_tab'
    __select__ = ArchiveUnitContentTab.__select__ & full_seda2_profile()
    content_vid = 'seda_content_services'


class ContentServicesView(viewlib.PrimaryTabWithoutBoxes):
    """Display services related to an archive unit content."""

    __regid__ = 'seda_content_services'
    __select__ = is_instance(CONTENT_ETYPE)

    rtype_role_targets = [
        ('seda_originating_agency_from', 'object', None),
        ('seda_submission_agency_from', 'object', None),
        ('seda_authorized_agent_from', 'object', None),
    ]
    rsection, display_ctrl = rtags_from_rtype_role_targets(CONTENT_ETYPE, rtype_role_targets)


# agents tab ###################################################################

class ArchiveUnitAgentsTab(ArchiveUnitContentTab):
    """Display agents related to a full seda2 archive unit."""

    __regid__ = 'seda_agents_tab'
    __select__ = ArchiveUnitContentTab.__select__ & full_seda2_profile()
    content_vid = 'seda_content_agents'


class ContentAgentsView(ContentSubObjectsView):
    """Display agents related to an archive unit content."""

    __regid__ = 'seda_content_agents'
    __select__ = is_instance(CONTENT_ETYPE)
    tabid = ArchiveUnitAgentsTab.__regid__

    rtype_role_targets = [
        ('seda_writer_from', 'object', None),
        ('seda_addressee_from', 'object', None),
        ('seda_recipient_from', 'object', None),
    ]

    _('creating SEDAWriter (SEDAWriter seda_writer_from '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')
    _('creating SEDAAddressee (SEDAAddressee seda_addressee_from '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')
    _('creating SEDARecipient (SEDARecipient seda_recipient_from '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linto)s)')


# coverage tab #################################################################

class ArchiveUnitCoverageTab(ArchiveUnitContentTab):
    """Display coverage information about a full seda2 archive unit."""

    __regid__ = 'seda_coverage_tab'
    __select__ = ArchiveUnitContentTab.__select__ & full_seda2_profile()
    content_vid = 'seda_content_coverage'


class ContentCoverageView(ContentSubObjectsView):
    """Display coverage information about an archive unit content."""

    __regid__ = 'seda_content_coverage'
    __select__ = is_instance(CONTENT_ETYPE)
    tabid = ArchiveUnitCoverageTab.__regid__

    rtype_role_targets = [('seda_spatial', 'object', None),
                          ('seda_temporal', 'object', None),
                          ('seda_juridictional', 'object', None)]

    _('creating SEDASpatial (SEDASpatial seda_spatial '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')
    _('creating SEDATemporal (SEDATemporal seda_temporal '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')
    _('creating SEDAJuridictional (SEDAJuridictional seda_juridictional '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')


class TypeListItemContentView(viewlib.ListItemContentView):
    """Extended list item content view including the entity's type (for case where the list may
    include entities of different types).
    """
    __select__ = is_instance('SEDAWriter', 'SEDAAddressee', 'SEDARecipient',
                             'SEDASpatial', 'SEDATemporal', 'SEDAJuridictional')

    def entity_call(self, entity):
        entity.view('seda.type_meta', w=self.w)


# indexation tab ###############################################################

class ArchiveUnitIndexationTab(ArchiveUnitContentTab):
    """Display content's indexation about an archive unit."""

    __regid__ = 'seda_indexation_tab'
    content_vid = 'seda_content_indexation'


class ContentIndexationView(ContentSubObjectsView):
    """Display indexation (keywords and tags) about an archive unit content."""

    __regid__ = 'seda_content_indexation'
    tabid = ArchiveUnitIndexationTab.__regid__

    rtype_role_targets = [
        ('seda_keyword', 'object', 'SEDAKeyword'),
        ('seda_tag', 'object', 'SEDATag'),
    ]
    keyword_custom_arguments = [
        ('keyword_type', 'concept_keyword', _('keyword concept')),
        ('keyword_type', 'simple_keyword', _('keyword simple')),
    ]

    _('creating SEDAKeyword (SEDAKeyword seda_keyword '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')
    _('creating SEDATag (SEDATag seda_tag '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')

    def display_add_button(self, entity):
        urlparams = self.url_params(entity)
        links = add_links_with_custom_arguments(entity, 'seda_keyword', 'object', urlparams,
                                                self.keyword_custom_arguments)
        rtype_roles = [(rtype, role) for rtype, role, _ in self.rtype_role_targets
                       if rtype != 'seda_keyword']
        links += viewlib.add_links_from_rtype_roles(entity, rtype_roles, urlparams)
        viewlib.display_add_button(self.w, links, entity._cw.__('add'))


class SimplifiedArchiveUnitContentIndexationView(ContentIndexationView):

    __select__ = ContentIndexationView.__select__ & simplified_profile()

    rtype_role_targets = [('seda_keyword', 'object', 'SEDAKeyword')]


class KeywordBusinessValueEntityView(viewlib.ListItemContentView):

    __select__ = viewlib.ListItemContentView.__select__ & is_instance('SEDAKeyword')

    def entity_call(self, entity):
        if entity.reverse_seda_keyword_reference_from:
            kwr = entity.reverse_seda_keyword_reference_from[0]
            if kwr.concept:
                kwr_value = kwr.concept.view('oneline')
                msg = xml_escape(self._cw._('keyword concept: {0}')).format(kwr_value)
            elif kwr.scheme:
                kwr_value = kwr.scheme.view('oneline')
                msg = xml_escape(self._cw._('keyword scheme: {0}')).format(kwr_value)
            else:
                msg = xml_escape(self._cw._('<no keyword scheme specified>'))
        else:
            if entity.keyword_content:
                content = entity.keyword_content
            else:
                content = self._cw._('<no value specified>')
            msg = xml_escape(self._cw._('keyword: {0}').format(content))
        self.w(u'<span class="value">{0} {1}</span>'.format(msg, entity.view('seda.xsdmeta')))

        if entity.reverse_seda_keyword_type_from:
            kwt = entity.reverse_seda_keyword_type_from[0]
            if kwt.seda_keyword_type_to:
                kwt_value = kwt.seda_keyword_type_to[0].label()
            else:
                kwt_value = self._cw._('<no type specified>')
            msg = xml_escape(self._cw._('keyword type: {0}').format(kwt_value))
            self.w(u'<br/><span>{0} {1}</span>'.format(msg, kwt.view('seda.xsdmeta')))


afs.tag_subject_of(('SEDAKeywordReference', 'seda_keyword_reference_to_scheme', '*'),
                   'main', 'attributes')
affk.set_field_kwargs('SEDAKeywordReference', 'seda_keyword_reference_to_scheme',
                      help=_('select a type to filter out unrelated vocabularies'))
affk.set_field_kwargs('SEDAKeywordReference', 'seda_keyword_reference_to',
                      help=_('select first a vocabulary then type here to prompt auto-completion'),
                      widget=widgets.ConceptAutoCompleteWidget(
                          slave_name='seda_keyword_reference_to',
                          master_name='seda_keyword_reference_to_scheme'))
affk.set_fields_order('SEDAKeywordReference', ['user_cardinality',
                                               'seda_keyword_reference_to_scheme',
                                               'seda_keyword_reference_to'])

# add rule in afs for 'complex keyword'
afs.tag_attribute(('SEDAKeyword', 'keyword_content'), 'main', 'hidden')
afs.tag_attribute(('SEDAKeywordReference', 'user_cardinality'), 'main', 'hidden')
# custom afs to handle 'simple keyword'
kw_simple_afs = afs.derive(__name__,
                           is_instance('SEDAKeyword') & is_simple_keyword())
kw_simple_afs.tag_attribute(('SEDAKeyword', 'keyword_content'), 'main', 'attributes')
kw_simple_afs.tag_object_of(
    ('*', 'seda_keyword_reference_from', 'SEDAKeyword'),
    'main', 'hidden')
# but one ordering is enough to rule them all
affk.set_fields_order('SEDAKeyword', [('seda_keyword_type_from', 'object'),
                                      'keyword_content',
                                      ('seda_keyword_reference_from', 'object')])

affk.set_field_kwargs('SEDAKeywordType', 'seda_keyword_type_to',
                      widget=widgets.KeywordTypeMasterWidget(
                          slave_base_name='seda_keyword_reference_to_scheme'))


class ComplexKeywordAutomaticEntityForm(autoform.AutomaticEntityForm):
    __select__ = (is_instance('SEDAKeyword') & ~is_simple_keyword())

    def should_display_inline_creation_form(self, rschema, existing, card):
        # force display of type and keyword
        if not existing and rschema in ('seda_keyword_type_from', 'seda_keyword_reference_from'):
            return True
        return False

    def should_display_add_new_relation_link(self, rschema, existing, card):
        return False


class ComplexKeywordEditionFormView(autoform.InlineEntityEditionFormView):
    __select__ = (autoform.InlineEntityEditionFormView.__select__
                  & is_instance('SEDAKeywordType', 'SEDAKeywordReference')
                  & ~is_simple_keyword())
    removejs = None


class ComplexKeywordCreationFormView(autoform.InlineEntityCreationFormView):
    __select__ = (autoform.InlineEntityCreationFormView.__select__
                  & specified_etype_implements('SEDAKeywordType', 'SEDAKeywordReference')
                  & ~is_simple_keyword())
    removejs = None


# relations tab ################################################################

class ArchiveUnitRelationsTab(ArchiveUnitContentTab):
    """Display content's relations about a full seda2  archive unit."""

    __regid__ = 'seda_relations_tab'
    __select__ = ArchiveUnitContentTab.__select__ & full_seda2_profile()
    content_vid = 'seda_content_relations'


class ContentRelationsView(ContentSubObjectsView):
    """Display relation information about an archive unit content."""

    __regid__ = 'seda_content_relations'
    tabid = ArchiveUnitRelationsTab.__regid__

    rtype_role_targets = [('seda_is_version_of', 'object', None),
                          ('seda_replaces', 'object', None),
                          ('seda_requires', 'object', None),
                          ('seda_is_part_of', 'object', None),
                          ('seda_references', 'object', None)]

    _('creating SEDAIsVersionOf (SEDAIsVersionOf seda_is_version_of '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')
    _('creating SEDAReplaces (SEDAReplaces seda_replaces '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')
    _('creating SEDARequires (SEDARequires seda_requires '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')
    _('creating SEDAIsPartOf (SEDAIsPartOf seda_is_part_of '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')
    _('creating SEDAReferences (SEDAReferences seda_references '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')


class ReferenceListItemContentView(viewlib.ListItemContentView):
    __select__ = is_instance('SEDAIsVersionOf', 'SEDAReplaces', 'SEDARequires', 'SEDAIsPartOf',
                             'SEDAReferences')

    def entity_call(self, entity):
        self.w(u'<b>{} '.format(entity.dc_type()))
        entity.view('seda.xsdmeta')
        self.w(u'</b> :')
        alt_rtype = 'seda_alt_{}_archive_unit_ref_id'.format(un_camel_case(entity.cw_etype[4:]))
        alt = entity.related(alt_rtype).one()
        alternatives = viewlib.alternative_values(alt, alt_rtype)
        self.w(u'<div class="value alternative">')
        if alternatives:
            self.w(alternatives)
        else:
            self.wdata(self._cw._('<no value specified>'))
        self.w(u'</div>')
        self.w(u'<div class="clearfix"/>')


do_ref_afs = afs.derive(__name__,
                        is_instance('SEDADataObjectReference') & typed_reference())
do_ref_afs.tag_attribute(('SEDADataObjectReference', 'user_cardinality'), 'main', 'hidden')

for etype in ('SEDAAltIsPartOfArchiveUnitRefId',
              'SEDAAltIsVersionOfArchiveUnitRefId',
              'SEDAAltReferencesArchiveUnitRefId',
              'SEDAAltReplacesArchiveUnitRefId',
              'SEDAAltRequiresArchiveUnitRefId'):
    affk.set_fields_order(etype, [('seda_data_object_reference', 'object'),
                                  ('seda_repository_object_pid', 'object'),
                                  ('seda_archive_unit_ref_id_from', 'object'),
                                  ('seda_repository_archive_unit_pid', 'object')])


# event tab ####################################################################

class ArchiveUnitEventsTab(ArchiveUnitContentTab):
    """Display content's relations about a full seda2 archive unit."""

    __regid__ = 'seda_events_tab'
    __select__ = ArchiveUnitContentTab.__select__ & full_seda2_profile()
    content_vid = 'seda_content_events'


class ContentEventsView(ContentSubObjectsView):
    """Display events about an archive unit content."""

    __regid__ = 'seda_content_events'
    tabid = ArchiveUnitEventsTab.__regid__

    rtype_role_targets = [
        ('seda_event', 'object', None),
    ]

    _('creating SEDAEvent (SEDAEvent seda_event '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')


class EventListItemContentView(viewlib.ListItemContentView):

    __select__ = viewlib.ListItemContentView.__select__ & is_instance('SEDAEvent')

    def entity_call(self, entity):
        entity.view('seda.xsdmeta', w=self.w, skip_one_card=True, with_annotation=False)
        attrs = []
        for rtype in ['seda_event_type_from',
                      'seda_event_identifier',
                      'seda_event_detail']:
            related = getattr(entity, 'reverse_' + rtype)
            if related:
                if related[0].user_cardinality == '1':
                    card = self._cw._('mandatory')
                else:
                    card = self._cw._('optional')
                value = ''
                if rtype == 'seda_event_type_from':
                    value = related[0].seda_event_type_to
                    if value:
                        value = value[0].label()
                attrs.append(u'{rtype} {value} {card}'.format(rtype=self._cw.__(rtype + '_object'),
                                                              value=value,
                                                              card=card))
        if attrs:
            self.w(u' ({0})'.format(', '.join(attrs)))
        description = getattr(entity, 'user_annotation', None)
        if description:
            self.w(u' <div class="description text-muted">%s</div>' % description)


affk.set_fields_order('SEDAEvent', ['user_cardinality',
                                    ('seda_event_type_from', 'object'),
                                    ('seda_event_identifier', 'object'),
                                    ('seda_event_detail', 'object')])


# history tab ##################################################################

class ArchiveUnitHistoryTab(ArchiveUnitContentTab):
    """Display content's custodial history about an archive unit."""

    __regid__ = 'seda_history_tab'
    content_vid = 'seda_content_history'


class ContentHistoryView(ContentSubObjectsView):
    """Display custodial history information about an archive unit content."""

    __regid__ = 'seda_content_history'
    tabid = ArchiveUnitHistoryTab.__regid__

    rtype_role_targets = [('seda_custodial_history_item', 'object', None)]

    _('creating SEDACustodialHistoryItem (SEDACustodialHistoryItem seda_custodial_history_item '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')


class CustodialHistoryItemListItemContentView(viewlib.ListItemContentView):

    __select__ = viewlib.ListItemContentView.__select__ & is_instance('SEDACustodialHistoryItem')

    def entity_call(self, entity):
        super(CustodialHistoryItemListItemContentView, self).entity_call(entity)
        if entity.reverse_seda_when:
            when = entity.reverse_seda_when[0]
            if when.user_cardinality == '1':
                self.w(u' ({})'.format(self._cw._('mandatory timestamp')))
            else:
                self.w(u' ({})'.format(self._cw._('optional timestamp')))


# main tab for archive unit content ############################################

class ArchiveUnitPrimaryTab(tabs.PrimaryTab):
    """Overriden primary tab to display attributes from both the archive unit and it's content
    sequence.
    """

    __select__ = is_instance('SEDAArchiveUnit') & ~is_archive_unit_ref()

    def render_entity_attributes(self, entity):
        """Renders all attributes and relations in the 'attributes' section.
        """
        display_attributes = list(self._display_attributes(entity))
        seq = entity.first_level_choice.content_sequence
        view = self._cw.vreg['views'].select('seda_content_main', self._cw, rset=seq.as_rset())
        display_attributes += view._display_attributes(seq)
        if display_attributes:
            self.w(u'<table class="table cw-table-primary-entity">')
            for rschema, role, dispctrl, value in display_attributes:
                label = self._rel_label(entity, rschema, role, dispctrl)
                self.render_attribute(label, value, table=True)
            self.w(u'</table>')


# add as a monkey patch the first step of original 'render_entity_attributes'
# method, which is unfortunatly monolitic in cubicweb. We need this so we can
# have attributes from two distinct entities as if it was only one.

@monkeypatch(tabs.PrimaryTab)
def _display_attributes(self, entity):
    for rschema, targets, role, dispctrl in self._section_def(entity, 'attributes'):
        vid = dispctrl.get('vid', 'reledit')
        if rschema.final or vid == 'reledit' or dispctrl.get('rtypevid'):
            value = entity.view(vid, rtype=rschema.type, role=role,
                                initargs={'dispctrl': dispctrl})
        else:
            rset = self._relation_rset(entity, rschema, role, dispctrl)
            if rset:
                value = self._cw.view(vid, rset)
            else:
                value = None
        if value is not None and value != '':
            yield (rschema, role, dispctrl, value)


content_ordered_fields = [
    ('seda_description_level', 'subject'),
    ('seda_title', 'object'),
    ('seda_start_date', 'object'),
    ('seda_end_date', 'object'),
    ('seda_description', 'object'),
    ('seda_originating_agency_from', 'object'),
    ('seda_transferring_agency_archive_unit_identifier', 'object'),
    ('seda_system_id', 'object'),
    ('seda_version', 'object'),
    ('seda_type_from', 'object'),
    ('seda_document_type', 'object'),
    ('seda_status', 'object'),
    ('seda_language_from', 'object'),
    ('seda_description_language_from', 'object'),
]


class ContentMainView(viewlib.PrimaryTabWithoutBoxes):
    """Display content information which are not in a dedicated tab."""

    __regid__ = 'seda_content_main'
    __select__ = is_instance(CONTENT_ETYPE)

    rtype_role_targets = [field_def + (None,) for field_def in content_ordered_fields]
    rsection, display_ctrl = rtags_from_rtype_role_targets(CONTENT_ETYPE, rtype_role_targets)


class SimplifiedContentMainView(ContentMainView):
    """Display content information which are not in a dedicated tab for a simplified archive unit.
    """
    __select__ = ContentMainView.__select__ & simplified_profile()

    rtype_role_targets = [
        ('seda_description_level', 'subject', None),
        ('seda_title', 'object', None),
        ('seda_start_date', 'object', None),
        ('seda_end_date', 'object', None),
        ('seda_description', 'object', None),
        ('seda_originating_agency_from', 'object', None),
        ('seda_transferring_agency_archive_unit_identifier', 'object', None),
        ('seda_system_id', 'object', None),
        ('seda_language_from', 'object', None),
    ]
    rsection, display_ctrl = rtags_from_rtype_role_targets(CONTENT_ETYPE, rtype_role_targets)


for rtype, role in content_ordered_fields:
    if role == 'subject':
        pvs.tag_subject_of((CONTENT_ETYPE, rtype, '*'), 'attributes')
    else:
        pvs.tag_object_of(('*', rtype, CONTENT_ETYPE), 'attributes')
    if rtype == 'seda_description_level':
        novalue_label = _('<no value specified>')
    else:
        novalue_label = ' '
    vid = 'seda.reledit.complexlink' if rtype.endswith('_from') else 'seda.reledit.text'
    if role == 'subject':
        rec.tag_subject_of((CONTENT_ETYPE, rtype, '*'),
                           {'rvid': vid, 'novalue_label': novalue_label})
    else:
        rec.tag_object_of(('*', rtype, CONTENT_ETYPE),
                          {'rvid': vid, 'novalue_label': novalue_label})

pvs.tag_object_of(('*', 'seda_seq_alt_archive_unit_archive_unit_ref_id_management', '*'), 'hidden')

for rtype in ('seda_language_to', 'seda_description_language_to',
              'seda_archival_agency', 'seda_transferring_agency',
              'seda_originating_agency_to', 'seda_submission_agency_to',
              'seda_authorized_agent_to',
              'seda_writer_to', 'seda_addressee_to', 'seda_recipient_to'):
    affk.tag_subject_of(('*', rtype, '*'),
                        {'widget': rwdg.RelationFacetWidget})

affk.set_fields_order(CONTENT_ETYPE,
                      ['user_cardinality', 'user_annotation'] + content_ordered_fields)
pvdc.set_fields_order(CONTENT_ETYPE,
                      ['user_cardinality', 'user_annotation'] + content_ordered_fields)

# remove from relations section and autoform what is shown in tabs
for cls in (ContentIdentificationView,
            ContentDatesView,
            ContentServicesView,
            ContentAgentsView,
            ContentIndexationView,
            ContentEventsView):
    for rtype, role, target in cls.rtype_role_targets:
        if role == 'object':
            pvs.tag_object_of(('*', rtype, CONTENT_ETYPE), 'hidden')
            afs.tag_object_of(('*', rtype, CONTENT_ETYPE), 'main', 'hidden')
        else:
            pvs.tag_subject_of((CONTENT_ETYPE, rtype, '*'), 'hidden')
            afs.tag_subject_of((CONTENT_ETYPE, rtype, '*'), 'main', 'hidden')


# archive units tab ############################################################

class ArchiveUnitArchiveUnitsTab(ArchiveUnitSubObjectsTab):
    """Tab for sub-archive units of an archive unit"""

    __regid__ = 'seda_archive_units_tab'

    rtype = 'seda_archive_unit'
    role = 'object'
    unit_custom_arguments = [
        ('unit_type', 'unit_content', _('archive unit (content)')),
        ('unit_type', 'unit_ref', _('archive unit (reference)')),
    ]

    _('creating SEDAArchiveUnit (SEDAArchiveUnit seda_archive_unit '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')

    def display_add_button(self, entity):
        urlparams = self.url_params(entity)
        links = add_links_with_custom_arguments(entity, self.rtype, self.role, urlparams,
                                                self.unit_custom_arguments)
        if links:
            import_url = clone.import_unit_url(self._cw, parent_archive_unit(entity))
            links.append(tags.a(self._cw._('import_unit'), href=import_url))
        viewlib.display_add_button(self.w, links, self._cw.__('add'))

    def display_subobjects_list(self, entity):
        rset = entity.related(self.rtype, self.role)
        if rset:
            subvid = 'seda.listitem'
            self._cw.view('list', rset=rset, w=self.w, subvid=subvid,
                          parent=self.parent(entity), tabid=self.__regid__)


class SimplifiedArchiveUnitArchiveUnitsTab(ArchiveUnitArchiveUnitsTab):

    __select__ = ArchiveUnitArchiveUnitsTab.__select__ & simplified_profile()

    unit_custom_arguments = [
        ('unit_type', 'unit_content', _('archive unit (content)')),
    ]


# data objects tab #############################################################

class ArchiveUnitDataObjectReferencesTab(ArchiveUnitSubObjectsTab):
    """Tab for data object references of an archive unit"""

    __regid__ = 'seda_data_objects_tab'

    rtype_role_targets = [('seda_data_object_reference', 'object', None)]

    _('creating SEDADataObjectReference (SEDADataObjectReference seda_data_object_reference '
      'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement %(linkto)s)')


class SimplifiedArchiveUnitDataObjectReferencesTab(ArchiveUnitDataObjectReferencesTab):
    """Tab for data object references of an archive unit within a simplified transfer: see
    referenced data object as if they were children of the archive unit referencing them (only one
    reference is allowed in such case, so this is fine).
    """

    __select__ = ArchiveUnitDataObjectReferencesTab.__select__ & simplified_profile()

    rtype_role_targets = [('seda_binary_data_object', 'object', 'SEDABinaryDataObject')]

    def display_add_button(self, entity):
        rtype_roles = [(rtype, role) for rtype, role, _ in self.rtype_role_targets]
        params = self.url_params(entity)
        params['referenced_by'] = text_type(entity.eid)
        transfer = entity.container[0]
        links = []
        if transfer.cw_etype == 'SEDAArchiveTransfer':
            links = viewlib.add_links_from_rtype_roles(transfer, rtype_roles, params)
            label = self._cw.__('add')
        else:
            if has_rel_perm('add', entity, 'seda_data_object_reference', 'object'):
                vreg = self._cw.vreg
                url = vreg['etypes'].etype_class('SEDABinaryDataObject').cw_create_url(
                    self._cw, **params)
                label = self._cw.__('seda_binary_data_object_object')
                links = [tags.a(label, href=url, title=self._cw.__('New SEDABinaryDataObject'))]
        viewlib.display_add_button(self.w, links, self._cw.__('add'))

    def display_subobjects_list(self, entity):
        rset = self._cw.execute(
            'Any DO, DOUA, DOUC ORDERBY DOUA WHERE '
            'DO user_annotation DOUA, DO user_cardinality DOUC, '
            'REF seda_data_object_reference_id DO, REF seda_data_object_reference SEQ, '
            'SEQ eid %(x)s', {'x': entity.eid})
        if rset:
            self._cw.view('list', rset=rset, parent=self.parent(entity), w=self.w,
                          subvid=self.subvid, tabid=self.tabid)


# reference / content archive unit forms #######################################

# Top level ArchiveUnit form: create to distinct forms, one form archive unit reference and the
# other for archive unit content. This is done by a mix of uicfg, form and renderer customization
# depending on a 'unit_type' parameter in form params.

pvs.tag_object_of(('*', 'seda_data_object_reference', CONTENT_ETYPE),
                  'hidden')
afs.tag_object_of(('*', 'seda_data_object_reference', CONTENT_ETYPE),
                  'main', 'hidden')

# add rtags for content archive unit in default afs
afs.tag_object_of(
    ('*', 'seda_archive_unit_ref_id_from', 'SEDAAltArchiveUnitArchiveUnitRefId'),
    'inlined', 'hidden')
afs.tag_subject_of(
    ('SEDAAltArchiveUnitArchiveUnitRefId',
     'seda_seq_alt_archive_unit_archive_unit_ref_id_management', '*'),
    'inlined', 'inlined')

# and create a custom one for reference archive unit
au_ref_afs = afs.derive(__name__,
                        is_instance('SEDAAltArchiveUnitArchiveUnitRefId')
                        & is_archive_unit_ref())
au_ref_afs.tag_object_of(
    ('*', 'seda_archive_unit_ref_id_from', 'SEDAAltArchiveUnitArchiveUnitRefId'),
    'inlined', 'inlined')
au_ref_afs.tag_subject_of(
    ('SEDAAltArchiveUnitArchiveUnitRefId',
     'seda_seq_alt_archive_unit_archive_unit_ref_id_management', '*'),
    'inlined', 'hidden')


class AltArchiveUnitRefIdSimplifiedAutomaticEntityForm(widgets.SimplifiedAutomaticEntityForm):
    """Force display of AltArchiveUnitArchiveUnitRefId's sub-ArchiveUnitRefId or
    SeqAltArchiveUnitArchiveUnitRefIdManagement (uicfg will control which of them is displayed).
    """

    __select__ = (widgets.SimplifiedAutomaticEntityForm.__select__
                  & is_instance('SEDAAltArchiveUnitArchiveUnitRefId'))


class ArchiveUnitNoTitleEntityInlinedFormRenderer(widgets.NoTitleEntityInlinedFormRenderer):
    """Don't display any title nor remove link for AltArchiveUnitArchiveUnitRefId,
    SeqAltArchiveUnitArchiveUnitRefIdManagement or ArchiveUnitRefId in the context of an archive
    unit reference.
    """

    __select__ = (widgets.NoTitleEntityInlinedFormRenderer.__select__
                  & (is_instance('SEDAAltArchiveUnitArchiveUnitRefId',
                                 CONTENT_ETYPE)
                     | (is_instance('SEDAArchiveUnitRefId')
                        & is_archive_unit_ref())))


copy_afs = afs.derive(__name__, afs.__select__ & match_form_params(vid='copy'))
copy_afs.tag_subject_of(('*', 'seda_alt_archive_unit_archive_unit_ref_id', '*'), 'main', 'hidden')
