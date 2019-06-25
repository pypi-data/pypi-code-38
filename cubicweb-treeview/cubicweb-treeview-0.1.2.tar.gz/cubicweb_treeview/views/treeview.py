# copyright 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <http://www.gnu.org/licenses/>.
"""Set of tree
"""

__docformat__ = "restructuredtext en"
from cubicweb.uilib import cut
from cubicweb.web.views import baseviews, treeview
from cubicweb.predicates import match_kwargs, adaptable
from logilab.mtconverter import xml_escape
import json


class TVTreeViewItemView(treeview.TreeViewItemView):

    def _is_leaf(self, itree):
        return itree is None or itree.is_leaf()

    def _children(self, itree):
        return itree.children(entities=False)

    def cell_call(self, row, col, treeid, vid='oneline',
                  parentvid='treeview',
                  is_last=False, **morekwargs):
        w = self.w
        entity = self.cw_rset.get_entity(row, col)
        itree = entity.cw_adapt_to('ITree')
        # XXX treeview customization : add css class
        liclasses = [u'cw-%s' % entity.__regid__.lower()]
        # XXX
        is_open = self.open_state(entity.eid, treeid)
        is_leaf = self._is_leaf(itree)
        if is_leaf:
            if is_last:
                liclasses.append('last')
            w(u'<li class="%s">' % u' '.join(liclasses))
        else:
            rql = itree.children_rql() % {'x': entity.eid}
            url = xml_escape(self._cw.build_url('json', rql=rql, vid=parentvid,
                                                pageid=self._cw.pageid,
                                                treeid=treeid,
                                                fname='view',
                                                treesubvid=vid,
                                                morekwargs=json.dumps(morekwargs)))
            divclasses = ['hitarea']
            if is_open:
                liclasses.append('collapsable')
                divclasses.append('collapsable-hitarea')
            else:
                liclasses.append('expandable')
                divclasses.append('expandable-hitarea')
            if is_last:
                if is_open:
                    liclasses.append('lastCollapsable')
                    divclasses.append('lastCollapsable-hitarea')
                else:
                    liclasses.append('lastExpandable')
                    divclasses.append('lastExpandable-hitarea')
            if is_open:
                w(u'<li class="%s">' % u' '.join(liclasses))
            else:
                w(u'<li cubicweb:loadurl="%s" class="%s">' % (url, u' '.join(liclasses)))
            if treeid.startswith('throw_away'):
                divtail = ''
            else:
                divtail = """ onclick="asyncRemoteExec('node_clicked', '%s', '%s')" """ % (
                    treeid, entity.eid)
            w(u'<div class="%s"%s></div>' % (u' '.join(divclasses), divtail))

            # add empty <ul> because jquery's treeview plugin checks for
            # sublists presence
            if not is_open:
                w(u'<ul class="placeholder"><li>place holder</li></ul>')
        # the local node info
        self.wview(vid, self.cw_rset, row=row, col=col, **morekwargs)
        if is_open and not is_leaf:  # => rql is defined
            self.wview(parentvid, self._children(itree), subvid=vid,
                       treeid=treeid, initial_load=False, **morekwargs)
        w(u'</li>')


class TVDefaultTreeViewItemView(treeview.DefaultTreeViewItemView):

    def cell_call(self, row, col, vid='oneline', treeid=None, **morekwargs):
        assert treeid is not None
        entity = self.cw_rset.get_entity(row, col)
        itemview = entity.view(vid, **morekwargs)
        # treeview customization : add css classe
        liclasses = [u'cw-%s' % entity.__regid__.lower()]
        if morekwargs['is_last']:
            liclasses.append('last')
        self.w(u'<li class="%s">%s</li>' % (u' '.join(liclasses), itemview))


class TVTreeViewEditItemView(TVTreeViewItemView):
    """keeps track of which branches to open according to the X rtype
    Y value given to the TreeView
    """
    __regid__ = 'itemvid_edit'
    __select__ = (treeview.TreeView.__select__
                  & (match_kwargs('related', 'required', 'multiple', 'leavesonly',
                                  'tree_uid', 'level')))
    _open_branch_memo = None

    def open_state(self, eeid, treeid):
        return eeid in self._open_branch_memo

    def cell_call(self, row, col, treeid, vid='oneline_edit', parentvid='treeview_edit',
                  is_last=False, **morekwargs):
        entity = self.cw_rset.get_entity(row, col)
        self._open_branch_memo = set(entity.cw_adapt_to('ITree').path())
        return super(TVTreeViewEditItemView, self).cell_call(
            row, col, treeid, vid=vid, parentvid=parentvid, is_last=is_last, **morekwargs)

    def _is_leaf(self, itree):
        return itree is None or itree.is_editable_leaf()

    def _children(self, itree):
        return itree.editable_children(entities=False)


