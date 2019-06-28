# -*- coding: utf-8 -*-

from crispy_forms.bootstrap import InlineField, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from dal.forms import FutureModelForm
# Configurações globais de novos templates para Crispy Forms
# Ver http://django-crispy-forms.readthedocs.io/en/latest/layouts.html#overriding-layout-objects-templates
from django import forms
from django.urls import reverse_lazy

from goflow.runtime.models import WorkItem
from table import Table
from table.columns import DatetimeColumn, Column

InlineField.template = 'common/inline_field_common.html'

formatoNumero = """ function ( data, type, full, meta ) { return accounting.formatMoney(accounting.unformat(data, ","), {symbol: "", precision: 2, decimal : ",", thousand: ".", format: {pos : "%v", neg : "(%v)", zero: "--"} }); }"""  # NOQA
formatoNumeroPonto = """ function ( data, type, full, meta ) { return accounting.formatMoney(accounting.unformat(data, "."), {symbol: "", precision: 2, decimal : ",", thousand: ".", format: {pos : "%v", neg : "(%v)", zero: "--"} }); }"""  # NOQA
formatoNumeroZero6 = """ function ( data, type, full, meta ) {return parseInt(data).toLocaleString("en-US", {style: "decimal", minimumIntegerDigits: 6, useGrouping: false }); }"""
formatoNumeroZero9 = """ function ( data, type, full, meta ) {return parseInt(data).toLocaleString("en-US", {style: "decimal", minimumIntegerDigits: 9, useGrouping: false }); }"""

ACAO_ADD = '1'
ACAO_EDIT = '2'
ACAO_DELETE = '3'
ACAO_VIEW = '4'
ACAO_REPORT = '5'
ACAO_REPORT_EXPORT = '55'
ACAO_WORKFLOW_START = '6'
ACAO_WORKFLOW_EDIT = '7'
ACAO_WORKFLOW_TO_APPROVE = '8'  # Solicita aprovação, para alterar buttons automaticamente
ACAO_WORKFLOW_APPROVE = '9'  # Em aprovação / rejeição, para alterar buttons automaticamente
ACAO_WORKFLOW_RATIFY = 'Y'  # Ratifica homologação do WF, ex. salva e continua editando contrato adm ou ratificar
ACAO_WORKFLOW_READONLY = 'R'  # Consulta, não permite gravação
ACAO_EMAIL = 'E'  # Relatório para ser enviado por email

"""
tl;dr: See FutureModelForm's docstring.

Many apps provide new related managers to extend your django models with. For
example, django-tagulous provides a TagField which abstracts an M2M relation
with the Tag model, django-gm2m provides a GM2MField which abstracts an
relation, django-taggit provides a TaggableManager which abstracts a relation
too, django-generic-m2m provides RelatedObjectsDescriptor which abstracts a
relation again.

While that works pretty well, it gets a bit complicated when it comes to
encapsulating the business logic for saving such data in a form object. This is
three-part problem:

- getting initial data,
- saving instance attributes,
- saving relations like reverse relations or many to many.

Django's ModelForm calls the form field's ``value_from_object()`` method to get
the initial data. ``FutureModelForm`` tries the ``value_from_object()`` method
from the form field instead, if defined. Unlike the model field, the form field
doesn't know its name, so ``FutureModelForm`` passes it when calling the form
field's ``value_from_object()`` method.

Django's ModelForm calls the form field's ``save_form_data()`` in two
occasions:

- in ``_post_clean()`` for model fields in ``Meta.fields``,
- in ``_save_m2m()`` for model fields in ``Meta.virtual_fields`` and
  ``Meta.many_to_many``, which then operate on an instance which as a PK.

If we just added ``save_form_data()`` to form fields like for
``value_from_object()`` then it would be called twice, once in
``_post_clean()`` and once in ``_save_m2m()``. Instead, ``FutureModelForm``
would call the following methods from the form field, if defined:

- ``save_object_data()`` in ``_post_clean()``, to set object attributes for a
  given value,
- ``save_relation_data()`` in ``_save_m2m()``, to save relations for a given
  value.

For example:

- a generic foreign key only sets instance attributes, its form field would do
  that in ``save_object_data()``,
- a tag field saves relations, its form field would do that in
  ``save_relation_data()``.


class dal.forms.FutureModelForm(*args, **kwargs)[source]

    ModelForm which adds extra API to form fields.

    Form fields may define new methods for FutureModelForm:

        FormField.value_from_object(instance, name) should return the initial value to use in the form,
            overrides ModelField.value_from_object() which is what ModelForm uses by default,

        FormField.save_object_data(instance, name, value) should set instance attributes.
            Called by save() before writting the database, when instance.pk may not be set,
            it overrides ModelField.save_form_data() which is normally used in this occasion for non-m2m and
            non-virtual model fields.

        FormField.save_relation_data(instance, name, value) should save relations required for value on the instance.
            Called by save() after writting the database, when instance.pk is necessarily set,
            it overrides ModelField.save_form_data() which is normally used in this occasion for m2m and
            virtual model fields.

    For complete rationale, see this module’s docstring.

    save(commit=True)[source]

        Backport from Django 1.9+ for 1.8.
"""


