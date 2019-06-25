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

# # Optimisation Run Flexibility
# It is possible to change the configuration of the aglorithm part way through the optimisation process, or even to switch algorithms completely. Doing so requires using platypus algorithms directly, instead of the algorithm wrappers provided through the optimizations module.
#
# First we create an example problem.

# +
from besos import eppy_funcs as ef

from besos.parameters import expand_plist
from besos.evaluator import EvaluatorEP
from besos.problem import EPProblem
from besos import optimizer
import platypus

# +
idf = ef.get_idf()

parameters=expand_plist(
    {'NonRes Fixed Assembly Window':
     {'UFactor':(0.1,5),
      'Solar Heat Gain Coefficient':(0.01,0.99)
     },
     'Mass NonRes Wall Insulation':{'Thickness':(0.01,0.09)},
    })

objectives = ['Electricity:Facility', 'Gas:Facility']

problem = EPProblem(parameters, objectives)

evaluator = EvaluatorEP(problem, idf)
# -

# Here we set up the first algorithm. The `to_platypus` shortcut converts the evaluator to a `platypus.Problem` object.

platypus_problem = evaluator.to_platypus()
algorithm = platypus.NSGAII(problem=platypus_problem)

# Use the **stop button** at the top of the notebook to interrupt the following cell, since it will take a while.  
# Note: The output from the next cells will vary from run to run, due to the randomness used in platypus' algorithms, as well as the amount of time this cell runs for.

try:
    algorithm.run(1000)
except KeyboardInterrupt:
    print('Algorithm interrupted')
algorithm.population[:5]

# Now we want to continue from where the first algorithm left off, but with `EpsMOEA` and only 10 evaluations. In order to make the population carry over, we use the `InjectedPopulation` generator. Then we run the second algorithm.
#
# If we had let the first algorithm finish, we could use `algorithm.result` instead of `algorithm.population` to use the solutions found by the first algorithm as a starting point for the next.

generator = platypus.InjectedPopulation(algorithm.population)
alg2 = platypus.EpsMOEA(problem=platypus_problem, generator=generator, epsilons=3, population_size=10)
alg2.run(10)

# Now we convert the solutions that were found to a dataframe and display them.

optimizer.solutions_to_df(alg2.result, problem, parts=['inputs', 'outputs'])
