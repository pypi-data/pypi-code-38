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
"""cubicweb-seda views for management rules"""

import json

from six import text_type

from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance
from cubicweb.web import INTERNAL_FIELD_VALUE
from cubicweb.web.views import reledit, uicfg

from ..entities import parent_and_container, rule_type_from_etype
from . import viewlib
from . import uicfg as sedauicfg  # noqa - ensure those rules are defined first


affk = uicfg.autoform_field_kwargs


def rule_ref_vocabulary(form, field):
    """Form vocabulary function, for fields referencing a management rules (i.e. a concept in a
    scheme defined on the archive transfer)
    """
    req = form._cw
    parent, container = parent_and_container(form.edited_entity)
    assert container is not None
    parent_etype = form.edited_entity.cw_etype
    if parent_etype == 'SEDARefNonRuleId':
        if parent is not None:
            parent_etype = parent.cw_etype
        else:
            parent_etype = json.loads(req.form['arg'][1])
    return _rule_ref_vocabulary(container, parent_etype)


def _rule_ref_vocabulary(container, parent_etype):
    req = container._cw
    rule_type = rule_type_from_etype(parent_etype)
    if container.cw_etype == 'SEDAArchiveTransfer':
        rql = ('Any C WHERE C in_scheme CS, AT eid %(at)s, '
               'CACLV seda_{0}_rule_code_list_version_from AT, '
               'CACLV seda_{0}_rule_code_list_version_to CS'.format(rule_type))
        rset = req.execute(rql, {'at': container.eid})
    else:
        # component archive unit, suppose we can use default vocabularies
        assert rule_type in ('access', 'appraisal')
        rql = ('Any C WHERE C in_scheme CS, CS scheme_relation_type RT, RT name %(rt)s,'
               'CS scheme_entity_type ET, ET name %(et)s')
        etype = 'SEDASeq{0}RuleRule'.format(rule_type.capitalize())
        rset = req.execute(rql, {'rt': 'seda_rule', 'et': etype})
    if rset:
        return ([(req._('<no value specified>'), INTERNAL_FIELD_VALUE)]
                + sorted([(concept.label(), text_type(concept.eid))
                          for concept in rset.entities()]))
    else:
        scheme_relation = 'seda_{0}_rule_code_list_version_from_object'.format(rule_type)
        scheme_relation = req._(scheme_relation)
        msg = req._('you must specify a scheme for {0} to select a value').format(scheme_relation)
        return [(msg, INTERNAL_FIELD_VALUE)]


affk.tag_subject_of(('*', 'seda_ref_non_rule_id_to', '*'),
                    {'choices': rule_ref_vocabulary,
                     'sort': False})
affk.tag_subject_of(('*', 'seda_rule', '*'),
                    {'choices': rule_ref_vocabulary,
                     'sort': False})


class RuleComplexLinkEntityAttributeView(viewlib.TextEntityAttributeView):
    __select__ = (viewlib.ComplexLinkEntityAttributeView.__select__
                  & is_instance('SEDAAccessRule', 'SEDADisseminationRule', 'SEDAReuseRule'))

    def entity_call(self, entity):
        _ = self._cw._
        for rule_seq in entity.rules:
            if rule_seq.seda_rule:
                rule = rule_seq.seda_rule[0].label()
                rule = _('rule: {0}').format(rule)
            else:
                rule = _('<no rule specified>')
            if rule_seq.reverse_seda_start_date:
                start_date = _('with {0} start date').format(
                    rule_seq.reverse_seda_start_date[0].user_cardinality)
            else:
                start_date = _('without start date')
            self.w(u'<div>{0} {1}, {2}</div>'.format(xml_escape(rule),
                                                     rule_seq.view('seda.xsdmeta'),
                                                     xml_escape(start_date),))
        if entity.inheritance_control:
            ctrl = entity.inheritance_control
            alternatives = []
            if ctrl.reverse_seda_prevent_inheritance:
                prevent = ctrl.reverse_seda_prevent_inheritance[0]
                # if prevent.prevent_inheritance is None:
                #     alternatives.append(_('XXX prevent to be specified'))
                if prevent.prevent_inheritance:
                    alternatives.append(xml_escape(_('prevent all rules')))
                elif prevent.prevent_inheritance is False:
                    alternatives.append(xml_escape(_("don't prevent inheritance")))
                else:  # unspecified
                    alternatives.append(xml_escape(_("prevent inheritance or not to be specified")))
            non_rules = []
            for non_rule in ctrl.reverse_seda_ref_non_rule_id_from:
                if non_rule.seda_ref_non_rule_id_to:
                    rule_name = non_rule.seda_ref_non_rule_id_to[0].label()
                    non_rules.append(xml_escape(_('prevent rule {0}').format(rule_name)))
                else:
                    non_rules.append(xml_escape(_('<no rule to prevent specified>'))
                                     + ' ' + non_rule.view('seda.xsdmeta'))
            if non_rules:
                alternatives.append(u', '.join(non_rules))
            self.w((u'<b>{0}</b>'.format(self._cw._(' ALT_I18N '))).join(alternatives))


