### - annotation: 
###   mainTitle:  webdriver._ _ _init_ _ _
###   text_description:
###     - paragraph:
###       - Neste arquivo esta todas as instancias para utilizar dos drivers, e criar o objeto que contera todos os metodos do Lib.
###   title: Imports
###   unorderedList:
###     - selenium.webdriver.Chrome
###     - selenium.webdriver.Edge
###     - selenium.webdriver.Firefox
###     - selenium.webdriver.Ie
###     - selenium.webdriver.Remote
###     - webautomators.actions.Actions
from selenium.webdriver import Chrome as SeleniumChromeDriver
from selenium.webdriver import Edge as SeleniumEdgeDriver
from selenium.webdriver import Firefox as SeleniumGeckoDriver
from selenium.webdriver import Ie as SeleniumIeDriver
from selenium.webdriver import Opera as SeleniumOperaDriver
from selenium.webdriver import Remote as SeleniumRemoteDriver

from webautomators.actions import Actions


class WebChromeDriver(SeleniumChromeDriver, Actions):
    pass
### - annotation: 
###   title: Class@ WebChromeDriver
###   text_description1:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - Chrome
###     - Actions
###   text_description2:
###     - paragraph:
###       - "_"
###     - paragraph:
###       - "**Metodos**"
###     - paragraph:
###       - 'Construtor/_ _ _init_ _ _'
###   parameters:
###     - str: executable_path='chromedriver'
###     - int: port=0
###     - WebChromeOptions: options=None
###     - list: service_args=None
###     - dict: desired_capabilities=None
###     - str: service_log_path=None
###   ex:
###     - language: python
###     - browser= WebChromeDriver(executable_path="docs/chromedriver")
###   ex1:
###     - language: python
###     - browser= WebChromeDriver(options=WebChromeOptions())
###   return:
###     - WebChromeDriver: Instancia


class WebEdgeDriver(SeleniumEdgeDriver, Actions):
    pass
### - annotation: 
###   title: Class@ WebEdgeDriver
###   text_description1:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - Edge
###     - Actions
###   text_description2:
###     - paragraph:
###       - "_"
###     - paragraph:
###       - "**Metodos**"
###     - paragraph:
###       - 'Construtor/_ _ _init_ _ _'
###   parameters:
###     - str: executable_path='MicrosoftWebDriver.exe'
###     - int: port=DEFAULT_PORT
###     - str: log_path=DEFAULT_SERVICE_LOG_PATH
###     - list: service=None
###     - dict: capabilities=None
###     - str: service_log_path=None
###     - bool: verbose=False
###   ex:
###     - language: python
###     - browser= WebEdgeDriver(executable_path="docs/'MicrosoftWebDriver.exe")
###   ex1:
###     - language: python
###     - browser= WebEdgeDriver(log_path="log/log_edge.log")
###   return:
###     - WebEdgeDriver: Instancia

class WebGeckoDriver(SeleniumGeckoDriver, Actions):
    pass
### - annotation: 
###   title: Class@ WebGeckoDriver
###   text_description1:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - Firefox
###     - Actions
###   text_description2:
###     - paragraph:
###       - "_"
###     - paragraph:
###       - "**Metodos**"
###     - paragraph:
###       - 'Construtor/_ _ _init_ _ _'
###   parameters:
###     - WebFirefoxProfile: firefox_profile=None 
###     - str: firefox_binary=None
###     - int: timeout=30
###     - dict: capabilities=None
###     - Proxy: proxy=None
###     - str: executable_path="geckodriver"
###     - WebFirefoxOptions: options=None
###     - str: service_log_path="geckodriver.log"
###     - list: service_args=None
###     - str: log_path=None
###   ex:
###     - language: python
###     - browser= WebGeckoDriver(executable_path="docs/geckodriver.exe")
###   return:
###     - WebGeckoDriver: Instancia


class WebIeDriver(SeleniumIeDriver, Actions):
    pass
### - annotation: 
###   title: Class@ WebIeDriver
###   text_description1:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - Ie
###     - Actions
###   text_description2:
###     - paragraph:
###       - "_"
###     - paragraph:
###       - "**Metodos**"
###     - paragraph:
###       - 'Construtor/_ _ _init_ _ _'
###   parameters:
###     - str: executable_path='IEDriverServer.exe'
###     - dict: capabilities=None
###     - int: port=DEFAULT_PORT
###     - int: timeout=DEFAULT_TIMEOUT
###     - str: host=DEFAULT_HOST
###     - int: log_level=DEFAULT_LOG_LEVEL
###     - str: service_log_path=DEFAULT_SERVICE_LOG_PATH
###   ex1:
###     - language: python
###     - browser= WebIeDriver()
###   return:
###     - WebIeDriver: Instancia

class WebRemoteDriver(SeleniumRemoteDriver, Actions):
    pass
### - annotation: 
###   title: Class@ WebRemoteDriver
###   text_description1:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - Remote
###     - Actions
###   text_description2:
###     - paragraph:
###       - "_"
###     - paragraph:
###       - "**Metodos**"
###     - paragraph:
###       - 'Construtor/_ _ _init_ _ _'
###   parameters:
###     - str: command_executor='http://127.0.0.1:4444/wd/hub'
###     - dict: desired_capabilities=None
###     - str: browser_profile=None
###     - Proxy: proxy=None
###     - dict: options=None
###   ex1:
###     - language: python
###     - browser= WebRemoteDriver("http://127.0.0.1:4444/wd/hub",DesiredCapabilities.CHROME)
###     - browser= WebRemoteDriver("http://zalenium:4444/wd/hub",DesiredCapabilities.CHROME)
###   return:
###     - WebRemoteDriver: Instancia
