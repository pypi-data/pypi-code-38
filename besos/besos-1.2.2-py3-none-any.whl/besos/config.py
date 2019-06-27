"""
Script used to configure the inputs, outputs and defaults for Evaluators.
"""
import os
import sys
sys.path.insert(0, '..')

from pathlib import Path
import warnings
from errors import ModeError

baseDir = Path(__file__).resolve().parents[1]
# where to store output from simulations, or None for a temporary directory
out_dir = None
# where to move output files from failed runs
err_dir = Path(baseDir, 'E_Plus_Files')
# where to look for input files
data_dir = Path(baseDir, 'Data')
# whether to use 'idf' or 'json' format by default
energy_plus_mode = 'json'

# Produces a dictionary in the form {'extension': '/path/from/root/file.extension'}
# it is assumed that 'file.extension' is in the directory `inDir`
# When a file of the type 'json', 'idf', 'idd', 'epw', 'xlsx' or 'schema' is needed,
# the default is taken from this dictionary
files = {key: str(Path(data_dir, name).resolve()) for key, name in {
    'json': 'example_building.epJSON',
    'schema': 'Energy+.schema.epJSON',
    'idf': 'example_idf.idf',
    'idd': 'example_idd.idd',
    'epw': 'example_epw.epw',
    'xlsx': 'example_xlsx.xlsx',
}.items()}

# alias json and epJSON to the same building
if 'json' in files and 'epJSON'in files:
    warnings.warn('two defaults are created for json buildings')
elif 'epJSON' in files:
    files['json'] = files['epJSON']
elif 'json' in files:
    files['epJSON'] = files['json']

# set files['building'] equal to the building for the default mode
if energy_plus_mode == 'idf':
    files['building'] = files['idf']
    files['data dict'] = files['idd']
elif energy_plus_mode == 'json':
    files['building'] = files['json']
    files['data dict'] = files['schema']
else:
    raise ModeError(energy_plus_mode)

# the default min and max values for range_parameters
range_parameter = dict(
    min=0,
    max=float('inf')
)

# the default arguments for the lru_cache
cache = dict(
    enabled=True,
    size=None,
    typed=False
)

# the default objective(s) to extract from simulations
objectives = 'Electricity:Facility'  # TODO: Make this only apply to EvaluatorEP, not all evaluators

# The default `class_name` of meters/variables
objective_meter_type = 'Output:Meter'
objective_variable_type = 'Output:Variable'

# default arguments for optimizers
optimizer = dict(
    evaluations=1000,
)
