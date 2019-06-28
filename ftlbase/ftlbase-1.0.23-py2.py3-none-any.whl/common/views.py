# -*- coding: utf-8 -*-

import itertools
import json
import re
import warnings

from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Submit, Button
from django import forms
from django.conf.urls import url
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login as authlogin, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template import Context, RequestContext
from django.urls import reverse, resolve
from django.utils.crypto import get_random_string
from django.utils.deprecation import RemovedInDjango21Warning
from django.utils.safestring import mark_safe
from render_block import render_block_to_string

from common import empresa as emp
from common.logger import Log
from goflow.apptools.forms import ProcessesInstanceTable
from goflow.runtime.models import InvalidWorkflowStatus, ProcessInstance, WorkItem, WorkItemManager
from goflow.workflow.models import Process
from .form import ACAO_VIEW, ACAO_EDIT, ACAO_REPORT, ACAO_REPORT_EXPORT, ACAO_DELETE, ACAO_ADD, ACAO_WORKFLOW_START, \
    ACAO_WORKFLOW_TO_APPROVE, ACAO_WORKFLOW_APPROVE, ACAO_WORKFLOW_RATIFY, ACAO_WORKFLOW_READONLY, ACAO_EMAIL, \
    PeriodoForm
from .reports import montaURLjasperReport

log = Log('commom.views')


# Create your views here.


def get_form(form):
    if form and isinstance(form, str):
        # Se form_class existe então deve ser no formado <módulo>.<arquivo>.FormClass
        #   e faz seu carregamento manualmente abaixo
        p = form.split('.')
        if len(p) == 3:
            the_module = __import__(p[0] + '.' + p[1])
            the_class = getattr(the_module, p[1])
            form = getattr(the_class, p[2])
    return form


def configuraButtonsNoForm(form, acao, goto):
    """
    Configura botões padrões de save ou delete e cancel no final do form
    """
    linkCancel = "window.location.href='#%s'" % reverse(goto)
    linkWorkflow = "ftltabs.trigger('closeTab', 'Workflow', '#%s');" % reverse(goto)
    css_class = 'col-md-11 text-right buttons-do-form'
    if acao in (ACAO_WORKFLOW_START, ACAO_WORKFLOW_TO_APPROVE, ACAO_WORKFLOW_APPROVE,
                ACAO_WORKFLOW_RATIFY, ACAO_WORKFLOW_READONLY):
        cancel = Button('cancel', 'Cancelar', css_class="btn-cancel btn-sm", onclick=linkWorkflow)
    else:
        cancel = Button('cancel', 'Cancelar', css_class="btn-cancel btn-sm", onclick=linkCancel)

    # onde = mark_safe("<i class='fa fa-map-marker' style='font-size:18px;color:#09568d;' data-toggle='tooltip' " +
    #                  "title='Onde estou?'>Onde estou?</i>")

    # form.helper['save'].update_attributes(css_class="hello")
    if acao in (ACAO_ADD, ACAO_EDIT, ACAO_WORKFLOW_START):
        form.helper.layout.extend([
            FormActions(
                Submit('save', 'Salvar', css_class="btn-primary btn-sm"),
                cancel,
                css_class=css_class)
        ])
    elif acao == ACAO_DELETE:
        form.helper.layout.extend([
            FormActions(
                Submit('DELETE', 'Confirmar exclusão do registro', css_class="btn-danger btn-sm", aria_hidden="true"),
                cancel,
                css_class=css_class)
        ])
    elif acao == ACAO_REPORT:
        form.helper.layout.extend([
            FormActions(
                Submit('save', 'Consultar', css_class="btn-primary btn-sm"),
                Button('cancel', 'Cancelar', css_class="btn-cancel btn-sm", onclick=linkCancel),
                css_class='col-md-11 text-right')
        ])
    elif acao == ACAO_REPORT_EXPORT:
        form.helper.layout.extend([
            FormActions(
                Submit('save', 'Consultar', css_class="btn-primary btn-sm"),
                Submit('save', 'Exportar', css_class="btn-success btn-sm"),
                cancel,
                css_class=css_class)
        ])
    elif acao == ACAO_WORKFLOW_TO_APPROVE:
        form.helper.layout.extend([
            FormActions(
                Submit('save', 'Salvar Andamento', css_class="btn-primary btn-sm"),
                Submit('save', 'Solicitar Aprovação', css_class="btn-danger btn-sm"),
                cancel,
                css_class=css_class)
        ])
    elif acao == ACAO_WORKFLOW_APPROVE:
        form.helper.layout.extend([
            FormActions(
                Submit('save', 'Aprovar', css_class="btn-primary btn-sm"),
                Submit('save', 'Rejeitar', css_class="btn-danger btn-sm"),
                cancel,
                css_class=css_class)
        ])
    elif acao == ACAO_WORKFLOW_RATIFY:
        form.helper.layout.extend([
            FormActions(
                Submit('save', 'Salva e Continua Editando', css_class="btn-primary btn-sm"),
                Submit('save', 'Homologa e Conclui', css_class="btn-danger btn-sm"),
                cancel,
                css_class=css_class)
        ])
    else:
        form.helper.layout.extend([
            FormActions(
                cancel,
                css_class='col-md-11 text-right')
        ])
    return form


