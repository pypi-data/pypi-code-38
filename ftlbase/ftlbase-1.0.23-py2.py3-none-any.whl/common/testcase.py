# import unittest

# from unittest import TestCase

from django.test import Client, TestCase
from django.urls import reverse
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from common.form import ACAO_DELETE, ACAO_EDIT
from common.views import ACAO_ADD
from goflow.runtime.models import ProcessInstance

client = Client()
verbosity = 2


# from django.test import TestCase

# import sys
# print(sys.path)
#
# import os
#
# chromedriver = "/home/was/alugarImovel/test/chromedriver"
# os.environ["webdriver.chrome.driver"] = chromedriver
# driver = webdriver.Chrome(chromedriver)
# driver.get('http://stackoverflow.com')
# driver.quit()


# from runtests import client, verbosity


class FTL_Html_Test(TestCase):
    def setUp(self):
        firefox = True
        if firefox:
            from selenium.webdriver.firefox.options import Options
            # profile = FirefoxProfile()
            # profile.set_preference("intl.accept_languages", "pt-BR")
            options = Options()
            options.set_preference("intl.accept_languages", "pt-BR")
            self.driver = webdriver.Firefox('/home/was/.virtualenvs/alugar/bin', options=options)
        else:
            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.add_argument("--lang=pt-BR")
            options.add_argument("--start-maximized")
            options.add_experimental_option("prefs", {"intl.accept_languages": "pt-BR"})
            self.driver = webdriver.Chrome(options=options)
            # self.driver = webdriver.Chrome('/home/was/.virtualenvs/alugar/bin/chromedriver', options=options)
        self.time_to_wait = 5
        self.driver.implicitly_wait(self.time_to_wait)
        self.base_url = "http://127.0.0.1:8000/"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.driver_wait = WebDriverWait(self.driver, self.time_to_wait)
        self.driver.set_page_load_timeout(self.time_to_wait)
        self.driver.get(self.base_url + 'common/login/?next=/')

        self.driver.find_element_by_id('username').clear()
        self.driver.find_element_by_id('username').send_keys('teste')
        self.driver.find_element_by_name('password').clear()
        self.driver.find_element_by_name('password').send_keys('Temp1234')
        self.driver.find_element_by_name('save').click()

    def wait_for_loaded(self):
        element = self.driver_wait.until(EC.text_to_be_present_in_element_value((By.ID, 'ftl-page-load'), 'loaded'))
        return element

    def wait(self, url=None):
        # element = self.driver_wait.until(EC.text_to_be_present_in_element_value((By.ID, 'ftl-page-load'), 'loaded'))
        element = self.wait_for_loaded()

        if url:
            try:
                self.driver.get(self.base_url + url)
            except TimeoutException:
                pass
            self.wait()

        return element

    def is_element_present(self, how, what):
        try:
            self.driver.implicitly_wait(0)
            self.driver.find_element(by=how, value=what)
            self.driver.implicitly_wait(self.time_to_wait)
        except NoSuchElementException as e:
            self.driver.implicitly_wait(self.time_to_wait)
            return False
        return True

    def is_element_present_by_id(self, id):
        return self.is_element_present(By.ID, id)

    def is_element_present_by_name(self, name):
        return self.is_element_present(By.NAME, name)

    def is_alert_present(self):
        try:
            self.driver.switch_to.alert
        except NoAlertPresentException as e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def get_element_attribute_by_id(self, id, attr):
        return self.driver.find_element(by=By.ID, value=id).get_attribute(attr)

    def set_element(self, element, val):
        element.clear()
        return element.send_keys(val)

    def set_element_by_id(self, id, val):
        return self.set_element(self.driver.find_element(by=By.ID, value=id), val)

    def set_element_by_css_selector(self, css, val):
        return self.set_element(self.driver.find_element(by=By.CSS_SELECTOR, value=css), val)

    def set_select_by_id(self, id, txt):
        element = self.driver.find_element_by_id(id)
        return Select(element).select_by_visible_text(txt)

    def set_checkbox_by_id(self, id):
        return self.driver.find_element_by_id(id).click()

    def set_datepicker_by_id(self, id, date):
        # date no formado dd/mm/yyyy
        return self.driver.execute_script('$("#{0}").datepicker("setDate", "{1}")'.format(id, date))

    def set_autocomplete_by_id(self, id, val):
        # aria-labelledby="select2-id_nested-cliente-pessoafisica-0-banco-container"
        actions = ActionChains(self.driver)
        element = self.driver.find_element_by_id(id)
        actions.move_to_element(element)
        actions.click(element)
        actions.send_keys(val)
        actions.send_keys(Keys.ENTER)
        actions.perform()

    def click_element_by_id(self, id=None):
        if self.driver.capabilities['browserName'] == 'firefox':
            return self.driver.find_element_by_id(id).click()

        # Chrome
        return self.driver.execute_script('document.getElementById("{}").click()'.format(id))

    def click_element_by_name(self, name=None):
        if self.driver.capabilities['browserName'] == 'firefox':
            return self.driver.find_element_by_css_selector('button[name="{}"]'.format(name)).click()

        # Chrome
        return self.driver.execute_script('document.getElementsByName("{}")[0].click()'.format(name))

    def click_element_by_link_text(self, txt):
        element = self.wait_by_link_text(txt, msg='Não encontrou texto: {}'.format(txt))
        return element.click()
        # return self.driver.find_element_by_link_text(txt).click()

    def click_element_by_css_selector(self, css):
        self.wait_by_css_selector(css, msg='Não achou css_celector {}'.format(css))
        return self.driver.find_element_by_css_selector(css).click()

    def click_element_by_xpath(self, xpath):
        return self.driver.find_element_by_xpath(xpath).click()

    def check_value_by_id(self, id, val, msg=None):
        # element = self.driver_wait.until(EC.presence_of_element_located((By.ID, id)))
        element = self.driver_wait.until(EC.visibility_of_element_located((By.ID, id)))
        return self.assertEqual(element.get_attribute('value'), val, msg=msg)
        # return self.assertEqual(self.driver.find_element_by_id(id).get_attribute('value'), val, msg=msg)

    def wait_by_css_selector(self, css, msg=None):
        # self.wait_for_loaded()
        # element = self.driver_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
        element = self.driver_wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css)))
        self.assertTrue(element is not None, msg=msg)
        return element

    def wait_by_link_text(self, txt, msg=None):
        # element = self.driver_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
        element = self.driver_wait.until(EC.visibility_of_element_located((By.LINK_TEXT, txt)))
        self.assertTrue(element is not None, msg=msg)
        return element

    def check_has_error_by_id(self, id, msg=None):
        return self.assertTrue('has-error' in self.get_element_attribute_by_id(id, 'class').split(), msg=msg)

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


