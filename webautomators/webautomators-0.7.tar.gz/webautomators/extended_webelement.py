# from typing import List # not supported in 3.4

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium.webdriver.remote.webelement import WebElement as RemoteWebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select as SeleniumSelect
from selenium.webdriver.support.ui import WebDriverWait

from webautomators import expected_conditions as wec


###- annotation: 
###   mainTitle: webautomators.extended_webelement
class ExtendedWebElement:
###   title: Class@ ExtendedWebElement
###   text_description:
###     - paragraph:
###       - "**Metodos**"

    selector_type = None
    selector_value = None
    name = None

    def check(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**check** Verifica se o elemento é caixa de seleção ou botçao de opção." 
###       - Se o elemento já estiver marcado, isso é ignorado 
###   return:
###     - void: none
        """Check element if element is checkbox or radiobutton.
        If element is already checked, this is ignored.
        """
        checkbox_or_radio = (
            self.tag_name == 'input' and self.get_attribute('type') in [
                'checkbox', 'radio'])
        if checkbox_or_radio:
            if not self.is_selected():
                self.click()
        else:
            msg = 'Element {} is not checkbox or radiobutton'.format(self.name)
            raise ValueError(msg)

    def double_click(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**double_click** Clique duplo no elemento" 
###   return:
###     - void: none

        """Double click the element"""
        action_chains = ActionChains(self.parent)
        action_chains.double_click(self).perform()

    def drag_and_drop(self, target):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**drag_and_drop** Arrasta e solta alvo" 
###   parameters:
###     - str: target
###   return:
###     - void: none

        action_chains = ActionChains(self.parent)
        action_chains.drag_and_drop(self.parent, target.parent).perform()

    def focus(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**focus** Dá foco ao elemento" 
###   return:
###     - void: none
        """Give focus to element"""
        self.parent.execute_script('arguments[0].focus();', self)

    def has_attribute(self, attribute):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**has_attribute** Verifica se o elemento tem atributo" 
###   parameters:
###     - string: attribute
###   return:
###     - void: Retorna se o elemento tem atributo.
        """Returns whether element has attribute"""
        return self.get_attribute(attribute) is not None

    def has_focus(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**has_focus** Verifica se o elemento tem foco" 
###   return:
###     - void: Retorna se o elemento tem foco.
        """Returns whether element has focus"""
        script = 'return arguments[0] == document.activeElement'
        return self.parent.execute_script(script, self)

    def javascript_click(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**javascript_click* Click no elento usando JavaScript." 
###   return:
###     - void: none.
        """Click element using Javascript"""
        self.parent.execute_script('arguments[0].click();', self)

    def mouse_click(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**mouse_click* Cursor no elemento." 
###   return:
###     - void: none.
        """Mouse over element"""
        action_chains = ActionChains(self.parent)
        action_chains.click(self).perform()

    def mouse_click_context(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**mouse_click_context* Cursor no elemento." 
###   return:
###     - void: none.
        """Mouse over element"""
        action_chains = ActionChains(self.parent)
        action_chains.context_click(self).perform()

    def mouse_over(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**mouse_over* Cursor no elemento" 
###   return:
###     - void: none.
        """Mouse over element"""
        action_chains = ActionChains(self.parent)
        action_chains.move_to_element(self).perform()
    

    @property
    def select(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**select** Seleciona um objeto."
###   return:
###     - void: Retorna um objeto selecionado.
        """Return a Select object"""
        return Select(self)

    def uncheck(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**uncheck** Desmarca o elemento se o elemento for caixa de seleção."
###       - Se o elemento já estiver desmarcado, isso será ignorado.
###   return:
###     - void: none.
        """Uncheck element if element is checkbox.
        If element is already unchecked, this is ignored.
        """
        is_checkbox = (self.tag_name == 'input' and
                       self.get_attribute('type') == 'checkbox')
        if is_checkbox:
            if self.is_selected():
                self.click()
        else:
            raise ValueError('Element {} is not checkbox'.format(self.name))

    @property
    def value(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**value** Valor atribuido do elemento."
###   return:
###     - void: none.
        """The value attribute of element"""
        return self.get_attribute('value')

    def wait_displayed(self, timeout=30):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_displayed** Aguarda o elemento a ser exibido."
###   parameters:
###     - int: timeout 
###   return:
###     - void: Retorna o elemento.
        """Wait for element to be displayed

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} to be displayed'
                   .format(self.name))
        wait.until(ec.visibility_of(self), message=message)
        return self

    def wait_enabled(self, timeout=30):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_enable** Aguarda o elemento a ser ativado."
###   parameters:
###     - int: timeout 
###   return:
###     - void: Retorna o elemento.
        """Wait for element to be enabled

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = 'Timeout waiting for element {} to be enabled'.format(
            self.name)
        wait.until(wec.element_to_be_enabled(self), message=message)
        return self

    def wait_has_attribute(self, attribute, timeout=30):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_has_attribute** Aguarda o elemento ter atributo"
###   parameters:
###     - int: timeout
###     - string: attribute
###   return:
###     - void: Retorna o elemento.        
        """Wait for element to have attribute

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} to have attribute {}'
                   .format(self.name, attribute))
        wait.until(
            wec.element_to_have_attribute(
                self,
                attribute),
            message=message)
        return self

    def wait_has_not_attribute(self, attribute, timeout=30):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_has_not_attribute** Aguarda o elemento não ter atributo"
###   parameters:
###     - int: timeout 
###     - string: attribute
###   return:
###     - void: Retorna o elemento.        
        """Wait for element to not have attribute

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} to not have attribute {}'
                   .format(self.name, attribute))
        wait.until_not(wec.element_to_have_attribute(self, attribute),
                       message=message)
        return self

    def wait_not_displayed(self, timeout=30):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_has_not_displayed** Aguarda o elemento não seja exibido"
###   parameters:
###     - int: timeout 
###   return:
###     - void: Retorna o elemento. 
        """Wait for element to be not displayed

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} to be not displayed'
                   .format(self.name))
        wait.until_not(ec.visibility_of(self), message=message)
        return self

    def wait_not_enabled(self, timeout=30):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_not_enable** Aguarda o elemento não ter atributo"
###   parameters:
###     - int: timeout 
###   return:
###     - void: Retorna o elemento.
        """Wait for element to be not enabled

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = 'Timeout waiting for element {} to be not enabled'.format(
            self.name)
        wait.until_not(wec.element_to_be_enabled(self), message=message)
        return self

    def wait_text(self, text, timeout=30):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_text** Aguarda o texto do elemento corresponder ao texto recebido"
###   parameters:
###     - int: timeout 
###     - string: text
###   return:
###     - void: Retorna o elemento.
        """Wait for element text to match given text

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} text to be \'{}\''
                   .format(self.name, text))
        wait.until(wec.element_text_to_be(self, text), message=message)
        return self

    def wait_text_contains(self, text, timeout=30):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_text_contains** Aguarda o elemento conter o texto recebido"
###   parameters:
###     - int: timeout 
###     - string: text
###   return:
###     - void: Retorna o elemento.
        """Wait for element to contain given text

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} text to contain \'{}\''
                   .format(self.name, text))
        wait.until(wec.element_text_to_contain(self, text), message=message)
        return self

    def wait_text_is_not(self, text, timeout=30):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_text_is_not** Aguarda que o texto do elemento não corresponda ao texto recebido"
###   parameters:
###     - int: timeout 
###     - string: text
###   return:
###     - void: Retorna o elemento.
        """Wait fo element text to not match given text

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} text not to be \'{}\''
                   .format(self.name, text))
        wait.until_not(wec.element_text_to_be(self, text), message=message)
        return self

    def wait_text_not_contains(self, text, timeout=30):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**wait_text_is_not_contains** Aguarda que o texto do elemento não contenha o texto "
###   parameters:
###     - int: timeout 
###     - string: text
###   return:
###     - void: Retorna o elemento.
        """Wait for element text to not contain text

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} text to not contain \'{}\''
                   .format(self.name, text))
        wait.until_not(wec.element_text_to_contain(self, text),
                       message=message)
        return self


class Select(SeleniumSelect):

    @property
    def first_selected_option(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**first_selected_option** Seleciona a primeira opção no webelement"
###   return:
###     - void: none
        """Return the first selected option as a
        ExtendedWebElement"""
        option = super(Select, self).first_selected_option
        return extend_webelement(option)

###- annotation: 
###   mainTitle: webautomators.extended_webelement
class ExtendedRemoteWebElement(RemoteWebElement, ExtendedWebElement):
###   title: Class@ ExtendedRemoteWebElement
###   text_description:
###     - paragraph:
###       - "**Metodos**"
    pass

###- annotation: 
###   mainTitle: webautomators.extended_webelement
class ExtendedFirefoxWebElement(FirefoxWebElement, ExtendedWebElement):
###   title: Class@ ExtendedFirefoxWebElement
###   text_description:
###     - paragraph:
###       - "**Metodos**"
    pass


def extend_webelement(web_element) -> ExtendedRemoteWebElement:
###- annotation:
###   text_description:
###     - paragraph:
###       - "**first_selected_option** Estende o webelement do selênio usando o ExtendedRemoteWebElement ou ExtendedFirefoxWebElement class "
###   parameters:
###     - string: web_element
###   return:
###     - void: none

    """Extend the selenium WebElement using the
    ExtendedRemoteWebElement or ExtendedFirefoxWebElement class
    """
    if isinstance(web_element.parent, FirefoxDriver):
        web_element.__class__ = ExtendedFirefoxWebElement
    else:
        web_element.__class__ = ExtendedRemoteWebElement
    return web_element
