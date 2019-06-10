from unittest import TestCase
from webautomators import WebChromeDriver
from webautomators import WebGeckoDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ChromeOptions
import time
import assertpy
class TestWait(TestCase):
    def setUp(self):
        self.options=ChromeOptions()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--window-size=1420,1080')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.driver = WebChromeDriver(chrome_options=self.options)

    def test_wait_for_title(self):
        self.driver.navigate('https://www.google.com/')
        self.driver.find(xpath='/html/body/div/div[3]/form/div[2]/div/div[1]/div/div[1]/input')
        start_time = time.time()
        self.driver.wait_for_title("Google",10)
        elapsed_time = time.time() - start_time
        assert elapsed_time < 10

    def test_wait_for_title_contains(self):
        self.driver.navigate('https://google.com.br')
        self.driver.find(xpath='/html/body/div/div[3]/form/div[2]/div/div[1]/div/div[1]/input')
        start_time = time.time()
        self.driver.wait_for_title_contains("Goo",10)
        elapsed_time = time.time() - start_time
        assert elapsed_time < 10

    def test_wait_for_title_is_not(self):
        self.driver.navigate('https://bol.uol.com.br')
        self.driver.find(xpath='//*[@id="buscaWeb"]/input')
        start_time = time.time()
        self.driver.wait_for_title_is_not("BOL",10)
        elapsed_time = time.time() - start_time
        assert elapsed_time > 10

    def test_wait_for_title_not_contains(self):
        self.driver.navigate('https://mail.terra.com.br/')
        self.driver.find(xpath='//*[@id="username"]')
        start_time = time.time()
        self.driver.wait_for_title_not_contains('goo',10)
        elapsed_time = time.time() - start_time
        assert elapsed_time > 10

    def test_wait_for_window_present_by_partial_title(self):
        self.driver.navigate('https://mail.google.com/mail/u/0/')
        self.driver.find(xpath='//*[@id="identifierId"]')
        start_time = time.time()
        self.driver.wait_for_window_present_by_partial_title('mail',10)
        elapsed_time = time.time() - start_time
        assert elapsed_time < 10

    def test_wait_for_window_present_by_partial_url(self):
        self.driver.navigate('https://junit.org/junit5/')
        self.driver.find(xpath='/html/body/div/div[1]/ul/li[1]/a')
        start_time = time.time()
        self.driver.wait_for_window_present_by_partial_url('/junit.org/',10)
        elapsed_time = time.time() - start_time
        assert elapsed_time < 10

    def test_wait_for_window_present_by_title(self):
        self.driver.navigate('https://hibernate.org/')
        self.driver.find(xpath='//*[@id="content"]/div/div/div[1]/div/div/h3/a')
        start_time = time.time()
        self.driver.wait_for_window_present_by_title('Hibernate. Everything data. - Hibernate',10)
        elapsed_time = time.time() - start_time
        assert elapsed_time < 10

    def test_wait_for_window_present_by_url(self):
        self.driver.navigate('https://spring.io/')
        self.driver.find(xpath='/html/body/div/header/div[1]/div/ul/li[1]/a')
        start_time = time.time()
        self.driver.wait_for_window_present_by_url('https://spring.io/',10)
        elapsed_time = time.time() - start_time
        assert elapsed_time < 10

    def test_wait_for_page_not_contains_text(self):
        self.driver.navigate('https://www.globo.com/')
        self.driver.find(xpath='//*[@id="home-search-field"]')
        start_time = time.time()
        self.driver.wait_for_page_not_contains_text('Texto não presente na pagina',10)
        elapsed_time = time.time() - start_time
        assert elapsed_time < 10

    def tearDown(self):
        self.driver.close()

