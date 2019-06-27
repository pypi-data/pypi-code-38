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

from ..xsd2yams import RULE_TYPES
from . import generated, itree


def _extract_title(annotation):
    """Return the first line in the annotation to use as a title"""
    annotation = annotation.strip()
    assert annotation
    return annotation.splitlines()[0]


def _climb_rule_holders(transfer_or_archive_unit):
    """Starting from a transfer or archive unit entity, yield entity that may be linked to
    management rule until the root (transfer) is reached.
    """
    while transfer_or_archive_unit is not None:
        if transfer_or_archive_unit.cw_etype == 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement':
            yield transfer_or_archive_unit
            transfer_or_archive_unit = itree.parent_archive_unit(transfer_or_archive_unit)
        elif transfer_or_archive_unit.cw_etype == 'SEDAArchiveTransfer':
            yield transfer_or_archive_unit
        else:
            yield transfer_or_archive_unit.first_level_choice.content_sequence
        transfer_or_archive_unit = transfer_or_archive_unit.cw_adapt_to('ITreeBase').parent()


def _inherited_rule(self, rule_type):
    """Return the rule entity of the given type, defined on this unit or in its nearest parent
    possible defining it, or None if no matching rule has been found.
    """
    assert rule_type in RULE_TYPES
    rtype = 'reverse_seda_{}_rule'.format(rule_type)
    for rule_holder in _climb_rule_holders(self):
        if getattr(rule_holder, rtype):
            return getattr(rule_holder, rtype)[0]
    return None


class SEDAArchiveTransfer(generated.SEDAArchiveTransfer):

    def dc_title(self):
        return self.title

    @property
    def formats_compat(self):
        if self.compat_list is None:
            return set()
        return set(self.compat_list.split(', '))

    @property
    def archival_agreement(self):
        if self.reverse_seda_archival_agreement:
            return self.reverse_seda_archival_agreement[0]
        return None

    @property
    def comments(self):
        return self.reverse_seda_comment

    @property
    def archive_units(self):
        return self.reverse_seda_archive_unit

    @property
    def physical_data_objects(self):
        return self.reverse_seda_physical_data_object

    @property
    def binary_data_objects(self):
        return self.reverse_seda_binary_data_object

    inherited_rule = _inherited_rule


class SEDAArchiveUnit(generated.SEDAArchiveUnit):

    def dc_title(self):
        return _extract_title(self.user_annotation)

    @property
    def is_archive_unit_ref(self):
        """Return true if this is a 'reference' archive unit, else false for 'description' archive
        unit.
        """
        return not bool(self.first_level_choice.content_sequence)

    @property
    def first_level_choice(self):
        """Return the choice element of an archive unit (SEDAAltArchiveUnitArchiveUnitRefId),
        holding either a reference or descriptive content
        """
        return self.related('seda_alt_archive_unit_archive_unit_ref_id', 'subject').one()

    inherited_rule = _inherited_rule


class SEDABinaryDataObject(generated.SEDABinaryDataObject):

    def dc_title(self):
        return _extract_title(self.user_annotation)

    @property
    def format_id(self):
        return self.reverse_seda_format_id_from[0] if self.reverse_seda_format_id_from else None

    @property
    def encoding(self):
        return self.reverse_seda_encoding_from[0] if self.reverse_seda_encoding_from else None

    @property
    def mime_type(self):
        return self.reverse_seda_mime_type_from[0] if self.reverse_seda_mime_type_from else None

    @property
    def date_created_by_application(self):
        if self.reverse_seda_date_created_by_application:
            return self.reverse_seda_date_created_by_application[0]
        return None

    @property
    def referenced_by(self):
        """Return an iterator on archive unit's content sequences referencing this data-object."""
        for ref in self.reverse_seda_data_object_reference_id:
            for seq in ref.seda_data_object_reference:
                yield seq


class SEDAPhysicalDataObject(generated.SEDAPhysicalDataObject):

    def dc_title(self):
        return _extract_title(self.user_annotation)


class SEDAAltArchiveUnitArchiveUnitRefId(generated.SEDAAltArchiveUnitArchiveUnitRefId):

    @property
    def reference(self):
        """Return the reference element for an archive unit which has no content"""
        rset = self.related('seda_archive_unit_ref_id_from', 'object')
        if rset:
            return rset.one()
        return None

    @property
    def content_sequence(self):
        """Return the sequence element holding content for an archive unit which is not a reference
        """
        rset = self.related('seda_seq_alt_archive_unit_archive_unit_ref_id_management', 'subject')
        if rset:
            return rset.one()
        return None


