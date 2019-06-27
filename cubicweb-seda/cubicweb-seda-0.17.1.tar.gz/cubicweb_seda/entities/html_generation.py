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
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-seda adapter classes for generation of a profile generation as HTML"""

from six import string_types

from cubicweb import _

from .profile_generation import SEDA2ExportAdapter, content_types
from .profile_generation import xselement_scheme_attribute, _concept_value


def element_uml_cardinality(occ, card_entity):
    """Return UML like cardinality for the given pyxst Occurence. Cardinality may be
    overriden by the data model's user_cardinality value.
    """
    cardinality = getattr(card_entity, 'user_cardinality', None)
    if cardinality is None:
        minimum = occ.minimum
        maximum = occ.maximum
        if minimum == maximum == 1:
            return '1'
        elif maximum != 1:
            maximum = 'n'
        return '%s..%s' % (minimum, maximum)
    else:
        return cardinality


def attribute_cardinality_as_string(occ, card_entity):
    """Return 'optional' or 'mandatory' for the given pyxst attribute's Occurence. Cardinality may be
    overriden by the data model's user_cardinality value.
    """
    cardinality = getattr(card_entity, 'user_cardinality', None)
    if cardinality is None:
        minimum = occ.minimum
    else:
        # XXX assert cardinality in ('0..1', '1'), cardinality
        if cardinality[0] == '0':
            minimum = 0
        else:
            minimum = 1
    return _('mandatory') if minimum else _('optional')


class SEDA2HTMLExport(SEDA2ExportAdapter):
    """Adapter to build a HTML representation of a SEDA profile"""
    __regid__ = 'SEDA-2.0.html'
    namespaces = {}
    css = '''
    h1{
      font-variant: small-caps;
      color : #FF9800;
      text-align: center;
      padding : 10px;
      font-weight: lighter;
      border-bottom : 2px solid  #E0E0E0;
    }

    a{
      color : #EF6C00;
    }
    body {
      font-family: helvetica, Arial;
      background-color: #FAFAFA;
      color : #666;
    }
    body >div{
      background-color: #FFF;
      padding-bottom : 20px;
      margin-top : 20px;
      box-shadow: 2px 2px 2px 0px #E0E0E0;
    }

    body >div >h3{
      font-variant: normal;
      font-weight: lighter;
      font-size:15px;
      padding : 10px;
      background-color: #EF6C00;
      color : white;
      font-variant: small-caps;
      cursor : pointer;
    }

    body >div >h3 span.card{
      font-size: 70%;
      color : #E0E0E0;
      margin-left : 5px;
    }

    body>div>div, .sequence >div{
      margin-top : 20px
    }

    body>div>div div{
      padding-left : 20px;
      margin-left: 15px;
      border-left : 1px dashed #EF6C00;
    }

    body>div>div h3{
      margin-bottom : 10px;
    }

    h3 span.card {
      font-size: 70%;
      color : #EF6C00;
      margin-left : 5px;
    }

    span {
      font-size: 90%;
      color: #555;
    }
    span.label {
      font-weight: bold;
      padding-left: 1px;
    }

    div.attribute {
      color: #888;
      width: 40em;
      font-size: small;
      padding : 10px;
    }

    div.attribute span.label {
      float: left;
      color : #EF6C00;
      font-weight: lighter;
      margin-right : 20px;
    }

    .sequence >h3:first-child{
      color :  #EF6C00;
    }
    '''

    def dump_etree(self):
        """Return an XSD etree for the adapted SEDA profile."""
        root = self.element('html')
        head = self.element('head', root)
        self.element('title', head, text=self.entity.dc_title())
        self.element('meta', head, {'http-equiv': 'content-type',
                                    'content': 'text/html; charset=UTF-8'})
        self.element('style', head, text=self.css)
        body = self.element('body', root)
        self._dump(body)
        return root

    def init_transfer_element(self, xselement, root, entity):
        self.element('h1', root, text=entity.title)
        if entity.user_annotation:
            self.element('div', root, text=entity.user_annotation,
                         attributes={'class': 'description'})
        return root

    def jumped_element(self, profile_element):
        return profile_element[-1]

    def element_alternative(self, occ, profile_element, target_value, to_process, card_entity):
        div = self.element('div', profile_element,
                           attributes={'class': 'choice'})
        self.title(div, self._cw._('Alternative'), occ, card_entity)
        to_process[occ.target].append((target_value, div))

    def element_sequence(self, occ, profile_element, target_value, to_process, card_entity):
        div = self.element('div', profile_element,
                           attributes={'class': 'sequence'})
        self.title(div, self._cw._('Sequence'), occ, card_entity)
        to_process[occ.target].append((target_value, div))

    def element_xmlattribute(self, occ, profile_element, target_value, to_process, card_entity):
        div = self.element('div', profile_element,
                           attributes={'class': 'attribute'})
        card = self._cw._(attribute_cardinality_as_string(occ, card_entity))
        self.element('span', div, text=occ.target.local_name, attributes={'class': 'label'})
        self.element('span', div, text=card, attributes={'class': 'card'})
        fixed_value = self.serialize(target_value)
        if isinstance(fixed_value, string_types):
            self.element('span', div, text=fixed_value, attributes={'class': 'value'})
        else:
            span = self.element('span', div, attributes={'class': 'value'})
            if fixed_value is not None:
                span.append(fixed_value)

    def element_xmlelement(self, occ, profile_element, target_value, to_process, card_entity):
        xselement = occ.target
        if isinstance(occ, dict):  # fake occurence introduced for some elements'content
            return
        attrs = {}
        if hasattr(target_value, 'id'):
            attrs['id'] = target_value.id
        div = self.element('div', profile_element, attrs)
        self.title(div, xselement.local_name, occ, card_entity)
        annotation = getattr(card_entity, 'user_annotation', None)
        if annotation:
            self.element('div', div, text=annotation,
                         attributes={'class': 'description'})
        xstypes = content_types(xselement.textual_content_type)
        self.fill_element(xselement, div, target_value, card_entity, xstypes)
        if getattr(target_value, 'eid', None):  # value is an entity
            to_process[xselement].append((target_value, div))

    def fill_element(self, xselement, div, target_value, card_entity, xstypes=None):
        if xselement.local_name == 'KeywordType':
            list_div = self.element('div', div)
            self.element('span', list_div, text=u'listVersionID',
                         attributes={'class': 'label'})
            if target_value:
                list_value = target_value.scheme.description or target_value.scheme.dc_title()
            else:
                list_value = 'edition 2009'
            self.element('span', list_div, text=list_value, attributes={'class': 'value'})

        elif (xselement.local_name == 'KeywordReference' and card_entity.scheme):
            self.concept_scheme_attribute(xselement, div, card_entity.scheme)

        elif getattr(target_value, 'cw_etype', None) == 'Concept':
            self.concept_scheme_attribute(xselement, div, target_value.scheme)
        if xstypes:
            ct_div = self.element('div', div)
            self.element('span', ct_div, text=self._cw._('XSD content type'),
                         attributes={'class': 'label'})
            xstypes = self._cw._(' ALT_I18N ').join(u'xsd:' + xstype for xstype in xstypes)
            self.element('span', ct_div, text=xstypes, attributes={'class': 'value'})
        if target_value is None:
            values = ()
        elif not isinstance(target_value, (tuple, list)):
            values = [target_value]
        else:
            values = target_value
        value_div = None
        for value in values:
            fixed_value = self.serialize(value)
            if fixed_value is None:
                continue
            if value_div is None:
                value_div = self.element('div', div)
                self.element('span', value_div, text=self._cw._('fixed value'),
                             attributes={'class': 'label'})
            if isinstance(fixed_value, string_types):
                self.element('span', value_div, text=fixed_value, attributes={'class': 'value'})
            else:
                span = self.element('span', value_div, attributes={'class': 'value'})
                span.append(fixed_value)

    def concept_scheme_attribute(self, xselement, div, scheme):
        try:
            xsattr = xselement_scheme_attribute(xselement)
        except KeyError:
            return  # no attribute to define scheme (e.g. for language specification)
        div = self.element('div', div)
        self.element('span', div, text=xsattr, attributes={'class': 'label'})
        self.element('a', self.element('span', div, attributes={'class': 'value'}),
                     {'href': scheme.absolute_url()}, text=scheme.dc_title())

    def title(self, div, label, occ, card_entity):
        h3 = self.element('h3', div, text=label)
        self.element('span', h3, attributes={'class': 'card'},
                     text=u'[{0}]'.format(self._cw._(element_uml_cardinality(occ, card_entity))))

    def serialize(self, value):
        """Return value as None or some text or etree node to be inserted in the HTML DOM."""
        if value is None:
            return None
        if hasattr(value, 'eid'):
            if value.cw_etype in ('AuthorityRecord', 'ConceptScheme'):
                href, label = value.absolute_url(), value.dc_title()
            elif value.cw_etype == 'Concept':
                href = value.absolute_url()
                label = _concept_value(value, 'seda-2')
                if value.label() != label:
                    label = u'{0} ({1})'.format(label, value.label())
            elif hasattr(value, 'id'):
                # value is something in the profile which has a id (e.g. archive unit, data object)
                href, label = u'#{0}'.format(value.id), value.id
            else:
                return None  # intermediary entity
            return self.element('a', self.element('span', attributes={'class': 'value'}),
                                attributes={'href': href}, text=label)
        else:
            if isinstance(value, bool):
                value = 'true' if value else 'false'
            assert isinstance(value, string_types), repr(value)
            return value