class FTL_Test(TestCase):
    def workflow_status(self, instance, status):
        _status = ProcessInstance.objects.get_process_by_instance(instance).first().status
        self.assertEqual(_status, status, msg='Status do workflow errado: {}, deveria ser {}'.format(_status, status))


def get(url, data=None, args=None, **kwargs):
    return client.get(reverse(url, args=args), data, HTTP_X_REQUESTED_WITH='XMLHttpRequest', **kwargs)


def post(url, data=None, args=None, **kwargs):
    return client.post(reverse(url, args=args), data, follow=True, **kwargs)


def management_form(formset, acao, formset_delete=False):
    """
    Retorna um management form para formsets
    formset:= [{'prefix': 'nested-cliente-estado',
                'data': [{'nome': 'xxxx', 'ibge': '909090'}],
                'formset_pk_name': 'uf',
                'model': Municipio,
                'fk': None,
                'fk_name': None,
                'widget': False,
                'insert': False,
                'update': False,
                'delete': False}]
    formset_delete: Executa ou não o formset_delete

    """
    ret = {}

    if formset:
        for f in formset:
            if f['prefix'] and ((f['widget']) or acao != ACAO_ADD):
                if f['data'] and acao != ACAO_DELETE:
                    total = len(f['data'])
                    for index, obj in enumerate(f['data']):
                        if f['formset_pk_name']:
                            # Referência da pk associada ao formset 'uf': 'DF'
                            ret.update({'{0}-{1}-{2}'.format(f['prefix'], index, f['formset_pk_name']):
                                            # (f['fk'][index] if f['fk'] else f['pk']) if acao != ACAO_ADD else ''})
                                            f['pk'] if acao != ACAO_ADD else ''})

                        if f['fk_name']:
                            # id da fk no formset 'id': 123
                            ret.update({'{0}-{1}-{2}'.format(f['prefix'], index,
                                                             f['fk_name']): f['fk'][index] if f['fk'] else ''})
                        for k, v in obj.items():
                            if isinstance(v, dict):
                                v['prefix'] = '{0}-{1}-{2}'.format(f['prefix'], index, k)
                                vv=[v]
                                ret.update(management_form(vv, acao, formset_delete=formset_delete))
                            else:
                                ret.update({'{0}-{1}-{2}'.format(f['prefix'], index, k): v})
                        if formset_delete:
                            ret.update({'{0}-{1}-{2}'.format(f['prefix'], index, 'DELETE'): 'on'})
                else:
                    total = 0

                ret.update({'{}-TOTAL_FORMS'.format(f['prefix']): total,
                            '{}-INITIAL_FORMS'.format(f['prefix']): total if formset_delete else 0,
                            '{}-MIN_NUM_FORMS'.format(f['prefix']): 0,
                            '{}-MAX_NUM_FORMS'.format(f['prefix']): 1000})

                if f['widget']:
                    # ret.update({'{}-formset-id'.format(f['prefix']): 'None' if acao == ACAO_ADD else f['fk']})
                    ret.update({'{}-formset-id'.format(f['prefix']): '' if acao == ACAO_ADD else f['pk']})

    return ret


