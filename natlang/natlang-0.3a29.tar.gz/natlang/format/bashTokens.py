import json
import os
import sys


class BashCode:
    def __init__(self, tokens, valueTypes, canoCode=None, createSketch=True):
        self.value = tokens
        self.valueTypes = valueTypes
        # assert len(self.value) == len(self.valueTypes)
        self.canoCode = canoCode
        self.astTree = None
        self.sketch = None
        # if self.canoCode is not None:
        #     self.astTree = bash2astTree(canoCode)
        if createSketch is True:
            self.sketch = self.getSketch()

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return "<BashCode: " + str(self.value) + ">"

    def __getitem__(self, key):
        return self.value[key]

    def getSketch(self):
        raise NotImplementedError

    def export(self):
        return ''.join(self.value)


def load(file, linesToLoad=sys.maxsize):
    with open(os.path.expanduser(file)) as f:
        content = [line.strip() for line in f][:linesToLoad]
    result = []
    for line in content:
        entry = json.loads(line)
        result.append(BashCode(entry['token'], [], createSketch=False))
    return result


if __name__ == '__main__':
    loaded = load('/Users/ruoyi/Projects/PycharmProjects/data_fixer/bash/train.jsonl')
