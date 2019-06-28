# -*- coding: utf-8 -*-
from crispy_forms.layout import LayoutObject, HTML, Layout, Div, Field, Fieldset, Row
from crispy_forms.utils import TEMPLATE_PACK
from django.template.loader import get_template
from django.utils.html import conditional_escape

# layout de endereço padrão para a aplicação
layout_endereco = Layout(
    Div(
        Row(
            Div(Field('cep', data_ftl="cep"), css_class='col-md-3'),
            Div(css_class='col-md-8'),
        ),
        Row(
            Div('endereco', css_class='col-md-8'),
            Div(css_class='col-md-1'),
            Div('enderecoNumero', css_class='col-md-2'),
        ),
        Row(
            Div('complemento', css_class='col-md-11'),
        ),
        Row(
            Div('bairro', 'estado', css_class='col-md-5'),
            Div(css_class='col-md-1'),
            Div('municipio', css_class='col-md-5'),
        ),
    ),
)

# layout de log de usuário para a aplicação
layout_logusuario = Layout(
    Row(
        Fieldset('Log',
                 Row(
                     Div(Field('created_by', readonly=True, extra_context='disabled'), css_class='col-sm-2'),
                     Div(css_class='col-xs-1'),
                     Div(Field('created_at', readonly=True), css_class='col-sm-2'),
                     Div(css_class='col-xs-1'),
                     Div(Field('modified_by', readonly=True, extra_context='disabled'), css_class='col-sm-2'),
                     Div(css_class='col-xs-1'),
                     Div(Field('modified_at', readonly=True), css_class='col-sm-2 nowrap'),
                 ),
                 disabled='disabled',
                 # css_class='col-md-11',
                 ),
        # css_class='row',
    ),
)

glyphicon_calendar = '<span class=\"glyphicon glyphicon-calendar\"></span>'


def Label(label, first=False):
    """
        LabelFirstDetail: Usado nos forms estilo master/detail para colocar título do campo do detail
        somente no primeiro registro dos detalhes
        Não sei porque cargas d'água isso não funciona quando está em REST, só quando está direto.
        Exemplo: os Municípios do Estado não funcionam direito.
        Marretada: passando um array xpto [1,2], forçar um for para a first ficar false e só gerar o detail template
        no segundo item do array.
        Horrível.
    """
    return HTML("%s%s%s" % (
        "<label class=\"control-label " + ("ftl-inlines-first-only" if first else "") + "\">", label, "</label>"))


def LabelFirstDetail(label):
    """
        LabelFirstDetail: Usado nos forms estilo master/detail para colocar título do campo do detail
        somente no primeiro registro dos detalhes
        Não sei porque cargas d'água is
        so não funciona quando está em REST, só quando está direto.
        Exemplo: os Municípios do Estado não funcionam direito.
        Marretada: passando um array xpto [1,2], forçar um for para a first ficar false e só gerar o detail template
        no segundo item do array.
        Horrível.
    """
    return HTML("%s%s%s" % ("{% if forloop.first %}<label class=\"control-label\">", label, "</label>{% endif %}"))


def Tree(idTree="masterTreeManager", idModal="ftl-form-modal"):
    """
        LabelFirstDetail: Usado nos forms estilo master/detail para colocar título do campo do detail
        somente no primeiro registro dos detalhes
        Não sei porque cargas d'água is
        so não funciona quando está em REST, só quando está direto.
        Exemplo: os Municípios do Estado não funcionam direito.
        Marretada: passando um array xpto [1,2], forçar um for para a first ficar false e só gerar o detail template
        no segundo item do array.
        Horrível.
    """
    return HTML('<div id="{0}"></div><div id="{1}"></div>'.format(idTree, idModal))


class M2MSetField(LayoutObject):
    """
    Usado para listar num formato table relações M2M, como por exemplo listar o conjunto de contratos de administração
    ou de locação de um imóvel.

    Layout object: It contains one field name, and you can add attributes to it easily.
    For setting class attributes, you need to use `css_class`, as `class` is a Python keyword.

    """
    template = "table-widget.html"

    def __init__(self, *args, **kwargs):
        self.fields = list(args)

        if not hasattr(self, 'attrs'):
            self.attrs = {}

        if 'css_class' in kwargs:
            if 'class' in self.attrs:
                self.attrs['class'] += " %s" % kwargs.pop('css_class')
            else:
                self.attrs['class'] = kwargs.pop('css_class')

        self.wrapper_class = kwargs.pop('wrapper_class', None)
        self.template = kwargs.pop('template', self.template)
        self.table_form = kwargs.pop('table_form', None)  # ContratoAdmImovelTable / ContratoLocImovelTable
        self.m2m = kwargs.pop('m2m', None)  # imoveis

        # We use kwargs as HTML attributes, turning data_id='test' into data-id='test'
        self.attrs.update(dict([(k.replace('_', '-'), conditional_escape(v)) for k, v in kwargs.items()]))

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, extra_context=None, **kwargs):
        if extra_context is None:
            extra_context = {}
        if hasattr(self, 'wrapper_class'):
            extra_context['wrapper_class'] = self.wrapper_class

        template = get_template(self.get_template_name(template_pack))

        if form.instance.pk is not None:
            queryset = getattr(form.instance, self.fields[0]).all()
            if len(self.table_form.opts.sort) > 0:
                ordem = [(('-' if des == 'desc' else '') + self.table_form.base_columns[i].field) for (i, des) in
                         self.table_form.opts.sort]
                queryset = queryset.order_by(*ordem)
        else:
            queryset = form.instance._meta.model.objects.none()

        # request = context['request']

        objetos = self.table_form(queryset)
        context.update({'objetos': objetos})
        # ctx = {k: v for d in context for k, v in d.items() if d}
        ctx = context.flatten()

        html = template.render(ctx)

        return html
