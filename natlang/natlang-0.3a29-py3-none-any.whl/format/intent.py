# -*- coding: utf-8 -*-
# Python version: 2/3
#
# Django Dataset Intention Loader class
# Simon Fraser University
# Ruoyi Wang
#
# For loading the intentions as a sequence of natural language tokens
import re
import sys
import os

str_nfa = re.compile(r'''
(?<=\W)("[^"]*")(?=\W)|(?<=\W)('([^'])*')(?=\W)|    # str
([^\s]+)    #other stuff
''', re.VERBOSE)


def proc_line(line):
    matches = str_nfa.finditer(line)
    result = []
    for m in matches:
        group = m.group()
        if isinstance(group, tuple):
            raise RuntimeError("Multiple match of group {}".format(group))
        if group.endswith("\'s"):
            if group[:-1]:
                result.append(group[:-2])
            result.append('s')
        elif group.endswith('.') or group.endswith(','):
            if group[:-1]:
                result.append(group[:-1])
            result.append(group[-1])
        else:
            result.append(group)
    return result


def load(file, linesToLoad=sys.maxsize):
    with open(os.path.expanduser(file)) as f:
        lines = [line for line in f][:linesToLoad]

    results = []
    return [proc_line(line) for line in lines]


# if __name__ == '__main__':
#     results = load('test/sampleDjangoAnno.txt')
#     f = open('test/sampleDjangoAnno.txt')
#     lines = list(f)
#     r2 = proc_line(lines[-1])