def commonRender(request, template_name, dictionary):
    """
    Executa o render do template normal para html ou se a requisição é Ajax, então executa separadamente cada parte para JSON
    """
    goto = dictionary.get('goto', 'index')
    try:
        url = reverse(goto)
        dictionary['goto'] = url
        linkCancel = "window.location.href='#%s'" % url
    except Exception as e:  # NOQA
        linkCancel = "window.location.href='#%s'" % goto

    ctx = None

    if request is not None:
        ctx = RequestContext(request, dictionary)
        ctx.update({'ajax': request.is_ajax()})
    else:
        ctx = Context(dictionary)

    ctx.update({'linkCancel': linkCancel})
    ctx = {k: v for d in ctx for k, v in d.items() if d}

    if dictionary.get('acao', ACAO_VIEW) == ACAO_EMAIL:
        html = render_block_to_string(template_name, "content", context=ctx)
        return HttpResponse(html)

    if request.is_ajax():
        title = render_block_to_string(template_name, "title_html", context=ctx)
        html = render_block_to_string(template_name, "content", context=ctx)
        html = re.sub('<link(.*?)/>', '', html)
        html = re.sub('<script type="text/javascript" src=(.*?)</script>', '', html)

        script = render_block_to_string(template_name, "extrajavascript", context=ctx)

        return HttpResponse(
            json.dumps({'title': title, 'html': html, 'extrajavascript': script, 'goto': goto,
                        'form_errors': dictionary.get('form_errors'),
                        'formset_errors': dictionary.get('formset_errors')}),
            content_type='application/json'
        )

    return render(request, template_name, ctx)


def commonProcess(form, formset, request, acao, goto, process_name=None, instance_label=None, workitem=None,
                  extrajavascript=''):
    # print('commonProcess')
    regs = 10
    if acao in (ACAO_ADD, ACAO_EDIT, ACAO_WORKFLOW_START, ACAO_WORKFLOW_TO_APPROVE,
                ACAO_WORKFLOW_APPROVE, ACAO_WORKFLOW_RATIFY):
        from django.db import transaction
        obj = None
        # Não faz o try pois as exceptions serão tratadas na view, para que os erros sejam mostrados
        # try:
        with transaction.atomic():
            obj = form.save()
            if formset is not None:
                # formset.save()
                if isinstance(formset, forms.formsets.BaseFormSet):
                    formset.save()
                else:
                    # formset[0]['formset'].forms[0].fields['beneficiarios']
                    for d in formset:
                        if d['formset']:
                            d['formset'].save()
                            # except IntegrityError:
                            #     handle_exception()
                            # else:
            # Ainda dentro da transaction.atomic, faz o tratamento do start do processo e
            if acao in (ACAO_WORKFLOW_START) and obj:
                # Start Workflow
                # Prioridade é tratada no start
                workitem = ProcessInstance.objects.start(process_name, request, obj, instance_label)
                # priority = int(form.cleaned_data.get('prioridade', Process.DEFAULT_PRIORITY))
                # try:
                #     priority = obj.get_priority()
                # except:
                #     priority = Process.DEFAULT_PRIORITY
                # workitem=ProcessInstance.objects.start(process_name, request, obj, instance_label, priority=priority)
            elif workitem:
                # workitem.process_autofinish(request, obj)
                workitem.process(request)

    elif acao == ACAO_DELETE:
        try:
            form.instance.delete()
        except Exception as e:
            if hasattr(e, protected_objects) and e.protected_objects:
                itens = []
                for item in e.protected_objects[:regs]:
                    itens.append({'msg': '{}: {}'.format(item._meta.model._meta.verbose_name.title(), item.__str__())})
                return JsonResponse({'msg': [{'type': 'danger',
                                              'msg': 'Desculpe, mas há {} registro(s) dependente(s) desse {}:'.format(
                                                  len(e.protected_objects),
                                                  form._meta.model._meta.verbose_name.title()),
                                              'itens': itens,
                                              'total': len(e.protected_objects) - regs}, ],
                                     'goto': request.get_full_path()})
            else:
                return JsonResponse({'msg': [{'type': 'danger',
                                              'msg': 'Desculpe, mas houve erro na exclusão {}:'.format(e)}],
                                     'goto': request.get_full_path()})

    return JsonResponse({'goto': goto,
                         'extrajavascript': extrajavascript if request.POST else None}) if request.is_ajax() else redirect(
        goto)


