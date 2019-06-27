'''
 # @ Author: Yiming Qiu
 # @ Description: Pre-defined regex module
 # @ Email: yiming404@gmail.com
 '''

import re

def find(text):
    inetrval = '[/ -.|]'
    year = '(?:1[7-9]\d\d|2[01]\d\d)'
    day = '(?:0[1-9](?:st|nd|rd|th)?|[12][0-9]|3[01])(?:st|nd|rd|th)?'
    month_alpha = '(?:Jan(?:urary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(?:Nov|Dec)(?:ember)?)'
    month_digit = '(?:01|02|03|04|05|06|07|08|09|10|11|12)'
    rules = [
        '(?:'+ day + inetrval + month_alpha + inetrval+ year + ')',
        '(?:'+ year + inetrval + month_alpha + inetrval+ day + ')',
        '(?:'+ month_alpha + inetrval + year + ')',
        '(?:'+ year + inetrval + month_alpha + ')',
        '(?:'+ day + inetrval + month_digit + inetrval+ year + ')',
        '(?:'+ year + inetrval + month_digit + inetrval+ day + ')',
        '(?:'+ year + inetrval + month_digit + ')',
        '(?:'+ month_digit + inetrval + year + ')',
        

    ]
    rules_overall = '('+ '|'.join(rules) +')'

    result_list = re.findall(rules_overall,text)
    fileter_list = []

    interval = [' ','/','|','-','.']
    for result in result_list:
        interval_set = set()
        for char in result:
            if char in interval:
                interval_set.add(char)
        if len(interval_set)==1:
            fileter_list.append(result)
    return fileter_list
