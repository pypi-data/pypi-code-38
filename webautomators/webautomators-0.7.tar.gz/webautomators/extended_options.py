from selenium.webdriver import ChromeOptions, FirefoxProfile
from selenium.webdriver.firefox.options import Options

###- annotation: 
###   mainTitle: webautomators.extended_options
class WebChromeOptions(ChromeOptions):
###   title: Class@ WebChromeOptions
###   text_description:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - ChromeOptions
###   text_description2:
###     - paragraph:
###       - "**Metodos**"

    def background(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**background** Rodar em Background"
###   return:
###     - void: none

        self.add_argument('--headless')

    def private(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**private** Rodar em modo privado"
###   return:
###     - void: none

        self.add_argument('--incognito')

    def maximized(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**maximized** Maximizar navegador"
###   return:
###     - void: none

        self.add_argument('--start-maximized')

    def set_path_user(self, perfil_path):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**set_path_user** Definir caminho do usuário"
###   parameters:
###     - str: perfil_path
###   return:
###     - void: none

        self.options.add_argument('user-data-dir={}'.format(perfil_path))

    def window_size(self, width, heigth):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**window_size** Definir tamanho da janela"
###   parameters:
###     - int: width
###     - int: heigth
###   return:
###     - void: none

        self.add_argument('--window-size={},{}'.format(width, heigth))

    def window_position(self, point_x, point_y):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**window_position** Definir tamanho da janela"
###   parameters:
###     - int: point_x
###     - int: point_y
###   return:
###     - void: none

        self.add_argument('--window-position={},{}'.format(point_x, point_y))

    def set_proxy(self, proxy):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**set_proxy** Definir proxy"
###   parameters:
###     - str: proxy
###   return:
###     - void: none

        self.add_argument('--proxy-server={}'.format(proxy))


###- annotation: 
###   mainTitle: webautomators.extended_options
class WebFirefoxOptions(Options):
###   title: Class@ WebFirefoxOptions
###   text_description:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - Options
###   text_description2:
###     - paragraph:
###       - "**Metodos**"

    def background(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**background** Rodar em Background"
###   return:
###     - void: none

        self.headless = True


###- annotation: 
###   mainTitle: webautomators.extended_options
class WebFirefoxProfile(FirefoxProfile):
###   title: Class@ WebFirefoxProfile
###   text_description:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - FirefoxProfile
###   text_description2:
###     - paragraph:
###       - "**Metodos**"

    def private(self):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**private** Rodar em modo privado"
###   return:
###     - void: none

        self.set_preference("browser.privatebrowsing.autostart", True)