def commonPermission(request, clsModel, acao, permission, raise_exception=True):
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
        # elif acao == common_forms.ACAO_VIEW:
        else:
            perm = 'view'
        content_type = ContentType.objects.get_for_model(clsModel)
        # a.has_perm(content_type.app_label+'.add_'+content_type.model)
        perm = '{}.{}_{}'.format(content_type.app_label, perm, content_type.model)
    # print('permission=', permission, 'perm=', perm)
    # # a = permission_required(perm, raise_exception=raise_exception)
    # print('user=', request.user, 'has=', request.user.has_perm(perm), 'perm_recq=',vars(a))
    if (not request.user.is_authenticated) or (not request.user.has_perm(perm)):
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return True
    # return permission_required(perm, raise_exception=raise_exception)


def commom_detail_handler(clsMaster, formInlineDetail, can_delete=True, isTree=False):
    # fs = []
    detail = []

    if formInlineDetail:
        if isinstance(formInlineDetail, list):
            for f in formInlineDetail:
                detail.append({'prefix': formInlineDetail.index(f), 'clsDetail': f._meta.model, 'formInlineDetail': f})
        else:
            if hasattr(formInlineDetail, '_meta'):
                clsDetail = formInlineDetail._meta.model
            elif hasattr(formInlineDetail, 'Meta'):
                clsDetail = formInlineDetail.Meta.model
            else:
                clsDetail = formInlineDetail.form.Meta.model
            detail = [{'prefix': '', 'clsDetail': clsDetail, 'formInlineDetail': formInlineDetail}]

        if isinstance(isTree, list):
            for i, d in enumerate(detail):
                d['isTree'] = isTree[i]
        else:
            detail[0]['isTree'] = isTree

        for d in detail:
            d['tituloDetail'] = d['clsDetail']._meta.verbose_name.title()
            # forms = django.forms
            d['Detail'] = (
                d['clsDetail'] if d['isTree'] else forms.inlineformset_factory(parent_model=clsMaster,
                                                                               model=d['clsDetail'],
                                                                               form=d['formInlineDetail'],
                                                                               extra=0, min_num=0,
                                                                               can_delete=can_delete)) if issubclass(
                d['formInlineDetail'], forms.BaseModelForm) else d['formInlineDetail']
    # return fs, detail
    return detail


