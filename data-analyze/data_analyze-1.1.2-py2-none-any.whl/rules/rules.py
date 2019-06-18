# -*- coding: utf-8 -*-
# 读取规则
# chang.lu
import os
import json
from dataanalyze.rules.rule import Rule

# 规则文件
rules_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rules.json')


def read_rules(rule_path):
    with open(rule_path, mode='r') as output:
        content = output.read()
        output.close()
        rules_list = json.loads(content)
        return rules_list


def read_rules_by_type(type):
    rules = list()
    for rule in read_rules(rules_json):
        rule_object = Rule(rule)
        if rule_object.type == type:
            rules.append(rule_object)
    return rules


system_rules = read_rules_by_type('system')
coredump_rules = read_rules_by_type('coredump')
test_rules = read_rules_by_type('test')
