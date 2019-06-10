import time

from selenium.webdriver.remote.webelement import WebElement

from webautomators.extended_driver import WebExtendedDriver

#from exceptions import ElementNotFound

###- annotation: 
###   mainTitle: webautomators.extended_find
class FindElemennt():
###   title: Class@ FindElemennt
###   text_description:
###     - paragraph:
###       - "**Metodos**"

    # def find_by_text(self,*args,**kwargs,reference=None):
    #    if reference==None:
    #        raise Exception
    #    if len(args) == 1:
    #        kwargs['element'] = args[0]
    #    list_elements=self._find_all(self, **kwargs)
    #    for element in list_elements:
    #        if(element.text==kwargs['element']):
    #            return element

    #    raise ElementNotFound

    def find(self, *args, **kwargs):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**find** Critérios de pesquisa: O primeiro argumento deve ser: uma tupla de elemento, uma string CSS ou"
###       - um objeto WebElement.
###       - "Critérios de pesquisa de palavra-chave: id, nome, link_text, partial_link_text,"
###       - css, xpath, tag_name.
###       - Apenas um critério de pesquisa deve ser fornecido. 
###   parameters:
###     - list: *args
###     - dict: **kwargs
###   return:
###     - void: a webautomators.webdriver.extended_webelement.ExtendedRemoteWebElement

        """Find a WebElement

        Search criteria:
        The first argument must be: an element tuple, a CSS string or
        a WebElement object.
        Keyword search criteria: id, name, link_text, partial_link_text,
        css, xpath, tag_name.
        Only one search criteria should be provided.

        Other args:
        - timeout: timeout (in seconds) to wait for element to be present.
                   by default it uses the *search_timeout* setting value
        - wait_displayed: wait for element to be displayed (visible).
                          by default uses the *wait_displayed* setting value

        :Usage:
            driver.find('div#someId > input.class')
            driver.find(('id', 'someId'))
            driver.find(id='someId')
            driver.find(xpath='//div/input', timeout=5, wait_displayed=True)

        :Returns:
          a webautomators.webdriver.extended_webelement.ExtendedRemoteWebElement
        """
        if len(args) == 1:
            kwargs['element'] = args[0]
        return self._find(**kwargs)

    # should use type annotation:
    # from typing import List
    # -> List[ExtendedRemoteWebElement]
    # typing not supported in 3.4
    def find_all(self, *args, **kwargs):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**find_all** Critérios de pesquisa: O primeiro argumento deve ser: uma tupla de elemento, uma string CSS ou"
###       - um objeto WebElement.
###       - "Critérios de pesquisa de palavra-chave: id, nome, link_text, partial_link_text,"
###       - css, xpath, tag_name.
###       - Apenas um critério de pesquisa deve ser fornecido. 
###   parameters:
###     - list: *args
###     - dict: **kwargs
###   return:
###     - void: uma lista de ExtendedRemoteWebElement

        
        """Find all WebElements that match the search criteria.

        Search criteria:
        The first argument must be: an element tuple, a CSS string or
        a WebElement object.
        Keyword search criteria: id, name, link_text, partial_link_text,
        css, xpath, tag_name.
        Only one search criteria should be provided.

        :Usage:
            driver.find_all('div#someId > span.class')
            driver.find(('tag_name', 'input'))
            driver.find(xpath='//div/input')

        :Returns:
            a list of ExtendedRemoteWebElement
        """
        if len(args) == 1:
            kwargs['element'] = args[0]
        return self._find_all(self, **kwargs)

    def _find_webelement(self, selector_type, selector_value, element_name,
                         wait_displayed=False, attempt=1, implicit=10):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**find_webelement** Encontra um elemento da web."
