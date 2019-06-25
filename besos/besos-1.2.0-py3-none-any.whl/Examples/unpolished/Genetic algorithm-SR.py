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

from besos.parameters import RangeParameter, expand_plist, Parameter
from besos.IO_Objects import DummySelector
from besos.evaluator import EvaluatorSR
from besos.problem import Problem
from besos import optimizer

# +
parameters=[Parameter(DummySelector(), RangeParameter(0, i+1)) for i in range(3)]

def single(vals):
    return ((sum(vals),), ())

def multi(vals):
    return ((sum(vals), min(vals)),())

def multi2(vals):
    return ((sum(vals), -max(vals)), ())

single_evaluator = EvaluatorSR(single, Problem(parameters, 1))
multi_evaluator = EvaluatorSR(multi, Problem(parameters, 2,  minimize_outputs=[True, False]))
multi_min = EvaluatorSR(multi, Problem(parameters, 2,))
# -

parameters

# +
from besos.optimizer import *

single_objective = [GeneticAlgorithm]
multi_objective = [NSGAII, GDE3, SPEA2, SMPSO, CMAES,IBEA]
multi_eps = [EpsMOEA, OMOPSO, EpsNSGAII]

# the change to add JSON support somehow broke EvolutionaryStrategy and PAES

# shortcuts for periodic actions are not included
periodic_actions = [platypus.PeriodicAction, platypus.AdaptiveTimeContinuation,
                    platypus.EpsilonProgressContinuation]

# PESA2 is broken, view https://github.com/Project-Platypus/Platypus/issues/72 for details

# +
def fitness(solutions):
    for s in solutions:
        s.fitness = -s.variables[0] + s.variables[1]


def call(evaluator, alg, **kwargs):
    print(alg.__name__, end=' ')
    try:
        results = alg(evaluator, **kwargs)
        print(len(results))
    except Exception as e:
        print(e)
        
print('-- single objective')
for alg in single_objective:
    call(single_evaluator, alg)
print('-- multiple objective')
for alg in multi_objective:
    call(multi_evaluator, alg)
print('-- multiple objective, epsilon needed')
for alg in multi_eps:
    call(multi_evaluator, alg, epsilons=4)
print('-- other')
call(multi_min, MOEAD)
call(multi_min, NSGAIII, divisions_outer=4)
call(multi_evaluator, ParticleSwarm, fitness=fitness)
# -

# the results for the periodic actions are a bit odd, I may be misusing them.
for pa in periodic_actions:
    alg = platypus.NSGAII(multi_evaluator.to_platypus())
    x = pa(alg)
    x.run(1000)
    print(str(x.__class__).split('.')[-1][:-2], len(x.result))


