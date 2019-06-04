import os
import json

def from_file(file):
    return TruffleContract(json.load(file))

def from_abi(name):
    with open(os.path.join(os.path.dirname(__file__), os.pardir, 'abi', name)) as f:
        return from_file(f)

def from_mock_abi(name):
    with open(os.path.join(os.path.dirname(__file__), 'mockabi', name)) as f:
        return from_file(f)

class TruffleContract:
    def __init__(self, json):
        self.json = json

    def abi(self):
        return self.json['abi']

    def bytecode(self):
        return self.json['bytecode']