###   parameters:
###     - string: selector_type
###     - int: selector_value
###     - string: element_name
###     - boolean: wait_displayed
###     - int: attempt
###     - int: implicit 
###   return:
###     - void:  none

        """Finds a web element."""
        webelement = None
        self.implicitly_wait(implicit)
        try:
            if selector_type == 'id':
                webelement = self.find_element_by_id(selector_value)
            elif selector_type == 'css':
                webelement = self.find_element_by_css_selector(selector_value)
            elif selector_type == 'link_text':
                webelement = self.find_element_by_link_text(selector_value)
            elif selector_type == 'partial_link_text':
                webelement = self.find_element_by_partial_link_text(
                    selector_value)
            elif selector_type == 'name':
                webelement = self.find_element_by_name(selector_value)
            elif selector_type == 'xpath':
                webelement = self.find_element_by_xpath(selector_value)
            elif selector_type == 'tag_name':
                webelement = self.find_element_by_tag_name(selector_value)
            else:
                msg = 'Selector {} is not a valid option'.format(selector_type)
                raise IncorrectSelectorType(msg)
        except BaseException:
            pass
        if webelement is None:
            raise ElementNotFound(
                'Element {0} not found using selector {1}:\'{2}\'' .format(
                    element_name, selector_type, selector_value))
        else:
            if wait_displayed:
                while not webelement.is_displayed() or attempt != 0:
                    time.sleep(0.5)
                    attempt -= 1
                if not webelement.is_displayed():
                    msg = (
                        'Timeout waiting for element {0} to be displayed, '
                        'using selector {1}:\'{2}\'' .format(
                            element_name, selector_type, selector_value))
                    raise ElementNotDisplayed(msg)
            return webelement

    def _find(self, element=None, id=None, name=None,
              link_text=None, partial_link_text=None, css=None,
              xpath=None, tag_name=None, timeout=None, wait_displayed=None):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**_find** Encontra um elemento da web. Um elemento pode ser:"
###       - um elemento web
###       - uma tupla com formato (<selector_type>, <selector_value>, [<display_nane>])
###       - uma string de seletor css 
###   parameters:
###     - webelement: element
###     -int: id
###     -string: name
###     -string: link_text
###     -string: partial_link_text
###     -string: css
###     -string: xpath
###     -string: tag_name
###     -int: timeout
###     -int: wait_displayed
###   return:
###     - void:  none
        """Find a webelement.

        `element` can be:
        a web element
        a tuple with format (<selector_type>, <selector_value>, [<display_nane>])
        a css selector string
        """
        # TODO: avoid circular import
        from webautomators.extended_webelement import ExtendedWebElement, extend_webelement
        webelement = None

        selector_type = None
        selector_value = None
        element_name = None

        if isinstance(
                element,
                WebElement) or isinstance(
                element,
                ExtendedWebElement):
            webelement = element
        elif isinstance(element, tuple):
            selector_type = element[0]
            selector_value = element[1]
            element_name = element[2] if len(element) == 3 else element[1]
        elif isinstance(element, str):
            selector_type = 'css'
            selector_value = element
            element_name = element
        elif id:
            selector_type = 'id'
            selector_value = element_name = id
        elif name:
            selector_type = 'name'
            selector_value = element_name = name
        elif link_text:
            selector_type = 'link_text'
            selector_value = element_name = link_text
        elif partial_link_text:
            selector_type = 'partial_link_text'
            selector_value = element_name = partial_link_text
        elif css:
            selector_type = 'css'
            selector_value = element_name = css
        elif xpath:
            selector_type = 'xpath'
            selector_value = element_name = xpath
        elif tag_name:
            selector_type = 'tag_name'
            selector_value = element_name = tag_name
        else:
            raise IncorrectSelectorType('Selector is not a valid option')

        if not webelement:
            webelement = self._find_webelement(
                selector_type,
                selector_value,
                element_name,
                wait_displayed,
                timeout)
            webelement.selector_type = selector_type
            webelement.selector_value = selector_value
            webelement.name = element_name

        return extend_webelement(webelement)

    def _find_all(self, element=None, id=None, name=None, link_text=None,
                  partial_link_text=None, css=None, xpath=None, tag_name=None):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**_find_all** Encontra todos os elementos da web. Um elemento pode ser:"
