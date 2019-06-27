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
"""cubicweb-seda views for ArchiveTransfer"""

from logilab.common.decorators import monkeypatch
from logilab.common.registry import objectify_predicate

from cubicweb import _, tags
from cubicweb.predicates import is_instance
from cubicweb.web import formwidgets as fw
from cubicweb.web.views import tabs, uicfg, reledit

from cubes.relationwidget import views as rwdg

from ..xsd2yams import RULE_TYPES
from ..entities import full_seda2_profile, simplified_profile, parent_and_container
from . import rtags_from_xsd_element, rtags_from_rtype_role_targets
from . import clone, viewlib
from . import uicfg as sedauicfg  # noqa - ensure those rules are defined first

at_ordered_fields = [
    ('seda_archival_agency', 'subject'),
    ('seda_transferring_agency', 'subject'),
    ('seda_transfer_request_reply_identifier', 'object'),
    ('seda_comment', 'object'),
    ('seda_signature', 'object'),
    ('seda_archival_agreement', 'object'),
    ('seda_service_level', 'object'),
    ('seda_acquisition_information_from', 'object'),
    ('seda_legal_status_from', 'object'),
    ('seda_originating_agency_identifier', 'object'),
    ('seda_submission_agency_identifier', 'object')]

pvs = uicfg.primaryview_section
pvdc = uicfg.primaryview_display_ctrl
rec = uicfg.reledit_ctrl
afs = uicfg.autoform_section
affk = uicfg.autoform_field_kwargs

pvs.tag_attribute(('SEDAArchiveTransfer', 'title'), 'hidden')
pvs.tag_attribute(('SEDAArchiveTransfer', 'simplified_profile'), 'hidden')
pvs.tag_attribute(('SEDAArchiveTransfer', 'compat_list'), 'hidden')

for rtype, role in at_ordered_fields:
    if rtype.endswith('agency'):
        assert role == 'subject'
        pvs.tag_subject_of(('SEDAArchiveTransfer', rtype, '*'), 'attributes')
        rec.tag_subject_of(('SEDAArchiveTransfer', rtype, '*'),
                           {'rvid': 'seda.reledit.simplelink',
                            'novalue_label': _('<no value specified>')})
    else:
        assert role == 'object'
        pvs.tag_object_of(('*', rtype, 'SEDAArchiveTransfer'), 'attributes')
        if rtype in ('seda_archival_agreement', 'seda_comment'):
            simplified_section = 'attributes'
        else:
            simplified_section = 'hidden'
        rec.tag_object_of(('*', rtype, 'SEDAArchiveTransfer'),
                          {'rvid': 'seda.reledit.text',
                           'novalue_label': ' '})
        # hide extra-fields from main form, as their appearance depends on the simplified_profile
        # switch
        afs.tag_object_of(('*', rtype, 'SEDAArchiveTransfer'), 'main', 'hidden')

affk.set_field_kwargs('SEDAArchiveTransfer', 'title', widget=fw.TextInput({'size': 80}))
affk.set_fields_order('SEDAArchiveTransfer',
                      ['title', 'simplified_profile', 'user_annotation'] + at_ordered_fields)
pvdc.set_fields_order('SEDAArchiveTransfer', ['title', 'user_annotation'] + at_ordered_fields)


# don't show inheritance control on top level rules
@objectify_predicate
def top_level_rule(cls, req, rset=None, entity=None, **kwargs):
    """Predicate returning 1 score if rule is linked to the transfer, not to an archive unit."""
    if entity is None:
        entity = rset.one()
    parent = parent_and_container(entity)[0]
    if parent.cw_etype == 'SEDAArchiveTransfer':
        return 1
    return 0


top_level_rule_afs = afs.derive(
    __name__,
    is_instance(*['SEDA{0}Rule'.format(rule_type.capitalize())
                  for rule_type in RULE_TYPES]) & top_level_rule())
for rule_type in RULE_TYPES:
    etype = 'SEDA{0}Rule'.format(rule_type.capitalize())
    rtype = 'seda_alt_{0}_rule_prevent_inheritance'.format(rule_type)
    top_level_rule_afs.tag_subject_of((etype, rtype, '*'), 'main', 'hidden')


class ArchiveTransferTabbedPrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('SEDAArchiveTransfer')
    tabs = [
        'main_tab',
        _('seda_at_code_list_versions_tab'),
        _('seda_management_tab'),
        _('seda_data_objects_tab'),
        _('seda_archive_units_tab'),
        _('seda_at_related_transfers_tab'),
        _('seda_at_diagnose_tab'),
    ]

    def entity_call(self, entity, **kwargs):
        super(ArchiveTransferTabbedPrimaryView, self).entity_call(entity, **kwargs)
        rwdg.bootstrap_dialog(self.w, self._cw._, clone._import_div_id(entity))


class ArchiveTransferCodeListVersionsTab(viewlib.PrimaryTabWithoutBoxes):
    """Tab for code list versions information of an archive transfer."""
    __regid__ = 'seda_at_code_list_versions_tab'
    __select__ = is_instance('SEDAArchiveTransfer') & full_seda2_profile()

    rsection, display_ctrl = rtags_from_xsd_element('SEDAArchiveTransfer', 'CodeListVersions')


