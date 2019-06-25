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
"""Set of tree-building widgets, some based on jQuery treeview
plugin.
"""

__docformat__ = "restructuredtext en"
from cubicweb.web import formwidgets as fwdgs
from cubicweb import tags
from logilab.mtconverter import xml_escape


class TreeViewWidget(fwdgs.FieldWidget):
    """form widget to link to keywords of a given classification"""

    subvid = 'oneline_edit'

    needs_js = ('cubicweb.ajax.js', 'cubicweb.widgets.js',
                'jquery.treeview.js', 'jquery.ui.js', 'cubes.treeview.js')
    needs_css = ('jquery.treeview.css', 'jquery.ui.css', 'cubes.treeview.css')

    html = (u'''<a href="javascript:$.noop()" '''
            u'''onclick="$('#%(tree_uid)s').treewidget(%(required)s, %(multiple)s, false, {'cancelButton': '%(cancel)s', 'okButton': '%(ok)s'}) ;return false;">'''  # noqa
            u'''%(open_link)s&nbsp;%(remove_link)s</a>'''
            u'''<div id="sel_%(tree_uid)s">%(selected)s</div>'''
            u'''<div id="%(tree_uid)s" style="display: none;">'''
            u'''<div class="error"></div><div id="holder_%(tree_uid)s">%(form)s</div></div>''')  # '

    remove_link_html = u'''<a href="javascript:$.noop()" cubicweb:link="%s" class="remove_link"
    onclick="$('#sel_%s').empty()">[%s]</a>'''

    def __init__(self, leavesonly=False,
                 multiple=None, level=None, **kwargs):
        """
        :param leavesonly: True if only leaves can be selected
        :param multiple: True if more than one value can be selected. If this parameter is set,
                         the rtype's cardinality is ignored
        :param level: only select values on the given tree level
        """
        super(TreeViewWidget, self).__init__(**kwargs)
        self.leavesonly = int(leavesonly)
        self.multiple = multiple
        self.level = level

    def _render(self, form, field, renderer):
        _ = form._cw._
        treerset = self._filter_rset(field, form)
        if not treerset:
            return _(u"no available values")
        self.required = int(field.required)
        self.guess_multiple(field, form)
        tree_uid = field.input_name(form, self.suffix).replace(':', '--')
        related = self.compute_related(form, field)
        treeform = self.render_treeform(form, treerset, tree_uid, related)
        remove_link = self.remove_link_html % (field.name, tree_uid, _('remove'))
        selected = u'\n'.join(self.render_selected(field.input_name(form, self.suffix), related))
        return self.html % {
            'required': self.required,
            'multiple': self.multiple,
            'selected': selected,
            'tree_uid': tree_uid, 'form': treeform,
            'open_link': xml_escape(_('select').capitalize()),
            'remove_link': remove_link,
            'cancel': _('button_cancel'),
            'ok': _('button_ok'),
        }

    def guess_multiple(self, field, form):
        if self.multiple is None:
            eschema = form._cw.vreg.schema.eschema(form.edited_entity.__regid__)
            rschema = eschema.schema.rschema(field.name)
            rdef = eschema.rdef(rschema, field.role)
            card = rdef.role_cardinality(field.role)
            self.multiple = card in '*+'
        self.multiple = int(self.multiple)

    def _filter_rset(self, field, form):
        """filter the rset to only get the root entities"""
        vocab = field.vocabulary(form)
        if vocab:
            entities = [form._cw.entity_from_eid(i[1]) for i in vocab]
            eids = ', '.join(str(e.eid) for e in entities
                             if e.cw_adapt_to('ITree') and e.cw_adapt_to('ITree').is_root())
            return form._cw.execute('Any X WHERE X eid IN (%(e)s)' % {'e': eids})
        return None

    def render_treeform(self, form, treerset, tree_uid, related):
        return form._cw.view('treeview_edit', treerset, subvid="oneline_edit",
                             tree_uid=tree_uid,
                             related=[k.eid for k in related],
                             leavesonly=self.leavesonly,
                             required=self.required,
                             multiple=self.multiple,
                             level=self.level)

    def compute_related(self, form, field):
        if not hasattr(form, 'edited_entity'):
            return ()
        # set initial values if exist
        initial_values = self.values(form, field)
        if initial_values:
            related = form._cw.execute('Any K WHERE K eid IN (%(eid)s)' %
                                       {'eid': ','.join([str(v) for v in initial_values])})
        else:
            related = form.edited_entity.related(field.name, field.role)
        if related:
            return list(related.entities())
        return ()

    def render_selected(self, name, related):
        if not related:
            yield tags.input(id=name, name=name, value='', type='hidden')
        for keyword in related:
            input = tags.input(id=name, name=name, value=keyword.eid, type='hidden')
            yield tags.div(u'<a href="javascript:$.noop()" onclick="$(this).parent().remove()">[x]'
                           u'</a>'
                           u'%(input)s %(title)s' % {'input': input,
                                                     'title': xml_escape(keyword.dc_title())})
