from itertools import chain
from django.core.urlresolvers import reverse
from django.forms.utils import flatatt
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer

from django import forms
from django.forms import CheckboxInput
from django.forms.widgets import ClearableFileInput, MultiWidget, SubWidget, RadioSelect
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape, escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


class BootstrapRadioFieldRenderer(forms.widgets.RadioFieldRenderer):
    def render(self):
        return mark_safe(u'%s' % u'\n'.join(
            [u'<div class="radio">%s</div>' % force_unicode(w) for w in self]))


class RatingRadioFieldRenderer(forms.widgets.RadioFieldRenderer):
    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield NoLabelRadioInput(self.name, self.value, self.attrs.copy(), choice, i)

    def render(self):
        return mark_safe(u'%s' % u'\n'.join(
            [u'%s' % force_unicode(w) for w in self]))


class QuizRadioFieldRenderer(forms.widgets.RadioFieldRenderer):
    def render(self):
        list_items = []

        for w in self:
            klass = "correct" if int(w.choice_value) \
            in self.attrs['correct_options'] else ""
            list_items.append(u'<li class="option %s">%s</li>' % (klass,
                                                           force_unicode(w)))

        """Outputs a <ul> for this set of radio fields."""
        return mark_safe(u'<ul>\n%s\n</ul>' % u'\n'.join(list_items))


class QuizBootstrapCheckboxSelectMultiple(forms.widgets.SelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = []
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        enum = enumerate(chain(self.choices, choices))

        for i, (option_value, option_label) in enum:
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = CheckboxInput(
                final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))

            klass = "correct" if int(option_value)\
            in self.attrs['correct_options'] else ""

            output.append(
                u'<label%s class="checkbox option %s">%s %s</label>' % (
                    label_for, klass, rendered_cb, option_label))
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_


class NoLabelRadioInput(SubWidget):
    """
    An object used by RadioFieldRenderer that represents a single
    <input type='radio'>.
    """

    def __init__(self, name, value, attrs, choice, index):
        self.name, self.value = name, value
        self.attrs = attrs
        self.choice_value = force_unicode(choice[0])
        self.choice_label = force_unicode(choice[1])
        self.index = index

    def __unicode__(self):
        return self.render()

    def render(self, name=None, value=None, attrs=None, choices=()):
        name = name or self.name
        value = value or self.value
        attrs = attrs or self.attrs
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = conditional_escape(force_unicode(self.choice_label))
        return mark_safe(u'%s' % (self.tag()))

    def is_checked(self):
        return self.value == self.choice_value

    def tag(self):
        if 'id' in self.attrs:
            self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)
        final_attrs = dict(self.attrs, type='radio', name=self.name, value=self.choice_value)
        if self.is_checked():
            final_attrs['checked'] = 'checked'
        return mark_safe(u'<input%s />' % flatatt(final_attrs))


class BootstrapCheckboxSelectMultiple(forms.widgets.SelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = []
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        enum = enumerate(chain(self.choices, choices))
        for i, (option_value, option_label) in enum:
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = CheckboxInput(
                final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(
                u'<label%s class="checkbox">%s %s</label>' % (
                    label_for, rendered_cb, option_label))
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_


class MatrixRadioInput(RadioSelect):
    # def __init__(self, attrs=None, choices=()):
    def __init__(self, name, value, attrs=None, choices=(), idx=None):
        super(MatrixRadioInput, self).__init__(attrs, choices)
        self.name = name
        self.value = value
        self.idx = idx

    # def render(self, name=None, value=None, attrs=None, choices=()):
    # def render(self, name, value, attrs=None):
    def render(self):
        ## almost working solution
        # return super(MatrixRadioInput, self).render(self.name, self.value, self.attrs)

        ## old solution
        # name = name or self.name
        # value = value or self.value
        # attrs = attrs or self.attrs
        # choice_label = conditional_escape(force_unicode(self.choice_label))
        # return mark_safe(self.tag())

        ## currently working solution
        choice = self.choices[0]

        if 'correct_options' in self.attrs:
            correct_options = self.attrs['correct_options']
            # correct_options_ids = list(correct_options.values_list('pk', flat=True))
            correct_options_ids_joined = ','.join([str(id) for id in correct_options])
        else:
            correct_options_ids_joined = ''

        input_value = choice[0]
        is_checked = str(input_value) == str(self.value)

        return u'<input type="radio" id="{}" value="{}" name="{}" correct_options="[{}]" {} {}>'.format(
            self.attrs['id'],
            input_value,
            self.name,
            correct_options_ids_joined,
            'checked="checked"' if is_checked else '',
            'disabled="disabled"' if self.attrs.get('disabled', None) == 'disabled' else ''
        )


class BootstrapRadioTableFieldRenderer(forms.widgets.RadioFieldRenderer):
    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield MatrixRadioInput(self.name, self.value, self.attrs.copy(), [choice], i)

    def __getitem__(self, idx):
        choice = self.choices[idx]  # Let the IndexError propagate
        return MatrixRadioInput(self.name, self.value, self.attrs.copy(), [choice], idx)

    def render(self):
        output = []
        for w in self:
            w.choice_label = ''
            # output.append('<td><div class="radio">%s</div></td>' % force_unicode(w))
            output.append('<td><div class="radio">%s</div></td>' % w.render())
        return mark_safe(''.join(output))


class Matrix(MultiWidget):
    def __init__(self, rows=None, columns=None):
        widgets = []
        self.rows = rows
        self.columns = columns

        for row in rows:
            widgets.append(forms.RadioSelect(choices=columns, renderer=BootstrapRadioTableFieldRenderer))
        super(Matrix, self).__init__(widgets)

    def render(self, name, value, attrs=None):
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
                # value is a list of values, each corresponding to a widget
                # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []

        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)

        is_quiz = 'correct_options' in self.attrs

        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None

            option_id = self.rows[i][0]
            klass = "correct" if is_quiz and option_id in self.attrs['correct_options'] else ""

            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))

            rendered_output = widget.render(name + '_%s' % i, widget_value, final_attrs)
            rendered_headings = self.rows[i][1]
            output.append('<tr><th class="option %s">%s</th>%s</td>' % (klass, rendered_headings, rendered_output))
        return mark_safe(
            '<table class="table table-bordered %s">%s%s</table>' % (
                'quiz' if is_quiz else '', self._rendered_heading(), self.format_output(output)))

    def _rendered_heading(self):
        output = ['<th></th>']
        for column in self.columns:
            output.append('<th>%s</th>' % column[1])
        return '<tr>%s</tr>' % ''.join(output)

    def decompress(self, value):
        result = []
        for row in self.rows:
            result.append(None)
        return result


