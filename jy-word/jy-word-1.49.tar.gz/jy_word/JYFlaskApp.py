# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2019/4/1 0001
__author__ = 'huohuo'

import os
import socket
import requests
import logging
from Web2 import login_manager, blues
from Class.JY_config import env, env_name, session_cookie_domain, debug, system_config, footer_config, \
    register_phone, API_service_JYAUTH, API_service, JYConfig, refresh_footer
from flask import request, g, render_template, redirect, session, Flask
from flask_login import current_user
from Class.common import Common, JYRequestsException
from Class.jinja_filter import MyJinja
from Class.flask_wraps import del_session

try:
    from flask_wtf.csrf import CSRFProtect
except Exception, e:
    from flask_wtf.csrf import CsrfProtect as CSRFProtect
from Class.dingding_message_tool import send_msg_by_dd

"""
# File Name: create_app.py
# Description: create system app for web.
"""
common = Common()
Jinja = MyJinja()
csrf = CSRFProtect()
jyc = JYConfig()


def create_app():
    app = Flask(__name__)
    sys_config_dict = {
        "env": env,
        "setting_name": "", "system_name": "",
        "logo_url": "", "log_info": "",
        "module_config": {},
        "footer_setting": {},
        "db_config_dict": {},
        "system_api_host_setting": {}
    }
    for item in sys_config_dict:
        app.config[item] = ""
    app.config["JINGDU_DB_SETTING"] = ""
    app.config["validate_ttf_path"] = "%s/flask_tools/huawenxinsong.ttf" % app.root_path
    app.config["validate_code_setting"] = {
        "path": "%s/flask_tools/huawenxinsong.ttf" % app.root_path,
        "background_color": "#ffffff", "word_count": 4,
        "draw_lines": False, "draw_points": False,
        "fg_color": "black", "font_size": 16,
        "width": 140, "height": 30
    }
    app.config["access_token"] = "6758503db71f223cf23fd0251d6fd07ef58ad5ceaeb3e06204440a324a97f5ef"
    app.config["LOGIN_DISABLED"] = True
    # 默认前端通知
    if session_cookie_domain != "":
        app.config["SESSION_COOKIE_DOMAIN"] = session_cookie_domain
    app.secret_key = 'a string'
    login_manager.init_app(app)

    system_module_dict = jyc.module_config  #
    # get_system_module()
    for module_name in system_module_dict:
        module_load_flag = system_module_dict[module_name]
        if module_load_flag in ["true", 'True', True]:
            # print app.root_path
            web_files = os.listdir("%s/views/%s" % (app.root_path, module_name))
            # print web_files
            for web_file in web_files:
                if web_file != "__init__.py":
                    if web_file.endswith(".py"):
                        __import__("Web2.views.%s.%s" % (module_name, web_file[:-3]))

    if "Development" in env:
        __import__("Web2.views.test.auth_test")
    for key, value in blues.items():
        if len(value[1]) > 1:
            app.register_blueprint(value[0], url_prefix=value[1])
        else:
            app.register_blueprint(value[0])

    @app.context_processor
    def context_processor():
        """
        系统级别的变量
        :return:
        """

        host = request.host
        system_debug = app.config["DEBUG"]

        env = system_config["env"]
        log_info = eval(system_config["log_info"])
        system_name = system_config["system_name"]
        url = request.args.get('company_info_url')
        if url is not None and os.path.exists(url):
            os.environ['company_info_url'] = url
            refresh_footer(url)
        logo_login_url = system_config["logo_login_url"]
        logo_url = system_config["logo_url"]
        system_module = jyc.module_config
        account = '' if not hasattr(current_user, 'account') else current_user.account
        base_host = "http://%s" % host

        return {"env": env, 'env_name': env_name,
                "register_phone": register_phone,
                "sys_account": account, "system_debug": system_debug,
                "host": host, "log_info": log_info,  "base_host": base_host, "debug": system_debug,
                "logo_url": logo_url, "logo_login_url": logo_login_url,
                "footer_config_dict": footer_config,
                "system_module": system_module,
                "system_name": system_name}

    @app.errorhandler(500)
    def handlers_500(error):
        """
        500 错误，钉钉通知，session 中必须存在 mobile_phone 参数
        session 中 dingding_module，machine_man 两个参数需一起存在，方可选择制定群通知
        :param error:
        :return:
        """
        error_status = 100
        error_num = 1003
        error_info = '' if not hasattr(error, 'message') else error.message
        status = '' if not hasattr(error, 'status') else error.status
        try:
            account = current_user.account
        except Exception, e:
            logging.warn(e.args)
            account = ""
        error_message = "!!500错误!!\n"
        if account:
            error_message += "\n【用户名】：%s\n" % (account)
        error_info = '%s: %s' % (str(type(error)), str(error_info))
        error_message += "【路径】: %s\n【请求方式】: %s\n" % (request.url, request.method)
        error_message += "【错误信息】: %s\n" % error_info
        send_msg_by_dd(error_message)
        return '网络异常，已通知管理员维修，请稍后重试'

    @app.before_request
    def before_request():

        my_headers = {}
        if "X-Forwarded-For" in request.headers:
            my_headers["X-Forwarded-For"] = request.headers["X-Forwarded-For"] + "," + request.remote_addr
        else:
            my_headers["X-Forwarded-For"] = request.remote_addr
        if "sample_token_ams" in request.args:
            sample_token_ams = request.args['sample_token_ams']
            my_headers['sample_token_ams'] = request.args['sample_token_ams']
            if 'sample_token_ams' in session:
                del session['sample_token_ams']
            session['sample_token_ams'] = sample_token_ams
        if env == "Development":
            if "login_disabled" in session:
                my_headers["X-Skip-Auth"] = session["login_disabled"]
        g.user_name = session.get('user_name')
        g.requests = requests.session()
        g.requests.headers = my_headers
        if current_user.is_authenticated:
            try:
                g.requests.auth = current_user.auth
            except AttributeError, e:
                logging.error(e.message)

    @app.after_request
    def after_request(res):
        if res.status_code == 302 or res.status_code == 301:
            if "X-Request-Protocol" in request.headers:
                pro = request.headers["X-Request-Protocol"]
                if "Location" in res.headers:
                    location = res.headers["location"]
                    if location.startswith("http:"):
                        res.headers["Location"] = pro + ":" + res.headers["Location"][5:]
                    elif location.startswith("/"):
                        res.headers["Location"] = "%s://%s%s" % (pro, request.headers["Host"], location)
        return res

    csrf.init_app(app)
    Jinja.filter(app)
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

    app.debug = debug
    # set a 'SECRET_KEY' to enable the Flask session cookies
    app.config['SECRET_KEY'] = 'GATC SECRET_KEY SDFSDF234234SDF342?>:K;SDK'
    return app
    

