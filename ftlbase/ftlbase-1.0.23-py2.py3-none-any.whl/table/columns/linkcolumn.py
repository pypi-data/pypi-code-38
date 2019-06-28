#!/usr/bin/env python
# coding: utf-8
from django.template import Template, Context
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

from common.middleware import get_current_request
from table.columns.base import Column
from table.utils import Accessor

ACAO_ADD = '1'
ACAO_EDIT = '2'
ACAO_DELETE = '3'
ACAO_VIEW = '4'
ACAO_REPORT = '5'


def commonPermission(request, clsModel, acao, permission, raise_exception=True):
    from django.contrib.contenttypes.models import ContentType
    from django.core.exceptions import PermissionDenied

    # login_required()

    if not request.user.is_authenticated:
        if raise_exception:
            raise PermissionDenied
        return False

    if permission:
        perm = permission
    else:
        perm = ''
        if acao == ACAO_ADD:
            perm = 'add'
        elif acao == ACAO_EDIT:
            perm = 'change'
        elif acao == ACAO_DELETE:
            perm = 'delete'
        # elif acao == ACAO_VIEW:
        else:
            perm = 'view'
        content_type = ContentType.objects.get_for_model(clsModel)
        # a.has_perm(content_type.app_label+'.add_'+content_type.model)
        perm = '{}.{}_{}'.format(content_type.app_label, perm, content_type.model)
    # print('permission=', permission, 'perm=', perm)
    # print('user=', request.user, 'has=', request.user.has_perm(perm), 'perm_recq=',vars(a))
    if (not request.user.is_authenticated) or (not request.user.has_perm(perm)):
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return True


class LinkColumn(Column):
    def __init__(self, header=None, links=None, delimiter='&nbsp', field=None, **kwargs):
        self.links = links
        self.delimiter = delimiter
        kwargs['safe'] = False
        super(LinkColumn, self).__init__(field, header, **kwargs)

    def render(self, obj):
        return self.delimiter.join([link.render(obj) for link in self.links])


class Link(object):
    """
    Represents a html <a> tag.
    """

    def __init__(self, text=None, viewname=None, args=None, kwargs=None, urlconf=None,
                 current_app=None, attrs=None, permission=None, acao=None, ajax=True, new_window=False):
        self.basetext = text
        self.viewname = viewname
        self.args = args or []
        self.kwargs = kwargs or {}
        self.urlconf = urlconf
        self.current_app = current_app
        self.base_attrs = attrs or {}
        self.permission = permission
        self.acao = acao
        self.ajax = ajax
        self.new_window = new_window
        self.obj = None

    @property
    def text(self):
        if isinstance(self.basetext, Accessor):
            basetext = self.basetext.resolve(self.obj)
        else:
            basetext = self.basetext
        return escape(basetext)

    @property
    def url(self):
        if self.viewname is None:
            return ""

        # The following params + if statements create optional arguments to
        # pass to Django's reverse() function.
        params = {}
        if self.args:
            params['args'] = [arg.resolve(self.obj)
                              if isinstance(arg, Accessor) else arg
                              for arg in self.args]
        if self.kwargs:
            params['kwargs'] = {}
            for key, value in self.kwargs.items():
                params['kwargs'][key] = (value.resolve(self.obj)
                                         if isinstance(value, Accessor) else value)
        if self.urlconf:
            params['urlconf'] = (self.urlconf.resolve(self.obj)
                                 if isinstance(self.urlconf, Accessor)
                                 else self.urlconf)
        if self.current_app:
            params['current_app'] = (self.current_app.resolve(self.obj)
                                     if isinstance(self.current_app, Accessor)
                                     else self.current_app)

        return reverse(self.viewname, **params)

    @property
    def attrs(self):
        if self.url:
            self.base_attrs["href"] = self.url
        return self.base_attrs

    def render(self, obj):
        """ Render link as HTML output tag <a>.
        """
        try:
            self.obj = obj
            base = '%s="#%s"' if self.ajax else '%s="%s"'
            attrs = ' '.join([
                base % (attr_name, attr.resolve(obj)) if isinstance(attr, Accessor) \
                    else base % (attr_name, attr) for attr_name, attr in self.attrs.items()
            ])
            if self.permission or self.acao:
                if not commonPermission(get_current_request(), self.obj.__class__, self.acao, permission=self.permission,
                                        raise_exception=False):
                    return mark_safe(u'')  # se não tem permissão então não gera o link
            new_window = 'target="_blank"' if self.new_window else ''
            return mark_safe('<a {0} {1}>{2}</a>'.format(attrs, new_window, self.text))
        except:
            return mark_safe('')