class ArchiveTransferManagementTab(viewlib.PrimaryTabWithoutBoxes):
    """Main tab for management data of an archive transfer"""
    __regid__ = 'seda_management_tab'
    __select__ = is_instance('SEDAArchiveTransfer')

    rtype_role_targets = [
        ('seda_storage_rule', 'object', None),
        ('seda_appraisal_rule', 'object', None),
        ('seda_access_rule', 'object', None),
        ('seda_dissemination_rule', 'object', None),
        ('seda_reuse_rule', 'object', None),
        ('seda_classification_rule', 'object', None),
        ('seda_need_authorization', 'object', None),
    ]
    rsection, display_ctrl = rtags_from_rtype_role_targets('SEDAArchiveTransfer',
                                                           rtype_role_targets)


class SimplifiedArchiveTransferManagementTab(ArchiveTransferManagementTab):
    __select__ = ArchiveTransferManagementTab.__select__ & simplified_profile()

    rtype_role_targets = [
        ('seda_appraisal_rule', 'object', None),
        ('seda_access_rule', 'object', None),
    ]
    rsection, display_ctrl = rtags_from_rtype_role_targets('SEDAArchiveTransfer',
                                                           rtype_role_targets)


class ArchiveTransferDataObjectsTab(viewlib.SubObjectsTab):
    """Tab for data objects of an archive transfer"""
    __regid__ = 'seda_data_objects_tab'
    __select__ = is_instance('SEDAArchiveTransfer') & full_seda2_profile()

    rtype_role_targets = [
        ('seda_binary_data_object', 'object', 'SEDABinaryDataObject'),
        ('seda_physical_data_object', 'object', 'SEDAPhysicalDataObject'),
    ]

    _('creating SEDABinaryDataObject (SEDABinaryDataObject seda_binary_data_object '
      'SEDAArchiveTransfer %(linkto)s)')
    _('creating SEDAPhysicalDataObject (SEDAPhysicalDataObject seda_physical_data_object '
      'SEDAArchiveTransfer %(linkto)s)')


class ArchiveTransferArchiveUnitsTab(viewlib.SubObjectsTab):
    """Tab for archive units of an archive transfer"""
    __regid__ = 'seda_archive_units_tab'
    __select__ = is_instance('SEDAArchiveTransfer')

    rtype_role_targets = [('seda_archive_unit', 'object', None)]

    _('creating SEDAArchiveUnit (SEDAArchiveUnit seda_archive_unit '
      'SEDAArchiveTransfer %(linkto)s)')

    def display_add_button(self, entity):
        rtype_roles = [(rtype, role) for rtype, role, _ in self.rtype_role_targets]
        links = viewlib.add_links_from_rtype_roles(entity, rtype_roles, self.url_params(entity))
        if links:
            import_url = clone.import_unit_url(self._cw, entity)
            links.append(tags.a(self._cw._('import_unit'), href=import_url))
        viewlib.display_add_button(self.w, links, self._cw.__('add'))

    def url_params(self, entity):
        return {'__redirectparams': 'tab=' + self.__regid__,
                'unit_type': 'unit_content'}


class ArchiveTransferRelatedTransfersTab(viewlib.SubObjectsTab):
    """Tab for previous transfers related to an archive transfer"""
    __regid__ = 'seda_at_related_transfers_tab'
    __select__ = is_instance('SEDAArchiveTransfer') & full_seda2_profile()

    rtype_role_targets = [('seda_related_transfer_reference', 'object', None)]

    _('creating SEDARelatedTransferReference (SEDARelatedTransferReference '
      'seda_related_transfer_reference SEDAArchiveTransfer %(linkto)s)')


class ArchiveTransferDiagnoseTab(viewlib.SubObjectsTab):
    """Tab to diagnose supported format of an archive transfer"""
    __regid__ = 'seda_at_diagnose_tab'
    __select__ = is_instance('SEDAArchiveTransfer')

    def entity_call(self, entity):
        self.w(u'<p class="bg-info">')
        formats = entity.formats_compat
        if 'simplified' in formats:
            formats.remove('simplified')
        self.w(self._cw._('Supported formats: {0}.').format(', '.join(sorted(formats))))
        self.w(u'</p>')
        doctor = entity.cw_adapt_to('ISEDACompatAnalyzer')
        data = [(tags.a(e.entity.dc_title(),
                        href=e.entity.absolute_url(tab=e.tab_id)),
                 ', '.join(e.impacted_formats),
                 self._cw._(e.message))
                for e in doctor.detect_problems()]
        if data:
            self.wview('pyvaltable', pyvalue=data,
                       headers=(self._cw._('Entity'),
                                self._cw._('Impacted formats'),
                                self._cw._('Message')))
        else:
            self.w(self._cw._('No problem detected, congratulation!'))


@monkeypatch(reledit.AutoClickAndEditFormView)
def _compute_formid_value(self, rschema, role, rvid, formid):
    """Overriden to give rtype/role information to the view"""
    related_rset = self.entity.related(rschema.type, role)
    if related_rset:
        value = self._cw.view(rvid, related_rset,
                              initargs={'rtype': rschema.type, 'role': role})  # path is here
    else:
        value = self._compute_default_value(rschema, role)
    if not self._should_edit_relation(rschema, role):
        return None, value
    return formid, value
