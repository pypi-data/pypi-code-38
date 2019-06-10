import time

import requests

from webautomators.extended_driver import WebExtendedDriver
from webautomators.extended_find import FindElemennt


###- annotation:
###   mainTitle: webautomators.actions
class Actions(WebExtendedDriver, FindElemennt):
###   title: Class@ Actions
###   text_description1:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - WebExtendedDriver
###     - FindElemennt
###   text_description2:
###     - paragraph:
###       - "_"
###     - paragraph:
###       - "**Metodos**"

    def assert_alert_not_present(self):
###- annotation:        
###   text_description3:
###     - paragraph:
###       - "**assert_alert_not_present** verifica se existe alerta no browser."
###   return3:
###     - void: None
        assert not self.alert_is_present(), 'an alert was present'

    def assert_alert_present(self):
###- annotation:
###   text_description4:
###     - paragraph:
###       - "**assert_alert_present** afirmar que um alerta está presente."
###   return4:
###     - void: None
        """Assert an alert is present"""
        assert self.alert_is_present(), 'an alert was not present'

    def assert_alert_text(self, text):
###- annotation:
###   text_description5:
###     - paragraph:
###       - "**assert_alert_text** declarar texto de alerta, Isso falhará se não houver nenhum alerta presente."
###   parameters5:
###     - str: text 
###   return5:
###     - void: None
        """Assert alert text
        This will fail if there is no alert present.

        Parameters:
        text : value
        """
        alert_text = self.switch_to.alert.text
        error_msg = "expected alert text to be '{}' but was '{}'".format(
            text, alert_text)
        assert alert_text == text, error_msg

    def assert_alert_text_is_not(self, text):
###- annotation:
###   text_description6:
###     - paragraph:
###       - "**assert_alert_text_is_not** declarar texto de alerta não aparece, Isso falhará se não houver nenhum alerta presente."
###   parameters6:
###     - str: text 
###   return6:
###     - void: None
        """Assert alert text is not `text`
        This will fail if there is no alert present.

        Parameters:
        text : value
        """
        alert_text = self.switch_to.alert.text
        error_msg = "expected alert text not to be '{}'".format(text)
        assert alert_text != text, error_msg

    def assert_amount_of_windows(self, amount):
###- annotation:
###   text_description7:
###     - paragraph:
###       - "**assert_amount_of_windows** Afirme a quantidade de janelas / abas abertas."
###   parameters7:
###     - int: amount 
###   return7:
###     - void: None
        """Assert the amount of open windows/tabs

        Parameters:
        amount : value
        """
        actual_amount = len(self.get_window_handles())
        error_msg = 'expected {} windows but got {}'.format(
            amount, actual_amount)
        assert actual_amount == amount, error_msg

    def assert_cookie_present(self, name):
###- annotation: 
###   text_description8:
###     - paragraph:
###       - "**assert_cookie_present** Afirma que um cookie existe na sessão atual. O cookie é encontrado pelo seu nome"
###   parameters8:
###     - str: name 
###   return8:
###     - void: None 
        """Assert a cookie exists in the current session.
        The cookie is found by its name.

        Parameters:
        name: value
        """
        cookie = self.get_cookie(name)
        assert cookie, "cookie '{}' was not found".format(name)

    def assert_cookie_value(self, name, value):
###- annotation: 
###   text_description9:
###     - paragraph:
###       - "**assert_cookie_value** Afirma o valor de um cookie, Isso falhará se um cookie não existir"
###   parameters9:
###     - str: name
###     - str: value
###   return9:
###     - void: None  
        """Assert the value of a cookie.
        This will fail if the cookie does not exist.

        Parameters:
        name: value
        value: value
        """
        cookie = self.get_cookie(name)
        if not cookie:
            raise Exception('Cookie "{}" was not found'.format(name))
        elif 'value' not in cookie:
            raise Exception(
                'Cookie "{}" did not have "value" key'.format(name))
        else:
            msg = (
                "expected cookie '{}' value to be '{}' but was '{}'".format(
                    name, value, cookie['value']))
            assert cookie['value'] == value, msg

    def assert_element_attribute(self, element, attribute, value):
