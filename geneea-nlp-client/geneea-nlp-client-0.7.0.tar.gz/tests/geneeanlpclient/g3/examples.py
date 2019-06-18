import json
import os

from geneeanlpclient.g3 import fromDict, G3, JsonType

EXAMPLE = os.path.join(os.path.dirname(__file__), 'examples', 'example.json')
EXAMPLE_FULL = os.path.join(os.path.dirname(__file__), 'examples', 'example_FULL.json')
EXAMPLE_F2 = os.path.join(os.path.dirname(__file__), 'examples', 'F2_example.json')
EXAMPLE_F2_CS = os.path.join(os.path.dirname(__file__), 'examples', 'F2_example_cs.json')

EXAMPLE_REQ = os.path.join(os.path.dirname(__file__), 'examples', 'request.json')

def example_obj() -> G3:
    with open(EXAMPLE, 'r') as file:
        return fromDict(json.load(file))


def example_full_obj() -> G3:
    with open(EXAMPLE_FULL, 'r') as file:
        return fromDict(json.load(file))


def example_req_js() -> JsonType:
    with open(EXAMPLE_REQ, 'r') as file:
        return json.load(file)
