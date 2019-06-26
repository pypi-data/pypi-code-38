# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.3'
#       jupytext_version: 0.8.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from besos import eppy_funcs as ef
from besos import sampling
from besos.evaluator import EvaluatorEP
from besos.parameters import FieldSelector, FilterSelector, GenericSelector, Parameter
from besos.problem import EPProblem

import pandas as pd
# -

building = ef.get_building(mode='json')
# we need the json example file because of how the insulation_filter function works

# Selectors identify which part of the building to modify, and how to modify it.
# `FieldSelector`s allow for modifying individual fields in a building.  
#
# The example building loaded above contains a `Material` class object named `Mass NonRes Wall Insulation` which has a `Thickness` field. Below is how to make a selector that modifies this insulation's thickness.

FieldSelector(class_name='Material', object_name='Mass NonRes Wall Insulation', field_name='Thickness')

# However, there is only one object in the example building with the name `Mass NonRes Wall Insulation`, so we can ommit the `class_name`. The building will be searched for any object with the correct `object_name`.

FieldSelector(object_name='Mass NonRes Wall Insulation', field_name='Thickness')

#  If the `class_name` is provided, but the `object_name` is omitted, then the first object with that `class_name` will be used. Since JSON files do not guarentee ordering, this only works for idf files. `field_name` is mandatory.

# `FilterSelectors` allow us to use custom function to select the objects to modify. Here we define a function that finds all materials with `Insulation` in their name. Then we use this function to modify the thickness of all materials in the building.

# +
def insulation_filter(building):
    return [obj for name, obj in building['Material'].items() if 'Insulation' in name]

insulation = FilterSelector(insulation_filter, 'Thickness')
insulation
# -

# When you have multiple objects of the same type that all share the same field, and want to vary that field's value, you can set the `object_name` to `'*'`, and the selector will modify all of those objects at once.

lights = FieldSelector(class_name='Lights', object_name='*', field_name='Watts per Zone Floor Area')
lights

# Parameters can also be created by defining a function that takes an idf and a value and mutates the idf. These functions can be specific to a certain idf's format, and can perform any arbitrary transformation. Creating these can be more involved.  
# `eppy_funcs` contains the functions `one_window` and `wwr_all`. `one_window` removes windows from a building untill it has only one per wall. `wwr_all` takes a building with one window per wall and adjusts it to have a specific window to wall ratio.

window_to_wall = GenericSelector(set=ef.wwr_all, setup=ef.one_window)
window_to_wall

# ### Sampling
# Since Selectors do not describe the values they can take on, only where those values go, they are not sufficient for sampling. We can specify our samples manually.

samples = pd.DataFrame({
    'Thickness': [x/10 for x in range(1,10)]*2,
    'Watts': [8,10,12]*6,
    'wwr': [0.25, 0.5]*9
})
samples.head()

# We also need to put the selectors in parameters before we can use them in an evaluator.

# +
parameters= [Parameter(selector=x) for x in(insulation, lights, window_to_wall)]
problem = EPProblem(inputs=parameters)

evaluator = EvaluatorEP(problem, building)
# The evaluator will use this objective by default
outputs = evaluator.df_apply(samples ,keep_input=True)
# outputs is a pandas dataframe with one column since only one objective was requested
# -

outputs


