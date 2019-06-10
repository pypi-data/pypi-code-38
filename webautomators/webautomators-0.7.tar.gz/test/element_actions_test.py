from unittest import TestCase
from webautomators import WebChromeDriver
from webautomators import WebGeckoDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ChromeOptions
import time
class TestElementActions(TestCase):
    def setUp(self):
        self.options=ChromeOptions()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--window-size=1420,1080')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.driver = WebChromeDriver(chrome_options=self.options)

    def test_double_click(self):
        self.driver.navigate('https://www.cvc.com.br/passagens-aereas')
        element = self.driver.find(id='ember872')
        element.double_click()
        self.driver.assert_element_checked(element)
        
    def test_has_attribute(self):
        self.driver.navigate('https://bing.com.br')
        element = self.driver.find(xpath='//*[@id="sb_form_q"]')
        a=element.has_attribute('search')
        assert a == False

    def test_checkbox(self):
        self.driver.navigate('https://www.cvc.com.br/resorts/')
        element = self.driver.find(xpath='/html/body/div[1]/div/div[2]/div/fieldset/div/label[2]/span[1]/span[1]/input')
        element.check()
        self.driver.assert_element_not_checked(element)

    def test_drag_and_drop(self):
        self.driver.navigate('https://www.w3schools.com/html/html5_draganddrop.asp')
        element = self.driver.find(xpath='//*[@id="div1"]')
        element2 = self.driver.find(xpath='//*[@id="div2"]')
        element.drag_and_drop(element2)

    def test_focus(self):
        self.driver.navigate('https://www.w3schools.com/html/html5_draganddrop.asp')
        elemenet=self.driver.find(xpath='//*[@id="footer"]/div[5]/div[4]/div/a[10]')
        elemenet.focus()
        self.driver.assert_element_has_focus(elemenet)
    
    def test_has_attribute(self):
        self.driver.navigate('https://www.w3schools.com/html/html5_draganddrop.asp')
        element = self.driver.find(xpath='//*[@id="div1"]')
        element.has_attribute("div1")
        self.driver.assert_element_has_attribute(element,'id')

    def test_has_focus(self):
        self.driver.navigate('https://www.w3schools.com/html/html5_draganddrop.asp')
        element = self.driver.find(xpath='//*[@id="div1"]')
        element.has_focus()
        self.driver.assert_element_has_focus(element)

    def test_javascript_click(self):
        self.driver.navigate('https://www.cvc.com.br/passagens-aereas')
        element = self.driver.find(id='ember872')
        element.javascript_click()
        self.driver.assert_element_checked(element)
    
    def test_mouse_click(self):
        self.driver.navigate('https://www.cvc.com.br/passagens-aereas')
        element = self.driver.find(id='ember872')
        element.mouse_click()
        self.driver.assert_element_checked(element)

    def test_mouse_click_context(self):
        self.driver.navigate('https://www.cvc.com.br/passagens-aereas')
        element = self.driver.find(id='ember872')
        element.mouse_click_context()
        self.driver.assert_element_not_checked(element)

    def test_mouse_over(self):
        self.driver.navigate('https://www.extra.com.br/')
        element = self.driver.find(xpath='//*[@id="navbar-collapse"]/div/nav/ul/li[1]')
        element.mouse_over()
        self.driver.assert_element_not_checked(element)

    def test_select_option_by_index(self):
        self.driver.navigate('https://www.cvc.com.br/passagens-aereas')
        element = self.driver.find(id='ember905')
        self.driver.select_option_by_index(element,2)

    def test_select_option_by_text(self):
        self.driver.navigate('https://www.cvc.com.br/passagens-aereas')
        element = self.driver.find(id='ember905')
        self.driver.select_option_by_text(element,"7")

    def test_select_option_by_value(self):
        self.driver.navigate('https://www.cvc.com.br/passagens-aereas')
        element = self.driver.find(id='ember905')
        self.driver.select_option_by_value(element,"7")


    def tearDown(self):
        self.driver.close()