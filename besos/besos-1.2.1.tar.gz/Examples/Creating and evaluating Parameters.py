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

# # Parametric Model
# This notebook covers how to define a parametric eppy model, and get it's energy use for different parameter values.
# ### Various Imports
# `EvaluatorEP` manages energy-plus simulations for a single problem.  
# Problems, like `EPProblem` organise several parameters together.  
# Parameters, like `Parameter` describe a single variable for the building.
# They are composed of a `Descriptor` and a `Selector`.
# `RangeParameter` is a descriptor that indicates a parameter that can take on values from an interval.  
# `CategoryParameter` is a descriptor that indicates a paramter that can take on values from a list.
#

# +
from besos import eppy_funcs as ef
from besos import sampling
from besos.evaluator import EvaluatorEP
from besos.parameters import RangeParameter, CategoryParameter, expand_plist, FieldSelector, Parameter, wwr
from besos.problem import EPProblem

import pandas as pd
# -

# Each building is described by an `.idf` or `epJSON` file. In order to modify it programatically, we load it as a python object.

# by default this will get an example building specifed in the config file.
building = ef.get_building()
# we can specify our own files too.
# (changing the idd file can cause issues, only use one per script/notebook)
# when in idf mode the arguments are building=idf file, data_dict=idd file
# when in json mode the arguments are 

# [Eppy's documentation](https://eppy.readthedocs.io/en/latest/) describes how to explore and modify the idf object. If you are using the newer JSON format, then any JSON parsing library will work.  
# This example uses the fact that the example building contains the following items:
#  - Various `Material` class objects with the 
#    - `Mass NonRes Wall Insulation` (having a `Thickness` field)
#    - `8IN CONCRETE HW` and
#    - `HW CONCRETE` 
#  - A `Construction` class object called `ext-slab` with an `Outside Layer` field
#  - A `WindowMaterial:SimpleGlazingSystem` class object with `UFactor` and `Solar Heat Gain Coefficient` fields
#  - Multiple `Lights` class objects, all of which have a `Watts per Zone Floor Area` field.
#
#  The names class, object and field refer to the 3 layers of nesting present in energyplus building description.

# ## Parameters
# Each way in which the building can be modified is represented by a single parameter. These can be created in various ways, and can be used to automatically modify the idf, as well as to optimise it's design.
# ### Making Parameters
# Parameters are composed of a `Selector` and a `Descriptor`. They can also optionally have a name.  
# There are notebooks which go into more detail on each of these.
# #### Selectors
# Selectors identify which part of the building to modify, and how to modify it. The most common type of selector is a `FieldSelector`. `FieldSelectors` can be created by specifying the class, object, and field names that they apply to.  
#
# The example building loaded above contains a `Material` class object named `Mass NonRes Wall Insulation` which has a `Thickness` field. Below is how to make a selector that modifies this insulation's thickness.

insulation = FieldSelector(class_name='Material', 
                           object_name='Mass NonRes Wall Insulation',
                           field_name='Thickness')

# #### Descriptors
# Descriptors specify what kinds of values are valid for a parameter. If we want to vary a parameter from zero to one excluding the endpoints, we can use a `RangeParameter`, with the apropriate minimum and maximum. (Note that values like 0.001 are also excluded by this example.)

zero_to_one_exclusive = RangeParameter(min_val = 0.01, max_val=0.99)

insulation_param = Parameter(selector=insulation,
                                 value_descriptor=zero_to_one_exclusive,
                                 name='Insulation Thickness')
print(insulation_param)

# Sometimes you might want to specify several `RangeParameter`s at once. The `expand_plist` funcion can do this more concisely. It takes a nested dictionary as input.  
# The keys in the first layer of this dictionary are the names of the idf objects to make parameters for.  
# These are associated with a dictionary that has keys matching the Fields of that object which should be modified. Each field-key corresponds to a tuple containing the minimum and maximum values for that parameter.
# The `class_name` is not specified. Instead the building is searched for objects with the correct `object_name`.

# +
more_parameters = expand_plist(
    # class_name is NOT provided
    #{'object_name':
    # {'field_name':(min, max)}}
    {'NonRes Fixed Assembly Window':
     {'U-Factor':(0.1,5),
      'Solar Heat Gain Coefficient':(0.01,0.99)
     }
    })

for p in more_parameters:
    print(p)
# -

# BESOS also includes some premade parameters, such as window to wall ratio. These can be customised, but for now we will just use the defaults.

# use a special shortcut to get the window-to-wall parameter
window_to_wall = wwr()
print(window_to_wall)

# Parameters can also be created by defining a function that takes an idf and a value and mutates the idf. These functions can be specific to a certain idf's format, and can perform any arbitrary transformation. Creating these can be more involved, and is not covered in this example.

# ## Problems
# problem objects represent the inputs and outputs that we are interested in. We have defined the inputs using parameters above, and will use the default output of electricity use, and the default of no constraints.

parameters = [insulation_param] + more_parameters + [window_to_wall]
problem = EPProblem(inputs=parameters)

# ## Sampling
# Once you have defined your parameters, you may want to generate some random possible buildings. Sampling functions allow you to do this.

samples = sampling.dist_sampler(sampling.lhs, problem, num_samples=3, criterion='maximin')
# arguments can be passed to the specific sampler, here criterion is optional
samples

# ## Evaluation
# Now we can evaluate the samples. We create an energy plus evaluator (`EvaluatroEP`) using the parameters, and idf describing the building, and the objectives we want to measure. For this example we will just use one of the premade objectives: Electricity use for the whole facility.

evaluator = EvaluatorEP(problem, building)
# The evaluator will output electricity use by default
outputs = evaluator.df_apply(samples ,keep_input=True)
# outputs is a pandas dataframe with one new column since only one objective was requested

outputs


