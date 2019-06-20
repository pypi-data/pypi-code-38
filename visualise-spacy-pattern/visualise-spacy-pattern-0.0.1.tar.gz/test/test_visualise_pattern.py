from pprint import pprint
import json
import pytest
from visualise_spacy_pattern import to_pydot


pattern_files = [
    # 'examples/pattern_0.json',
    # 'examples/pattern_1.json',
    'examples/pattern_2.json',
]


def test_visualise_pattern():
    for i, pattern_file in enumerate(pattern_files):
        with open(pattern_file) as f:
            pattern = json.load(f)
        graph = to_pydot(pattern)
        png = graph.create_png()
        graph_file = 'examples/graph_{}.png'.format(i)
        with open(graph_file, 'wb') as f:
            f.write(png)
