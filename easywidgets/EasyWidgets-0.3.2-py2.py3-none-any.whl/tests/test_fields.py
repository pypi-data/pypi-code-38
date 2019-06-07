from __future__ import absolute_import
from __future__ import unicode_literals
from datetime import date, time

import formencode as fe
from formencode import validators as fev
from bs4 import BeautifulSoup

import ew
import ew.jinja2_ew
from ew.tests.helpers import TestCase

def soup(text):
    soup = BeautifulSoup(text)
    for n in soup.findAll():
        n.attrs = sorted(n.attrs)
    return soup

class _TestFields(TestCase):

    def test_text_field(self):
        w = self.ew.InputField(id="w", name='foo')
        text = w.display(value='bar')
        assert soup(text)==soup('<input id="w" name="foo" value="bar">'), text
        text = w.display()
        assert text=='<input id="w" name="foo">'

    def test_hidden_field(self):
        w = self.ew.HiddenField(id="w", name='foo')
        text = w.display(value='bar')
        assert soup(text)==soup('<input id="w" name="foo" type="hidden" value="bar">'), soup(text)
        text = w.display()
        assert text=='<input id="w" name="foo" type="hidden">', text

    def test_validate(self):
        w = self.ew.InputField(
            name='foo',
            validator=fev.UnicodeString(min=2))
        self.assertRaises(fe.Invalid, w.to_python, 'x', None)
        assert isinstance(ew.widget_context.validation_error, fe.Invalid)

    def test_html_field(self):
        fld = self.ew.HTMLField()
        assert '9' == fld.display(text='${value+4}', value=5)
        fld = self.ew.HTMLField()
        assert '<h1>Hi</h1>' == fld.display(value='<h1>Hi</h1>')

    def test_link_field(self):
        fld = self.ew.LinkField(href='/foo/${value}/', label='Bar')
        text = fld.display(value=5)
        assert soup('<a href="/foo/5/">Bar</a>') == soup(text), text

class _TestFieldSet(TestCase):

    def setUp(self):
        super(_TestFieldSet, self).setUp()
        self.w = self.ew.FieldSet(
            id="w", 
            fields=[
                self.ew.InputField(
                    name='foo',
                    validator=fev.UnicodeString(min=2)),
                self.ew.InputField(
                    name='bar',
                    validator=fev.UnicodeString(min=2)),
                ])
        self.nested_w = self.ew.FieldSet(
            id="w",
            fields=[self.ew.FieldSet(
                    name='fs',
                    fields=[
                        self.ew.InputField(
                            name='foo',
                            validator=fev.UnicodeString(min=2)),
                        self.ew.InputField(
                            name='bar',
                            validator=fev.UnicodeString(min=2)),
                        ])
                    ])

    def test_display(self):
        text = self.w.display()
        assert '<label for="w.foo"' in text
        assert '<input id="w.foo" name="foo"' in text
        text = self.w.display(value=dict(foo='bar', bar='baz'))
        assert '<label for="w.foo"' in text
        assert '<input id="w.foo" name="foo" value="bar"' in text
        assert '<label for="w.bar"' in text
        assert '<input id="w.bar" name="bar" value="baz"' in text

    def test_validation(self):
        self.assertRaises(fe.Invalid, self.w.to_python, dict(foo='x', bar='xxy'), None)
        assert isinstance(ew.widget_context.validation_error, fe.Invalid)
        text = self.w.display()
        assert '<label for="w.foo"' in text, text
        assert '<span class="fielderror">Enter' in text, text
        assert '<input id="w.foo" name="foo" value="x"' in text, text
        assert '<input id="w.bar" name="bar" value="xxy"' in text, text

    def test_nested_display(self):
        text = self.nested_w.display()
        assert '<label for="w.fs.foo"' in text
        assert '<input id="w.fs.foo" name="fs.foo"' in text
        text = self.nested_w.display(value=dict(fs=dict(foo='bar')))
        assert '<label for="w.fs.foo"' in text, text
        assert '<input id="w.fs.foo" name="fs.foo" value="bar"' in text
        
    def test_nested_validation(self):
        self.assertRaises(fe.Invalid, self.nested_w.to_python,
                          dict(fs=dict(foo='x')), None)
        assert isinstance(ew.widget_context.validation_error, fe.Invalid)
        text = self.nested_w.display()
        assert '<label for="w.fs.foo"' in text
        assert '<span class="fielderror"' in text
        assert '<input id="w.fs.foo" name="fs.foo" value="x"' in text

