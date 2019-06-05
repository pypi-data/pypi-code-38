from os.path import join, dirname
from parglare import Grammar, GLRParser


file_name = join(dirname(__file__), 'test_inputs', 'LightSwitch.rpy')
this_folder = dirname(__file__)
g = Grammar.from_file(join(this_folder, 'rhapsody.pg'))
parser = GLRParser(g, default_actions=True, debug=False)
with open(file_name) as f:
    parser.parse(f.read())