###- annotation: 
###   text_description10:
###     - paragraph:
###       - "**assert_element_attribute** Afirma valor do atributo do elemento"
###   parameters10:
###     - webelement: element
###     - str: value
###     - str: attribute
###   return10:
###     - void: None
        """Assert value of element attribute

        Parameters:
        element : element
        attribute : value
        value : value
        """
        element = self.find(element, timeout=0)
        attr_value = element.get_attribute(attribute)
        msg = ("expected element {} attribute {} value to be '{}' was '{}'"
               .format(element.name, attribute, value, attr_value))
        assert attr_value == value, msg

    def assert_element_attribute_is_not(self, element, attribute, value):
###- annotation: 
###   text_description11:
###     - paragraph:
###       - "**assert_element_attribute_is_not** Afirme que o valor do atributo do elemento não é `value'"
###   parameters11:
###     - webelement: element
###     - str: attribute
###     - str: value
###   return11:
###     - void: None
        """Assert the value of element attribute is not `value`

        Parameters:
        element : element
        attribute : value
        value : value
        """
        element = self.find(element, timeout=0)
        attr_value = element.get_attribute(attribute)
        msg = ('expected element {} attribute {} value to not be {}'
               .format(element.name, attribute, value))
        assert attr_value != value, msg

    def assert_element_checked(self, element):
###- annotation: 
###   text_description12:
###     - paragraph:
###       - "**assert_element_checked** O elemento de declaração está marcado. Isso se aplica a caixas de seleção e botões de opção"
###   parameters12:
###     - webelement: element
###   return12:
###     - void: None
        """Assert element is checked.
        This applies to checkboxes and radio buttons.

        Parameters:
        element : element
        """
        element = self.find(element, timeout=0)
        assert element.is_selected(), 'element {} is not checked'.format(element.name)

    def assert_element_displayed(self, element):
###- annotation: 
###   text_description13:
###     - paragraph:
###       - "**assert_element_displayed** Elemento de declaração é exibido (visível para o usuário)"
###   parameters13:
###     - webelement: element
###   return13:
###     - void: None
        """Assert element is displayed (visible to the user)

        Parameters:
        element : element
        """
        element = self.find(element, timeout=0, wait_displayed=False)
        assert element.is_displayed(), 'element {} is not displayed'.format(element.name)

    def assert_element_enabled(self, element):
###- annotation: 
###   text_description14:
###     - paragraph:
###       - "**assert_element_enabled** Afirma que o elemento está ativado"
###   parameters14:
###     - webelement: element
###   return14:
###     - void: None
        """Assert element is enabled.

        Parameters:
        element : element
        """
        element = self.find(element, timeout=0)
        assert element.is_enabled(), 'element {} is not enabled'.format(element.name)

    def assert_element_has_attribute(self, element, attribute):
###- annotation: 
###   text_description15:
###     - paragraph:
###       - "**assert_element_has_attribute** Afirma que o elemento tem atributo"
###   parameters15:
###     - webelement: element
###     - str: attribute
###   return15:
###     - void: None
        """Assert element has attribute

        Parameters:
        element : element
        attribute : value
        """
        element = self.find(element, timeout=0)
        error_msg = 'element {} does not have attribute {}'.format(
            element.name, attribute)
        assert element.has_attribute(attribute), error_msg

    def assert_element_has_focus(self, element):
###- annotation: 
###   text_description16:
###     - paragraph:
###       - "**assert_element_has_focus** Afirma que o elemento tem focus"
###   parameters16:
###     - webelement: element
###   return16:
###     - void: None
        """Assert element has focus

        Parameters:
        element : element
        """
        element = self.find(element, timeout=0)
        error_msg = 'element {} does not have focus'.format(element.name)
        assert element.has_focus(), error_msg

    def assert_element_has_not_attribute(self, element, attribute):
###- annotation: 
###   text_description17:
###     - paragraph:
###       - "**assert_element_has_not_attribute** Afirma que o elemento não tem atributo"
###   parameters17:
###     - webelement: element
###     - str: attribute
###   return17:
###     - void: None
        """Assert element has not attribute

        Parameters:
        element : element
        attribute : value
        """
        element = self.find(element, timeout=0)
        error_msg = 'element {} has attribute {}'.format(
            element.name, attribute)
        assert not element.has_attribute(attribute), error_msg

    def assert_element_has_not_focus(self, element):
