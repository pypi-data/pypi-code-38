###- annotation: 
###   mainTitle: webautomators.expected_conditions 
class element_to_be_enabled(object):
###   title: Class@ element_to_be_enabled
###   text_description:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - object
###   text_description2:
###     - paragraph:
###       - "**Metodos**"

    """An Expectation for checking an element is enabled"""

    def __init__(self, element):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__init__** Construção do objeto com os parametros recebidos"
###   parameters:
###     - webelement: element
###   return:
###     - void: None
        self.element = element

    def __call__(self, driver):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__call__**"
###   parameters:
###     - WebDriver: driver
###   return:
###     - void: Retorna se o elemento é ativo
        return self.element.is_enabled()

###- annotation: 
###   mainTitle: webautomators.expected_conditions
class text_to_be_present_in_page(object):
###   title: Class@ text_to_be_present_in_page
###   text_description:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - object
###   text_description2:
###     - paragraph:
###       - "**Metodos**"
    """An Expectation for checking page contains text"""

    def __init__(self, text):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__init__** Construção do objeto com os parametros recebidos"
###   parameters:
###     - str: text
###   return:
###     - void: None
        self.text = text

    def __call__(self, driver):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__call__**"
###   parameters:
###     - WebDriver: driver
###   return:
###     - void: Retorna se texto entá em page_source do driver
        return self.text in driver.page_source

###- annotation: 
###   mainTitle: webautomators.expected_conditions
class element_text_to_be(object):
###   title: Class@ element_text_to_be
###   text_description:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - object
###   text_description2:
###     - paragraph:
###       - "**Metodos**"
    """An expectation for checking the given text matches element text"""

    def __init__(self, element, text):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__init__** Construção do objeto com os parametros recebidos"
###   parameters:
###     - str: text
###     - webelement: element
###   return:
###     - void: None
        self.element = element
        self.text = text

    def __call__(self, driver):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__call__**"
###   parameters:
###     - WebDriver: driver
###   return:
###     - void: Retorna se o texto do elemento é igual ao texto 
        return self.element.text == self.text

###- annotation: 
###   mainTitle: webautomators.expected_conditions
class element_text_to_contain(object):
###   title: Class@ element_text_to_contain
###   text_description:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - object
###   text_description2:
###     - paragraph:
###       - "**Metodos**"
    """An expectation for checking element contains the given text"""

    def __init__(self, element, text):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__init__** Construção do objeto com os parametros recebidos"
###   parameters:
###     - str: text
###     - webelement: element
###   return:
###     - void: None
        self.element = element
        self.text = text

    def __call__(self, driver):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__call__**"
###   parameters:
###     - WebDriver: driver
###   return:
###     - void: Retorna se o texto do elemento tem o texto recebido
        return self.text in self.element.text

###- annotation: 
###   mainTitle: webautomators.expected_conditions
class element_to_have_attribute(object):
###   title: Class@ element_to_have_attribute
###   text_description:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - object
###   text_description2:
###     - paragraph:
###       - "**Metodos**"
    """An expectation for checking element has attribute"""

    def __init__(self, element, attribute):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__init__** Construção do objeto com os parametros recebidos"
###   parameters:
###     - str: attribute
###     - webelement: element
###   return:
###     - void: None
        self.element = element
        self.attribute = attribute

    def __call__(self, driver):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__call__**"
###   parameters:
###     - WebDriver: driver
###   return:
###     - void: Retorna se o atributo do elemento é vazio
        return self.element.get_attribute(self.attribute) is not None

###- annotation: 
###   mainTitle: webautomators.expected_conditions
class window_present_by_partial_title(object):
###   title: Class@ window_present_by_partial_title
###   text_description:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - object
###   text_description2:
###     - paragraph:
###       - "**Metodos**"
    """An expectation for checking a window is present by partial title"""

    def __init__(self, partial_title):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__init__** Construção do objeto com os parametros recebidos"
###   parameters:
###     - str: partial_title
###   return:
###     - void: None
        self.partial_title = partial_title

    def __call__(self, driver):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__call__**"
###   parameters:
###     - WebDriver: driver
###   return:
###     - void: Retorna se a janela está presente pelo titulo parcial
        return any(self.partial_title in t for t in driver.get_window_titles())

###- annotation: 
###   mainTitle: webautomators.expected_conditions
class window_present_by_partial_url(object):
###   title: Class@ window_present_by_partial_url
###   text_description:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - object
###   text_description2:
###     - paragraph:
###       - "**Metodos**"
    """An expectation for checking a window is present by partial url"""

    def __init__(self, partial_url):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__init__** Construção do objeto com os parametros recebidos"
###   parameters:
###     - str: partial_url
###   return:
###     - void: None
        self.partial_url = partial_url

    def __call__(self, driver):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__call__**"
###   parameters:
###     - WebDriver: driver
###   return:
###     - void: Retorna se a janela está presente pelo url parcial
        return any(self.partial_url in u for u in driver.get_window_urls())

###- annotation: 
###   mainTitle: webautomators.expected_conditions
class window_present_by_title(object):
###   title: Class@ window_present_by_title
###   text_description:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - object
###   text_description2:
###     - paragraph:
###       - "**Metodos**"
    """An expectation for checking a window is present by title"""

    def __init__(self, title):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__init__** Construção do objeto com os parametros recebidos"
###   parameters:
###     - str: title
###   return:
###     - void: None
        self.title = title

    def __call__(self, driver):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__call__**"
###   parameters:
###     - WebDriver: driver
###   return:
###     - void: Retorna se a janela está presente pelo titulo
        return self.title in driver.get_window_titles()

###- annotation: 
###   mainTitle: webautomators.expected_conditions
class window_present_by_url(object):
###   title: Class@ window_present_by_url
###   text_description:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - object
###   text_description2:
###     - paragraph:
###       - "**Metodos**"
    """An expectation for checking a window is present by url"""

    def __init__(self, url):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__init__** Construção do objeto com os parametros recebidos"
###   parameters:
###     - str: url
###   return:
###     - void: None
        self.url = url

    def __call__(self, driver):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**__call__**"
###   parameters:
###     - WebDriver: driver
###   return:
###     - void: Retorna se a janela está presente pelo url
        return self.url in driver.get_window_urls()