@login_required
def commonCadastro(request, acao, formModel, goto, **kwargs):
    """
    Cadastro genérico.
        Parâmetros são:
            pk: chave principal
            acao: common_forms.ACAO_ADD, common_forms.ACAO_EDIT ou common_forms.ACAO_DELETE
            formModel: form de cadastro do Model
            goto: nome da url para onde será redirecionado após submmit
            template_name: nome do template a ser usado, default o template padrão
    """
    formInlineDetail = get_form(kwargs.get('formInlineDetail', None))
    pk = kwargs.get('pk', None)
    template_name = kwargs.get('template_name', 'cadastroPadrao.html')
    # can_add = kwargs.get('can_add', True)
    can_delete = kwargs.get('can_delete', True)
    configuraButtons = kwargs.get('configuraButtons', True)
    extrajavascript = kwargs.get('extrajavascript', '')
    permission = kwargs.get('permission', None)
    isTree = kwargs.get('isTree', False)
    idTree = kwargs.get('idTree', 'masterTreeManager')
    acaoURL = kwargs.get('acaoURL', None)
    dataUrl = kwargs.get('dataUrl', None)
    updateParent = kwargs.get('updateParent', None)
    dictionary = kwargs.get('dictionary', None)
    workitem = kwargs.get('workitem', None)
    instance_label = kwargs.get('instance_label', None)

    formM = get_form(formModel)

    clsModel = formM._meta.model
    titulo = clsModel._meta.verbose_name.title()

    commonPermission(request=request, clsModel=clsModel, acao=acao, permission=permission)

    if pk and acao not in (ACAO_ADD, ACAO_REPORT, ACAO_WORKFLOW_START):
        mymodel = get_object_or_404(clsModel, pk=pk)
        titulo = '{0} - {1}'.format(titulo, mymodel.__str__())
    else:
        mymodel = clsModel()

    form_errors = None
    formset_errors = None

    pref = 'nested-' + clsModel._meta.label_lower.replace('.', '-')

    dataTreeURL = dataUrl % pk if dataUrl and pk else ""

    # TODO: É necessário esse tratamento de formM.formInlineDetail? Pois numa busca não achei uso dessa situação
    # Verificar se haverá erro no tratamento de detalhe
    # if not formInlineDetail and hasattr(formM, 'formInlineDetail'):
    #     formInlineDetail = formM.formInlineDetail

    detail = commom_detail_handler(clsMaster=clsModel, formInlineDetail=formInlineDetail, can_delete=can_delete,
                                   isTree=isTree)

    script = formM.extrajavascript()
    extrajavascript = "\n".join([extrajavascript, script])

    if workitem:
        if (acao == ACAO_WORKFLOW_RATIFY) and (request.method == 'POST'):
            # Força close do Tab e ignora extrajavascript configurado
            script = 'ftltabs.trigger("closeTab", "Workflow");'
        else:
            # Javascript para buscar se há formset com classe disableMe e faz o disable (inclusão de andamento)
            script = 'configuraCampos("%s" == "True", "%s" == "True");' % (dictionary.get('disableMe', False), (
                    workitem.status == WorkItem.STATUS_CONCLUDED and acao != ACAO_WORKFLOW_RATIFY))
        extrajavascript = "\n".join([extrajavascript, script])

        ok = (workitem.instance.status != ProcessInstance.STATUS_CONCLUDED)
        # # Se status é concluído então não pode inserir nem deletar
        # can_add &= ok
    else:
        ok = True

    if request.method == 'POST' and ok:
        form = formM(request.POST, request.FILES, instance=mymodel, acao=acao, prefix="main")
        for d in detail:
            d['formset'] = None if d['isTree'] else d['Detail'](request.POST, request.FILES, instance=mymodel,
                                                                prefix=pref + d['prefix'])
        # Cria campo detail no form master para posterior validação do form e dos formset em conjunto quando há dependência.
        # Exemplo, a soma dos percentuais de participação dos proprietários num contrato de adm deve ser 100%
        form.detail = detail
        # como form_tag é variável de classe, tem que forçar para ter <form na geração do html
        form.helper.form_tag = True

        if all(True if d['isTree'] else d['formset'].is_valid() for d in detail) and form.is_valid():
            if acao == ACAO_WORKFLOW_START:
                process_name = form.process_name()
                Process.objects.check_can_start(process_name=process_name, user=request.user)
                log.debug('commonCadastro: ACAO_WORKFLOW_START: instance_label:', instance_label)
            else:
                process_name = None

            return commonProcess(form=form, formset=detail, request=request, acao=acao, goto=reverse(goto),
                                 process_name=process_name, instance_label=instance_label,
                                 workitem=workitem, extrajavascript=extrajavascript)

        else:
            form_errors = form.errors
            errors = []

            for d in detail:
                errors.append([] if d['isTree'] else d['formset'].errors)
            # Flattening errors, transforma várias listas de erros em um única lista
            formset_errors = list(itertools.chain(*errors))
            # context['formset_errors'] = formset_errors
            messages.error(request, mark_safe('Erro no processamento'), fail_silently=True)
    else:
        form = formM(instance=mymodel, prefix="main", acao=acao)
        for d in detail:
            d['formset'] = d['formInlineDetail'] if d['isTree'] else d['Detail'](instance=mymodel,
                                                                                 prefix=pref + d['prefix'])
    if configuraButtons:
        configuraButtonsNoForm(form, acao, goto)

    # monta modal do help do workflow
    # print(idTree, pk, acao, acaoURL)
    if idTree and pk and acao and acaoURL and updateParent:
        extrajavascriptTree = ("""ftl_form_modal = riot.mount('div#ftl-form-modal', 'ftl-form-modal', {
          'modal': {isvisible: false, contextmenu: false, idtree: '%s'},
          'data': {pk: %s, action: %s, acaoURL: '%s', updateParent: '%s', modaltitle: '%s'},
        })
        """ % (idTree, pk, acao, acaoURL, reverse(updateParent), mymodel.__str__()))
        extrajavascriptTree = ("""$('#{0}').attr('data-url','{1}');
        ftl_form_modal = riot.mount('div#ftl-form-modal', 'ftl-form-modal', {{
          'modal': {{isvisible: false, contextmenu: false, idtree: '{0}'}},
          'data': {{pk: {2}, action: {3}, acaoURL: '{4}', updateParent: '{5}', modaltitle: '{6}'}},
        }});
        """.format(idTree, dataTreeURL, pk, acao, acaoURL, reverse(updateParent), mymodel.__str__()))
        extrajavascript = "\n".join([extrajavascript, extrajavascriptTree])
    # else:
    #     extrajavascriptTree = None

    if dictionary is None:
        dictionary = {}

    dictionary.update(
        {'empresa': emp, 'goto': goto, 'title': titulo, "form": form, 'form_errors': form_errors, "detail": detail,
         # "can_add": can_add, "delecao": (acao == ACAO_DELETE),
         'formset_errors': formset_errors, "idTree": idTree, "pk": pk, "isTree": True, "acaoURL": acaoURL,
         "dataUrl": dataTreeURL, "updateParent": reverse(updateParent) if updateParent else None,
         "extrajavascript": extrajavascript})  # if extrajavascript else extrajavascriptTree})

    # template_name = 'cadastroMasterDetail.html'

    return commonRender(request, template_name, dictionary)


