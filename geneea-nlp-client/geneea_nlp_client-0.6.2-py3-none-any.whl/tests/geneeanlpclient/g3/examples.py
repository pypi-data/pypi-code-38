import json
import os

from geneeanlpclient.g3.reader import fromDict

EXAMPLE = os.path.join(os.path.dirname(__file__), 'examples', 'example.json')
EXAMPLE_PHENO = os.path.join(os.path.dirname(__file__), 'examples', 'example_Pheno.json')
EXAMPLE_FULL = os.path.join(os.path.dirname(__file__), 'examples', 'example_Full.json')
EXAMPLE_F2 = os.path.join(os.path.dirname(__file__), 'examples', 'F2_example.json')
EXAMPLE_F2_CS = os.path.join(os.path.dirname(__file__), 'examples', 'F2_example_cs.json')

EXAMPLE_REQ = os.path.join(os.path.dirname(__file__), 'examples', 'request.json')

def example_obj():
    with open(EXAMPLE, 'r') as file:
        return fromDict(json.load(file))


def example_pheno_obj():
    with open(EXAMPLE_PHENO, 'r') as file:
        return fromDict(json.load(file))


def example_req_js():
    with open(EXAMPLE_REQ, 'r') as file:
        return json.load(file)
