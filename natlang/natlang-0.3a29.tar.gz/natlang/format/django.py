# -*- coding: utf-8 -*-
# Python version: 3
#
# Django Dataset Code Loader class
# Simon Fraser University
# Ruoyi Wang, Jetic Gū
#
# For loading the code as a sequence of tokens
import tokenize as tk
import keyword
from io import StringIO
import os
import sys


class Code:
    def __init__(self, string):
        self.value = list(tk.generate_tokens(StringIO(string).readline))[:-1]
        self.sketch = []
        self.createSketch()  # writes to self.sketch
        return

    def __iter__(self):
        return iter([t[1] for t in self.value])

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return "<DjangoCode: " + str([t[1] for t in self.value]) + ">"

    def createSketch(self):
        self.sketch = []
        for x in self.value:
            if x[0] == tk.NAME and not keyword.iskeyword(x[1]):
                x = '<SKETCH_NAME>'
            elif x[0] == tk.STRING:
                x = '<SKETCH_STRING>'
            elif x[0] == tk.NUMBER:
                x = '<SKETCH_NUMBER>'
            else:
                x = x[1]
            self.sketch.append(x)
        return

    def export(self):
        return " ".join([t[1] for t in self.value])


def load(file, linesToLoad=sys.maxsize):
    with open(os.path.expanduser(file)) as f:
        content = [line.strip() for line in f][:linesToLoad]
    result = []
    for line in content:
        result.append(Code(line))
    return result


# if __name__ == '__main__':
#     loaded = load(
#         '/Users/ruoyi/Projects/PycharmProjects/datatool/simple_code.txt')
#     tokens = createSketch(loaded[0], None, None)
