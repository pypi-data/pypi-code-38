# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-seda custom fields/widgets"""

from six import text_type

from logilab.common.decorators import monkeypatch

from cubicweb import tags, utils
from cubicweb.uilib import js
from cubicweb.web import formfields as ff, formwidgets as fw
from cubicweb.web.views import ajaxcontroller, autoform, formrenderers

from cubes.relationwidget import views as rwdg


# deactivate relation widget's creation form by default, it causes some js error if e.g. there are
# some calendar widgets. Also, we don't really want that from an UX POV, IMO.
rwdg.SearchForRelatedEntitiesView.has_creation_form = False


def configure_relation_widget(req, div, search_url, title, multiple, validate):
    """Build a javascript link to invoke a relation widget

    Widget will be linked to div `div`, with a title `title`. It will display selectable entities
    matching url `search_url`. bool `multiple` indicates whether several entities can be selected or
    just one, `validate` identifies the javascript callback that must be used to validate the
    selection.
    """
    req.add_js(('jquery.ui.js',
                'cubicweb.ajax.js',
                'cubicweb.widgets.js',
                'cubicweb.facets.js',
                'cubes.relationwidget.js',
                'cubes.editionext.js'))
    return 'javascript: %s' % js.editext.relateWidget(div, search_url, title, multiple,
                                                      utils.JSString(validate))


class ConceptOrTextField(ff.Field):
    """Compound field, using the :class:`ConceptAutoCompleteWidget` to handle values which may be
    either a relation to a `Concept` or a string

    It's expected to be set on the text attribute. Also, as you should prefer specifying a field's
    class, you will usually sublcass this field to set the following attributes:

    * 'scheme_relation', relation whose object will be the selected scheme
    * 'concept_relation', relation whose object will be the linked concept

    Example::

        class KeywordConceptOrTextField(ConceptOrTextField):
            scheme_relation = 'keyword_scheme'
            concept_relation = 'keyword_concept'

            def __init__(self, **kwargs):
                super(EquivalentConceptOrTextField, self).__init__(required=True, **kwargs)
                self.help = _('when linked to a vocabulary, value is enforced to the label of a '
                              'concept in this vocabulary. Remove it if you want to type text '
                              'freely.')

        aff = uicfg.autoform_field
        aff.tag_attribute(('Keyword', 'keyword_value'), KeywordConceptOrTextField)

    You may also configure the ajax function that will be used for the completion values, by
    specifying it using the 'ajax_autocomplete_func' attribute (or by overriding this ajax
    func). Default is :func:`scheme_concepts_autocomplete`.
    """

    scheme_relation = concept_relation = None
    ajax_autocomplete_func = 'scheme_concepts_autocomplete'

    def get_widget(self, form):
        return ConceptAutoCompleteWidget(self.name, self.scheme_relation,
                                         self.ajax_autocomplete_func, optional=True)

    def has_been_modified(self, form):
        return True  # handled in process_posted below

    def process_posted(self, form):
        posted = form._cw.form
        text_val = posted.get(self.input_name(form, 'Label'), '').strip()
        equivalent_eid = posted.get(self.input_name(form), '').strip()
        equivalent_eids = set()
        if equivalent_eid:
            equivalent_eids.add(int(equivalent_eid))
        if self.required and not (text_val or equivalent_eid):
            raise ff.ProcessFormError(form._cw.__("required field"))
        entity = form.edited_entity
        if not entity.has_eid() or getattr(entity, self.name) != text_val:
            yield (ff.Field(name=self.name, role='subject', eidparam=True), text_val)
        if (not entity.has_eid() and equivalent_eids) \
           or (entity.has_eid()
               and set(x.eid for x in entity.equivalent_concept) != equivalent_eids):
            subfield = ff.Field(name=self.concept_relation, role='subject', eidparam=True)
            # register the association between the value and the field, because on entity creation,
            # process_posted will be recalled on the newly created field, and if we don't do that it
            # won't find the proper value (this is very nasty)
            form.formvalues[(subfield, form)] = equivalent_eids
            yield (subfield, equivalent_eids)


