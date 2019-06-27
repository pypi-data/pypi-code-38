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
"""cubicweb-seda views configuration / overrides for simplified profiles."""

from logilab.common.registry import objectify_predicate

from cubicweb.predicates import is_instance
from cubicweb.web.views import uicfg, autoform

from ..xsd2yams import RULE_TYPES
from ..entities import simplified_profile
from . import CONTENT_ETYPE, widgets
# ensure those are registered first
from . import mgmt_rules, archivetransfer, dataobject, archiveunit  # noqa


# Add arbitrary score using `yes` to overtake e.g. afs for DataObjectReference defined in content
afs = uicfg.autoform_section
simplified_afs = afs.derive(__name__, simplified_profile())
pvs = uicfg.primaryview_section
simplified_pvs = pvs.derive(__name__, simplified_profile())

# appraisal/access rules have a single top level cardinality in simplified profile, as well as
# always a start date. This implies:
# 1. force one and only one eg AppraisalRuleRule,
# 2. force start date, but hide it,
# 3. hide eg AppraisalRuleRule's cardinality.

# 3. hide rule rule's cardinality
simplified_afs.tag_attribute(('SEDASeqAppraisalRuleRule', 'user_cardinality'),
                             'main', 'hidden')
simplified_afs.tag_attribute(('SEDASeqAccessRuleRule', 'user_cardinality'),
                             'main', 'hidden')


# 2. hide start date's cardinality - uicfg is not enough since we want it when edited in the context
# of archive unit's content but not of rule entity types

class StartDateAutomaticEntityForm(autoform.AutomaticEntityForm):
    __select__ = (is_instance('SEDAStartDate')
                  & simplified_profile())

    def editable_attributes(self, strict=False):
        """return a list of (relation schema, role) to edit for the entity"""
        attributes = list(super(StartDateAutomaticEntityForm, self).editable_attributes(strict))
        if self.linked_to.get(('seda_start_date', 'subject')):
            eid = self.linked_to[('seda_start_date', 'subject')][0]
            start_date_of = self._cw.entity_from_eid(eid).cw_etype
        elif self.edited_entity.has_eid():
            start_date_of = self.edited_entity.seda_start_date[0].cw_etype
        else:
            start_date_of = self.cw_extra_kwargs.get('petype')
        if start_date_of != CONTENT_ETYPE:
            attributes.remove(('user_cardinality', 'subject'))
        return attributes


class RuleAutomaticEntityForm(autoform.AutomaticEntityForm):
    __select__ = (is_instance('SEDAAppraisalRule', 'SEDAAccessRule')
                  & simplified_profile())

    def should_display_inline_creation_form(self, rschema, existing, card):
        # 1. force creation of one appraisal/access rule
        if not existing and rschema in ('seda_seq_appraisal_rule_rule',
                                        'seda_seq_access_rule_rule'):
            return True
        return super(RuleAutomaticEntityForm, self).should_display_inline_creation_form(
            rschema, existing, card)

    def should_display_add_new_relation_link(self, rschema, existing, card):
        # 1. don't allow creation of more than one appraisal/access rule
        if rschema in ('seda_seq_appraisal_rule_rule',
                       'seda_seq_access_rule_rule'):
            return False
        return super(RuleAutomaticEntityForm, self).should_display_add_new_relation_link(
            rschema, existing, card)


class SeqRuleRuleAutomaticEntityForm(autoform.AutomaticEntityForm):
    __select__ = (is_instance('SEDASeqAppraisalRuleRule', 'SEDASeqAccessRuleRule')
                  & simplified_profile())

    def should_display_inline_creation_form(self, rschema, existing, card):
        # 2. force start date
        if not existing and rschema == 'seda_start_date':
            return True
        return super(SeqRuleRuleAutomaticEntityForm, self).should_display_inline_creation_form(
            rschema, existing, card)


@objectify_predicate
def simplified_rule_rule(cls, req, rtype=None, pform=None, **kwargs):
    # check we're within a simplified profile
    if isinstance(pform, RuleAutomaticEntityForm) and rtype in ('seda_seq_appraisal_rule_rule',
                                                                'seda_seq_access_rule_rule'):
        return 1
    return 0


# 1. don't allow deletion of our appraisal/access rule

class RuleRuleInlineEntityEditionFormView(autoform.InlineEntityEditionFormView):
    __select__ = (autoform.InlineEntityEditionFormView.__select__
                  & simplified_rule_rule())
    removejs = None


class RuleRuleInlineEntityCreationFormView(autoform.InlineEntityCreationFormView):
    __select__ = (autoform.InlineEntityCreationFormView.__select__
                  & simplified_rule_rule())
    removejs = None


# 2. hide start date