###       - uma tupla com formato (<selector_type>, <selector_value>, [<display_nane>])
###       - uma string de seletor css 
###   parameters:
###     - webelement: element
###     -int: id
###     -string: name
###     -string: link_text
###     -string: partial_link_text
###     -string: css
###     -string: xpath
###     -string: tag_name
###   return:
###     - void:  none
        """Find all webelements

        `element` can be:
        a tuple with format (<selector_type>, <selector_value>, [<display_nane>])
        a css selector string
        """
        # TODO: avoid circular import
        from webautomators.extended_webelement import extend_webelement
        webelements = []
        tuple_element_name = None
        if isinstance(element, tuple):
            selector_type = element[0]
            selector_value = element[1]
            tuple_element_name = element[2] if len(
                element) >= 3 else element[1]
            if selector_type == 'id':
                id = selector_value
            elif selector_type == 'css':
                css = selector_value
            elif selector_type == 'link_text':
                link_text = selector_value
            elif selector_type == 'partial_link_text':
                partial_link_text = selector_value
            elif selector_type == 'name':
                name = selector_value
            elif selector_type == 'xpath':
                xpath = selector_value
            elif selector_type == 'tag_name':
                tag_name = selector_value
            else:
                raise Exception('Incorrect element {}'.format(element))
        elif isinstance(element, str):
            css = element

        if id:
            selector_type = 'id'
            selector_value = id
            element_name = tuple_element_name or id
            webelements = self.find_elements_by_id(id)
        elif css:
            selector_type = 'css'
            selector_value = css
            element_name = tuple_element_name or css
            webelements = self.find_elements_by_css_selector(css)
        elif link_text:
            selector_type = 'link_text'
            selector_value = link_text
            element_name = tuple_element_name or link_text
            webelements = self.find_elements_by_link_text(link_text)
        elif partial_link_text:
            selector_type = 'partial_link_text'
            selector_value = partial_link_text
            element_name = tuple_element_name or partial_link_text
            webelements = self.find_elements_by_partial_link_text(
                partial_link_text)
        elif name:
            selector_type = 'name'
            selector_value = name
            element_name = tuple_element_name or name
            webelements = self.find_elements_by_name(name)
        elif xpath:
            selector_type = 'xpath'
            selector_value = xpath
            element_name = tuple_element_name or xpath
            webelements = self.find_elements_by_xpath(xpath)
        elif tag_name:
            selector_type = 'tag_name'
            selector_value = element_name = tag_name
            element_name = tuple_element_name or tag_name
            webelements = self.find_elements_by_tag_name(tag_name)
        else:
            raise IncorrectSelectorType('Incorrect selector provided')

        extended_webelements = []
        for elem in webelements:
            elem.selector_type = selector_type
            elem.selector_value = selector_value
            elem.name = element_name
            extended_webelements.append(extend_webelement(elem))

        return extended_webelements
import time

from selenium.webdriver.remote.webelement import WebElement

from webautomators.extended_driver import WebExtendedDriver

#from exceptions import ElementNotFound

###- annotation: 
###   mainTitle: webautomators.extended_find
class FindElemennt():
###   title: Class@ FindElemennt
###   text_description:
###     - paragraph:
###       - "**Metodos**"

    # def find_by_text(self,*args,**kwargs,reference=None):
    #    if reference==None:
    #        raise Exception
    #    if len(args) == 1:
    #        kwargs['element'] = args[0]
    #    list_elements=self._find_all(self, **kwargs)
    #    for element in list_elements:
    #        if(element.text==kwargs['element']):
    #            return element

    #    raise ElementNotFound

    def find(self, *args, **kwargs):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**find** Critérios de pesquisa: O primeiro argumento deve ser: uma tupla de elemento, uma string CSS ou"
###       - um objeto WebElement.
###       - "Critérios de pesquisa de palavra-chave: id, nome, link_text, partial_link_text,"
###       - css, xpath, tag_name.
###       - Apenas um critério de pesquisa deve ser fornecido. 
###   parameters:
###     - list: *args
###     - dict: **kwargs
###   return:
###     - void: a webautomators.webdriver.extended_webelement.ExtendedRemoteWebElement

        """Find a WebElement

        Search criteria:
        The first argument must be: an element tuple, a CSS string or
        a WebElement object.
        Keyword search criteria: id, name, link_text, partial_link_text,
        css, xpath, tag_name.
        Only one search criteria should be provided.

        Other args:
        - timeout: timeout (in seconds) to wait for element to be present.
                   by default it uses the *search_timeout* setting value
        - wait_displayed: wait for element to be displayed (visible).
                          by default uses the *wait_displayed* setting value

        :Usage:
            driver.find('div#someId > input.class')
            driver.find(('id', 'someId'))
            driver.find(id='someId')
            driver.find(xpath='//div/input', timeout=5, wait_displayed=True)

        :Returns:
          a webautomators.webdriver.extended_webelement.ExtendedRemoteWebElement
        """
        if len(args) == 1:
            kwargs['element'] = args[0]
        return self._find(**kwargs)

    # should use type annotation:
    # from typing import List
    # -> List[ExtendedRemoteWebElement]
    # typing not supported in 3.4
    def find_all(self, *args, **kwargs):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**find_all** Critérios de pesquisa: O primeiro argumento deve ser: uma tupla de elemento, uma string CSS ou"
