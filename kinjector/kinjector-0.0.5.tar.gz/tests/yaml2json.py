import json
import os
import sys

import yaml

yaml_fname = sys.argv[1]
with open(yaml_fname, 'r') as yfp:
    data_dict = yaml.load(yfp, Loader=yaml.Loader)
    with open(os.path.splitext(yaml_fname)[0]+'.json', 'w') as jfp:
        json.dump(data_dict, jfp, indent=4)
