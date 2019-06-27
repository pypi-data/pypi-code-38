'''
 # @ Author: Yiming Qiu
 # @ Description: Pre-defined regex module
 # @ Email: yiming404@gmail.com
 '''


import re
import sys
import os
def find(text):
    if not isinstance(text,str):
        return "Input error: only support string"
    else:
        rule = """[:\s]([\w!#$%&'*+-/=?^_`{|}~]+[\w!#$%&'*+-/=?^_`{|}~]*@\w+(?:\.\w+)*)"""
        result_list = re.findall(rule,text)

        if result_list:
            current_dir = sys.path[0]
            full_domains_dir = os.path.join(current_dir,'top_level_domain.txt')
            full_domain = open(full_domains_dir,'r').read()
            domian_list = full_domain.split('\n')
            filtered_list = []
            for email in result_list:
                if email.split('.')[-1].upper() in domian_list:
                    filtered_list.append(email)
            return filtered_list
        else:
            return None
def judge(email):
    rule = """^([\w!#$%&'*+-/=?^_`{|}~]+[\w!#$%&'*+-/=?^_`{|}~]*@\w+(?:\.\w+)*)$"""
    if re.match(rule,email):
        current_dir = sys.path[0]
        full_domains_dir = os.path.join(current_dir,'top_level_domain.txt')
        full_domain = open(full_domains_dir,'r').read()
        domian_list = full_domain.split('\n')
        if email.split('.')[-1].upper() in domian_list:
            return True
    return False