class CommonForm(forms.Form):
    acao = ACAO_ADD  # Definição de ação: 1 - Add, 2 - Edit, 3 - Delete
    salvar = "Salvar"

    @staticmethod
    def extrajavascript(*args, **kwargs):
        return ""

    def layout(self):
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal form-group-sm'
        self.helper.form_class = 'form-vertical form-group-sm'
        # self.helper.label_class = 'col-md-5'
        # self.helper.field_class = 'col-md-5'
        self.helper.layout = self.layout()
        # remove acao de kwargs, não corre o risco de passar para super esse argumento
        self.acao = kwargs.pop('acao', None)
        if self.acao in (ACAO_ADD, ACAO_EDIT):
            self.salvar = u'Salvar'
        elif self.acao == ACAO_DELETE:
            self.salvar = u'Confirmar exclusão'
        self.helper.form_tag = True
        # if self.acao == ACAO_ADD:
        #     self.helper.form_tag = True
        # else:
        #     self.helper.form_tag = False
        super().__init__(*args, **kwargs)


class CommonModelForm(FutureModelForm):
    acao = ACAO_ADD  # Definição de ação: 1 - Add, 2 - Edit, 3 - Delete
    salvar = "Salvar"

    # Habilita crítica de required via HTML5, o próprio browser mostra a msg,
    # porém não fica legal quando há TABS, pois o browser não seleciona o tab onde ocorreu o erro,
    # então o usuário fica sem saber onde foi o erro.
    # html5_required = True

    @staticmethod
    def extrajavascript(*args, **kwargs):
        return ""

    def layout(self):
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        # self.helper.form_class = 'form-horizontal form-group-sm'
        self.helper.form_class = 'form-vertical form-group-sm'
        # self.helper.label_class = 'col-md-5'
        # self.helper.field_class = 'col-md-5'
        self.helper.layout = self.layout()
        # remove acao de kwargs, não corre o risco de passar para super esse argumento
        self.acao = kwargs.pop('acao', None)
        if self.acao in (ACAO_ADD, ACAO_EDIT):
            self.salvar = u'Salvar'
        elif self.acao == ACAO_DELETE:
            self.salvar = u'Confirmar exclusão'
        if self.acao == ACAO_ADD:
            self.helper.form_tag = True
        else:
            self.helper.form_tag = False

        super().__init__(*args, **kwargs)

        # Quando um campo não é obrigatório pelo modelo, mas é obrigatório na tela,
        # cria-se o campo fields_required em Meta para listar os campos que terão required forçados
        fields_required = getattr(self.Meta, 'fields_required', None)
        if fields_required:
            for key in fields_required:
                self.fields[key].required = True


class ProcessWorkItemTable(Table):
    # id = Column(header=u'#', field='instance.pk')
    date = DatetimeColumn(header=u'Início', field='date')
    user = Column(header=u'Alocado Para', field='user')
    descricao = Column(header='Descrição', field='instance.content_object')
    activity = Column(header='Atividade', field='activity')
    priority = Column(header=u'Prioridade', field='priority')
    status = Column(header=u'Status', field='status')

    # id = Column(header=u'#', field='instance.pk')
    # process = Column(header=u'Processo', field='instance.process.description')
    # action = GoFlowColumn(header='Ação', field='pk')

    class Meta:
        model = WorkItem
        # ajax = True
        # sort = [(0, 'asc'), ]
        std_button = False
        search = False
        pagination = False
        totals = False
        info = False
        std_button_create = {'text': 'Incluir novo atendimento', 'icon': 'fa fa-plus-square fa-fw',
                             'href': reverse_lazy('atendimentoAdd'),
                             "className": 'btn btn-primary btn-sm', }


class PeriodoForm(CommonForm):
    dataini = forms.DateField(label='Data Inicial')
    datafin = forms.DateField(label='Data Final')

    def layout(self):
        return Layout(Div(
            Div(
                AppendedText('dataini', '<span class="glyphicon glyphicon-calendar" </span>', active=True),
                css_class='row'
            ),
            Div(
                AppendedText('datafin', '<span class="glyphicon glyphicon-calendar" </span>', active=True),
                css_class='row'
            ),
            css_class='col-md-2'
        ))

    class Meta:
        include_hidden = True
        fields = '__all__'
        # exclude = ['user', 'user_id', 'pessoa_ptr_id', 'tipo']