@login_required
def commonListaTable(request, model=None, queryset=None, goto='index', template_name="table.html", tableScript=None,
                     referencia=None, dictionary=None, permission=None):
    """
    Lista padrão no formato tabela.
        Parâmetros são:
            model: form de cadastro do Model Master
            queryset: queryset para seleção dos registros a serem listados
            template_name: nome do template a ser usado, default o template padrão de tabela
            tableScript: script a ser injetado dinamicamente no html para tratamento da tabela (totalização de campos, etc.)
    """

    if queryset is not None:
        objetos = model(queryset)
    else:
        if model:
            objetos = model()
        else:
            return "z"
    # objetos = model.queryset.exclude(codtaxa__gte =10000)
    # objetos = objetos.exclude(codtaxa__gte=10000).order_by('codtaxa')
    clsTable = model.opts.model
    titulo = clsTable._meta.verbose_name.title()
    # token =  Token.objects.get(user=request.user)

    commonPermission(request=request, clsModel=clsTable, acao=ACAO_VIEW, permission=permission)

    if dictionary is None:
        dictionary = {}

    # extrajavascript = mark_safe(model.extrajavascript().join(dictionary.get('extrajavascript','')))
    extrajavascript = mark_safe(model.extrajavascript())

    dictionary.update({'empresa': emp, 'goto': goto, 'objetos': objetos, 'title': titulo, 'tableScript': tableScript,
                       'referencia': referencia, "extrajavascript": extrajavascript})

    # update id of datatables to random name
    model.opts.id = get_random_string(length=10)

    return commonRender(request, template_name, dictionary)


def commonRelatorioTable(model=None, queryset=None, template_name="table.html", tableScript=None, extrajavascript='',
                         dictionary=None):
    """
    Lista padrão no formato tabela.
        Parâmetros são:
            model: form de cadastro do Model Master
            queryset: queryset para seleção dos registros a serem listados
            template_name: nome do template a ser usado, default o template padrão de tabela
            tableScript: script a ser injetado dinamicamente no html para tratamento da tabela (totalização de campos, etc.)
    """
    if queryset:
        objetos = model(queryset)
    else:
        if model:
            objetos = model()
        else:
            return "z"

    clsTable = model.opts.model
    titulo = clsTable._meta.verbose_name.title()

    if dictionary is None:
        dictionary = {}

    dictionary.update({'empresa': emp, 'objetos': objetos, 'title': titulo, 'tableScript': tableScript,
                       'extrajavascript': extrajavascript})

    return commonRender(request=None, template_name=template_name, dictionary=dictionary)


@login_required
def common_workflow_table_process(request, table=ProcessesInstanceTable, goto='index', my_work=False, news=False,
                                  pending=False, goal=None, add=True):
    query = ProcessInstance.objects.all_safe(user=request.user, my_work=my_work, news=news, pending=pending, goal=goal)
    # if request.resolver_match.url_name != 'workflow':
    #     href = request.resolver_match.url_name.split('_all')[0]
    #
    # else:
    #     href = request.resolver_match.url_name
    # href = href+'/add'
    # href = 'add/'
    # self.std_button_create_href = getattr(options, 'std_button_create_href', 'add/')
    if add:
        table.opts.std_button_create = {'text': 'Incluir novo registro', 'icon': 'fa fa-plus-square fa-fw',
                                        'href': table.opts.std_button_create_href,
                                        "className": 'btn btn-primary btn-sm', }
    else:
        table.opts.std_button_create = False
    # ProcessesInstanceTable.opts.std_button_create = {'text': 'Incluir novo atendimento', 'icon': 'fa fa-plus-square fa-fw',
    #                                               'href': href, "className": 'btn btn-primary btn-sm', }

    if goal and table == ProcessesInstanceTable:
        table.base_columns[0].visible = False  # Column pk is hidden if filtering by goal
        table.base_columns[1].visible = False  # Column Processo is hidden if filtering by goal
    else:
        table.base_columns[0].visible = True
        table.base_columns[1].visible = True

    return commonListaTable(request, model=table, queryset=query, goto=goto)


@login_required
def common_history_workitems_table(request, pk, model=None, queryset=None, goto='index', template_name="table.html",
                                   tableScript=None, referencia=None,
                                   extrajavascript='', dictionary=None, permission=None):
    workitems = WorkItemManager.get_process_workitems(pk, user=request.user)
    return commonListaTable(request, model=model, queryset=workitems, goto=goto, template_name=template_name,
                            tableScript=tableScript, referencia=referencia, dictionary=dictionary,
                            permission=permission)
    # extrajavascript=extrajavascript, dictionary=dictionary, permission=permission)


