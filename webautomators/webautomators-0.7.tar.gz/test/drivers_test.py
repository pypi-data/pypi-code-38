# -*- coding: utf-8 -*-

import time
from unittest import TestCase

from selenium.webdriver import ChromeOptions
from webautomators import WebRemoteDriver, WebGeckoDriver, WebChromeDriver

### - annotation: 
class TestDriverClose(TestCase):

    def setUp(self):
        self.options=ChromeOptions()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--window-size=1420,1080')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.driver = WebChromeDriver(chrome_options=self.options)
        self.driver.navigate('http://google.com.br')


    def test_close(self):
        self.driver.close_browser()
    
    def test_close_window_index(self):
        self.driver.execute_script("window.open(arguments[0])", "http://google.com.br")
        self.driver.close_window_by_index(1)
        self.driver.quit()
    
    def test_close_window_partial_title(self):
        self.driver.execute_script("window.open(arguments[0])", "http://submarino.com.br")
        self.driver.close_window_by_partial_title("Submari")
        self.driver.quit()

    def test_close_window_partial_url(self):
        self.driver.execute_script("window.open(arguments[0])", "http://submarino.com.br")
        self.driver.close_window_by_partial_url("submarino.com")
        self.driver.quit()

    def test_close_window_title(self):
        self.driver.execute_script("window.open(arguments[0])", "http://submarino.com.br")
        self.driver.close_window_by_title("Submarino - Os Produtos que você curte estão aqui. Explore!")
        self.driver.quit()

    def test_close_window_url(self):
        self.driver.execute_script("window.open(arguments[0])", "http://submarino.com.br")
        self.driver.close_window_by_url("https://www.submarino.com.br/")
        self.driver.quit()
    
    def test_close_window(self):
        self.driver.execute_script("window.open(arguments[0])", "http://submarino.com.br")
        self.driver.close_window()
        self.driver.quit()

# class TestAlert(TestCase):
#     def setUp(self):
        # self.options=ChromeOptions()
        # self.options.add_argument('--no-sandbox')
        # self.options.add_argument('--window-size=1420,1080')
        # self.options.add_argument('--headless')
        # self.options.add_argument('--disable-gpu')
        # self.driver = WebChromeDriver(chrome_options=self.options)
        

#     def test_dimiss_alert(self):
#         self.driver.navigate('http://google.com.br')
#         self.driver.execute_script("prompt('Test')")
#         self.driver.dismiss_alert()
#         assert self.driver.alert_is_present()==False

#     def test_accept_alert(self):
#         self.driver.navigate('http://google.com.br')
#         self.driver.execute_script("prompt('Test')")
#         self.driver.accept_alert()
#         assert self.driver.alert_is_present()==False


#     def test_submit_prompt_alert(self):
#         self.driver.navigate('http://google.com.br')
#         self.driver.execute_script("prompt('Test')")
#         self.driver.submit_prompt_alert("variable")
#         assert self.driver.alert_is_present()==False

#     def tearDown(self):
#         self.driver.close()
    
# class TestDriver(TestCase):

#     def setUp(self):
#         self.options=ChromeOptions()
        # self.options.add_argument('--no-sandbox')
        # self.options.add_argument('--window-size=1420,1080')
        # self.options.add_argument('--headless')
        # self.options.add_argument('--disable-gpu')
        # self.driver = WebChromeDriver(chrome_options=self.options)

#     def test_navigate(self):
#         self.driver.navigate('http://google.com.br')
#         title = self.driver.title
#         assert title == "Google"

#     def test_current_url(self):
#         self.driver.navigate('https://google.com/')
#         url = self.driver.get_current_url()
#         assert url == "https://www.google.com/"

#     def test_driver_name(self):
#         self.driver.navigate('https://www.google.com/')
#         name = self.driver.get_name()
#         assert name == "chrome"
    
#     def test_get_window_urls(self):
#         self.driver.navigate('https://pypi.org/')
#         self.driver.open_new_window("http://google.com.br")

#         urls = self.driver.get_window_urls()
#         assert  len(urls) == 2 