###       - um objeto WebElement.
###       - "Critérios de pesquisa de palavra-chave: id, nome, link_text, partial_link_text,"
###       - css, xpath, tag_name.
###       - Apenas um critério de pesquisa deve ser fornecido. 
###   parameters:
###     - list: *args
###     - dict: **kwargs
###   return:
###     - void: uma lista de ExtendedRemoteWebElement

        
        """Find all WebElements that match the search criteria.

        Search criteria:
        The first argument must be: an element tuple, a CSS string or
        a WebElement object.
        Keyword search criteria: id, name, link_text, partial_link_text,
        css, xpath, tag_name.
        Only one search criteria should be provided.

        :Usage:
            driver.find_all('div#someId > span.class')
            driver.find(('tag_name', 'input'))
            driver.find(xpath='//div/input')

        :Returns:
            a list of ExtendedRemoteWebElement
        """
        if len(args) == 1:
            kwargs['element'] = args[0]
        return self._find_all(self, **kwargs)

    def _find_webelement(self, selector_type, selector_value, element_name,
                         wait_displayed=False, attempt=1, implicit=10):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**find_webelement** Encontra um elemento da web."
###   parameters:
###     - string: selector_type
###     - int: selector_value
###     - string: element_name
###     - boolean: wait_displayed
###     - int: attempt
###     - int: implicit 
###   return:
###     - void:  none

        """Finds a web element."""
        webelement = None
        self.implicitly_wait(implicit)
        try:
            if selector_type == 'id':
                webelement = self.find_element_by_id(selector_value)
            elif selector_type == 'css':
                webelement = self.find_element_by_css_selector(selector_value)
            elif selector_type == 'link_text':
                webelement = self.find_element_by_link_text(selector_value)
            elif selector_type == 'partial_link_text':
                webelement = self.find_element_by_partial_link_text(
                    selector_value)
            elif selector_type == 'name':
                webelement = self.find_element_by_name(selector_value)
            elif selector_type == 'xpath':
                webelement = self.find_element_by_xpath(selector_value)
            elif selector_type == 'tag_name':
                webelement = self.find_element_by_tag_name(selector_value)
            else:
                msg = 'Selector {} is not a valid option'.format(selector_type)
                raise IncorrectSelectorType(msg)
        except BaseException:
            pass
        if webelement is None:
            raise ElementNotFound(
                'Element {0} not found using selector {1}:\'{2}\'' .format(
                    element_name, selector_type, selector_value))
        else:
            if wait_displayed:
                while not webelement.is_displayed() or attempt != 0:
                    time.sleep(0.5)
                    attempt -= 1
                if not webelement.is_displayed():
                    msg = (
                        'Timeout waiting for element {0} to be displayed, '
                        'using selector {1}:\'{2}\'' .format(
                            element_name, selector_type, selector_value))
                    raise ElementNotDisplayed(msg)
            return webelement

    def _find(self, element=None, id=None, name=None,
              link_text=None, partial_link_text=None, css=None,
              xpath=None, tag_name=None, timeout=None, wait_displayed=None):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**_find** Encontra um elemento da web. Um elemento pode ser:"