###- annotation: 
###   text_description18:
###     - paragraph:
###       - "**assert_element_has_not_focus** Afirma que o elemento de declaração não tem focu"
###   parameters18:
###     - webelement: element
###   return18:
###     - void: None
        """Assert element does not have focus

        Parameters:
        element : element
        """
        element = self.find(element, timeout=0)
        error_msg = 'element {} has focus'.format(element.name)
        assert not element.has_focus(), error_msg

    def assert_element_not_checked(self, element):
###- annotation: 
###   text_description19:
###     - paragraph:
###       - "**assert_element_not_checked** Afirma que o elemento está marcado. Isso se aplica a caixas de seleção e botões de opção."
###   parameters19:
###     - webelement: element
###   return19:
###     - void: None
        """Assert element is not checked.
        This applies to checkboxes and radio buttons.

        Parameters:
        element : element
        """
        element = self.find(element, timeout=0)
        assert not element.is_selected(), 'element {} is checked'.format(element.name)

    def assert_element_not_displayed(self, element):
###- annotation: 
###   text_description20:
###     - paragraph:
###       - "**assert_element_not_displayed** O elemento de declaração não é exibido (visível para o usuário)"
###   parameters20:
###     - webelement: element
###   return20:
###     - void: None
        """Assert element is not displayed (visible to the user)

        Parameters:
        element : element
        """
        element = self.find(element, timeout=0, wait_displayed=False)
        assert not element.is_displayed(), 'element {} is displayed'.format(element.name)

    def assert_element_not_enabled(self, element):
###- annotation: 
###   text_description21:
###     - paragraph:
###       - "**assert_element_not_enabled** Afirma que o elemento não está ativado"
###   parameters21:
###     - webelement: element
###   return21:
###     - void: None
        """Assert element is not enabled.

        Parameters:
        element : element
        """
        element = self.find(element, timeout=0)
        assert not element.is_enabled(), 'element {} is enabled'.format(element.name)

    def assert_element_not_present(self, element):
###- annotation: 
###   text_description22:
###     - paragraph:
###       - "**assert_element_not_present** Afirma que o elemento não está presente no DOM"
###   parameters22:
###     - webelement: element
###   return22:
###     - void: None
        """Assert element is not present in the DOM

        Parameters:
        element : element
        """
        msg = 'element {} is present'.format(element)
        assert not self.element_is_present(element), msg

    def assert_element_present(self, element):
###- annotation: 
###   text_description23:
###     - paragraph:
###       - "**assert_element_present** Afirma que o elemento está presente no DOM"
###   parameters23:
###     - webelement: element
###   return23:
###     - void: None
        """Assert element is present in the DOM

        Parameters:
        element : element
        """
        msg = 'element {} is not present'.format(element)
        assert self.element_is_present(element), msg

    def assert_element_text(self, element, text):
###- annotation: 
###   text_description24:
###     - paragraph:
###       - "**assert_element_text** Afirma o texto do elemento"
###   parameters24:
###     - webelement: element
###     - str: text
###   return24:
###     - void: None
        """Assert the text of the element

        Parameters:
        element : element
        text : value
        """
        element = self.find(element, timeout=0)
        msg = ("expected element {} text to be '{}' but was '{}'"
               .format(element.name, text, element.text))
        assert element.text == text, msg

    def assert_element_text_contains(self, element, text):
###- annotation: 
###   text_description25:
###     - paragraph:
###       - "**assert_element_text_contains** Afirma que elemento contem texto"
###   parameters25:
###     - webelement: element
###     - str: text
###   return25:
###     - void: None
        """Assert element contains text

        Parameters:
        element : element
        text : value
        """
        element = self.find(element, timeout=0)
        msg = ("expected element {} text '{}' to contain '{}'"
               .format(element.name, element.text, text))
        assert text in element.text, msg

    def assert_element_text_is_not(self, element, text):
###- annotation: 
###   text_description26:
###     - paragraph:
###       - "**assert_element_text_is_not** Afirma que o texto do elemento não é 'text'"
###   parameters26:
###     - webelement: element
###     - str: text
###   return26:
###     - void: None
        """Assert the text of the element is not `text`

        Parameters:
        element : element
        text : value
        """
        element = self.find(element, timeout=0)
        msg = "expected element {} text to not be '{}'".format(
            element.name, text)
        assert element.text != text, msg

    def assert_element_text_not_contains(self, element, text):