class _TestRowField(TestCase):

    def setUp(self):
        super(_TestRowField, self).setUp()
        self.w = self.ew.RowField(
            id="w-row",
            fields=[
                self.ew.InputField(
                    name='a',
                    validator=fev.UnicodeString(min=2)),
                self.ew.InputField(
                    name='b',
                    validator=fev.UnicodeString(min=2)),
                ])
    
    def test_display(self):
        text = self.w.display()
        assert '<input id="w-row.a" name="a"' in text
        text = self.w.display(value=dict(a='bar'))
        assert '<input id="w-row.a" name="a" value="bar"' in text

    def test_validation(self):
        self.assertRaises(fe.Invalid, self.w.to_python, dict(a='x', b='xx'), None)
        assert isinstance(ew.widget_context.validation_error, fe.Invalid)
        text = self.w.display()
        assert '<span class="fielderror"' in text
        assert '<input id="w-row.a" name="a" value="x"' in text, text

class _TestRepeatedField(TestCase):

    def setUp(self):
        super(_TestRepeatedField, self).setUp()
        self.w = self.ew.RepeatedField(
            id='w-a',
            field=self.ew.InputField(
                name='a',
                validator=fev.UnicodeString(min=2)))

    def test_display(self):
        text = self.w.display()
        assert '<input id="w-a-0" name="a-0"' in text
        assert '<input id="w-a-1" name="a-1"' in text
        assert '<input id="w-a-2" name="a-2"' in text
        text = self.w.display(value=['bar'])
        assert '<input id="w-a-0" name="a-0" value="bar"' in text, text
        assert '<input id="w-a-1" name="a-1"' not in text
        
    def test_validation(self):
        self.assertRaises(fe.Invalid, self.w.to_python, ['x', 'xx'], None)
        assert isinstance(ew.widget_context.validation_error, fe.Invalid)
        text = self.w.display(value=['xxx', 'xxx'])
        assert '<span class="fielderror"' in text
        assert '<input id="w-a-0" name="a-0" value="x"' in text, text


class _TestTableField(TestCase):

    def setUp(self):
        super(_TestTableField, self).setUp()
        self.w = self.ew.TableField(
            id="w-foo",
            name='foo',
            fields=[
                self.ew.InputField(
                    name='a',
                    validator=fev.UnicodeString(min=2)),
                self.ew.InputField(
                    name='b',
                    validator=fev.UnicodeString(min=2))
                ])

    def test_display(self):
        text = self.w.display()
        assert '<input id="w-foo-row-0.a" name="foo-0.a" value="">' in text, text
        text = self.w.display(value=[dict(a='xx',b='yy')])
        assert '<input id="w-foo-row-0.a" name="foo-0.a" value="xx">' in text, text
        
    def test_validation(self):
        self.assertRaises(
            fe.Invalid, self.w.to_python,
            [ dict(a='x', b='xx'),
              dict(a='yy', b='yy')],
            None)
        assert isinstance(ew.widget_context.validation_error, fe.Invalid)
        text = self.w.display()
        assert '<span class="fielderror"' in text, text
        assert '<input id="w-foo-row-0.a" name="foo-0.a" value="x">' in text, text