###       - um elemento web
###       - uma tupla com formato (<selector_type>, <selector_value>, [<display_nane>])
###       - uma string de seletor css 
###   parameters:
###     - webelement: element
###     -int: id
###     -string: name
###     -string: link_text
###     -string: partial_link_text
###     -string: css
###     -string: xpath
###     -string: tag_name
###     -int: timeout
###     -int: wait_displayed
###   return:
###     - void:  none
        """Find a webelement.

        `element` can be:
        a web element
        a tuple with format (<selector_type>, <selector_value>, [<display_nane>])
        a css selector string
        """
        # TODO: avoid circular import
        from webautomators.extended_webelement import ExtendedWebElement, extend_webelement
        webelement = None

        selector_type = None
        selector_value = None
        element_name = None

        if isinstance(
                element,
                WebElement) or isinstance(
                element,
                ExtendedWebElement):
            webelement = element
        elif isinstance(element, tuple):
            selector_type = element[0]
            selector_value = element[1]
            element_name = element[2] if len(element) == 3 else element[1]
        elif isinstance(element, str):
            selector_type = 'css'
            selector_value = element
            element_name = element
        elif id:
            selector_type = 'id'
            selector_value = element_name = id
        elif name:
            selector_type = 'name'
            selector_value = element_name = name
        elif link_text:
            selector_type = 'link_text'
            selector_value = element_name = link_text
        elif partial_link_text:
            selector_type = 'partial_link_text'
            selector_value = element_name = partial_link_text
        elif css:
            selector_type = 'css'
            selector_value = element_name = css
        elif xpath:
            selector_type = 'xpath'
            selector_value = element_name = xpath
        elif tag_name:
            selector_type = 'tag_name'
            selector_value = element_name = tag_name
        else:
            raise IncorrectSelectorType('Selector is not a valid option')

        if not webelement:
            webelement = self._find_webelement(
                selector_type,
                selector_value,
                element_name,
                wait_displayed,
                timeout)
            webelement.selector_type = selector_type
            webelement.selector_value = selector_value
            webelement.name = element_name

        return extend_webelement(webelement)

    def _find_all(self, element=None, id=None, name=None, link_text=None,
                  partial_link_text=None, css=None, xpath=None, tag_name=None):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**_find_all** Encontra todos os elementos da web. Um elemento pode ser:"
###       - uma tupla com formato (<selector_type>, <selector_value>, [<display_nane>])
###       - uma string de seletor css 
###   parameters:
###     - webelement: element
###     -int: id
###     -string: name
###     -string: link_text
###     -string: partial_link_text
###     -string: css
###     -string: xpath
###     -string: tag_name
###   return:
###     - void:  none
        """Find all webelements

        `element` can be:
        a tuple with format (<selector_type>, <selector_value>, [<display_nane>])
        a css selector string
        """
        # TODO: avoid circular import
        from webautomators.extended_webelement import extend_webelement
        webelements = []
        tuple_element_name = None
        if isinstance(element, tuple):
            selector_type = element[0]
            selector_value = element[1]
            tuple_element_name = element[2] if len(
                element) >= 3 else element[1]
            if selector_type == 'id':
                id = selector_value
            elif selector_type == 'css':
                css = selector_value
            elif selector_type == 'link_text':
                link_text = selector_value
            elif selector_type == 'partial_link_text':
                partial_link_text = selector_value
            elif selector_type == 'name':
                name = selector_value
            elif selector_type == 'xpath':
                xpath = selector_value
            elif selector_type == 'tag_name':
                tag_name = selector_value
            else:
                raise Exception('Incorrect element {}'.format(element))
        elif isinstance(element, str):
            css = element

        if id:
            selector_type = 'id'
            selector_value = id
            element_name = tuple_element_name or id
            webelements = self.find_elements_by_id(id)
        elif css:
            selector_type = 'css'
            selector_value = css
            element_name = tuple_element_name or css
            webelements = self.find_elements_by_css_selector(css)
        elif link_text:
            selector_type = 'link_text'
            selector_value = link_text
            element_name = tuple_element_name or link_text
            webelements = self.find_elements_by_link_text(link_text)
        elif partial_link_text:
            selector_type = 'partial_link_text'
            selector_value = partial_link_text
            element_name = tuple_element_name or partial_link_text
            webelements = self.find_elements_by_partial_link_text(
                partial_link_text)
        elif name:
            selector_type = 'name'
            selector_value = name
            element_name = tuple_element_name or name
            webelements = self.find_elements_by_name(name)
        elif xpath:
            selector_type = 'xpath'
            selector_value = xpath
            element_name = tuple_element_name or xpath
            webelements = self.find_elements_by_xpath(xpath)
        elif tag_name:
            selector_type = 'tag_name'
            selector_value = element_name = tag_name
            element_name = tuple_element_name or tag_name
            webelements = self.find_elements_by_tag_name(tag_name)
        else:
            raise IncorrectSelectorType('Incorrect selector provided')

        extended_webelements = []
        for elem in webelements:
            elem.selector_type = selector_type
            elem.selector_value = selector_value
            elem.name = element_name
            extended_webelements.append(extend_webelement(elem))

        return extended_webelements