@objectify_predicate
def simplified_start_date(cls, req, rtype=None, pform=None, **kwargs):
    # check we're within a simplified profile
    if isinstance(pform, SeqRuleRuleAutomaticEntityForm) and rtype == 'seda_start_date':
        return 1
    return 0


class StartDateInlineEntityEditionFormView(autoform.InlineEntityEditionFormView):
    __select__ = (autoform.InlineEntityEditionFormView.__select__
                  & simplified_start_date())
    removejs = None
    form_renderer_id = 'notitle'


class StartDateInlineEntityCreationFormView(autoform.InlineEntityCreationFormView):
    __select__ = (autoform.InlineEntityCreationFormView.__select__
                  & simplified_start_date())
    removejs = None
    form_renderer_id = 'notitle'


# simplified profil will have a single appraisal/access rule, hence we can remove all the
# inheritance control mecanism: override will simply mean redefining a rule at some point in the
# tree.
for rule_type in RULE_TYPES:
    etype = 'SEDA{0}Rule'.format(rule_type.capitalize())
    rtype = 'seda_alt_{0}_rule_prevent_inheritance'.format(rule_type)
    simplified_afs.tag_subject_of((etype, rtype, '*'), 'main', 'hidden')


# SEDAArchiveTransfer customization
for rtype, role in archivetransfer.at_ordered_fields:
    if not rtype.endswith('agency'):
        assert role == 'object'
        if rtype in ('seda_archival_agreement', 'seda_comment'):
            simplified_section = 'attributes'
        else:
            simplified_section = 'hidden'
        simplified_pvs.tag_object_of(('*', rtype, 'SEDAArchiveTransfer'), simplified_section)


# SEDAArchiveUnit
simplified_au_rtypes = set(
    rtype for rtype, role, targets in archiveunit.SimplifiedContentMainView.rtype_role_targets)
for rtype, role in archiveunit.content_ordered_fields:
    if role == 'object':
        section = 'inlined' if rtype in simplified_au_rtypes else 'hidden'
        simplified_afs.tag_object_of(('*', rtype, CONTENT_ETYPE), 'main', section)


# SEDABinaryDataObject/SEDAPhysicalDataObject customization
simplified_afs.tag_object_of(
    ('SEDADataObjectReference', 'seda_data_object_reference_id', '*'),
    'main', 'inlined')
simplified_afs.tag_object_of(
    ('SEDACustodialHistoryFile', 'seda_data_object_reference_id', '*'),
    'main', 'hidden')
simplified_pvs.tag_object_of(('*', 'seda_data_object_reference_id', '*'), 'hidden')
for rtype in ('seda_compressed', 'seda_data_object_version_from'):
    simplified_pvs.tag_object_of(('*', rtype, '*'), 'hidden')

simplified_pvs.tag_object_of(
    ('*', 'seda_date_created_by_application', 'SEDABinaryDataObject'),
    'attributes')


class DataObjectSimplifiedAutomaticEntityForm(widgets.SimplifiedAutomaticEntityForm):
    """On creation of a BinaryDataObject or PhysicalDataObject's in the context of a simplified
    profile, add a field to handle the creation of the relation to the archive unit specified in
    `req.form`.
    """

    # don't add match_form_params('referenced_by') since it's only specified for creation, not
    # edition
    __select__ = (widgets.SimplifiedAutomaticEntityForm.__select__
                  & is_instance('SEDABinaryDataObject', 'SEDAPhysicalDataObject')
                  & simplified_profile())

    def inlined_form_views(self):
        views = list(super(DataObjectSimplifiedAutomaticEntityForm, self).inlined_form_views())
        ref_forms = [v.form for v in views if v.rtype == 'seda_data_object_reference_id']
        if ref_forms:  # may be empty if user has no write access
            ref_form = ref_forms[0]
            if not ref_form.edited_entity.has_eid() and not ref_form.posting:
                ref_form.add_hidden(name='seda_data_object_reference', eidparam=True,
                                    role='subject',
                                    value=self._cw.form['referenced_by'])
        return views


# SEDADataObjectReference
simplified_afs.tag_subject_of(
    ('SEDADataObjectReference', 'seda_data_object_reference_id', '*'),
    'inlined', 'hidden')
simplified_afs.tag_attribute(
    ('SEDADataObjectReference', 'user_cardinality'),
    'inlined', 'hidden')


class DataObjectReferenceNoTitleEntityInlinedFormRenderer(widgets.NoTitleEntityInlinedFormRenderer):
    """Don't display any title nor remove link for DataObjectReference in the context of a
    simplified profile.
    """

    __select__ = (widgets.NoTitleEntityInlinedFormRenderer.__select__
                  & is_instance('SEDADataObjectReference')
                  & simplified_profile())