###- annotation: 
###   text_description27:
###     - paragraph:
###       - "**assert_element_text_is_not** Afirma que o texto do elemento não é 'text'"
###   parameters27:
###     - webelement: element
###     - str: text
###   return27:
###     - void: None
        """Assert the text of the element does not contain `text`

        Parameters:
        element : element
        text : value
        """
        element = self.find(element, timeout=0)
        msg = "element {} text '{}' contains text '{}'".format(
            element.name, element.text, text)
        assert text not in element.text, msg

    def assert_page_contains_text(self, text):
###- annotation: 
###   text_description28:
###     - paragraph:
###       - "**assert_page_contains_text** Afirme que o texto fornecido está presente em qualquer lugar na origem da página"
###   parameters28:
###     - str: text
###   return28:
###     - void: None
        """Assert the given text is present anywhere in the page source

        Parameters:
        text : value
        """
        assert text in self.page_source, "text '{}' not found in the page".format(
            text)

    def assert_page_not_contains_text(self, text):
###- annotation: 
###   text_description29:
###     - paragraph:
###       - "**assert_page_not_contains_text** Afirme que o texto fornecido não está presente em qualquer lugar na origem da página"
###   parameters29:
###     - str: text
###   return29:
###     - void: None
        """Assert the given text is not present anywhere in the page source

        Parameters:
        text : value
        """
        assert text not in self.page_source, "text '{}' was found in the page".format(
            text)

    @staticmethod
    def assert_response_status_code(response, status_code):
###- annotation: 
###   text_description30:
###     - paragraph:
###       - "**assert_response_status_code** Afirma que a resposta é igual a 'status_code'"
###   parameters30:
###     - int: status_code
###     - response: response
###   return30:
###     - void: None
        """Assert the response status code.

        Parameters:
        response : value
        status_code : value
        """
        if isinstance(status_code, str):
            if status_code.isdigit():
                status_code = int(status_code)
        msg = ('expected response status code to be {} but was {}'
               .format(status_code, response.status_code))
        assert response.status_code == status_code, msg

    def assert_selected_option_by_text(self, element, text):
###- annotation: 
###   text_description31:
###     - paragraph:
###       - "**assert_selected_option_by_text** Afirmar que um elemento tem uma opção selecionada pelo texto da opção"
###   parameters31:
###     - webelement: element
###     - str: text
###   return31:
###     - void: None
        """Assert an element has a selected option by the option text

        Parameters:
        element : element
        text : value
        """
        element = self.find(element)
        selected_option_text = element.select.first_selected_option.text
        error_msg = (
            "expected selected option in element {} to be '{}' but was '{}'" .format(
                element.name, text, selected_option_text))
        assert selected_option_text == text, error_msg

    def assert_selected_option_by_value(self, element, value):
###- annotation: 
###   text_description32:
###     - paragraph:
###       - "**assert_selected_option_by_value** Afirmar que um elemento tem uma opção selecionada pelo valor da opção"
###   parameters32:
###     - webelement: element
###     - str: value
###   return32:
###     - void: None
        """Assert an element has a selected option by the option value

        Parameters:
        element : element
        value : value
        """
        element = self.find(element)
        selected_option_value = element.select.first_selected_option.value
        error_msg = (
            'expected selected option in element {} to be {} but was {}' .format(
                element.name, value, selected_option_value))
        assert selected_option_value == value, error_msg

    def assert_title(self, title):
###- annotation: 
###   text_description33:
###     - paragraph:
###       - "**assert_title** Afirma o titulo da pagina"
###   parameters33:
###     - str: title
###   return33:
###     - void: None
        """Assert the page title

        Parameters:
        title : value
        """
        error_msg = ("expected title to be '{}' but was '{}'"
                     .format(title, self.title))
        assert self.title == title, error_msg

    def assert_title_contains(self, partial_title):
###- annotation: 
###   text_description34:
###     - paragraph:
###       - "**assert_title_contains** Afirma que o titulo da pagina contem 'partial_title'"
###   parameters34:
###     - str: partial_title
###   return34:
###     - void: None
        """Assert the page title contains partial_title

        Parameters:
        partial_title : value
        """
        error_msg = "expected title to contain '{}'".format(partial_title)
        assert partial_title in self.title, error_msg

    def assert_title_is_not(self, title):
