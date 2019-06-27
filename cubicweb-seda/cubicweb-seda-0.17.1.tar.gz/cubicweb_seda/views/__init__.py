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

from yams import BASE_TYPES

from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape

from cubicweb import tags, neg_role
from cubicweb.utils import UStringIO
from cubicweb.web import formfields as ff
# XXX alias to avoid weird side effect: uicfg will become our uicfg submodule
from cubicweb.web.views import primary, uicfg as cwuicfg

from ..xsd import XSDM_MAPPING
from ..xsd2uicfg import FIRST_LEVEL_ETYPES
from .uicfg import ETYPE_ATTR_DOC
from .widgets import SEDAMetaField


CONTENT_ETYPE = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'


pvs = cwuicfg.primaryview_section
afs = cwuicfg.autoform_section
aff = cwuicfg.autoform_field
affk = cwuicfg.autoform_field_kwargs
rec = cwuicfg.reledit_ctrl

pvs.tag_subject_of(('*', 'container', '*'), 'hidden')
pvs.tag_object_of(('*', 'container', '*'), 'hidden')
afs.tag_subject_of(('*', 'container', '*'), 'main', 'hidden')
afs.tag_object_of(('*', 'container', '*'), 'main', 'hidden')

pvs.tag_subject_of(('*', 'scheme_relation_type', '*'), 'hidden')
afs.tag_subject_of(('*', 'scheme_relation_type', '*'), 'main', 'hidden')
pvs.tag_subject_of(('*', 'scheme_entity_type', '*'), 'hidden')
afs.tag_subject_of(('*', 'scheme_entity_type', '*'), 'main', 'hidden')

pvs.tag_object_of(('*', 'seda_keyword_reference_to_scheme', '*'), 'hidden')
afs.tag_object_of(('*', 'seda_keyword_reference_to_scheme', '*'), 'main', 'hidden')

afs.tag_subject_of(('*', 'code_keyword_type', '*'), 'main', 'attributes')
pvs.tag_subject_of(('*', 'code_keyword_type', '*'), 'attributes')
afs.tag_object_of(('*', 'code_keyword_type', '*'), 'main', 'hidden')
pvs.tag_object_of(('*', 'code_keyword_type', '*'), 'hidden')

aff.tag_attribute(('*', 'user_cardinality'), SEDAMetaField)
afs.tag_attribute(('*', 'user_annotation'), 'main', 'hidden')
for etype in FIRST_LEVEL_ETYPES:
    aff.tag_attribute((etype, 'user_cardinality'), ff.StringField)
    afs.tag_attribute((etype, 'user_annotation'), 'main', 'attributes')

pvs.tag_attribute(('*', 'ordering'), 'hidden')
afs.tag_attribute(('*', 'ordering'), 'main', 'hidden')


def rtags_from_xsd_element(etype, element_name):
    """Return primary view section and display control rtags, generated from information in the XSD
    for the given element name.
    """
    rtype_role_targets = ((rtype, role, path[-1][-2])
                          for rtype, role, path in XSDM_MAPPING.iter_rtype_role(element_name))
    return rtags_from_rtype_role_targets(etype, rtype_role_targets)


def rtags_from_rtype_role_targets(etype, rtype_role_targets):
    """Return primary view section and display control rtags from a list of (`rtype`, `role`,
    `target entity type`).
    """
    ordered = []
    rsection = cwuicfg.PrimaryViewSectionRelationTags(__module__=__name__)
    for rtype, role, target in rtype_role_targets:
        if role == 'subject':
            if target in BASE_TYPES:
                # attribute handled by the main tab (e.g. filename), skip it
                continue
            # mandatory elements
            relation = (etype, rtype, '*', role)
            rec.tag_subject_of(('*', rtype, '*'),
                               {'rvid': 'seda.reledit.simplelink'})
        else:
            relation = ('*', rtype, etype, role)
            if target in BASE_TYPES or not rtype.endswith('_from'):
                vid = 'seda.reledit.text'
            else:
                vid = 'seda.reledit.complexlink'
            rec.tag_object_of(('*', rtype, '*'),
                              {'rvid': vid,
                               'novalue_label': ' '})
        rsection.tag_relation(relation, 'attributes')
        ordered.append((rtype, role))
    display_ctrl = cwuicfg.DisplayCtrlRelationTags(__module__=__name__)
    display_ctrl.set_fields_order(etype, ordered)
    return rsection, display_ctrl


