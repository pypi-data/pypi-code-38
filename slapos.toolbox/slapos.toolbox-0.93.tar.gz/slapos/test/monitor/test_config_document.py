# -*- coding: utf-8 -*-
import os, time
import sys
import re
import shutil
import tempfile
import unittest
import json
from slapos.monitor.monitor_config_write import MonitorConfigWrite

class MonitorConfigDocument(unittest.TestCase):

  def setUp(self):
    self.base_dir = tempfile.mkdtemp()
    self.config_dir = os.path.join(self.base_dir, 'config')
    self.config_path = os.path.join(self.config_dir, 'config.json')
    os.mkdir(self.config_dir)
    self.httpd_passwd = "btouhjng"
    self.file_content = "wjkqelod"
    self.httpd_passwd_bin = os.path.join(self.base_dir, 'htpasswd')
    self.httpd_passwd_script = """#!/bin/sh
echo "htpasswd $@" > %s/monitor-htpasswd
""" % self.base_dir
    self.monitor_https_cors = os.path.join(self.base_dir, 'httpd-cors-template.cfg.in')
    self.parameter_dict = {
      "cors-domain": 
        {
          "gracefull_bin": ["/bin/echo", "restarted"],
          "type": "httpdcors",
          "cors_file": "%s/test-httpd-cors.cfg" % self.base_dir
        },
      "httpd-password":
        {
          "htpasswd": "%s/monitor-htpasswd" % self.base_dir,
          "type": "htpasswd",
          "user": "admin",
          "file": "%s/.httpd_pwd_real" % self.base_dir
        },
      "from-file": 
        {
          "type": "file",
          "file": "%s/content" % self.base_dir
        }
      }

    self.config = [
      {
        "value": "raw content2",
        "key": "",
        "title": "raw-content2"
      },
      {
        "value": "%s" % self.httpd_passwd,
        "key": "httpd-password",
        "title": "httpd-password"
      },
      {
        "value": "%s" % self.file_content,
        "key": "from-file",
        "title": "from-file"
      },
      {
        "value": "",
        "key": "cors-domain",
        "title": "cors-domain"
      },
      {
        "value": "raw content",
        "key": "",
        "title": "raw-value"
      }
    ]
    self.writeContent("%s/test-httpd-cors.cfg" % self.base_dir, "")
    self.writeContent("%s/monitor-htpasswd" % self.base_dir, "")
    self.writeContent("%s/content" % self.base_dir, self.file_content)
    self.writeContent("%s/.httpd_pwd_real" % self.base_dir, self.httpd_passwd)
    self.writeContent(self.httpd_passwd_bin, self.httpd_passwd_script)
    self.writeContent(self.monitor_https_cors, '{% set allow_domain = "|".join(domain.replace(".", "\.").split()) -%}\n'
                                               'SetEnvIf Origin "^http(s)?://(.+\.)?({{ allow_domain }})$" ORIGIN_DOMAIN=$0\n'
                                               'Header always set Access-Control-Allow-Origin "%{ORIGIN_DOMAIN}e" env=ORIGIN_DOMAIN')
    os.chmod(self.httpd_passwd_bin, 0755)

  def tearDown(self):
    if os.path.exists(self.base_dir):
      shutil.rmtree(self.base_dir)

  def writeContent(self, file_path, config):
    with open(file_path, 'w') as cfg:
      cfg.write(config)

  def generate_cors_string(self, cors_domain_list):
    cors_string = ""
    for domain in cors_domain_list:
      if cors_string:
        cors_string += '|'
      cors_string += re.escape(domain)

    cors_string = 'SetEnvIf Origin "^http(s)?://(.+\.)?(%s)$" ORIGIN_DOMAIN=$0\n' % cors_string
    cors_string += 'Header always set Access-Control-Allow-Origin "%{ORIGIN_DOMAIN}e" env=ORIGIN_DOMAIN'
    return cors_string

  def check_config(self):
    config_parameter = os.path.join(self.config_dir, 'config.parameters.json')
    config_parameter_json = json.load(open(config_parameter))
    config_json = json.load(open(self.config_path))

    for config in config_json:
      if config["key"]:
        self.assertTrue(config_parameter_json.has_key(config["key"]))
        parameter = config_parameter_json[config["key"]]
      else:
        continue
      if config["key"] == 'from-file':
        self.assertTrue(os.path.exists(parameter['file']))
        self.assertEqual(config["value"], open(parameter['file']).read())
      elif config["key"] == 'httpd-password':
        http_passwd = "%s/monitor-htpasswd" % self.base_dir
        #XXX where \n bellow come from ?
        command = 'htpasswd -cb %s admin %s%s' % (http_passwd, config["value"], '\n')
        self.assertTrue(os.path.exists(parameter['file']))
        self.assertTrue(os.path.exists(http_passwd))
        self.assertEqual(config["value"], open(parameter['file']).read())
        self.assertEqual(open(http_passwd).read(), command)
      elif config["key"] == 'cors-domain':
        cors_file = "%s/test-httpd-cors.cfg" % self.base_dir
        self.assertTrue(os.path.exists(cors_file))
        cors_string = self.generate_cors_string(config["value"].split())
        self.assertEqual(cors_string, open(cors_file).read())

  def check_cfg_config(self, config_list):
    cfg_output = os.path.join(self.config_dir, 'config.cfg')
    config_cfg = "[public]\n"
    for config in config_list:
      if config['key']:
        config_cfg += '%s = %s\n' % (config['key'], config['value'])
    with open(cfg_output) as cfg:
      self.assertEqual(cfg.read(), config_cfg)

  def test_write_config_default(self):
    self.writeContent(self.config_path, json.dumps(self.config))
    self.writeContent(os.path.join(self.config_dir, 'config.parameters.json'), json.dumps(self.parameter_dict))
    cfg_output = os.path.join(self.config_dir, 'config.cfg')

    instance = MonitorConfigWrite(
      self.config_path,
      self.httpd_passwd_bin,
      cfg_output,
      self.monitor_https_cors)

    result = instance.applyConfigChanges()
    self.assertTrue(os.path.exists(cfg_output))
    # Check result of non raw parameter edition
    self.assertEqual(result, {'cors-domain': True, 'from-file': True, 'httpd-password': True})
    self.check_config()
    self.check_cfg_config(self.config)

  def test_write_config_parts(self):
    # remove cors config
    for element in self.config:
      if element['key'] == "cors-domain":
        element['key'] = ""
    self.parameter_dict.pop("cors-domain")
    self.writeContent(self.config_path, json.dumps(self.config))
    self.writeContent(os.path.join(self.config_dir, 'config.parameters.json'), json.dumps(self.parameter_dict))
    cfg_output = os.path.join(self.config_dir, 'config.cfg')

    instance = MonitorConfigWrite(
      self.config_path,
      self.httpd_passwd_bin,
      cfg_output)

    result = instance.applyConfigChanges()
    self.assertTrue(os.path.exists(cfg_output))
    # Check result of non raw parameter edition
    self.assertEqual(result, {'from-file': True, 'httpd-password': True})
    self.check_config()
    self.check_cfg_config(self.config)

  def test_write_config_edit_values(self):
    self.writeContent(self.config_path, json.dumps(self.config))
    self.writeContent(os.path.join(self.config_dir, 'config.parameters.json'), json.dumps(self.parameter_dict))
    cfg_output = os.path.join(self.config_dir, 'config.cfg')

    instance = MonitorConfigWrite(
      self.config_path,
      self.httpd_passwd_bin,
      cfg_output,
      self.monitor_https_cors)

    result = instance.applyConfigChanges()
    self.assertTrue(os.path.exists(cfg_output))
    self.assertEqual(result, {'cors-domain': True, 'from-file': True, 'httpd-password': True})
    self.check_config()
    self.check_cfg_config(self.config)

    for config in self.config:
      if config["key"] != "":
        config["value"] = "changed.value"
    self.writeContent(self.config_path, json.dumps(self.config))

    result = instance.applyConfigChanges()
    self.assertEqual(result, {'cors-domain': True, 'from-file': True, 'httpd-password': True})
    self.check_config()
    self.check_cfg_config(self.config)

    # Add new domain in cors domain
    for config in self.config:
      if config["key"] != "cors-domain":
        config["value"] = "changed.value new.domain.com"
    self.writeContent(self.config_path, json.dumps(self.config))

    result = instance.applyConfigChanges()
    self.assertEqual(result, {'cors-domain': True, 'from-file': True, 'httpd-password': True})
    self.check_config()
    self.check_cfg_config(self.config)