###- annotation: 
###   text_description35:
###     - paragraph:
###       - "**assert_title_is_not** Afirma que o titulo da pagina não o fornecido"
###   parameters35:
###     - str: title
###   return35:
###     - void: None
        """Assert the page title is not the given value

        Parameters:
        title : value
        """
        error_msg = "expected title to not be '{}'".format(title)
        assert self.title != title, error_msg

    def assert_title_not_contains(self, text):
###- annotation: 
###   text_description36:
###     - paragraph:
###       - "**assert_title_not_contains** Afirma que o titulo da pagina não contem 'text'"
###   parameters36:
###     - str: text
###   return36:
###     - void: None
        """Assert the page title does not contain text

        Parameters:
        text : value
        """
        error_msg = "title contains '{}'".format(text)
        assert text not in self.title, error_msg

    def assert_url(self, url):
###- annotation: 
###   text_description37:
###     - paragraph:
###       - "**assert_url** Afirma a URL atual"
###   parameters37:
###     - str: url
###   return37:
###     - void: None
        """Assert the current URL

        Parameters:
        url : value
        """
        error_msg = ("expected URL to be '{}' but was '{}'"
                     .format(url, self.current_url))
        assert self.current_url == url, error_msg

    def assert_url_contains(self, partial_url):
###- annotation: 
###   text_description38:
###     - paragraph:
###       - "**assert_url_contains** Afirma a URL atual contem 'partial_url'"
###   parameters38:
###     - str: partial_url
###   return38:
###     - void: None
        """Assert the current URL contains partial_url

        Parameters:
        partial_url : value
        """
        error_msg = "expected URL to contain '{}'".format(partial_url)
        assert partial_url in self.current_url, error_msg

    def assert_url_is_not(self, url):
###- annotation: 
###   text_description39:
###     - paragraph:
###       - "**assert_url_is_not** Afirma que a URL atual não é 'url'"
###   parameters39:
###     - str: url
###   return39:
###     - void: None
        """Assert the current URL is not `url`

        Parameters:
        url : value
        """
        error_msg = "expected URL to not be '{}'".format(url)
        assert self.current_url != url, error_msg

    def assert_url_not_contains(self, partial_url):
###- annotation: 
###   text_description40:
###     - paragraph:
###       - "**assert_url_not_contains** Afirma a URL atual não contem 'partial_url'"
###   parameters40:
###     - str: partial_url
###   return40:
###     - void: None
        """Assert the current URL does not contain partial_url

        Parameters:
        partial_url : value
        """
        actual_url = self.current_url
        error_msg = ("expected URL '{}' to not contain '{}'"
                     .format(actual_url, partial_url))
        assert partial_url not in actual_url, error_msg

    def assert_window_present_by_partial_title(self, partial_title):
###- annotation: 
###   text_description41:
###     - paragraph:
###       - "**assert_window_present_by_partial_title** Afirmar que há uma janela / guia presente por 'partial_title'"
###   parameters41:
###     - str: partial_title
###   return41:
###     - void: None
        """Assert there is a window/tab present by partial title

        Parameters:
        partial_title : value
        """
        error_msg = "There is no window present with partial title '{}'".format(
            partial_title)
        window_titles = self.get_window_titles()
        assert any(partial_title in t for t in window_titles), error_msg

    def assert_window_present_by_partial_url(self, partial_url):
###- annotation: 
###   text_description42:
###     - paragraph:
###       - "**assert_window_present_by_partial_url** Afirmar que há uma janela / guia presente por 'partial_url'"
###   parameters42:
###     - str: partial_url
###   return42:
###     - void: None
        """Assert there is a window/tab present by partial URL

        Parameters:
        partial_url : value
        """
        urls = self.get_window_urls()
        error_msg = "There is no window present with partial URL '{}'".format(
            partial_url)
        assert any(partial_url in url for url in urls), error_msg

    def assert_window_present_by_title(self, title):
###- annotation: 
###   text_description43:
###     - paragraph:
###       - "**assert_window_present_by_title** Afirma qual é a janela/aba presente por 'title'"
###   parameters43:
###     - str: title
###   return43:
###     - void: None
        """Assert there is a window/tab present by title

        Parameters:
        title : value
        """
        error_msg = "There is no window present with title '{}'".format(title)
        assert title in self.get_window_titles(), error_msg

    def assert_window_present_by_url(self, url):