@login_required
def common_workflow(request, id, goto='workflow_pending', dictionary=None):
    """
    activates and redirect to the application.

    :param request:
    :param id: workitem id
    :param goto: 'workflow_pending' ou 'workflows_all' se workflow concluído
    :param dictionary: parâmetros extras, ex.: {'disableMe': True}
    :return: rendered html
    """

    def _app_response(request, workitem, goto, dictionary):
        """
        Verifica se há subworkflow e executa, senão faz o redirect para a configuração do WF

        :param workitem:
        :return:
        """

        # id = workitem.id
        def _execute_activity(workitem, activity, dictionary):
            # standard activity
            url = activity.application.get_app_url(workitem)
            func, args, kwargs = resolve(url)
            # params has to be an dict ex.: { 'form_class': 'imovel.form.ContratoLocForm', 'goto': 'contratoLoc'}
            params = activity.app_param
            # params values defined in activity override those defined in urls.py
            if params:
                try:
                    params = eval('{' + params.lstrip('{').rstrip('}') + '}')
                    # Carrega o form dos parâmetros form_class e formInlineDetail dinamicamente e faz a substituição
                    forms = ['form_class', 'formInlineDetail']
                    for f in forms:
                        if f in params:
                            # Se form_class existe então deve ser no formado <módulo>.<arquivo>.FormClass
                            #   e faz seu carregamento manualmente abaixo
                            p = params.get(f, None)
                            if p:
                                p = p.split('.')
                                if len(p) == 3:
                                    the_module = __import__(p[0] + '.' + p[1])
                                    the_class = getattr(the_module, p[1])
                                    the_form = getattr(the_class, p[2])
                                    params.update({f: the_form})
                                    dictionary.update({'disableMe': False})
                                    kwargs.update({'dictionary': dictionary})
                except Exception as v:
                    pass
                kwargs.update(params)

            # Marretada para evitar que o param acao seja injected em kwargs e dê problema no sendmail
            # Opção seria incluir acao no sendmail
            if activity.application.url not in ['apptools/sendmail', ]:
                kwargs.update({'workitem': workitem,
                               'acao': ACAO_WORKFLOW_READONLY if workitem.instance.status == ProcessInstance.STATUS_CONCLUDED
                               else ACAO_WORKFLOW_APPROVE if activity.approve
                               else ACAO_WORKFLOW_RATIFY if activity.ratify
                               else dictionary.get('acao', ACAO_EDIT)})
            ret = func(request, **kwargs)
            return ret

        if dictionary is None:
            dictionary = {}

        dictionary.update({'empresa': emp})

        activity = workitem.activity
        # try: TODO: Será?
        #     dictionary.update({'title': workitem.instance.content_object})
        # except:
        #     dictionary.update({'title': activity.process.title})

        if workitem.instance.status != ProcessInstance.STATUS_CONCLUDED:
            if request.method == 'POST':
                workitem.activate(request)

            if not activity.process.enabled:
                extrajavascript = 'riot.mount("ftl-error-message", {messages: [{type: \'error\', msg: "Processo %s está desabilitado."}, ]});' % activity.process.title
                dictionary.update({'extrajavascript': extrajavascript})
                return commonRender(request, 'error.html', dictionary)

            if activity.kind == 'subflow':
                # subflow
                sub_workitem = workitem.start_subflow(request)
                return _app_response(request, sub_workitem, goto, dictionary)

        # no application: default_app
        if not activity.application:
            url = 'default_app'

            # url = '../../../default_app'
            # return HttpResponseRedirect('%s/%d/' % (url, id))
            return HttpResponseRedirect('/#/' + reverse(url, args=[id]))

        if activity.kind == 'dummy':
            return _execute_activity(workitem, activity, dictionary)

        if activity.kind == 'standard':
            ret = _execute_activity(workitem, activity, dictionary)
            # Se não retornou nada (ex. sendmail(), então verifica se é autofinish para executar complete do workitem
            if ret is None and \
                    workitem.activity.autofinish and workitem.instance.status != ProcessInstance.STATUS_CONCLUDED:
                # log.debug('common_workflow autofinish: complete')
                workitem.complete(request)
                dictionary.update({'goto': goto})
                return commonRender(request, 'base.html', dictionary)
            return ret

        extrajavascript = 'riot.mount("ftl-error-message", {messages: [{type: \'error\', msg: "Erro no Workflow, não há aplicação configurada em %s."}, ]});' % activity.process.title
        dictionary.update({'extrajavascript': extrajavascript, 'goto': resolve(request.path).view_name})
        return commonRender(request, 'error.html', dictionary)
        # return HttpResponse('completion page.')

    id = int(id)
    try:
        workitem = WorkItem.objects.get_safe(id=id, user=request.user)
    except Exception as v:
        if type(v) == InvalidWorkflowStatus:
            workitem = v.workitem
        else:
            extrajavascript = 'riot.mount("ftl-error-message", {messages: [{type: \'error\', msg: "%s"}, ]});' % str(v)
            dictionary.update({'extrajavascript': extrajavascript,
                               'goto': resolve(request.path).view_name})  # OR resolve(request.path).url_name ?????
            return commonRender(request, 'base.html', dictionary)

    return _app_response(request, workitem, goto, dictionary)


