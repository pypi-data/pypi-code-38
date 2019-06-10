import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

###- annotation: 
###   mainTitle: webautomators.extend_wait
class Wait(WebDriverWait):
###   title: Class@ Wait
###   text_description:
###     - paragraph:
###       - "**Herança**"
###   unorderedList:
###     - WebDriverWait
###   text_description2:
###     - paragraph:
###       - "**Metodos**"

    def until_not(self, method, message=''):
###- annotation:
###   text_description:
###     - paragraph:
###       - "**until_not** Chama o método fornecido com o driver como um argumento até que o \ valor de retorno é falso"
###   parameters:
###     - method: method
###     - str: message
###   return:
###     - void: Retorna true caso o method não funcione no tempo pré estabelecido
        """Calls the method provided with the driver as an argument until the \
        return value is False."""
        end_time = time.time() + self._timeout
        while True:
            try:
                value = method(self._driver)
                if value:
                    break
            except self._ignored_exceptions:
                return True
            time.sleep(self._poll)
            if time.time() > end_time:
                return True
        raise TimeoutException(message)