###- annotation: 
###   text_description44:
###     - paragraph:
###       - "**assert_window_present_by_url** Afirma qual é a janela/aba presente por 'url'"
###   parameters44:
###     - str: url
###   return44:
###     - void: None
        """Assert there is a window/tab present by URL

        Parameters:
        url : value
        """
        error_msg = "There is no window present with URL '{}'".format(url)
        assert url in self.get_window_urls(), error_msg

    @staticmethod
    def http_get(url, headers={}, params={}, verify_ssl_cert=True):
###- annotation: 
###   text_description45:
###     - paragraph:
###       - "**assert_window_present_by_url** Execute uma solicitação HTTP GET para o URL fornecido."
###       - Cabeçalhos e params são dicionários opcionais.
###       - Armazenar resposta em data.last_response
###       - Retorna a resposta.
###   parameters45:
###     - str: url
###     - dict: headers
###     - dict: params
###     - boolean: verify_ssl_cert
###   return45:
###     - void: response
        """Perform an HTTP GET request to the given URL.
        Headers and params are optional dictionaries.
        Store response in data.last_response
        Returns the response

        Parameters:
        url : value
        headers (optional, dict) : value
        params (optional, dict) : value
        verify_ssl_cert (optional, True) : value
        """
        response = requests.get(url, headers=headers, params=params,
                                verify=verify_ssl_cert)
        return response

    @staticmethod
    def http_post(url, headers={}, data={}, verify_ssl_cert=True):
###- annotation: 
###   text_description46:
###     - paragraph:
###       - "**assert_window_present_by_url** Execute uma solicitação HTTP POST para o URL fornecido."
###       - Cabeçalhos e dados são dicionários opcionais.
###       - Armazena a resposta em data.last_response
###       - Retorna a resposta.
###   parameters46:
###     - str: url
###     - dict: headers
###     - dict: data
###     - boolean: verify_ssl_cert
###   return46:
###     - void: response
        """Perform an HTTP POST request to the given URL.
        Headers and data are optional dictionaries.
        Stores the response in data.last_response
        Returns the response

        Parameters:
        url : value
        headers (optional, dict) : value
        data (optional, dict) : value
        verify_ssl_cert (optional, default is True) : value
        """
        response = requests.post(url, headers=headers, data=data,
                                 verify=verify_ssl_cert)
        return response

    def select_option_by_index(self, element, index):
###- annotation: 
###   text_description47:
###     - paragraph:
###       - "**select_option_by_index** Selecione uma opção em uma lista suspensa de seleção por índice"
###   parameters47:
###     - webelement: element
###     - int: index
###   return47:
###     - void: None
        """Select an option from a select dropdown by index.

        Parameters:
        element : element
        index : value
        """
        element = self.find(element)
        element.select.select_by_index(index)

    def select_option_by_text(self, element, text):
###- annotation: 
###   text_description48:
###     - paragraph:
###       - "**select_option_by_text** Selecione uma opção em uma lista suspensa de seleção por texto"
###   parameters48:
###     - webelement: element
###     - str: text
###   return48:
###     - void: None
        """Select an option from a select dropdown by text.

        Parameters:
        element : element
        text : value
        """
        element = self.find(element)
        element.select.select_by_visible_text(text)

    def select_option_by_value(self, element, value):
###- annotation: 
###   text_description49:
###     - paragraph:
###       - "**select_option_by_value** Selecione uma opção em uma lista suspensa de seleção por valor"
###   parameters49:
###     - webelement: element
###     - str: value
###   return49:
###     - void: None
        """Select an option from a select dropdown by value.

        Parameters:
        element : element
        value : value
        """
        element = self.find(element)
        element.select.select_by_value(value)

    @staticmethod
    def wait(seconds):
###- annotation: 
###   text_description50:
###     - paragraph:
###       - "**wait** Aguarde por um periodo fixo de segundos."
###   parameters50:
###     - int: seconds
###   return50:
###     - void: None
        """Wait for a fixed amount of seconds.

        Parameters:
        seconds (int or float) : value
        """
        try:
            to_float = float(seconds)
        except BaseException:
            raise ValueError('seconds value should be a number')
        time.sleep(to_float)
