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
"""Dynamic patches to avoid hard dependancies on cubicweb releases"""

from logilab.common.decorators import monkeypatch

from cubicweb.web.views import autoform


# monkey patch autoform to add an hidden field container the parent container eid that may be used
# in parent_and_container (see entities/__init__.py)

orig_autoform_init = autoform.AutomaticEntityForm.__init__


@monkeypatch(autoform.AutomaticEntityForm)
def __init__(self, *args, **kwargs):
    orig_autoform_init(self, *args, **kwargs)
    if 'peid' not in kwargs and self.edited_entity.cw_etype.startswith('SEDA'):  # main form
        parent = None
        if self.edited_entity.has_eid():
            parent = self.edited_entity
        elif '__linkto' in self._cw.form:
            parent = self._cw.entity_from_eid(int(self._cw.form['__linkto'].split(':')[1]))
        if parent is not None:
            if parent.cw_adapt_to('IContainer') is not None:
                container = parent
            else:
                container = parent.cw_adapt_to('IContained').container
            self.add_hidden(name='sedaContainerEID', value=container.eid, id='sedaContainerEID')


# this js file contains a custom implementation of addInlineCreationForm that propage
# sedaContainerEID
autoform.AutomaticEntityForm.needs_js += ('cubes.seda.form.js',)
