#!/usr/bin/python
# -*- coding: utf-8 -*-
from cefpython3 import cefpython as cef
import webview.qt as gui
import webview.constant as constant
from threading import Event, Thread
from uuid import uuid4
import logging
import time
import os

default_window_width = constant.default_window_width
default_window_height = constant.default_window_height
default_window_title = constant.default_window_title
min_window_width = constant.min_window_width
min_window_height = constant.min_window_height
debug_log_dir = constant.debug_log_dir
web_view_ready = Event()


class Cookie(cef.Cookie):
    def setName(self, name):
        self.SetName(name)

    def setValue(self, value):
        self.SetValue(value)

    def setDomain(self, domain):
        self.SetDomain(domain)

    def setPath(self, path):
        self.SetPath(path)


def init_logging_config():
    if not os.path.exists(debug_log_dir):
        os.makedirs(debug_log_dir)

    logging.basicConfig(
        filename=os.path.join(debug_log_dir, time.strftime('%Y-%m-%d', time.localtime()) + '.log'),
        level=logging.DEBUG,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    )


def notify_application(title=''):
    hwnd = gui.find_main_window_hwnd(title=title)
    if hwnd != 0:
        try:
            import win32gui, win32con
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
        except Exception as e:
            logging.debug(e)


def generate_guid():
    return 'child_' + uuid4().hex[:8]


def create_main_window_sub_thread(url='', full_screen=False, width=default_window_width, height=default_window_height,
                                  context_menu=True):
    def new_web_view():
        uid = generate_guid()
        create_window(
            uid=uid,
            url=url,
            title=default_window_title,
            width=width,
            height=height,
            context_menu=context_menu,
            full_screen=full_screen
        )

    new_web_view_thread = Thread(target=new_web_view)
    new_web_view_thread.start()


def create_window(title=default_window_title, url=None, uid='master', width=default_window_height,
                  height=default_window_height, resizable=True,
                  full_screen=False, app_name="", user_agent=None,
                  min_size=(min_window_width, min_window_height), background_color='#FFFFFF', context_menu=False,
                  url_type='document', maximized=True, minimized=False, icon_path='', call_back=None, inject_obj={},
                  quit_app_when_main_window_close=True, application_version='No Version Info Specified',
                  enable_cef_cache=True, popup_validate=None, single_instance=True, splash_screen=False,
                  splash_text='', splash_style=''):
    web_view_ready.clear()
    format_url = url
    if url_type == 'string':
        format_url = gui.html_to_data_uri(url)
    gui.launch_main_window(uid, title, url=format_url, width=width, height=height, resizable=resizable,
                           full_screen=full_screen, min_size=min_size, app_name=app_name, user_agent=user_agent,
                           background_color=background_color, web_view_ready=web_view_ready, context_menu=context_menu,
                           maximized=maximized, minimized=minimized, icon_path=icon_path, call_back=call_back,
                           inject_obj=inject_obj, quit_app_when_main_window_close=quit_app_when_main_window_close,
                           application_version=application_version, enable_cef_cache=enable_cef_cache,
                           popup_validate=popup_validate, single_instance=single_instance, splash_screen=splash_screen,
                           splash_text=splash_text, splash_style=splash_style)


def evaluate_js(script, uid='master'):
    gui.execute_javascript(script, uid)


def launch_third_party_application(params):
    gui.BrowserView.instances['master'].view.ExecuteFunction('window.__cef__.nestApplication', params)


def get_main_window_current_menu():
    if 'master' in gui.BrowserView.menu_map.keys():
        return gui.BrowserView.menu_map['master']
    else:
        return False
