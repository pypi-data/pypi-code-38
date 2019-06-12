# -*- coding: utf-8 -*-

'''
Created on 2017-6-22
@author: linkeddt.com
'''

from __future__ import unicode_literals

import json
from datetime import datetime

from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.forms import widgets


__all__ = (
    'UploadFile', 'TreeView', 'QuickDateSelector', 'QuickDateSelectorField',
    'CoordinateSelector', 'CoordinateSelectorField', 'SelectInput', 'UEditor',
    'SLView',
)


class UploadFile(forms.Widget):

    def __init__(self, attrs=None):
        super(UploadFile, self).__init__(attrs)

    def render(self, name, values, attrs=None):
        output = [u'<div>']
        try:
            data = json.loads(values)
        except Exception:
            data = {'flag': 'edit' if values else 'add', 'filename': values}
        accept = self.attrs.get('accept', '*')

        if data['flag'] == 'add':
            output.append(format_html(
                u'<input id="{0}_file" type="file" name="{1}_file" accept="{2}" onchange="return UploadFile.change(this)"/>', attrs['id'], name, accept))
            output.append(
                format_html(u'<input id="{0}" type="hidden" name="{1}" />', attrs['id'], name))
        else:
            output.append(format_html(
                u'<input id="{0}_file" type="file" name="{1}_file" accept="{2}" onchange="return UploadFile.change(this)" style="display:none;"/>', attrs['id'], name, accept))
            output.append(format_html(
                u'<p class="file-item"><span>{1}</span><a class="icon-del" href="#" onclick="javascript:UploadFile.del(this)">删除</a></p>', "#", data['filename']))
            output.append(format_html(
                u'<input id="{0}" type="hidden" name="{1}" value="{2}" />', attrs['id'], name, json.dumps(data)))
        output.append(u'</div>')
        return mark_safe(u''.join(output))