class ImageLink(Link):
    """
    Represents a html <a> tag that contains <img>.
    """

    def __init__(self, image, image_title, *args, **kwargs):
        self.image_path = image
        self.image_title = image_title
        super(ImageLink, self).__init__(*args, **kwargs)

    @property
    def image(self):
        path = self.image_path
        if isinstance(self.image_title, Accessor):
            title = self.image_title.resolve(self.obj)
        else:
            title = self.image_title
        template = Template('{%% load static %%}<img src="{%% static "%s" %%}"'
                            ' title="%s">' % (path, title))
        return template.render(Context())

    @property
    def text(self):
        return self.image


class GlyphiconSpanLink(Link):
    """
    Represents a html <a> tag that contains <span> of Glyphicon.
    """
    span_text = None

    def __init__(self, span_text=None, *args, **kwargs):
        self.span_text = kwargs.pop('span_text', None)
        super(GlyphiconSpanLink, self).__init__(*args, **kwargs)

    @property
    def glyphiconSpan(self):
        # template = Template(self.span_text)
        template = Template('<span class="glyphicon glyphicon-%s" aria-hidden="true"></span>' % self.span_text)
        # template = Template('{%% load static %%}<img src="{%% static "%s" %%}"'
        #                    ' title="%s">' % (path, title))
        return template.render(Context())

    @property
    def text(self):
        return self.glyphiconSpan


class FontAwesomeLink(Link):
    """
    Represents a html <a> tag that contains <span> of FontAwesome.
    """
    span_text = None

    # def __init__(self, span_text=None, span_tip=None, *args, **kwargs):
    def __init__(self, *args, **kwargs):
        self.span_text = kwargs.pop('span_text', None)
        self.span_tip = kwargs.pop('span_tip', None)
        super(FontAwesomeLink, self).__init__(*args, **kwargs)

    @property
    def fontAwesome(self):
        template = Template(
            '<i class="fa fa-%s" style="font-size:18px;color:#09568d;" data-toggle="tooltip" title="%s"></i>' % (
                self.span_text, self.span_tip))
        return template.render(Context())

    @property
    def text(self):
        return self.fontAwesome


def ActionColumn(vieweditdelete, chave, can_delete=True, can_edit=True, can_view=False, can_drill_down=False,
                 can_workflow=False, report=False, ajax=True, new_window=False):
    links = []
    # print(vieweditdelete)

    if can_edit:
        links += [FontAwesomeLink(text=u'Editar', viewname=vieweditdelete, args=(Accessor(chave), ACAO_EDIT,),
                                  span_text='pencil-alt', span_tip='Editar', acao=ACAO_EDIT, ajax=ajax), ]
    if can_delete:
        links += [FontAwesomeLink(text=u'Excluir', viewname=vieweditdelete, args=(Accessor(chave), ACAO_DELETE,),
                                  span_text='trash-alt', span_tip='Excluir', acao=ACAO_DELETE, ajax=ajax), ]
    if can_view:
        links += [FontAwesomeLink(text=u'Consultar', viewname=vieweditdelete, args=(Accessor(chave), ACAO_VIEW,),
                                  span_text='eye', span_tip='Consultar', acao=ACAO_VIEW, ajax=ajax), ]
    if can_workflow:
        links += [FontAwesomeLink(text=u'Consultar', viewname=vieweditdelete, args=(Accessor(chave),),
                                  span_text='eye', span_tip='Consultar', acao=ACAO_VIEW, ajax=ajax), ]
    if can_drill_down:
        links += [FontAwesomeLink(text=u'Drill Down', viewname=vieweditdelete, args=(Accessor(chave), ACAO_VIEW,),
                                  span_text='level-down',
                                  span_tip='Drill Down - Aperte Ctrl+Left Mouse Click para abrir em outra aba',
                                  acao=ACAO_VIEW, ajax=ajax), ]  # pencil-square
    if report:
        links += [FontAwesomeLink(text=u'Imprimir', viewname=vieweditdelete, args=(Accessor(chave),),
                                  span_text='print', span_tip='Imprimir', ajax=ajax, new_window=new_window), ]

    return LinkColumn(header=u'Ação', links=links, searchable=False, sortable=False)