class TVTreeEditView(treeview.TreeView):
    __regid__ = 'treeview_edit'
    subvid = 'oneline_edit'
    itemvid = 'itemvid_edit'
    __select__ = (treeview.TreeView.__select__
                  & (match_kwargs('related', 'required', 'multiple', 'leavesonly',
                                  'tree_uid', 'level')) & adaptable('ITree'))

    def _init_params(self, subvid, treeid, initial_load, morekwargs):
        form = self._cw.form
        initial_fname = form.get('fname', None)
        if initial_fname == 'reledit_form':
            form.pop('fname')
        return super(TVTreeEditView, self)._init_params(
            subvid, treeid, initial_load, morekwargs)


class TVNotTreeEditView(treeview.DefaultTreeViewItemView):
    __regid__ = 'treeview_edit'
    __select__ = ~adaptable('ITree')
    itemvid = 'itemvid_edit'

    def cell_call(self, row, col, vid='oneline', treeid=None, **morekwargs):
        return u''


class TVNotTreeviewOneLineEditView(baseviews.InContextView):
    __regid__ = 'oneline_edit'
    __select__ = ~adaptable('ITree')

    def cell_call(self, row, col, tree_uid, multiple,
                  leavesonly, related, required, level):
        return u''


class TVTreeviewOneLineEditView(baseviews.InContextView):
    __regid__ = 'oneline_edit'
    __select__ = adaptable('ITree')

    def cell_call(self, row, col, tree_uid, multiple,
                  leavesonly, related, required, level):
        entity = self.cw_rset.get_entity(row, col)
        entity_name = xml_escape(entity.dc_title())
        itree = entity.cw_adapt_to('ITree')
        is_leaf = itree.is_editable_leaf()
        entity_level = self.entity_level(itree)
        if multiple:
            if level and entity_level != level:
                self.w(u'<span>%s</span>' % entity_name)
            elif not leavesonly or is_leaf:
                self.w(u'<input type="checkbox" name="selitems" value="%(eid)s" '
                       u'%(sel)s id="treeitem_%(eid)s"/>&nbsp;'
                       % {'eid': entity.eid, 'sel': entity.eid
                          in related and u'checked="checked"' or u''})
                self.w(u'<span class="hidden">%s</span>' % entity_name)
                self.w(u'<a href="javascript:$.noop()" onclick="$(\'#treeitem_%s\').click()"'
                       u'class="selectable">'
                       u'%s</a>' % (entity.eid, entity_name))
            else:
                self.w(u'<span>%s</span>' % (entity_name))
        else:
            cssclass = u"selected " if entity.eid in related else u""
            if level and entity_level.level != level:
                self.w(u'<span class="%s">%s</span>' % (cssclass, entity_name))
            elif not leavesonly or is_leaf:
                cssclass += u' selectable"'
                onclick = u"cw.treewidget.validateRelated(this, %s, \'%s\', %s)" % (
                    required, tree_uid, [[str(entity.eid)], []])
                self.w(u'<a href="javascript:$.noop()" onclick="%s" class="%s" '
                       % (onclick, cssclass))
                description = entity.dc_description()
                if description:
                    description = cut(description, 50)
                    self.w(u' title="%s"' % xml_escape(description))
                self.w(u'>%s</a>' % entity_name)
            else:
                self.w(u'<span class="%s">%s</span>' % (cssclass, entity_name))

    def entity_level(self, itree):
        if hasattr(itree, 'level'):
            return itree.level
        return None


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (
        TVTreeViewItemView,
        TVDefaultTreeViewItemView,
    ))
    vreg.register_and_replace(TVTreeViewItemView, treeview.TreeViewItemView)
    vreg.register_and_replace(TVDefaultTreeViewItemView, treeview.DefaultTreeViewItemView)