class KeywordTypeMasterWidget(fw.Select):
    """
    Usage::

      affk = uicfg.autoform_field_kwargs
      affk.set_field_kwargs('KeywordType', 'keyword_type_to',
                            widget=widgets.KeywordTypeMasterWidget(
                            slave_base_name='seda_keyword_reference_to_scheme'))
    """

    def __init__(self, slave_base_name, **kwargs):
        super(KeywordTypeMasterWidget, self).__init__(**kwargs)
        self.slave_base_name = slave_base_name

    def _render(self, form, field, render):
        req = form._cw

        vocabularies_data = []
        for eid, title, uri, keyword_type in req.execute(
                'Any CS,CST,CSU,CSKT WHERE CS title CST, CS cwuri CSU, CS code_keyword_type CSKT?'):
            vocabularies_data.append({'eid': eid, 'title': title or uri,
                                      'keyword_type': keyword_type})
        vocabularies_data.sort(key=lambda x: x['title'])

        req.add_js(('cubicweb.js', 'cubicweb.ajax.js', 'cubes.skoscomplete.js'))
        req.add_onload(js.typed_vocabularies.initKeywordTypeMasterWidget(
            field.dom_id(form, self.suffix), self.slave_base_name, vocabularies_data))

        return super(KeywordTypeMasterWidget, self)._render(form, field, render)


class ConceptAutoCompleteWidget(fw.TextInput):
    """Derive from simple text input to create an autocompletion widget if a scheme is specified,
    otherwise free text is fine if `optional` argument is true. In such case:

    * `slave_name` is expected to be the name of the concept attribute, or the text attribute if
      optional is true),

    * you'll have to use this widget from a custom field that will handle the relation to the
      concept (e.g. :class:`ConceptOrTextField`).

    When optional is false, a regular :class:`RelationField` is fine.

    You may configure the ajax function that will be used for the completion values by specifying it
    using the 'ajax_autocomplete_func' argument (or by overriding this ajax func). Default is
    :func:`scheme_concepts_autocomplete`.

    Usage::

      affk = uicfg.autoform_field_kwargs
      affk.set_field_kwargs('Keyword', 'keyword_value',
                            widget=ConceptAutoCompleteWidget(slave_name='keyword_value',
                                                             master_name='keyword_scheme',
                                                             optional=True))
    """
    needs_css = ('jquery.ui.css',)
    needs_js = ('jquery.ui.js',
                'cubicweb.js', 'cubicweb.ajax.js',
                'cubes.skoscomplete.js')

    def __init__(self, slave_name, master_name,
                 ajax_autocomplete_func='scheme_concepts_autocomplete',
                 optional=False,
                 **kwargs):
        super(ConceptAutoCompleteWidget, self).__init__(**kwargs)
        self.slave_name = slave_name
        self.master_name = master_name
        self.ajax_autocomplete_func = ajax_autocomplete_func
        self.optional = optional

    def _render(self, form, field, render):
        entity = form.edited_entity
        slave_id = field.dom_id(form, self.suffix)
        master_id = slave_id.replace(self.slave_name, self.master_name)
        if entity.has_eid():
            concept = entity.concept
        else:
            concept = None
        req = form._cw
        req.add_onload(js.concept_autocomplete.initConceptAutoCompleteWidget(
            master_id, slave_id, self.ajax_autocomplete_func))
        if concept is None:
            value = getattr(entity, self.slave_name) if self.optional else None
            eid = u''
        else:
            value = concept.label()
            eid = text_type(concept.eid)
        # we need an hidden input to handle the value while the text input display the label
        inputs = [
            tags.input(name=field.input_name(form, 'Label'), id=slave_id + 'Label',
                       klass='form-control', type='text',
                       value=value),
            tags.input(name=field.input_name(form), id=slave_id, type='hidden',
                       value=eid)
        ]
        return u'\n'.join(inputs)