class _TestInputFields(TestCase):

    def test_text_field(self):
        t = self.ew.TextField(id="w-foo", name='foo')
        assert t.display() == '<input id="w-foo" name="foo" type="text">', t.display()
    
    def test_email_field(self):
        t = self.ew.EmailField(id="w-foo", name='foo')
        assert t.display() == '<input id="w-foo" name="foo" type="text">'
        self.assertRaises(fe.Invalid, t.to_python, 'asdf', None)
        self.assertRaises(fe.Invalid, t.to_python, 'asdf@bar', None)
        self.assertRaises(fe.Invalid, t.to_python, 'asdf@bar@bar.com', None)
        t.to_python('foo@bar.com', None)
        
    def test_int_field(self):
        t = self.ew.IntField(id="w-foo", name='foo')
        assert t.display() == '<input id="w-foo" name="foo" type="text">'
        self.assertRaises(fe.Invalid, t.to_python, 'asdf', None)
        self.assertRaises(fe.Invalid, t.to_python, '42.5', None)
        assert 42 == t.to_python('42', None)
        
    def test_date_field(self):
        t = self.ew.DateField(id="w-foo", name='foo')
        text = t.display()
        assert soup(text) == soup('<input id="w-foo" name="foo" type="text" style="width:6em">'), text
        self.assertRaises(fe.Invalid, t.to_python, 'asdf', None)
        self.assertRaises(fe.Invalid, t.to_python, '1990.01.32', None)
        assert date(1990, 1, 1) == t.to_python('01/01/1990', None)

    def test_time_field(self):
        t = self.ew.TimeField(id="w-foo", name='foo')
        text = t.display()
        assert soup(text) == soup('<input id="w-foo" name="foo" style="width:5em" type="text">'), soup(text)
        self.assertRaises(fe.Invalid, t.to_python, 'asdf', None)
        self.assertRaises(fe.Invalid, t.to_python, '01:67', None)
        assert time(1,34) == t.to_python('1:34', None)
        assert time(13,34) == t.to_python('1:34 pm', None)

    def test_textarea(self):
        t = self.ew.TextArea(id="w-foo", name='foo', value="<script/>")
        text = t.display()
        assert text == '<textarea id="w-foo" name="foo">&lt;script/&gt;</textarea>', text

    def test_checkbox(self):
        t = self.ew.Checkbox(id="w-foo", name='foo')
        text = t.display()
        assert text.startswith('<input'), text
        assert 'type="checkbox"' in text, text
        assert 'name="foo"' in text, text
        assert '<label for="w-foo">Foo</label>' in text, text
        text = t.display(value=True)
        assert 'type="checkbox"' in text, text
        assert 'checked' in text, text

    def test_submit_button(self):
        t = self.ew.SubmitButton(name='foo')
        text = t.display()
        assert (soup(text)==soup('<input name="foo" '
                'value="Foo" type="submit" class="submit">')), soup(text)
        text = t.display(label='Bar')
        assert (soup(text)==soup('<input name="foo" '
                'value="Bar" type="submit" class="submit">')), text

class _TestSelectFields(TestCase):

    def test_single_select(self):
        for optlist in [
            'abc',
            lambda:'abc',
            [self.ew.Option(label='A', html_value='a'),
             self.ew.Option(label='B', html_value='b'),
             self.ew.Option(label='C', html_value='c') ]
            ]:
            t = self.ew.SingleSelectField(id="foo", name='foo', options=optlist)
            text = t.display()
            assert '<select id="foo" name="foo">' in text, text
            assert '<option value="a">' in text, text
            assert '<option value="b">' in text, text
            assert '<option value="c">' in text, text
            text = t.display(value="b")
            assert '<option value="a">' in text, text
            assert '<option selected value="b">' in text, text
            assert '<option value="c">' in text, text

    def test_select_escaping(self):
        o = self.ew.Option(label='<script>alert(1)</script>', html_value='b')
        text = o.display()
        assert '<option value="b">' in text, text
        assert '&lt;script&gt;alert(1)&lt;/script&gt;' in text, text


    def test_multi_select(self):
        for optlist in [
            'abc',
            lambda:'abc',
            [self.ew.Option(label='A', html_value='a'),
             self.ew.Option(label='B', html_value='b'),
             self.ew.Option(label='C', html_value='c') ]
            ]:
            t = self.ew.MultiSelectField(id="foo", name='foo', options=optlist)
            text = t.display()
            assert '<select id="foo" multiple name="foo">' in text, text
            assert '<option value="a">' in text, text
            assert '<option value="b">' in text, text
            assert '<option value="c">' in text, text
            text = t.display(value=["b","c"])
            assert '<option value="a">' in text, text
            assert '<option selected value="b">' in text, text
            assert '<option selected value="c">' in text, text

    def test_checkbox_set(self):
        for optlist in [
            'abc',
            lambda:'abc',
            [self.ew.Option(label='A', html_value='a'),
             self.ew.Option(label='B', html_value='b'),
             self.ew.Option(label='C', html_value='c') ]
            ]:
            t = self.ew.CheckboxSet(name='foo', options=optlist)
            text = t.display()
            assert '<fieldset' in text, text
            assert '<legend>Foo</legend>' in text, text
            assert '<input name="foo" type="checkbox" value="a">' in text, text
            assert '<input name="foo" type="checkbox" value="b">' in text, text
            assert '<input name="foo" type="checkbox" value="c">' in text, text
            text = t.display(value=["b","c"])
            assert '<input name="foo" type="checkbox" value="a">' in text, text
            assert '<input checked name="foo" type="checkbox" value="b">' in text, text
            assert '<input checked name="foo" type="checkbox" value="c">' in text, text