class TreeView(forms.Widget):

    def __init__(self, attrs=None):
        super(TreeView, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        field_id = attrs.get('id')
        tree_id = '%s_tree' % field_id

        output.append(u'<ul id="%s"></ul>' % tree_id)
        output.append(u'<input type="hidden" id="%s" value="%s" name="%s">' % (
            field_id, value, name))
        return mark_safe(u''.join(output))


class QuickDateSelector(widgets.MultiWidget):
    """
    https://docs.djangoproject.com/en/1.7/ref/forms/widgets/#django.forms.MultiWidget
    """
    defdata = ()

    def __init__(self, attrs=None):
        _widgets = (
            widgets.TextInput(attrs={'name': 'begin', 'class': 'form_text from_datetime', 'onClick':
                                     'WdatePicker({onpicked:quickDateSelector.datePicked, dateFmt:"yyyy-MM-dd HH"})'}),
            widgets.TextInput(attrs={'name': 'end', 'class': 'form_text from_datetime', 'onClick':
                                     'WdatePicker({onpicked:quickDateSelector.datePicked, dateFmt:"yyyy-MM-dd HH"})'}),
        )
        super(QuickDateSelector, self).__init__(_widgets, attrs)

    def decompress(self, value):
        return value
        if value:
            return value.split(',')
        return [None, None]

    def render(self, name, value, attrs=None):
        if value == [None, None] or value == [u'', u'']:
            value = self.defdata

        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized

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
                final_attrs = dict(final_attrs, id='%s_%s' %
                                   (id_, widget.attrs.get('name', i)))
                final_attrs.update({'aria-labelledby': name})

            output.append(widget.render(
                name + '_%s' % widget.attrs.get('name', i), widget_value, final_attrs))
        return mark_safe(self.format_output(name, output, value))

    def format_output(self, name, rendered_widgets, value):
        output = []
        output.append(format_html(
            '<div id="{0}" class="dropdown quickDateSelector">', name))
        output.append(format_html(
            '<div class="input-group" id="{0}Label" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">', name))
        output.append(format_html(
            '<input type="text" readonly="readonly" id="id_{1}_begin_read" class="form-control input-sm" value="{0}" style="width:100px;">', value[0], name))
        output.append(
            '<span class="input-group-addon">至</span>')
        output.append(format_html(
            '<input type="text" readonly="readonly" id="id_{1}_end_read" class="form-control input-sm" value="{0}" style="width:100px;">', value[1], name))
        output.append('</div>')

        output.append(
            format_html('<div class="{0}" aria-labelledby="{1}Label">', "dropdown-menu", name))
        output.append(format_html('<p>开始时间：{0}</p>', rendered_widgets[0]))
        output.append(format_html('<p>结束时间：{0}</p>', rendered_widgets[1]))
        output.append(format_html('<p>快捷选择</p>'))
        output.append(format_html('<div><ul class="quick-list clearfix">'))
        output.append(format_html(
            '<li><a href="javascript:void(0)" aria-labelledby="{0}" onClick="quickDateSelector.quickChangDate(this, 1)">今天</a></li>', name))
        output.append(format_html(
            '<li><a href="javascript:void(0)" aria-labelledby="{0}" onClick="quickDateSelector.quickChangDate(this, 2)">昨天</a></li>', name))
        output.append(format_html(
            '<li><a href="javascript:void(0)" aria-labelledby="{0}" onClick="quickDateSelector.quickChangDate(this, 3)">最近7天</a></li>', name))
        output.append(format_html(
            '<li><a href="javascript:void(0)" aria-labelledby="{0}" onClick="quickDateSelector.quickChangDate(this, 4)">上周</a></li>', name))
        output.append(format_html(
            '<li><a href="javascript:void(0)" aria-labelledby="{0}" onClick="quickDateSelector.quickChangDate(this, 5)">最近15天</a></li>', name))
        output.append(format_html(
            '<li><a href="javascript:void(0)" aria-labelledby="{0}" onClick="quickDateSelector.quickChangDate(this, 6)">本月</a></li>', name))
        output.append(format_html(
            '<li><a href="javascript:void(0)" aria-labelledby="{0}" onClick="quickDateSelector.quickChangDate(this, 7)">最近30天</a></li>', name))
        output.append(format_html(
            '<li><a href="javascript:void(0)" aria-labelledby="{0}" onClick="quickDateSelector.quickChangDate(this, 8)">上月</a></li>', name))
        output.append(format_html(u'</ul></div>'))
        output.append(format_html(u'</div>'))
        output.append(format_html(u'</div>'))
        return ''.join(output)

    def value_from_datadict(self, data, files, name):
        datelist = [
            widget.value_from_datadict(
                data, files, name + '_%s' % widget.attrs.get('name', i))
            for i, widget in enumerate(self.widgets)]

        lst = []
        if isinstance(datelist[0], datetime):
            lst.append(datetime.strftime(datelist[0], '%Y-%m-%d %H'))
        elif datelist[0] == '' or datelist[0] is None:
            lst.append(datetime.strftime(datetime.now(), '%Y-%m-%d %H'))
        else:
            lst.append(datelist[0])

        if isinstance(datelist[1], datetime):
            lst.append(datetime.strftime(datelist[1], '%Y-%m-%d %H'))
        elif datelist[1] == '' or datelist[1] is None:
            lst.append(datetime.strftime(datetime.now(), '%Y-%m-%d %H'))
        else:
            lst.append(datelist[1])
        return lst


class QuickDateSelectorField(forms.MultiValueField):
    widget = QuickDateSelector()

    def __init__(self, *args, **kwargs):
        fields = (
            forms.CharField(required=False),
            forms.CharField(required=False),
        )
        super(QuickDateSelectorField, self).__init__(fields, *args, **kwargs)

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        self._choices = self.widget.defdata = list([datetime.strftime(
            value[0], '%Y-%m-%d %H'), datetime.strftime(value[1], '%Y-%m-%d %H')])
    choices = property(_get_choices, _set_choices)

    def compress(self, data_list):
        if data_list:
            return datetime.strptime(data_list[0], '%Y-%m-%d %H'), datetime.strptime(data_list[1], '%Y-%m-%d %H')
        return None


class CoordinateSelector(widgets.MultiWidget):
    """
    https://docs.djangoproject.com/en/1.7/ref/forms/widgets/#django.forms.MultiWidget
    """
    defdata = ()

    def __init__(self, attrs=None):
        _widgets = (
            widgets.TextInput(attrs={'name': 'x', 'class': 'txt_coordinste'}),
            widgets.TextInput(attrs={'name': 'y', 'class': 'txt_coordinste'}),
        )
        super(CoordinateSelector, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split(',')
        return [None, None]

    def render(self, name, value, attrs=None):
        if value == [None, None] or value == [u'', u'']:
            value = self.defdata

        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized

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
                final_attrs = dict(final_attrs, id='%s_%s' %
                                   (id_, widget.attrs.get('name', i)))
            output.append(widget.render(
                name + '_%s' % widget.attrs.get('name', i), widget_value, final_attrs))
        return mark_safe(self.format_output(output, value))

    def format_output(self, rendered_widgets, value):
        output = []
        #output.append(format_html(u'<p>寮�濮嬫椂闂达細{0}</p>', rendered_widgets[0]))
        #output.append(format_html(u'<p>缁撴潫鏃堕棿锛歿0}</p>', rendered_widgets[1]))
        output.append(rendered_widgets[0])
        output.append(u" - ")
        output.append(rendered_widgets[1])
        output.append(format_html(
            u'<a href="javascript:void(0)" onclick="mapCoordinate()"><img alt="" src="/static/baseframe/img/icon/icon-map.png" title="瀹氫綅"/></a>'))
        return u''.join(output)

    def value_from_datadict(self, data, files, name):
        datelist = [
            widget.value_from_datadict(
                data, files, name + '_%s' % widget.attrs.get('name', i))
            for i, widget in enumerate(self.widgets)]
        return datelist


class CoordinateSelectorField(forms.MultiValueField):
    widget = CoordinateSelector()

    def __init__(self, *args, **kwargs):
        fields = (
            forms.DecimalField(max_digits=10, decimal_places=6, required=True),
            forms.DecimalField(max_digits=10, decimal_places=6, required=True),
        )
        super(CoordinateSelectorField, self).__init__(fields, *args, **kwargs)

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        self._choices = self.widget.defdata = list(value[0], value[1])
    choices = property(_get_choices, _set_choices)

    def compress(self, data_list):
        return data_list


class SelectInput(forms.Widget):

    def __init__(self, attrs=None):
        super(SelectInput, self).__init__(attrs)

    def render(self, name, values, attrs=None):
        output = []
        str_code = json.dumps(values)
        str_text = values.get('t', '')

        output.append(format_html(
            u'<input id="{0}" type="text" value="{1}" readonly="readonly"/>', attrs.get('id'), str_text))
        output.append(format_html(
            u'<a href="javascript:void(0)" onclick="open_{0}()"><img alt="" src="/static/baseframe/img/icon/icon-search.png"/></a>', name))
        output.append(format_html(
            u'<input type="hidden" value="{0}" name="{1}" id="{2}_hdn">', str_code, name, attrs.get('id')))
        return mark_safe(u''.join(output))


class UEditor(forms.Textarea):

    class Media:
        js = (
            '/static/ueditor/ueditor.config.js',
            '/static/ueditor/ueditor.all.min.js',
        )

    def __init__(self, attrs={'id': 'myEditor'}):
        super(UEditor, self).__init__(attrs)

    """
    def render(self, name, value, attrs=None):
        output = [super(UEditor, self).render('', '', attrs)]
        output.append(str(self.media))
        output.append(u'<script type="text/javascript">')
        output.append(u'var editor = new UE.ui.Editor();')
        output.append(u'editor.initialFrameWidth = 600;')
        output.append(u'editor.initialFrameHeight = 200;')
        output.append(u'</script>')
        return mark_safe(u''.join(output))
    """


class SLView(forms.Widget):

    def __init__(self, attrs=None):
        super(SLView, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        output.append(u'<div id="silverlightControlHost" class="slWrapper">')
        output.append(
            u'<object id="SLObject" data="data:application/x-silverlight-2," type="application/x-silverlight-2" width="100%" height="100%">')
        output.append(u'<param name="source" value="%s"/>' %
                      self.attrs.get('source'))
        output.append(u'<param name="initParams" value="%s"/>' %
                      self.attrs.get('initParams'))
        output.append(u'<param name="background" value="white" />')
        output.append(
            u'<param name="minRuntimeVersion" value="5.0.61118.0" />')
        output.append(u'<param name="autoUpgrade" value="true" />')
        output.append(u'<param name="windowless" value="true"/>')
        output.append(
            u'<a href="http://go.microsoft.com/fwlink/?LinkID=149156&v=5.0.61118.0" style="text-decoration:none"><img src="http://go.microsoft.com/fwlink/?LinkId=161376" alt="Get Microsoft Silverlight" style="border-style:none"/></a>')
        output.append(
            u'</object><iframe id="_sl_historyFrame" style="visibility:hidden;height:0px;width:0px;border:0px"></iframe>')
        output.append(u'</div>')
        return mark_safe(u''.join(output))
