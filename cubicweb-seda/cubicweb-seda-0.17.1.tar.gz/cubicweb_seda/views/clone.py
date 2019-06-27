# copyright 2015-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""Views related to cloning of SEDA compound tree."""

from cubicweb import uilib, _
from cubicweb.predicates import is_instance, match_form_params, score_entity
from cubicweb.web import Redirect, controller
from cubicweb.web.views import uicfg

from cubicweb_compound.entities import copy_entity
from cubicweb_compound import views as compound
from cubes.relationwidget import views as rwdg

from .widgets import configure_relation_widget


afs = uicfg.autoform_section
pvs = uicfg.primaryview_section

# clone relation
afs.tag_subject_of(('*', 'clone_of', '*'), 'main', 'hidden')
afs.tag_object_of(('*', 'clone_of', '*'), 'main', 'hidden')
pvs.tag_subject_of(('*', 'clone_of', '*'), 'relations')
pvs.tag_object_of(('*', 'clone_of', '*'), 'relations')


def import_unit_url(req, entity):
    """Return an URL to display the relation widget to search for an archive unit to import.
    """
    req.add_js('cubes.editionext.js')
    if entity.cw_etype == 'SEDAArchiveTransfer':
        root = entity
    else:
        root = entity.cw_adapt_to('IContained').container or entity
    search_url = req.build_url('ajax', fname='view', vid='search_related_entities',
                               __modal='1', multiple='1',
                               relation='clone_of:SEDAArchiveUnit:subject',
                               etype=root.cw_etype, target=root.eid)
    title = req._('Search entity to import')
    return configure_relation_widget(req, _import_div_id(entity), search_url, title,
                                     True, uilib.js.editext.buildSedaImportValidate(entity.eid))


class DoImportView(controller.Controller):
    __regid__ = 'seda.doimport'
    __select__ = match_form_params('eid', 'cloned')

    def publish(self, rset=None):
        ui_parent = self._cw.entity_from_eid(int(self._cw.form['eid']))
        if ui_parent.cw_etype == 'SEDAArchiveTransfer':
            parent = ui_parent
        else:
            parent = ui_parent.first_level_choice.content_sequence
        clones = []
        for cloned_eid in self._cw.form['cloned'].split(','):
            original = self._cw.entity_from_eid(int(cloned_eid))
            clones.append(copy_entity(original, seda_archive_unit=parent,
                                      clone_of=original))
        basemsg = (_('{0} has been imported') if len(clones) == 1 else
                   _('{0} have been imported'))
        msg = self._cw._(basemsg).format(u', '.join(clone.dc_title() for clone in clones))
        raise Redirect(ui_parent.absolute_url(__message=msg))


def _import_div_id(entity):
    """Return identifier of div place holder for the relation widget.

    You've to put this on entity's primary view for import action to work.
    """
    return 'importDiv%s' % entity.eid


class SearchForTargetToImportView(rwdg.SearchForRelatedEntitiesView):
    __select__ = (rwdg.SearchForRelatedEntitiesView.__select__
                  & rwdg.edited_relation('clone_of')
                  & match_form_params('target'))
    title = None
    has_creation_form = False

    def linkable_rset(self):
        """Return rset of entities to be displayed as possible values for the edited relation."""
        tetype = self._cw.form['relation'].split(':')[1]
        target = int(self._cw.form['target'])
        rql = ('Any X,MD ORDERBY MD DESC WHERE X is %s, X modification_date MD, '
               'NOT X seda_archive_unit P, NOT X eid %%(target)s') % tetype
        return self._cw.execute(rql, {'target': target})


class SEDAArchiveTransferCloneAction(compound.CloneAction):
    __select__ = compound.CloneAction.__select__ & is_instance('SEDAArchiveTransfer')


class SEDAArchiveUnitCloneAction(compound.CloneAction):
    __select__ = (compound.CloneAction.__select__ & is_instance('SEDAArchiveUnit')
                  & score_entity(lambda x: x.cw_adapt_to('IContained').container is None))

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid='copy', unit_type='unit_content',
                                   **compound.linkto_clone_url_params(entity))
