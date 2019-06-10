from unittest import TestCase
from webautomators import WebChromeDriver
from webautomators import WebGeckoDriver
from selenium.webdriver.common.keys import Keys
from webautomators.extended_find import *
from selenium.webdriver import ChromeOptions
import time

class TestExtendedFind(TestCase):
    def setUp(self):
        self.options=ChromeOptions()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--window-size=1420,1080')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.driver = WebChromeDriver(chrome_options=self.options)
    
    def test_01_find(self):
        self.driver.navigate('https://www.python.org/')
        element = self.driver.find(id='top')
        assert True == isinstance(element, WebElement)

    def test_02_find(self):
        self.driver.navigate('https://www.python.org/')
        element = self.driver.find(css='li.psf-meta')
        assert True == isinstance(element, WebElement)

    def test_03_find(self):
        self.driver.navigate('https://www.python.org/')
        element = self.driver.find(link_text='Python')
        assert True == isinstance(element, WebElement)

    def test_04_find(self):
        self.driver.navigate('https://www.python.org/')
        element = self.driver.find(partial_link_text='Pyth')
        assert True == isinstance(element, WebElement)

    def test_05_find(self):
        self.driver.navigate('https://www.python.org/')
        element = self.driver.find(name='q')
        assert True == isinstance(element, WebElement)

    def test_06_find(self):
        self.driver.navigate('https://www.python.org/')
        element = self.driver.find(tag_name='title')
        assert True == isinstance(element, WebElement)

    def test_07_find_all(self):
        self.driver.navigate('https://www.carrefour.com.br/')
        element = self.driver.find_all(css='div.owl-item')
        assert len(element) > 0
    
    def test_08_find_all(self):
        self.driver.navigate('https://www.carrefour.com.br/')
        element = self.driver.find_all(id='sm-tracking')
        assert len(element) > 0

    def test_09_find_all(self):
        self.driver.navigate('https://www.python.org/')
        element = self.driver.find_all(link_text='Python Core Developer Mentorship')
        assert len(element) > 0
    
    def test_10_find_all(self):
        self.driver.navigate('https://www.python.org/')
        element = self.driver.find_all(partial_link_text='Python')
        assert len(element) > 0

    def test_11_find_all(self):
        self.driver.navigate('https://www.carrefour.com.br/')
        element = self.driver.find_all(name='termo')
        assert len(element) > 0

    def test_12_find_all(self):
        self.driver.navigate('https://www.carrefour.com.br/')
        element = self.driver.find_all(xpath='//*[@id="ProductComponentCarrousel"]/div/div/div/div/div/div/div[1]/div/div[1]')
        assert len(element) > 0
    
    def test_13_find_all(self):
        self.driver.navigate('https://www.carrefour.com.br/')
        element = self.driver.find_all(tag_name='h3')
        assert len(element) > 0
        
    def tearDown(self):
        self.driver.close()