@login_required
def common_workflow_execute(request, **kwargs):
    """
    activates and redirect to the application.

    :param request:
    :param kwargs:
        acao: Ação a ser executada
        form_class: Form a ser usado
        formInlineDetail: Inline detail a ser usado (optional)
        goto: 'workflow_pending' ou 'workflows_all' se workflow concluído
        dictionary: parâmetros extras, ex.: {'disableMe': True}
        extrajavascript: javascript a ser anexado ao form
        workitem: workitem ativo
    :return:
    """
    workitem = kwargs.get('workitem', None)

    acao = kwargs.get('acao', ACAO_EDIT)
    formModel = kwargs.get('form_class')
    formInlineDetail = kwargs.get('formInlineDetail')
    goto = kwargs.get('goto',
                      'workflow_all' if workitem and workitem.status == WorkItem.STATUS_CONCLUDED else 'workflow_pending')
    dictionary = kwargs.get('dictionary', {})
    # submit_name é o nome do form que está sendo gravado
    dictionary.update({'submit_name': request.POST.get('save', '')})
    extrajavascript = kwargs.get('extrajavascript', '')

    pk = workitem.instance.wfobject().pk if workitem else None

    return commonCadastro(request, acao, formModel, goto, formInlineDetail=formInlineDetail, pk=pk,
                          dictionary=dictionary, workitem=workitem, extrajavascript=extrajavascript)


@login_required
def common_workflow_flag_myworks(request, **kwargs):
    """
    list all my workitems

    parameters:
    template: 'Atendimento'
    """
    template_name = kwargs.get('template_name', 'workflow_myworks.html')
    workitems = WorkItemManager.list_safe(user=request.user, roles=False, withoutrole=False, noauto=False)
    dictionary = kwargs.get('dictionary', {})
    dictionary.update({'workitems': workitems})

    return commonRender(request, template_name, dictionary)


@login_required
def common_workflow_flag_news(request, **kwargs):
    """
    list all my workitems

    parameters:
    template: 'Atendimento'
    """
    template_name = kwargs.get('template_name', 'workflow_news.html')
    workitems = WorkItemManager.list_safe(user=None, roles=True, status=[WorkItem.STATUS_INACTIVE, ],
                                          withoutrole=True, noauto=False)
    dictionary = kwargs.get('dictionary', {})
    dictionary.update({'workitems': workitems})

    return commonRender(request, template_name, dictionary)


@login_required
def common_workflow_graph(request, pk, template='graph.html'):
    """Gera gráfico do workflow
    pk: process id
    template: template
    """
    instance = ProcessInstance.objects.get(pk=pk)
    mark_pending = set()
    mark_completed = set()
    mark_problem = set()
    for a in instance.workitems.all():
        if a.status in [WorkItem.STATUS_INACTIVE, WorkItem.STATUS_PENDING]:
            mark_pending.add(a.activity.pk)
        elif a.status in [WorkItem.STATUS_CONCLUDED]:
            mark_completed.add(a.activity.pk)
        else:
            mark_problem.add(a.activity.pk)
    args = {'pending': list(mark_pending), 'completed': list(mark_completed), 'problem': list(mark_problem)}
    process = instance.process
    context = {
        'process': process,
        'args': args,
    }
    return commonRender(request, template, context)


@login_required
def common_process_graph(request, title, template='graph.html'):
    """Gera gráfico do process
    pk: process id or title
    template: template
    """
    try:
        process = Process.objects.get(title=title)
    except Exception as v:
        process = Process.objects.get(id=title)
    mark_pending = set()
    mark_completed = set()
    mark_problem = set()
    args = {'pending': list(mark_pending), 'completed': list(mark_completed), 'problem': list(mark_problem)}
    context = {
        'process': process,
        'args': args,
    }
    return commonRender(request, template, context)