class _TestForms(TestCase):

    def setUp(self):
        super(_TestForms, self).setUp()
        self.w = self.ew.SimpleForm(
            id="w-foo",
            fields=[
                self.ew.InputField(
                    name='foo',
                    validator=fev.UnicodeString(min=2)),
                self.ew.InputField(
                    name='bar',
                    validator=fev.UnicodeString(min=2)),
                ])

    def test_display(self):
        text = self.w.display()
        assert '<label for="w-foo.foo"' in text
        assert '<input id="w-foo.foo" name="foo"' in text
        text = self.w.display(value=dict(foo='bar', bar='baz'))
        assert '<label for="w-foo.foo"' in text
        assert '<input id="w-foo.foo" name="foo" value="bar"' in text
        assert '<label for="w-foo.bar"' in text
        assert '<input id="w-foo.bar" name="bar" value="baz"' in text

    def test_validation(self):
        self.assertRaises(fe.Invalid, self.w.to_python, dict(foo='x', bar='xxy'), None)
        assert isinstance(ew.widget_context.validation_error, fe.Invalid)
        text = self.w.display()
        assert '<label for="w-foo.foo"' in text, text
        assert '<span class="fielderror">Enter' in text, text
        assert '<input id="w-foo.foo" name="foo" value="x"' in text
        assert '<input id="w-foo.bar" name="bar" value="xxy"' in text

class TestFieldSetJinja2(_TestFieldSet): ew=ew.jinja2_ew
class TestRowFieldJinja2(_TestRowField): ew=ew.jinja2_ew
class TestRepeatedFieldJinja2(_TestRepeatedField): ew=ew.jinja2_ew
class TestTableFieldJinja2(_TestTableField): ew=ew.jinja2_ew
class TestInputFieldsJinja2(_TestInputFields): ew=ew.jinja2_ew
class TestSelectFieldsJinja2(_TestSelectFields): ew=ew.jinja2_ew
class TestFormsJinja2(_TestForms): ew=ew.jinja2_ew