def add_subobject_link(entity, rtype, role, extraurlparams, msg=None, klass=None):
    """Return a HTML link to add a subobject linked to `entity` through `rtype` relation where
    entity has `role`.

    If the user doesn't have the permission to add the relation or subobject, return an empty
    string.
    """
    req = entity._cw
    rschema = req.vreg.schema[rtype]
    targets = rschema.targets(role=role)
    assert len(targets) == 1, 'expecting a single {0} for relation {1}'.format(role, rschema)
    target_etype = targets[0].type
    if not has_rel_perm('add', entity, rtype, role, target_etype=target_etype):
        return u''
    linkto = '{rtype}:{eid}:{role}'.format(rtype=rtype, eid=entity.eid, role=neg_role(role))
    urlparams = {'__linkto': linkto,
                 '__redirectpath': entity.rest_path()}
    urlparams.update(extraurlparams)
    if msg is None:
        msg = req.__(rtype if role == 'subject' else rtype + '_object')
    return add_etype_link(req, target_etype, urlparams, msg=msg, klass=klass)


def add_etype_link(req, etype, urlparams, msg=u'', klass=None):
    """Return an HTML link to add an entity of type `etype`, or an empty string if the user doesn't
    have the permission.
    """
    vreg = req.vreg
    eschema = vreg.schema.eschema(etype)
    if eschema.has_perm(req, 'add'):
        if klass is None:
            klass = 'icon-plus-circled pull-right'
        url = vreg['etypes'].etype_class(etype).cw_create_url(req, **urlparams)
        return tags.a(msg, href=url, klass=klass)
    return u''


def has_rel_perm(action, entity, rtype, role, target_etype=None, target_entity=None):
    """Return True if the user has the permission for `action` on the relation `rtype` where
    `entity` is `role`. Either target entity type or target entity could also be specified.
    """
    if role == 'subject':
        kwargs = {'fromeid': entity.eid}
        if target_entity is not None:
            kwargs['toeid'] = target_entity.eid
    else:
        kwargs = {'toeid': entity.eid}
        if target_entity is not None:
            kwargs['fromeid'] = target_entity.eid
    if target_entity is not None:
        assert not target_etype
        target_etype = target_entity.cw_etype
    rdef = entity.e_schema.rdef(rtype, role, target_etype)
    return rdef.has_perm(entity._cw, action, **kwargs)


def dropdown_button(text, links):
    """Return an HTML button with `text` and dropdown content from `links`.
    """
    data = UStringIO()
    w = data.write
    w(u'<div class="btn-group pull-right clearfix">')
    w(tags.button(
        u' '.join([text, tags.span(klass='caret')]),
        escapecontent=False,
        klass='btn btn-success dropdown-toggle',
        **{'data-toggle': 'dropdown', 'aria-expanded': 'false'}))
    w(u'<ul class="dropdown-menu" role="menu">')
    for link in links:
        w(u'<li>{0}</li>'.format(link))
    w(u'</ul>')
    w(u'</div>')
    return data.getvalue()


orig_rel_label = primary.PrimaryView._rel_label


@monkeypatch(primary.PrimaryView)
def _rel_label(self, entity, rschema, role, dispctrl):
    label = orig_rel_label(self, entity, rschema, role, dispctrl)
    try:
        element_name, desc = ETYPE_ATTR_DOC[(entity.cw_etype, rschema.type, role)]
    except KeyError:
        return label
    description = xml_escape(desc[0]) if desc else u''
    title = xml_escape(element_name)
    self._cw.add_onload("$('.popOverLabel').popover();")
    return (u'<div class="popOverLabel" '
            'data-toggle="popover" data-placement="top" '
            'title="{}" data-content="{}">{}</div>'.format(
                title, description, label))