class SEDASeqAltArchiveUnitArchiveUnitRefIdManagement(
        generated.SEDASeqAltArchiveUnitArchiveUnitRefIdManagement):

    @property
    def title(self):
        return self.reverse_seda_title[0]

    @property
    def keywords(self):
        return self.reverse_seda_keyword

    @property
    def custodial_history_items(self):
        return self.reverse_seda_custodial_history_item

    @property
    def type(self):
        return self.reverse_seda_type_from[0] if self.reverse_seda_type_from else None

    @property
    def language(self):
        return self.reverse_seda_language_from[0] if self.reverse_seda_language_from else None

    @property
    def description_level_concept(self):
        return self.seda_description_level[0] if self.seda_description_level else None

    @property
    def description(self):
        return self.reverse_seda_description[0] if self.reverse_seda_description else None

    @property
    def start_date(self):
        return self.reverse_seda_start_date[0] if self.reverse_seda_start_date else None

    @property
    def end_date(self):
        return self.reverse_seda_end_date[0] if self.reverse_seda_end_date else None

    @property
    def system_id(self):
        return self.reverse_seda_system_id[0] if self.reverse_seda_system_id else None

    @property
    def transferring_agency_archive_unit_identifier(self):
        if self.reverse_seda_transferring_agency_archive_unit_identifier:
            return self.reverse_seda_transferring_agency_archive_unit_identifier[0]
        return None

    @property
    def originating_agency(self):
        if self.reverse_seda_originating_agency_from:
            return self.reverse_seda_originating_agency_from[0]
        return None

    inherited_rule = _inherited_rule


class SEDAKeyword(generated.SEDAKeyword):

    @property
    def reference(self):
        return (self.reverse_seda_keyword_reference_from[0]
                if self.reverse_seda_keyword_reference_from else None)

    @property
    def type(self):
        return (self.reverse_seda_keyword_type_from[0]
                if self.reverse_seda_keyword_type_from else None)


class SEDAKeywordReference(generated.SEDAKeywordReference):

    @property
    def scheme(self):
        return (self.seda_keyword_reference_to_scheme[0] if self.seda_keyword_reference_to_scheme
                else None)

    @property
    def concept(self):
        return self.seda_keyword_reference_to[0] if self.seda_keyword_reference_to else None


class SEDAKeywordType(generated.SEDAKeywordType):

    @property
    def concept(self):
        return self.seda_keyword_type_to[0] if self.seda_keyword_type_to else None


class RuleMixIn(object):

    @property
    def _rule_type(self):
        return self.cw_etype[4:-4].lower()

    @property
    def rules(self):
        return getattr(self, 'seda_seq_{0}_rule_rule'.format(self._rule_type))

    @property
    def inheritance_control(self):
        alt = getattr(self, 'seda_alt_{0}_rule_prevent_inheritance'.format(self._rule_type))
        return alt[0] if alt else None


class SEDAAccessRule(RuleMixIn, generated.SEDAAccessRule):
    pass


class SEDAAppraisalRule(RuleMixIn, generated.SEDAAppraisalRule):

    @property
    def final_action_concept(self):
        if self.seda_final_action:
            return self.seda_final_action[0]
        return None


class SEDAClassificationRule(RuleMixIn, generated.SEDAClassificationRule):
    pass


class SEDADisseminationRule(RuleMixIn, generated.SEDADisseminationRule):
    pass


class SEDAReuseRule(RuleMixIn, generated.SEDAReuseRule):
    pass


class SEDAStorageRule(RuleMixIn, generated.SEDAStorageRule):

    @property
    def final_action_concept(self):
        if self.seda_final_action:
            return self.seda_final_action[0]
        return None


class RuleRuleMixIn(object):

    @property
    def start_date(self):
        return self.reverse_seda_start_date[0] if self.reverse_seda_start_date else None

    @property
    def rule_concept(self):
        return self.seda_rule[0] if self.seda_rule else None


class SEDASeqAccessRuleRule(RuleRuleMixIn, generated.SEDASeqAccessRuleRule):
    pass


class SEDASeqAppraisalRuleRule(RuleRuleMixIn, generated.SEDASeqAppraisalRuleRule):
    pass


class SEDASeqClassificationRuleRule(RuleRuleMixIn, generated.SEDASeqClassificationRuleRule):
    pass


class SEDASeqDisseminationRuleRule(RuleRuleMixIn, generated.SEDASeqDisseminationRuleRule):
    pass


class SEDASeqReuseRuleRule(RuleRuleMixIn, generated.SEDASeqReuseRuleRule):
    pass


class SEDASeqStorageRuleRule(RuleRuleMixIn, generated.SEDASeqStorageRuleRule):
    pass


class SEDAFormatId(generated.SEDAFormatId):

    @property
    def concepts(self):
        return self.seda_format_id_to


class SEDAEncoding(generated.SEDAEncoding):

    @property
    def concept(self):
        return self.seda_encoding_to[0] if self.seda_encoding_to else None


class SEDAMimeType(generated.SEDAMimeType):

    @property
    def concepts(self):
        return self.seda_mime_type_to


class SEDAType(generated.SEDAType):

    @property
    def concept(self):
        return self.seda_type_to[0] if self.seda_type_to else None


class SEDALanguage(generated.SEDALanguage):

    @property
    def concept(self):
        return self.seda_language_to[0] if self.seda_language_to else None


class SEDAOriginatingAgency(generated.SEDAOriginatingAgency):

    @property
    def agency(self):
        return self.seda_originating_agency_to[0] if self.seda_originating_agency_to else None


class SEDACustodialHistoryItem(generated.SEDACustodialHistoryItem):

    @property
    def when(self):
        return self.reverse_seda_when[0] if self.reverse_seda_when else None
