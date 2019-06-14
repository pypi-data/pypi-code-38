"""
Python library to manage a single browser in pyppeteer
"""


__author__ = """Maxime Courtet & Félix Cloup"""
__version__ = "0.1.1"


from browser_manager.browser_manager_lib import *


__all__ = ['goto_page', 'goto_page_async', 'get_browser',
           'get_browser_list', 'get_browser_async', 'get_browser_list_async']
