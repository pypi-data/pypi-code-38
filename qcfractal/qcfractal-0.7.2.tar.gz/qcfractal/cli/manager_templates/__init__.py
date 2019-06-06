import os

this_directory, _ = os.path.split(__file__)
with open(os.path.join(this_directory, "base_header.string_py"), 'r') as f:
    template = f.read()
