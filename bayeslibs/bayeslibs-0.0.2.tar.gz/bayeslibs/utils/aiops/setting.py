"""
@project:medical_robot_backend
@language:python3
@create:2019/4/26
@author:qianyang@aibayes.com
@description:none
"""
import logging
import os

_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'aiops')
if not os.path.exists(_LOG_DIR):
    os.makedirs(_LOG_DIR)
LOG_DICT = {
    'acmbot': {'log_name': os.path.join(_LOG_DIR, 'bayes_medical_acmbot.aiops'),
               'log_level': logging.DEBUG},
    'mhbot': {'log_name': os.path.join(_LOG_DIR, 'bayes_medical_bcmbot.aiops'),
              'log_level': logging.DEBUG},
    'chatbot': {'log_name': os.path.join(_LOG_DIR, 'bayes_medical_chatbot.aiops'),
                'log_level': logging.DEBUG},
    'apollo': {'log_name': os.path.join(_LOG_DIR, 'bayes_medical_chatbot.aiops'),
               'log_level': logging.DEBUG},
    'default': {'log_name': os.path.join(_LOG_DIR, 'bayes_medical_default.aiops'),
                'log_level': logging.DEBUG}
}
