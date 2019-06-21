# -*- coding: utf-8 -*-
# 规则
# chang.lu


class Rule:

    def __init__(self, rule_json):
        self.type = rule_json['type']
        self.conditions = list()
        for condition_json in rule_json['conditions']:
            condition_object = Condition(condition_json)
            self.conditions.append(condition_object)
        self.result = Result(rule_json['result'])
        self.relation = rule_json['relation']
        self.weights = rule_json['weights']


class Result:

    def __init__(self, json):
        self.type = json['type']
        self.module = json['module']
        self.desc = json['desc']


class Condition:

    def __init__(self, json):
        self.id = json['id']
        self.type = json['type']
        self.condition = json['condition']