#     def test_get_window_handle(self):
#         self.driver.navigate('https://google.com.br')
#         handle = self.driver.get_window_handle()
#         assert type(handle) is str

    
#     def test_get_window_handles(self):
#         self.driver.navigate('https://google.com.br')
#         handles = self.driver.get_window_handles()
#         assert type(handles) is list

#     def test_get_window_title(self):
#         self.driver.navigate('https://google.com.br')
#         title=self.driver.get_window_title()
#         assert title == 'Google'
    
#     def test_refresh_page(self):
#         self.driver.navigate('https://google.com.br')
#         self.driver.refresh_page()
#         assert self.driver.get_window_title() == 'Google'

#     def tearDown(self):
#         self.driver.close_browser()


# class TestSwitchWindow(TestCase):

#     def setUp(self):
#         self.options=ChromeOptions()
        # self.options.add_argument('--no-sandbox')
        # self.options.add_argument('--window-size=1420,1080')
        # self.options.add_argument('--headless')
        # self.options.add_argument('--disable-gpu')
        # self.driver = WebChromeDriver(chrome_options=self.options)

#     def test_open_new_window(self):
#         self.driver.navigate('https://google.com.br')
#         self.driver.open_new_window("http://google.com.br")
#         handles = self.driver.get_window_handles()
#         assert len(handles) == 2
    
#     def test_switch_to_last_window(self):
#         self.driver.navigate('https://google.com.br')
#         self.driver.open_new_window("https://www.submarino.com.br/")
#         self.driver.switch_to_last_window()
        
#         assert self.driver.get_current_url() == "https://www.submarino.com.br/"

#     def test_switch_to_first_window(self):
#         self.driver.navigate('https://google.com.br')
#         self.driver.open_new_window("https://www.submarino.com.br/")
#         self.driver.switch_to_last_window()
#         self.driver.switch_to_first_window()
        
#         assert self.driver.title == "Google"
    
#     def test_switch_to_next_window(self):
#         self.driver.navigate('https://google.com.br')
#         self.driver.open_new_window("https://www.submarino.com.br/")
#         self.driver.switch_to_next_window()
#         assert self.driver.get_current_url() == "https://www.submarino.com.br/"

#     def test_switch_to_previous_window(self):
#         self.driver.navigate('https://google.com.br')
#         self.driver.open_new_window("https://www.submarino.com.br/")
#         self.driver.switch_to_last_window()
#         self.driver.switch_to_previous_window()
        
#         assert self.driver.title == "Google"
    
#     def test_switch_to_window_by_index(self):
#         self.driver.navigate('https://google.com.br')
#         self.driver.open_new_window("https://www.submarino.com.br/")
#         self.driver.switch_to_window_by_index(1)
#         assert self.driver.get_current_url() == "https://www.submarino.com.br/"

#     def test_switch_to_window_by_partial_title(self):
#         self.driver.navigate('https://google.com.br')
#         self.driver.open_new_window("https://www.submarino.com.br/")
#         self.driver.switch_to_window_by_partial_title("Submarino")
#         assert self.driver.get_current_url() == "https://www.submarino.com.br/"

#     def test_switch_to_window_by_partial_url(self):
#         self.driver.navigate('https://google.com.br')
#         self.driver.open_new_window("https://www.submarino.com.br/")
#         self.driver.switch_to_window_by_partial_url("www.submarino.com.br")
#         assert self.driver.get_current_url() == "https://www.submarino.com.br/"

#     def test_switch_to_window_by_title(self):
#         self.driver.navigate('https://google.com.br')
#         self.driver.open_new_window("https://www.submarino.com.br/")
#         self.driver.switch_to_window_by_title("Google")
#         assert self.driver.get_current_url() == "https://www.google.com.br/"

#     def test_switch_to_window_by_url(self):
#         self.driver.navigate('https://google.com.br')
#         self.driver.open_new_window("https://www.submarino.com.br/")
#         self.driver.switch_to_window_by_url("https://www.submarino.com.br/")
#         assert self.driver.get_current_url() == "https://www.submarino.com.br/"

#     def tearDown(self):
#         self.driver.close_browser()