class FinalActionRuleComplexLinkEntityAttributeView(RuleComplexLinkEntityAttributeView):
    __select__ = (viewlib.ComplexLinkEntityAttributeView.__select__
                  & is_instance('SEDAStorageRule', 'SEDAAppraisalRule'))

    def entity_call(self, entity):
        _ = self._cw._
        if entity.seda_final_action:
            action = entity.seda_final_action[0].label()
            final_action = _('final action: {0}').format(action)
        else:
            final_action = _('<no final action specified>')
        self.w(u'<div>{0} {1}</div>'.format(xml_escape(final_action), entity.view('seda.xsdmeta')))
        super(FinalActionRuleComplexLinkEntityAttributeView, self).entity_call(entity)


class ClassificationRuleComplexLinkEntityAttributeView(RuleComplexLinkEntityAttributeView):
    __select__ = (viewlib.ComplexLinkEntityAttributeView.__select__
                  & is_instance('SEDAClassificationRule'))

    def entity_call(self, entity):
        _ = self._cw._
        if entity.seda_classification_level:
            classification_level = entity.seda_classification_level[0].label()
            classification_level = _('classification level: {0}').format(classification_level)
        else:
            classification_level = _('<no classification level specified>')
        self.w(u'<div>{0} {1}</div>'.format(xml_escape(classification_level),
                                            entity.view('seda.xsdmeta')))
        if entity.classification_owner:
            classification_owner = entity.classification_owner
            classification_owner = _('classification owner: {0}').format(classification_owner)
        else:
            classification_owner = _('<no classification owner specified>')
        self.w(u'<div>{0}</div>'.format(xml_escape(classification_owner)))
        if entity.reverse_seda_classification_reassessing_date:
            reassessing_date = _('with {0} reassessing date').format(
                entity.reverse_seda_classification_reassessing_date[0].user_cardinality)
        else:
            reassessing_date = _('without reassessing date')
        self.w(u'<div>{0}</div>'.format(xml_escape(reassessing_date)))

        if entity.reverse_seda_need_reassessing_authorization:
            reassessing_authorization = entity.reverse_seda_need_reassessing_authorization[0]
            # if reassessing_authorization.need_reassessing_authorization is None:
            #     XXX
            if reassessing_authorization.need_reassessing_authorization:
                need_human = _('need human intervention')
            else:
                need_human = _('without human intervention')
            self.w(u'<div>{0}</div>'.format(xml_escape(need_human)))
        super(ClassificationRuleComplexLinkEntityAttributeView, self).entity_call(entity)


class MgmtRuleAutoClickAndEditFormView(reledit.AutoClickAndEditFormView):
    __select__ = (reledit.AutoClickAndEditFormView.__select__
                  & is_instance('SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'))

    def _compute_default_value(self, rschema, role):
        if rschema.type.endswith('_rule'):
            rule_type = rschema.type[len('seda_'):-len('_rule')]
            rule = self.entity.inherited_rule(rule_type)
            if rule:
                return rule.view('seda.reledit.text') + u'<p><mark>{}</mark></p>'.format(
                    self._cw._(u'inherited value'))
        return super(MgmtRuleAutoClickAndEditFormView, self)._compute_default_value(
            rschema, role)
