# from typing import List # not supported in 3.4

from selenium.common.exceptions import (NoAlertPresentException,
                                        TimeoutException)
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from webautomators import expected_conditions as wec
from webautomators.exceptions import ElementNotDisplayed, ElementNotFound
from webautomators.extend_wait import *
from webautomators.extended_webelement import ExtendedRemoteWebElement


###- annotation: 
###   mainTitle: webautomators.extended_driver
class WebExtendedDriver:
###   title: Class@ WebExtendedDriver
###   text_description:
###     - paragraph:
###       - "**Metodos**"

    def accept_alert(self, ignore_not_present=False):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**accept_alert** Aceita alerta"
###   parameters:
###     - boolean: ignore_not_present
###   return:
###     - void: None
        """Accepts alert.

        :Args:
         - ignore_not_present: ignore NoAlertPresentException
        """
        try:
            self.switch_to.alert.accept()
        except NoAlertPresentException:
            if not ignore_not_present:
                raise

    def alert_is_present(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**alert_is_present** "
###   return:
###     - void: Retorna se um alerta está presente

        """Returns whether an alert is present"""
        try:
            self.switch_to.alert
            return True
        except NoAlertPresentException:
            return False

    def close_window_by_index(self, index):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**close_window_by_index** Feche a janela / guia por índice."
###       - "Nota: A ordem em que os manipuladores de janela são retornados é arbitrária"
###   parameters:
###     - int: index
###   return:
###     - void: None

        """Close window/tab by index.
        Note: "The order in which the window handles are returned is arbitrary."

        :Args:
         - index: index of the window to close from window_handles
        """
        if index > len(self.window_handles) - 1:
            raise ValueError('Cannot close window {}, current amount is {}'
                             .format(index, len(self.window_handles)))
        else:
            handle_to_close = self.window_handles[index]
            self.close_window_switch_back(handle_to_close)

    def close_window_by_partial_title(self, partial_title):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**close_window_by_partial_title** Fechar janela/aba por title parcial"
###   parameters:
###     - str: partial_title
###   return:
###     - void: None

        """Close window/tab by partial title"""
        titles = self.get_window_titles()
        title_match = [title for title in titles if partial_title in title]
        if title_match:
            index = titles.index(title_match[0])
            handle_to_close = self.window_handles[index]
            self.close_window_switch_back(handle_to_close)
        else:
            msg = 'a window with partial title \'{}\' was not found'.format(
                partial_title)
            raise ValueError(msg)

    def close_window_by_partial_url(self, partial_url):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**close_window_by_partial_url** Fechar janela/aba por url parcial"
###   parameters:
###     - str: partial_url
###   return:
###     - void: None

        """Close window/tab by partial url"""
        urls = self.get_window_urls()
        url_match = [url for url in urls if partial_url in url]
        if url_match:
            index = urls.index(url_match[0])
            handle_to_close = self.window_handles[index]
            self.close_window_switch_back(handle_to_close)
        else:
            msg = 'a window with partial URL \'{}\' was not found'.format(
                partial_url)
            raise ValueError(msg)

    def close_window_by_title(self, title):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**close_window_by_title** Fechar janela/aba por title"
###   parameters:
###     - str: title
###   return:
###     - void: None

        """Close window/tab by title"""
        titles = self.get_window_titles()
        if title in titles:
            handle_to_close = self.window_handles[titles.index(title)]
            self.close_window_switch_back(handle_to_close)
        else:
            raise ValueError(
                'a window with title \'{}\' was not found'.format(title))

    def close_window_by_url(self, url):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**close_window_by_url** Fechar janela/aba por url"
###   parameters:
###     - str: url
###   return:
###     - void: None

        """Close window/tab by URL"""
        urls = self.get_window_urls()
        if url in urls:
            handle_to_close = self.window_handles[urls.index(url)]
            self.close_window_switch_back(handle_to_close)
        else:
            raise ValueError(
                'a window with URL \'{}\' was not found'.format(url))

    def close_window_switch_back(self, close_handle):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**close_window_switch_back** Feche uma janela / guia por alça e volte para a alça atual."
###       - Se o identificador atual for o mesmo que close_handle, tente mudar para a
###       - primeira janela / guia disponível.
###   parameters:
###     - str: close_handle
###   return:
###     - void: None

        """Close a window/tab by handle and switch back to current handle.
        If current handle is the same as close_handle, try to switch to the
        first available window/tab.
        """
        current_handle = self.current_window_handle
        self.switch_to.window(close_handle)
        self.close()
        if current_handle == close_handle:
            # closing active window, try to switch
            # to first window
            if self.window_handles:
                self.switch_to_first_window()
        else:
            # closing another window.
            # switch back to original handle
            self.switch_to.window(current_handle)

    def close_browser(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**close_browser** Fecha o navegador e todas a janelas/abas"
###   return:
###     - void: None

        """Close browser and all it's windows/tabs"""
        self.quit()

    def close_window(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**close_window** Fecha janela/aba atual."
###       - Se houver apenas uma janela, isso fechará o navegador também.
###       - Se houver outras janelas abertas, isso tentará alternar para
###       - a primeira janela 
###   return:
###     - void: None

        """Close current window/tab.
        If there is only one window, this will close the browser as well.
        If there are other windows open, this will try to switch to
        the first window depois.
        """
        browser_ = self
        browser_.close()
        if browser_.window_handles:
            browser_.switch_to_first_window()

    def dismiss_alert(self, ignore_not_present=False):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**dismiss_alert** Dispensar alerta." 
###   parameters:
###     - str: ignore_not_present
###   return:
###     - void: None

        """Dismiss alert.

        :Args:
         - ignore_not_present: ignore NoAlertPresentException
        """
        try:
            self.switch_to.alert.dismiss()
        except NoAlertPresentException:
            if not ignore_not_present:
                raise

    def element_is_present(self, element):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**element_is_present** Se o elemento está presente, retorna o elemento."
###       - Se o elemento não está presente retorna Falso.
###   parameters:
###     - webelement: element
###   return:
###     - void: element ou False

        """If element is present, return the element.
        If element is not present return False

        :Args:
        - element: an element tuple, a CSS string or a WebElement object
        """
        try:
            element = self.find(element, timeout=0)
            return element
        except ElementNotFound:
            return False

    def get_active_element(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**get_active_element** Retorna o elemento com foco, ou BODY se não tiver foco."
###       - Se o elemento não está presente retorna Falso.
###   return:
###     - void: element ou BODY

        """Returns the element with focus, or BODY if nothing has focus"""
        return self.switch_to.active_element

    def get_alert_text(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**get_alert_text** Pega texto do alerta."
###   return:
###     - void: texto do alerta

        """Get alert text"""
        return self.switch_to.alert.text

    def get_current_url(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**get_current_url** Retorna a URL atual do navegador."
###   return:
###     - void: Retorna URL atual

        """Return the current browser URL"""
        # return current_url
        return self.current_url

    def get_page_source(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**get_page_source** Pega o fonte da pagina."
###   return:
###     - void: Retorna fonte da pagina

        """Get the page source"""
        return self.page_source

    def get_name(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**get_name** Pega o nome."
###   return:
###     - void: Retorna nome

        return self.name

    def get_window_handle(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**get_window_handle** Obter o identificador da janela atual."
###   return:
###     - void: Retorna identificador da janela atual

        """Get current window handle"""
        return self.current_window_handle

    def get_window_handles(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**get_window_handlest** Retorna uma lista com todos os identificadores das janelas/abas abertas."
###   return:
###     - void: Retorna identificadores das janelas

        """Return a list with the handles of all the open windows/tabs"""
        return self.window_handles

    def get_window_title(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**get_window_title** Pega o titulo da pagina."
###   return:
###     - void: Retorna o titulo da pagina

        """Get window title"""
        return self.title

    def go_back(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**go_back** Volta uma pagina no historico do navegador."
###   return:
###     - void: None

        """Goes one step backward in the browser history"""
        self.back()

    def go_forward(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**go_forward** Vai uma para frente no historico do navegador."
###   return:
###     - void: None

        """Goes one step forward in the browser history"""
        self.forward()

    def get_window_index(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**get_window_index** Obtém o índice da janela/aba atual."
###   return:
###     - void: Retorna o índice da janela/aba atual.

        """Get the index of the current window/tab"""
        return self.window_handles.index(self.current_window_handle)

    def get_window_titles(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**get_window_titles** Pega uma lista com os titulos de todas as janelas/abas abertas."
###   return:
###     - void: Retorna uma lista com os titulos de todas as janelas/abas abertas.

        """Return a list of the titles of all open windows/tabs"""
        original_handle = self.current_window_handle
        titles = []
        for handle in self.window_handles:
            self.switch_to.window(handle)
            titles.append(self.title)
        self.switch_to.window(original_handle)
        return titles

    def get_window_urls(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**get_window_titles** Pega uma lista com as URL's de todas as janelas/abas abertas."
###   return:
###     - void: Retorna uma lista com as URL's de todas as janelas/abas abertas.

        """Return a list of the URLs of all open windows/tabs"""
        original_handle = self.current_window_handle
        urls = []
        for handle in self.window_handles:
            self.switch_to.window(handle)
            urls.append(self.current_url)
        self.switch_to.window(original_handle)
        return urls

    def navigate(self, url):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**navigate** Navega até a url recebida."
###   parameters:
###     - str: url
###   return:
###     - void: None
        """Navigate to a URL

        Parameters:
        url : value
        """
        self.get(url)

    def open_new_window(self, url):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**open_new_window** Abre uma nova janela e navega até a url recebida."
###   parameters:
###     - str: url
###   return:
###     - void: None

        """Navigate to a URL

        Parameters:
        url : value
        """
        self.execute_script("window.open(arguments[0])", url)

    def refresh_page(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**refresh_page** Recarrega a página."
###   return:
###     - void: None

        """Refresh the page"""
        self.refresh()

    def scroll_height(self, valor):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**scroll_height** Rola a tela para cima e para baixo."
###   parameters:
###     - int: valor
###   return:
###     - void: None

        """ Scroll screen to up and down"""
        self.execute_script(
            "window.scrollTo({valor}, document.body.scrollHeight);".format(valor=valor))

    def switch_to_first_window(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**switch_to_first_window** Mudar para a primeira Janela."
###   return:
###     - void: None

        """Switch to first window/tab"""
        self.switch_to_window_by_index(0)

    def switch_to_last_window(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**switch_to_last_window** Mudar para a última janela."
###   return:
###     - void: None

        """Switch to last window/tab"""
        self.switch_to.window(self.window_handles[-1])

    def switch_to_next_window(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**switch_to_next_window** Mudar para a proxima janela na lista de janelas ."
###       - Se a janela atual é ultima na lista isso vai circular de volta para o inicio
###   return:
###     - void: None
        """Switch to next window/tab in the list of window handles.
        If current window is the last in the list this will circle
        back from the start.
        """
        next_index = self.get_window_index() + 1
        if next_index < len(self.window_handles):
            self.switch_to_window_by_index(next_index)
        else:
            self.switch_to_window_by_index(0)

    def switch_to_previous_window(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**switch_to_previous_window** Mudar para a janela anterior na lista de janelas ."
###       - Se a janela atual é primeira na lista isso vai circular de volta para o final
###   return:
###     - void: None

        """Switch to previous window/tab in the list of window handles.
        If current window is the first in the list this will circle
        back from the top.
        """
        previous_index = self.get_window_index() - 1
        if previous_index >= 0:
            self.switch_to_window_by_index(previous_index)
        else:
            self.switch_to_window_by_index(len(self.window_handles) - 1)

    def switch_to_window_by_index(self, index):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**switch_to_window_by_index** Mudar para a janela/aba por index."
###       - A ordem em que as alças da janela são retornadas é arbitraria
###   parameters:
###     - int: index
###   return:
###     - void: None

        """Switch to window/tab by index.
        Note: "The order in which the window handles are returned is arbitrary."
        """
        self.switch_to.window(self.window_handles[index])

    def switch_to_window_by_partial_title(self, partial_title):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**switch_to_window_by_partial_title** Mudar para a janela/aba por titulo parcial."
###   parameters:
###     - str: partial_title
###   return:
###     - void: None

        """Switch to window/tab by partial title"""
        for handle in self.window_handles:
            self.switch_to.window(handle)
            if partial_title in self.title:
                return
        raise Exception(
            'Window with partial title \'{}\' was not found'.format(partial_title))

    def switch_to_window_by_partial_url(self, partial_url):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**switch_to_window_by_partial_url** Mudar para a janela/aba por url parcial."
###   parameters:
###     - str: partial_url
###   return:
###     - void: None

        """Switch to window/tab by partial URL"""
        for handle in self.window_handles:
            self.switch_to.window(handle)
            if partial_url in self.current_url:
                return
        raise Exception(
            'Window with partial URL \'{}\' was not found'.format(partial_url))

    def switch_to_window_by_title(self, title):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**switch_to_window_by_title** Mudar para a janela/aba por titulo."
###   parameters:
###     - str: title
###   return:
###     - void: None

        """Switch to window/tab by title"""
        for handle in self.window_handles:
            self.switch_to.window(handle)
            if self.title == title:
                return
        raise Exception('Window with title \'{}\' was not found'.format(title))

    def switch_to_window_by_url(self, url):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**switch_to_window_by_url** Mudar para a janela/aba por url."
###   parameters:
###     - str: url
###   return:
###     - void: None

        """Switch to window/tab by URL"""
        for handle in self.window_handles:
            self.switch_to.window(handle)
            if self.current_url == url:
                return
        raise Exception('Window with URL \'{}\' was not found'.format(url))

    def send_text_to_alert(self, text):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**send_text_to_alert** Enviar texto para um alerta."
###   parameters:
###     - str: text
###   return:
###     - void: None

        """Send text to an alert

        Parameters:
        text : value
        """
        self.switch_to.alert.send_keys(text)

    def submit_form(self, form_element):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**submit_form** Enviar formulario."
###       - Elemento pode ser o próprio formulario ou qualquer elemento filho.
###   parameters:
###     - webelement: form_element
###   return:
###     - void: None

        """Submit form.
        Element can be the form itself or any child element.

        Parameters:
        form_element : element
        """
        self.find(form_element).submit()

    def submit_prompt_alert(self, text):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**submit_prompt_alert** Enviar texto para um alerta de prompt e aceitá-lo."
###       - Se não houver alerta imediato, isso falhará.
###   parameters:
###     - str: text
###   return:
###     - void: None

        """Send text to a prompt alert and accept it.
        If there is no prompt alert present this will fail.

        Parameters:
        text : value
        """
        self.switch_to.alert.send_keys(text)
        self.switch_to.alert.accept()

    def switch_to_frame(self, frame):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**switch_to_frame** Mudar para o frame."
###       - frame deve ser o indice, nome ou o próprio webelement de frame.
###   parameters:
###     - str: frame
###   return:
###     - void: None

        """Switch to frame.
        frame must be the index, name, or the frame webelement itself.

        Parameters:
        frame : value
        """
        self.switch_to.frame(frame)

    def switch_to_parent_frame(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**switch_to_parent_frame** Mudar para pai do frame atual."
###   return:
###     - void: None

        """Switch to the parent of the current frame"""
        self.switch_to.parent_frame()

    def wait_for_alert_present(self, timeout):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_for_alert_present** Espera que um alerta esteja presente."
###   parameters:
###     - int: timeout
###   return:
###     - void: None

        """Wait for an alert to be present

        :Args:
        - timeout: time to wait (in seconds)
        """
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for alert to be present'
        wait.until(ec.alert_is_present(), message=message)

    def wait_for_element_not_present(self, element, timeout):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_for_element_not_present** Aguarde o elemento não estar presente no DOM."
###   parameters:
###     - int: timeout
###     - webelement: element
###   return:
###     - void: None

        """Wait for element not present in the DOM

        :Args:
        - element: an element tuple, a CSS string or a WebElement object
        - timeout: time to wait (in seconds)
        """
        found_element = None
        try:
            found_element = self.find(element, timeout=0)
        except ElementNotFound:
            pass
        if found_element:
            wait = WebDriverWait(self, timeout)
            message = ('Timeout waiting for element {} to not be present'
                       .format(found_element.name))
            wait.until(ec.staleness_of(found_element), message=message)

    def wait_for_page_contains_text(self, text, timeout):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_for_page_contains_text** Esperar por página para conter texto."
###   parameters:
###     - int: timeout
###     - str: text
###   return:
###     - void: None

        """Wait for page to contains text

        :Args:
        - text: text to be contained in page source
        - timeout: time to wait (in seconds)
        """
        wait = WebDriverWait(self, timeout)
        message = "Timeout waiting for page to contain '{}'".format(text)
        wait.until(wec.text_to_be_present_in_page(text), message=message)

    def wait_for_page_not_contains_text(self, text, timeout):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_for_page_not_contains_text** Esperar por página que não contem texto."
###   parameters:
###     - int: timeout
###     - str: text
###   return:
###     - void: None

        """Wait for page to not contain text

        :Args:
        - text: text to not be contained in page source
        - timeout: time to wait (in seconds)
        """
        wait = WebDriverWait(self, timeout)
        message = "Timeout waiting for page to not contain '{}'".format(text)
        wait.until_not(wec.text_to_be_present_in_page(text), message=message)

    def wait_for_title(self, title, timeout):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_for_title** Espera titulo da pagina ser o valor fornecido."
###   parameters:
###     - int: timeout
###     - str: title
###   return:
###     - void: None

        """Wait for page title to be the given value

        :Args:
        - title: expected title
        - timeout: time to wait (in seconds)
        """
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for title to be \'{}\''.format(title)
        wait.until(ec.title_is(title), message=message)

    def wait_for_title_contains(self, partial_title, timeout):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_for_title_contains** Espera titulo da pagina conter o valor fornecido."
###   parameters:
###     - int: timeout
###     - str: partial_title
###   return:
###     - void: None

        """Wait for page title to contain partial_title

        :Args:
        - partial_title: expected partial title
        - timeout: time to wait (in seconds)
        """
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for title to contain \'{}\''.format(
            partial_title)
        wait.until(ec.title_contains(partial_title), message=message)

    def wait_for_title_is_not(self, title, timeout):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_for_title_is_not** Espera titulo da pagina não seja o valor fornecido."
###   parameters:
###     - int: timeout
###     - str: title
###   return:
###     - void: None

        """Wait for page title to not be the given value

        :Args:
        - title: not expected title
        - timeout: time to wait (in seconds)
        """
        wait = Wait(self, timeout)
        message = 'Timeout waiting for title to not be \'{}\''.format(title)
        wait.until_not(ec.title_is(title), message=message)

    def wait_for_title_not_contains(self, partial_title, timeout):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_for_title_not_contains** Espera titulo da pagina não contenha titulo parcial."
###   parameters:
###     - int: timeout
###     - str: partial_title
###   return:
###     - void: None

        """Wait for page title to not contain partial_title

        :Args:
        - partial_title: not expected partial title
        - timeout: time to wait (in seconds)
        """
        wait = Wait(self, timeout)
        message = 'Timeout waiting for title to not contain \'{}\''.format(
            partial_title)
        wait.until_not(ec.title_contains(partial_title), message=message)

    def wait_for_window_present_by_partial_title(self, partial_title, timeout):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_for_title_not_contains** Espera pela janela/aba presente pelo titulo parcial."
###   parameters:
###     - int: timeout
###     - str: partial_title
###   return:
###     - void: None

        """Wait for window/tab present by partial title"""
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for window present by partial title \'{}\''.format(
            partial_title)
        wait.until(wec.window_present_by_partial_title(
            partial_title), message=message)

    def wait_for_window_present_by_partial_url(self, partial_url, timeout):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_for_window_present_by_partial_url** Espera pela janela/aba presente por url parcial."
###   parameters:
###     - int: timeout
###     - str: partial_title
###   return:
###     - void: None

        """Wait for window/tab present by partial url"""
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for window present by partial url \'{}\''.format(
            partial_url)
        wait.until(
            wec.window_present_by_partial_url(partial_url),
            message=message)

    def wait_for_window_present_by_title(self, title, timeout):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_for_window_present_by_title** Espera pela janela/aba presente por titulo."
###   parameters:
###     - int: timeout
###     - str: title
###   return:
###     - void: None

        """Wait for window/tab present by title"""
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for window present by title \'{}\''.format(
            title)
        wait.until(wec.window_present_by_title(title), message=message)

    def wait_for_window_present_by_url(self, url, timeout):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_for_window_present_by_url** Espera pela janela/aba presente por url."
###   parameters:
###     - int: timeout
###     - str: url
###   return:
###     - void: None

        """Wait for window/tab present by url"""
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for window present by url \'{}\''.format(
            url)
        wait.until(wec.window_present_by_url(url), message=message)