class BootstrapCheckboxSelectTableMultiple(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        enum = enumerate(chain(self.choices, choices))
        for i, (option_value, option_label) in enum:
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = CheckboxInput(
                final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<td>%s</td>' % rendered_cb)
        output.append(u'')
        return mark_safe(u'\n'.join(output))


class MatrixMultiple(MultiWidget):
    def __init__(self, rows=None, columns=None):
        widgets = []
        self.rows = rows
        self.columns = columns

        for row in rows:
            widgets.append(BootstrapCheckboxSelectTableMultiple(choices=columns))
        super(MatrixMultiple, self).__init__(widgets)

    def render(self, name, value, attrs=None):
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
                # value is a list of values, each corresponding to a widget
                # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []

        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None

            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
            rendered_output = widget.render(
                name + '_%s' % i, widget_value, final_attrs)
            rendered_headings = self.rows[i][1]
            output.append(
                '<tr><th>%s</th>%s</td>' % (
                    rendered_headings, rendered_output))
        return mark_safe(
            '<table class="table table-bordered">%s%s</table>' % (
                self._rendered_heading(), self.format_output(output)))

    def _rendered_heading(self):
        output = ['<th></th>']
        for column in self.columns:
            output.append('<th>%s</th>' % column[1])

        return '<tr>%s</tr>' % ''.join(output)

    def decompress(self, value):
        result = []
        for row in self.rows:
            result.append(None)
        return result


class SexyFileInput(ClearableFileInput):
    initial_text = _(u'Currently')
    input_text = _(u'Change')
    clear_checkbox_label = _(u'Clear')

    template_with_initial = u'%(initial)s %(clear_template)s\
    %(input)s'
    template_with_clear = u'<label for="%(clear_checkbox_id)s">\
    %(clear_checkbox_label)s %(clear)s</label>'

    def render(self, name, value, attrs=None):
        if value:
            self.template_with_clear = u'<a href="%(link)s" \
            class="remove">%(anchor)s</a>' % {
                'anchor': _(u'Remove image'),
                'link': self.attrs.get('remove_url', '/'),
            }

        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = u'%(input)s'
        substitutions['input'] = ''
        if not value:
            substitutions['input'] = super(ClearableFileInput, self).render(
                name, value, attrs)

        if value and hasattr(value, 'url'):
            template = self.template_with_initial
            crop = True

            if 'crop' in self.attrs:
                crop = self.attrs['crop']

            if 'width' in self.attrs and 'height' in self.attrs:
                options = {'size': (self.attrs['width'], self.attrs['height']),
                           'crop': crop}
            else:
                options = {'size': (60, 60), 'crop': crop}

            try:
                thumb_url = get_thumbnailer(value).get_thumbnail(options).url
            except InvalidImageFormatError:
                thumb_url = ''

            substitutions['initial'] = (u'<a href="%s"><img src="%s"></a>' % (
                reverse('media', args=(value, )), escape(thumb_url),
            ))

            if value:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(
                    checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(
                    checkbox_id)
                substitutions['clear'] = CheckboxInput().render(
                    checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = \
                    self.template_with_clear % substitutions

        return mark_safe(template % substitutions)