class CRUD_Test(object):
    """ Classe genérica para execução de testes padrão de CRUD em models """

    def __init__(self, testcase, model, url, data, pk, pk_name='pk', prefix='main', formset=None,
                 formset_delete=True, duplicidade=True, insert=True, update=True, delete=True):
        # formset_data: { 'formset_data': [{'uf': self.pk, 'nome': 'xxxx', 'ibge': '909090'}],  # um ou mais registros
        #            'formset_model': Municipio],  # model do formset
        #            'formset_pk_name': 'uf',  # nome do campo que faz referência ao model
        #            'fk_name': 'id',  # nome do campo de id do formset, normalmente 'id'
        #            'insert': False,  # Se o formset também será montado no insert
        #            'update': False,  # Se executa ou não o teste de update do formset
        #            'delete': False,  # Se executa ou não o teste de formset_delete do formset
        # }
        self.testcase = testcase
        self.model = model
        self.url = url
        self.pk = pk  # pk or alternate key
        self.data = {}
        self._data = data.copy()
        self.pk_name = pk_name
        self.prefix = prefix
        self.formset = formset
        # formset = {['formset_prefix':None, 'formset_data':None,'formset_pk_name': None, 'formset_model': None,'fk':None,
        #            'fk_name':None,'formset_insert':None,'formset_delete':None]}

        self.fk = []  # ids dos registros criado no update do form (formset inseridos)
        self.formset_delete = formset_delete
        self.duplicidade = duplicidade
        self.insert = insert
        self.update = update
        self.delete = delete
        self.verbosity = verbosity

        self.verbose = self.model._meta.verbose_name
        self.instance = None

        # Atualiza self.data com o prefix do form
        for k, v in self._data.items():
            if not isinstance(v, dict):
                self.data.update({'{0}-{1}'.format(self.prefix, k): v})

        self.login()

    def login(self):
        # response = client.post(reverse('loginX'), {'username': 'teste', 'password': 'Temp1234'})
        response = client.login(username='teste', password='Temp1234')
        if not response:
            raise Exception('Erro no login')

    @property
    def pk_lookup(self):
        return {self.pk_name: self.pk}

    # @property
    def fk_lookup(self, f):
        return {f['formset_pk_name']: f['pk']}

    def pk_update(self):
        pk = self.model.objects.filter(**self.pk_lookup)
        if pk:
            self.instance = pk[0]
            self.pk = pk[0].pk
            self.pk_name = self.model._meta.pk.name
        else:
            self.pk = None
        if self.formset:
            for f in self.formset:
                f['pk'] = self.pk
                f['pk_name'] = self.pk_name
        self.testcase.assertTrue(self.model.objects.filter(pk=self.pk).exists(),
                                 msg='Não foi incluído: {}'.format(self.verbose))
        self.pk_update_fk(self.pk, self.instance, self._data)

    def pk_update_fk(self, pk, instance, data):
        for index, obj in data.items():
            if isinstance(obj, dict):
                # obj['pk'] = instance.pk
                obj['pk'] = pk
                # obj['fk'] = [instance.pk]
                fks  = obj['model'].objects.filter(**{obj['formset_pk_name']:instance})
                obj['fk'] = [f.pk for f in fks]
                for i, x in enumerate(obj['data']):
                    self.pk_update_fk(fks[i].pk, fks[i], x)
                    # self.pk_update_fk(fks[i].pk, fks[i], x)

    def fields_prepare(self, acao=ACAO_ADD, formset_delete=False):
        _data = management_form(self.formset, acao, formset_delete=formset_delete)
        for k, v in self._data.items():
            if not isinstance(v, dict):
                _data.update({'{0}-{1}'.format(self.prefix, k): v})
            else:
                vv = v.copy()
                vv.update({'prefix': '{0}-{1}'.format(self.prefix, k)})
                vv = [vv]
                _data.update(management_form(vv, acao, formset_delete=formset_delete))
        return _data


    def test_insert(self):
        if self.verbosity > 1:
            print('Insert:')  # , self.formset_model._meta.verbose_name if self.formset_model else '')

        # Protocolo padrão de teste de inclusão
        # Busca a lista de objetos do modelo
        response = get(self.url)
        self.testcase.assertEqual(response.status_code, 200)

        _url = "{}Add".format(self.url)
        _data = self.fields_prepare(acao=ACAO_ADD, formset_delete=False)
        response = post(_url, _data)
        try:
            error = [{k:v} for k,v in response.context['form'].errors.items()]
        except Exception:
            error = ''

        self.testcase.assertNotContains(response, 'submit-id-save',
                                        msg_prefix='Não inseriu: {0}: {1}'.format(self.verbose, error))

        # Foi realmente incluído? Então atualiza a pk, pois pode ter sido passado uma alternate key
        self.pk_update()

        # Testa Duplicidade
        if self.duplicidade:
            response = post(_url, _data)
            self.testcase.assertContains(response, 'submit-id-save', msg_prefix='Duplicidade: {}'.format(self.verbose))

        return self.instance

    def test_update(self, formset_delete=False, post_update=None):
        if self.verbosity > 1:
            print('Update:')  # , self.formset_model._meta.verbose_name if self.formset_model else '')

        _url = "{}EditDelete".format(self.url)
        _data = self.fields_prepare(acao=ACAO_EDIT, formset_delete=formset_delete)
        args = [self.pk, ACAO_EDIT]

        response = post(_url, _data, args=args)
        try:
            error = [{k:v} for k,v in response.context['form'].errors.items()]
        except Exception:
            error = ''

        self.testcase.assertNotContains(response, 'submit-id-save',
                                        msg_prefix='Não fez update: {0}: {1}'.format(self.verbose, error))

        # Continua existindo?
        obj = self.model.objects.filter(pk=self.pk)
        self.testcase.assertTrue(obj.exists(), msg='Foi deletado no update: {}'.format(self.verbose))

        # Se tem formset, então verifica se criou ou deletou
        if self.formset:
            for f in self.formset:
                fks = f['model'].objects.filter(**self.fk_lookup(f))
                if formset_delete:
                    # segunda vez, tem que ter deletetado todos os formsets
                    self.testcase.assertFalse(fks.exists(),
                                              msg='Formset não foi deletado no update: {}'.format(self.verbose))
                else:
                    # primeira vez, tem que ter criado o formset
                    self.testcase.assertTrue(fks.exists(), msg='Formset não foi criado no update: {}'.format(self.verbose))
                    # Preciso buscar todos os formset_data criados e montar as referências
                    f['fk'] = []
                    for i in fks:
                        f['fk'].append(i.pk)

        if post_update:
            post_update(self.pk, self.model, formset_delete)

    def test_delete(self):
        if self.verbosity > 1:
            print('Delete:')  # , self.formset_model._meta.verbose_name if self.formset_model else '')

        _url = "{}EditDelete".format(self.url)
        _data = self.fields_prepare(acao=ACAO_DELETE)
        args = [self.pk, ACAO_DELETE]

        response = post(_url, _data, args=args)
        try:
            error = [{k:v} for k,v in response.context['form'].errors.items()]
        except Exception:
            error = ''

        self.testcase.assertNotContains(response, 'submit-id-save',
                                        msg_prefix='Não fez formset_delete: {0}: {1}'.format(self.verbose, error))

        # Continua existindo?
        obj = self.model.objects.filter(pk=self.pk)
        self.testcase.assertFalse(obj.exists(), msg='Não foi deletado: {}'.format(self.verbose))

    def test_crud(self):
        if self.verbosity > 1:
            print('')
            print(self.model._meta.verbose_name)

        if self.insert:
            self.test_insert()
        else:
            # se não fez o insert então força a atualização dos dados de pk e instance
            self.pk_update()

        if self.update:
            self.test_update()
        if self.formset_delete:
            self.test_update(formset_delete=self.formset_delete)

        if self.delete:
            self.test_delete()

        # self.instance = self.model.objects.get(**self.pk_lookup)

        return self.instance