# Autenticação
# @csrf_protect
def loginX(request, template_name='login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          extra_context=None, redirect_authenticated_user=False):
    warnings.warn(
        'The login() view is superseded by the class-based LoginView().',
        RemovedInDjango21Warning, stacklevel=2
    )
    return LoginView.as_view(
        template_name=template_name,
        redirect_field_name=redirect_field_name,
        form_class=authentication_form,
        extra_context=extra_context,
        redirect_authenticated_user=redirect_authenticated_user,
    )(request)


# def loginX(request):
#     logout(request)
#     username = password = ''
#     if request.POST:
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             if user.is_active:
#                 authlogin(request, user)
#                 # print(request.POST.get('next'), '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
#                 if request.POST.get('next') and request.POST.get('next')[:4] != 'http':
#                     return HttpResponseRedirect('/#' + request.POST.get('next'))
#                 return HttpResponseRedirect('/')
#         else:
#             messages.error(request, 'Usuário ou senha incorreta.')
#     # return render_to_response('login.html', context=RequestContext(request))
#     return render(request, 'login.html')


def logoutX(request):
    logout(request)
    return HttpResponseRedirect(reverse('loginX'))


def include_CRUD(name, table=None, form=None, add=True, edit=True):
    urls = []
    if table:
        urls.extend([
            url(r'^{0}/$'.format(name), commonListaTable, {'model': table}, name=name)
        ])
    if add:
        urls.extend([
            url(r'^{0}/add/$'.format(name), commonCadastro, {'acao': ACAO_ADD, 'formModel': form, 'goto': name},
                name="{0}Add".format(name)),
        ])
    if edit:
        urls.extend([
            url(r'^{0}/(?P<pk>[-\w]+)/(?P<acao>\w+)/$'.format(name), commonCadastro, {'formModel': form, 'goto': name},
                name="{0}EditDelete".format(name)),
        ])
    return urls


def include_Workflow(name, table=ProcessesInstanceTable, form=None, goal=None, pending=False, add=True):
    urls = []
    if table:
        urls.extend([
            url(r'^{0}/$'.format(name), common_workflow_table_process,
                {'table': table, 'goal': goal, 'pending': pending, 'add': add}, name=name)
        ])
    if add:
        urls.extend([
            url(r'^{0}/add/$'.format(name), common_workflow_execute,
                {'acao': ACAO_WORKFLOW_START, 'form_class': form, 'goto': name},
                name="{0}Add".format(name)),
            # Não tem Update ou Delete, pois é parte de Workflow
        ])
    return urls


@login_required
def relatorio(request, *args, **kwargs):
    """
    Report genérico.
        Parâmetros são:
            formRel: form do filtro do relatório
            # model: form dos dados do relatório
            goto: nome da url para onde será redirecionado após submit
            report_name: caminho e nome do relatório no servidor Jasper (/Imobiliar/Relatorios/Razao_por_Periodo)
            fields: campos adicionais que serão passado para a view de report
            titulo: título do relatório
            template_name: nome do template a ser usado para entrada de dados do relatório, default é cadastroPadrao.html
            # template_list: nome do template a ser usado para exibição do relatório, default é table.html
            template_report: nome do template a ser usado para exibição de relatório, default é report.html
    """
    formRel = kwargs.pop('formRel', PeriodoForm)
    # model = kwargs.pop('model', None)
    goto = kwargs.pop('goto', 'index')
    report_name = kwargs.pop('report_name', None)
    fields = kwargs.pop('fields', [])
    titulo = kwargs.pop('titulo', 'Relatório')

    template_name = kwargs.pop('template_name', 'cadastroPadrao.html')
    # template_list = kwargs.pop('template_list', 'table.html')
    template_report = kwargs.pop('template_report', 'report.html')

    home = 'index'

    configuraButtons = True

    form = formRel(request.POST or None)  # , request.FILES or None) #File uploads

    # form.helper.form_tag = True # como é variável de classe, tem que forçar para ter <form na geração do html

    if request.method == 'POST':
        if form.is_valid():
            dataini = form.cleaned_data['dataini']
            datafin = form.cleaned_data['datafin']
            # dataini = datetime(dataini.year,dataini.month,dataini.day,tzinfo=utc)
            # datafin = datetime(datafin.year,datafin.month,datafin.day, 23, 59, 59,tzinfo=utc)
            params = {'year_ini': dataini.year, 'month_ini': dataini.month, 'day_ini': dataini.day,
                      'year_fin': datafin.year, 'month_fin': datafin.month, 'day_fin': datafin.day, }

            # Prepara campos adicionais
            for f in fields:
                try:
                    params.update({f: form.cleaned_data[f]})
                except:
                    params.update({f: request.session.get(f, None)})

            if request.POST['save'] == 'Consultar' and redirect:
                params.update({'acao': ACAO_REPORT})
                url = reverse(goto, kwargs=params)
                return commonRender(request, template_report,
                                    {'empresa': emp, 'title': titulo, 'goto': url})
                # url = reverse(goto, **params)
                # return HttpResponseRedirect(url)
                # return redirect(goto, **params)
            elif request.POST['save'] == 'Exportar' and report_name:
                # dataini = dataini.isoformat()
                # datafin = datafin.isoformat()
                params.update({'acao': ACAO_REPORT_EXPORT})
                relatorio = montaURLjasperReport(report_name=report_name, params=params)
                return commonRender(request, template_report,
                                    {'empresa': emp, 'title': titulo, 'goto': goto, 'form_errors': form.errors,
                                     'relatorio': relatorio})
            else:
                pass
            return redirect('periodo')
        else:
            context = RequestContext(request)
            context['form_errors'] = form.errors

    if configuraButtons:
        configuraButtonsNoForm(form, ACAO_REPORT, goto=home)
    return commonRender(request, template_name, {'empresa': emp, 'title': titulo, 'goto': home, 'form': form})
