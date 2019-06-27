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

"""cubicweb-seda views for presenting tree data (using jqTree)."""

from functools import wraps

from cubicweb import tags, uilib
from cubicweb.utils import JSString
from cubicweb.view import EntityAdapter, EntityView, View
from cubicweb.predicates import adaptable, match_form_params
from cubicweb.web.views import ajaxcontroller, json


@ajaxcontroller.ajaxfunc(output_type='json')
def jqtree_reparent(self, child_eid, parent_eid, index):
    child = self._cw.entity_from_eid(child_eid)
    adapted = child.cw_adapt_to('IJQTree')
    assert adapted is not None
    adapted.reparent(parent_eid, index)


@ajaxcontroller.ajaxfunc(output_type='json')
def jqtree_reorder(self, parent_eid, child_eid, index):
    parent = self._cw.entity_from_eid(parent_eid)
    adapted = parent.cw_adapt_to('IJQTree')
    assert adapted is not None
    adapted.move_child_at_index(child_eid, index)


class IJQTreeAdapter(EntityAdapter):
    """Adapt an entity into a JQTree node."""
    __abstract__ = True
    __regid__ = 'IJQTree'

    def maybe_parent_of(self):
        """Return a list of entity type which `entity` may be parent of."""
        return []

    def maybe_moved(self):
        """Return True if entity may be moved from its location to another
        (i.e. may be reparented).
        """
        return False

    def reparent(self, peid, index):
        """Set entity as child of entity with `peid`, at the `index` position.
        """
        raise NotImplementedError

    def move_child_at_index(self, ceid, index):
        """Move child entity `ceid` at the `index` position."""
        raise NotImplementedError

    def json(self, on_demand=False):
        """Return a JSON dict of an entity."""
        entity = self.entity
        label = entity.view('jqtree.label')
        data = {
            'label': label,
            'id': entity.eid,
            'type': entity.cw_etype,
            'maybeMoved': self.maybe_moved(),
            'maybeParentOf': self.maybe_parent_of(),
        }
        if on_demand:
            data['load_on_demand'] = True
        return data


def itree_adaptable(func):
    """Decorator for a function taking an entity as argument, checking that
    the entity is adaptable as ITreeBase and eventually calling it or not.
    """
    @wraps(func)
    def wrapper(entity):
        itree = entity.cw_adapt_to('ITreeBase')
        if itree:
            return func(entity)
        return ()
    return wrapper


@itree_adaptable
def json_entity_children(entity):
    """Yield JSON data for children of a ITreeBase adapted entity.

    Each data will have `load_on_demand` unless it is a leaf of the tree.
    """
    for child in entity.cw_adapt_to('ITreeBase').iterchildren():
        ctree = child.cw_adapt_to('ITreeBase')
        on_demand = ctree and not ctree.is_leaf()
        ichild = child.cw_adapt_to('IJQTree')
        if ichild is not None:
            yield ichild.json(on_demand=on_demand)


@itree_adaptable
def json_entity_parents(entity):
    """Return the JSON data of the full tree walked upstream from `entity`.

    Each node along the path from this entity to the root will have
    `load_on_demand == False` so that the tree is opened down to `entity`.
    """
    # initialize data for "previous" parent when walking up the tree.
    previous, previous_children = None, []
    data = None
    for parent in entity.cw_adapt_to('ITreeBase').iterparents():
        # parent has to be strictly evaluated
        iparent = parent.cw_adapt_to('IJQTree')
        if iparent is None:
            continue
        data = iparent.json(on_demand=False)
        data['children'] = []
        # fetch JSON for children of this parent, setting the previous
        # parent we're coming from as strict (load_on_demand=False).
        for child in json_entity_children(parent):
            if previous_children and child['id'] == previous:
                # remove load_on_demand as this is the branch we are
                # walking on.
                child.pop('load_on_demand', None)
                # add children of previous parent (which is a child of
                # this parent).
                child.setdefault('children', []).extend(previous_children)
            data['children'].append(child)
        # store this parent as the previous one for next iteration.
        previous, previous_children = parent.eid, data.get('children', [])
    return data


class JsonTreeView(json.JsonMixIn, EntityView):
    """JSON view for an entity adaptable as a ITreeBase."""

    __regid__ = 'jqtree.json'
    __select__ = adaptable('ITreeBase') & ~match_form_params('node')

    def entity_call(self, entity, **kwargs):
        # compute the parent JSON tree.
        data = json_entity_parents(entity)
        if not data:
            # if empty, just return the current entity JSON tree (with
            # children) as the entity is probably the root.
            adapted = entity.cw_adapt_to('IJQTree')
            assert adapted is not None
            data = adapted.json(on_demand=False)
            children = list(json_entity_children(entity))
            if children:
                data['children'] = children
        data['selected'] = entity.eid
        self.wdata([data])


class JsonTreeNodeView(json.JsonMixIn, View):
    """JSON view for a node of tree, returning the children of that node for
    lazy loading.
    """

    __regid__ = 'jqtree.json'
    __select__ = match_form_params('node')

    def call(self):
        eid = self._cw.form.pop('node')
        entity = self._cw.entity_from_eid(eid)
        children = list(json_entity_children(entity))
        self.wdata(children)


class JQTreeItemLabelView(EntityView):
    """View for the "label" of a node of a jqTree.

    Default to "oneline" view.
    """
    __regid__ = 'jqtree.label'

    def entity_call(self, entity):
        entity.view('oneline', w=self.w)


class JQTreeView(EntityView):
    """Tree view using jqTree library."""
    __regid__ = 'jqtree.treeview'
    __select__ = adaptable('ITreeBase')

    def entity_call(self, entity, **kwargs):
        # TODO move jqTree js to its own file.
        self._cw.add_js(('cubes.jqtree.js', 'tree.jquery.js'))
        self._cw.add_css(('jqtree.css'))
        divid = 'jqtree' + str(entity.eid)
        data_url = entity.absolute_url(vid='jqtree.json')
        self.w(tags.div(id=divid, **{'data-url': data_url}))
        mayupdate = entity.e_schema.has_perm(
            self._cw, 'update', eid=entity.eid)
        adapted = entity.cw_adapt_to('IJQTree')
        self._cw.add_onload(uilib.js.jqtree.jqTree(divid, mayupdate,
                                                   JSString(adapted.js_can_move_to)))