@ajaxcontroller.ajaxfunc(output_type='json')
def scheme_concepts_autocomplete(self):
    assert self._cw.form['scheme']
    scheme = int(self._cw.form['scheme'])
    term = self._cw.form['q']
    limit = self._cw.form.get('limit', 50)
    return [{'value': eid, 'label': label}
            for eid, label in self._cw.execute(
                'DISTINCT Any C,N ORDERBY N LIMIT %s WHERE C in_scheme S, S eid %%(s)s, '
                'C preferred_label L, L label N, L label ILIKE %%(term)s' % limit,
                {'s': scheme, 'term': u'%%%s%%' % term})]


@monkeypatch(formrenderers.EntityInlinedFormRenderer)
def render_title(self, w, form, values):
    """Monkey-patched to remove counter"""
    w(u'<div class="iformTitle">')
    w(u'<span>%(title)s</span>' % values)
    if values['removejs']:
        values['removemsg'] = self._cw.__('remove-inlined-entity-form')
        w(u' [<a href="javascript: %(removejs)s;$.noop();">%(removemsg)s</a>]'
          % values)
    w(u'</div>')


class SEDAMetaField(ff.StringField):
    """Extends user_cardinality field to allow edition of a `user_annotation` all together.
    """

    @staticmethod
    def annotation_field(form):
        """Return the field for `user_annotation` entity. """
        eschema = form.edited_entity.e_schema
        rschema = eschema.subjrels['user_annotation']
        return ff.guess_field(eschema, rschema, 'subject', form._cw)

    def actual_fields(self, form):
        """Overriden from :class:`Field`"""
        yield self
        yield self.annotation_field(form)

    def render(self, form, renderer):
        """Overriden from :class:`Field` to render fields in a div which is hidden by default"""
        form._cw.add_js('cubes.seda.js')
        wdgs = [self.get_widget(form).render(form, self, renderer)]
        self._render_hidden_section(wdgs, form, renderer)
        return u'\n'.join(wdgs)

    def _render_hidden_section(self, wdgs, form, renderer):
        divid = '%s-advanced' % self.input_name(form)
        if form.edited_entity.has_eid() and form.edited_entity.user_annotation:
            hidden = ''
            icon = 'icon-up-open'
        else:
            hidden = ' hidden'
            icon = 'icon-list-add'
        wdgs.append(tags.a(u'', onclick=text_type(js.seda.toggleFormMetaVisibility(divid)),
                           href='javascript:$.noop()', title=form._cw._('show/hide meta fields'),
                           # take care, related js relies on the icon class position
                           klass=icon + ' metaFieldSwitch'))
        wdgs.append(u'<div id="{0}" class="metaField{1}">'.format(divid, hidden))
        wdgs.append(self._render_subfield(form, self.annotation_field(form), renderer))
        wdgs.append(u'</div>')

    @staticmethod
    def _render_subfield(form, field, renderer):
        """Render a sub-field: label + widget + help + EOL"""
        data = utils.UStringIO()
        w = data.write
        w(u'<div class="row">')
        w(renderer.render_label(form, field))
        w(u'<div class="col-md-9">')
        w(field.render(form, renderer))
        w(u'</div>')
        w(u'</div>')
        w(u'<div class="row">')
        w(u'<div class="col-md-offset-3 col-md-9">')
        w(renderer.render_help(form, field))
        w(u'</div>')
        w(u'</div>')
        return data.getvalue()


class SimplifiedAutomaticEntityForm(autoform.AutomaticEntityForm):
    """Custom autoform, forcing display of creation form instead of add new link.
    """

    __abstract__ = True

    def should_display_inline_creation_form(self, rschema, existing, card):
        return not existing

    def should_display_add_new_relation_link(self, rschema, existing, card):
        return False


class NoTitleEntityInlinedFormRenderer(formrenderers.EntityInlinedFormRenderer):
    """Custom inlined form renderer that doesn't display any title nor remove link.

    This is intended to be subclassed with a custom selector.
    """

    __abstract__ = True

    def render_title(self, w, form, values):
        pass


class ConcretNoTitleEntityInlinedFormRenderer(NoTitleEntityInlinedFormRenderer):
    """Concret implementation of `NoTitleEntityInlinedFormRenderer` with a custom regid.

    Use this one by specifying the renderer id explicitly, for case where you can't easily specify a
    selector.
    """
    __regid__ = 'notitle'