class TestFieldsJinja2(_TestFields):
    ew=ew.jinja2_ew

    def test_link_field(self):
        text = self.ew.LinkField().display(value='/foo/5/')
        self.assertEqual('<a href="/foo/5/">/foo/5/</a>', text)

        expected = '<a href="/foo">bar</a>'
        self.assertEqual(expected, self.ew.LinkField(href='/foo').display(value='bar'))
        self.assertEqual(expected, self.ew.LinkField(text='bar').display(value='/foo'))
        self.assertEqual(expected, self.ew.LinkField().display(value=dict(href='/foo', text='bar')))
        self.assertEqual(expected, self.ew.LinkField(label='bar').display(value=dict(href='/foo')))
        self.assertEqual(expected, self.ew.LinkField(href='/foo').display(value=dict(text='bar')))
        self.assertEqual(expected, self.ew.LinkField(attrs={'href':'/foo'}).display(value='bar'))
        self.assertEqual(expected, self.ew.LinkField(plaintext_if_no_href=True).display(value=dict(href='/foo', text='bar')))
        self.assertEqual(expected, self.ew.LinkField(plaintext_if_no_href=True).display(href='/foo', value='bar'))

    def test_link_plaintext(self):
        expected = 'bar'
        self.assertEqual(expected, self.ew.LinkField(plaintext_if_no_href=True).display(value=dict(text='bar')))
        self.assertEqual(expected, self.ew.LinkField(plaintext_if_no_href=True, label='bar').display(value=dict()))
        self.assertEqual(expected, self.ew.LinkField(plaintext_if_no_href=True, label='foo').display(value='bar'))

    def test_link_escaping(self):
        text = '<script>alert("foo")</script>'
        href = '" onclick="alert(\'foo\')'
        expected = '<a >&lt;script&gt;alert(&#34;foo&#34;)&lt;/script&gt;</a>'
        self.assertEqual(expected, self.ew.LinkField().display(text=text))
        self.assertEqual(expected, self.ew.LinkField().display(text=text, value={}))
        self.assertEqual(expected, self.ew.LinkField().display(label=text))
        self.assertEqual(expected, self.ew.LinkField().display(label=text, value={}))
        self.assertEqual(expected, self.ew.LinkField().display(value={'text':text}))
        self.assertEqual(expected, self.ew.LinkField(text=text).display())
        self.assertEqual(expected, self.ew.LinkField(text=text).display(value={}))
        self.assertEqual(expected, self.ew.LinkField(label=text).display())
        self.assertEqual(expected, self.ew.LinkField(label=text).display(value={}))
        self.assertEqual(expected, self.ew.LinkField(value={'text':text}).display())
        expected = '<a href="&lt;script&gt;alert(&#34;foo&#34;)&lt;/script&gt;">&lt;script&gt;alert(&#34;foo&#34;)&lt;/script&gt;</a>'
        self.assertEqual(expected, self.ew.LinkField().display(value=text))
        self.assertEqual(expected, self.ew.LinkField(value=text).display())
        expected = '<a href="&#34; onclick=&#34;alert(&#39;foo&#39;)">None</a>'
        self.assertEqual(expected, self.ew.LinkField().display(href=href))
        self.assertEqual(expected, self.ew.LinkField().display(href=href, value={}))
        self.assertEqual(expected, self.ew.LinkField().display(attrs={'href':href}))
        self.assertEqual(expected, self.ew.LinkField().display(attrs={'href':href}, value={}))
        self.assertEqual(expected, self.ew.LinkField().display(value={'href':href}))
        self.assertEqual(expected, self.ew.LinkField(href=href).display())
        self.assertEqual(expected, self.ew.LinkField(href=href).display(value={}))
        self.assertEqual(expected, self.ew.LinkField(attrs={'href':href}).display())
        self.assertEqual(expected, self.ew.LinkField(attrs={'href':href}).display(value={}))
        self.assertEqual(expected, self.ew.LinkField(value={'href':href}).display())
        expected = '&lt;script&gt;alert(&#34;foo&#34;)&lt;/script&gt;'
        self.assertEqual(expected, self.ew.LinkField(plaintext_if_no_href=True).display(text=text))
        self.assertEqual(expected, self.ew.LinkField(plaintext_if_no_href=True).display(label=text))
        self.assertEqual(expected, self.ew.LinkField(plaintext_if_no_href=True).display(value=text))
        self.assertEqual(expected, self.ew.LinkField(plaintext_if_no_href=True).display(value={'text':text}))
        self.assertEqual(expected, self.ew.LinkField(plaintext_if_no_href=True, label=text).display())
        self.assertEqual(expected, self.ew.LinkField(plaintext_if_no_href=True, text=text).display())
        self.assertEqual(expected, self.ew.LinkField(plaintext_if_no_href=True, value=text).display())
        self.assertEqual(expected, self.ew.LinkField(plaintext_if_no_href=True, value={'text':text}).display())
