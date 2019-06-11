#!/usr/bin/env python  #add this to make sure ***.py run in terminal
# -*- coding: utf-8 -*- #add this to make sure ***.py read by utf-8
"""【模块简介】用于计算公司员工的薪资"""
__author__ = "egret"


def year_salary(month_salary):
    """根据传入的月薪 计算年薪"""
    return month_salary*12

def day_salary(month_salary):
    """根据传入的月薪 计算日薪"""
    return month_salary/22

# 用于模块测试 不会在模块导入时自动运行
if __name__ == "__main__":
    print(year_salary(5000))
    print(day_salary(5000))
