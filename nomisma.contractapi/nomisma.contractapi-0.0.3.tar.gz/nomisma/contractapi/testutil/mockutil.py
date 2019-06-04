import os
import json


def from_abi(name):
    with open(os.path.join(os.path.dirname(__file__), 'mockabi', name)) as f:
        return json.load(f)