class Workflow_Test(CRUD_Test):
    """ Classe genérica para execução de testes padrão de workflow """

    def __init__(self, testcase, model, url, data, pk, pk_name='pk', prefix='main', formset=None,
                 formset_delete=True, duplicidade=True, insert=True, update=True, delete=True,
                 save='Salvar Andamento'):
        super().__init__(testcase, model, url, data, pk, pk_name, prefix, formset,
                         formset_delete, duplicidade, insert, update, delete)
        self.save = save

    def test_update(self, formset_delete=False, post_update=None):
        if self.verbosity > 1:
            print('Update:')  # , self.formset_model._meta.verbose_name if self.formset_model else '')

        # Acha o ProcessInstance da instance, isto é, o controle do workflow dessa instance
        self._qs = ProcessInstance.objects.get_process_by_instance(instance=self.instance)
        self.testcase.assertTrue(self._qs.exists(),
                                 msg='Não achou ProcessInstance para pk/instance no update: {}'.format(self.verbose))

        # De todos os ProcessInstance, pega o mais recente
        p = self._qs.first()
        # Com todos os Workitems do ProcessInstance, isto é, toda a história do workflow dessa instance
        # e pega o mais recente
        self._qs = p.workitems.all().order_by('-pk')
        self.testcase.assertTrue(self._qs.exists(),
                                 msg='Não achou Workitems do ProcessInstance no update: {}'.format(self.verbose))
        p = self._qs.first()
        args = [p.pk]

        # _url = "{}EditDelete".format(self.url)
        _url = 'workflow_action'
        _data = self.fields_prepare(acao=ACAO_EDIT, formset_delete=formset_delete)

        # Salva continuando o WF, não faz solicitação de aprovação
        _data.update(self._data)
        _data.update({'save': self.save})
        response = post(_url, _data, args=args)
        try:
            error = [{k:v} for k,v in response.context['form'].errors.items()]
        except Exception:
            error = ''

        self.testcase.assertNotContains(response, 'submit-id-save',
                                        msg_prefix='Não fez update: {0}: {1}'.format(self.verbose, error))

        # Continua existindo?
        obj = self.model.objects.filter(pk=self.pk)
        self.testcase.assertTrue(obj.exists(), msg='Foi deletado no update: {}'.format(self.verbose))

        # Se tem formset, então verifica se criou ou deletou
        if self.formset:
            for f in self.formset:
                fks = f['model'].objects.filter(**self.fk_lookup(f))
                if formset_delete:
                    # segunda vez, tem que ter deletetado todos os formsets
                    self.testcase.assertFalse(fks.exists(),
                                              msg='Formset não foi deletado no update: {}'.format(self.verbose))
                else:
                    # primeira vez, tem que ter criado o formset
                    self.testcase.assertTrue(fks.exists(), msg='Formset não foi criado no update: {}'.format(self.verbose))
                    # Preciso buscar todos os formset_data criados e montar as referências
                    f['fk'] = []
                    for i in fks:
                        f['fk'].append(i.pk)

        if post_update:
            post_update(self.pk, self.model, formset_delete)
