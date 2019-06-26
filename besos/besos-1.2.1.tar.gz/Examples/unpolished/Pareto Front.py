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

from besos.parameters import RangeParameter, expand_plist, wwr
from besos.objectives import clear_outputs
from besos.evaluator import EvaluatorEP
from besos.problem import EPProblem
from besos import optimizer
import platypus
from besos import sampling
import pandas as pd

import colorsys
from pandas.plotting import parallel_coordinates
import matplotlib.pyplot as plt
import seaborn as sns
# %matplotlib inline

# +
building = ef.get_building()
clear_outputs(building)

parameters = expand_plist(
    #{'Name of object in idf':
    # {'Property Name':(min, max)}}
    {'NonRes Fixed Assembly Window':
     {'U-Factor':(0.1,5),
      'Solar Heat Gain Coefficient':(0.01,0.99)
     },
     'Mass NonRes Wall Insulation':{'Thickness':(0.01,0.09)},
    })
parameters.append(wwr())

objectives = ['Cooling:EnergyTransfer', 'Heating:EnergyTransfer', 'Electricity:Facility']

constraints = ['CO2:Facility']

problem = EPProblem(parameters, objectives, constraints, constraint_bounds=['<= 900'])

evaluator = EvaluatorEP(problem, building)

plat_problem = evaluator.to_platypus()
# -

'FENESTRATIONSURFACE:DETAILED'.title()

class LoggingArchive(platypus.Archive):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.log = []
    
    def add(self, solution):
        super().add(solution)
        self.log.append(solution)

archive = LoggingArchive()
solutions = optimizer.NSGAII(evaluator, population_size=10, archive=archive, evaluations=20)
df = optimizer.solutions_to_df(archive.log, problem=problem)

df

# +
fig = plt.figure(figsize=(6,6))
ax = fig.add_subplot(111)

a = df['pareto-optimal']
b = df['violation'] == 0

x_label = 'Cooling:EnergyTransfer'
y_label = 'Heating:EnergyTransfer'

for optimal, valid in ((False, False), (False, True), (True, True)):
    if optimal:
        colour = 'g'
    else:
        colour = 'b'
    if valid:
        marker = 'o'
    else:
        marker = 'x'
    mask = (a==optimal) & (b==valid)
    d = df[mask]
    ax.scatter(x=d[x_label], y=d[y_label], marker=marker,
               c=colour, label=f'opt:{optimal}, valid:{valid}')

ax.legend()
ax.set_xlabel(x_label)
ax.set_ylabel(y_label)
# ax.set_ylim(0,2*10**9)
# ax.set_xlim(0,2*10**9)
# -

sns.pairplot(df, vars=problem.names(('inputs', 'outputs', 'constraints')), hue='pareto-optimal')

# adapted from https://stackoverflow.com/q/34071476/8061009
def heatmap(df, problem, parts=('inputs', 'outputs'), sort_by=None, cspace=2, figsize=(6,6)):
    if isinstance(parts, str):
        parts = (parts,)
    columns = problem.names(parts)
    if sort_by:
        df = df.sort_values(sort_by)
    df = df[columns]
    part_map = {part: {'names':problem.names(part)} for part in parts}
    num_colours = sum(len(v['names']) for v in part_map.values()) + cspace * (len(part_map)-1)
    for v in part_map.values():
        v['colours'] = [colorsys.hsv_to_rgb(x*1.0/(num_colours), 0.7, 0.5) for x in range(len(v['names']))]
    
    fig, ax = plt.subplots(figsize=figsize)

    with sns.axes_style('white'):
        for v in part_map.values():
            for colors, name in zip(v['colours'], v['names']):
                # Create cmap
                cmap = sns.light_palette(colors, input='rgb', reverse=False, as_cmap=True)

                sns.heatmap(df.mask(df.isin(df[name])!=1),
                            ax=ax,
                            cbar=False,
                            square=True,
                            annot=False,
                            cmap=cmap,
                            linewidths=0.1)
    ax.yaxis.set_visible(False)
    plt.show()

heatmap(df[df['pareto-optimal']], problem, sort_by='Heating:EnergyTransfer')

def par_coodrs(df, selector=None, label='selected', filter_=None, default_label='no_label',
              figsize=(10,8), columns=None, limit=None):
    fig, ax = plt.subplots(figsize=figsize) 
    for column in df:
        if df[column].min() == df[column].max():
            if columns is not None and column in columns:
                columns.remove(column)
                print(column, 'has a constant value of', df[column].min())
            df = df.drop(column, axis=1)
            
    
    df = (df - df.min())/(df.max()-df.min())
    
    df['colour'] = default_label
    if selector is not None:
        df.loc[selector, 'colour'] = label
    if filter_ is not None:
        df = df[filter_]
    if columns:
        df = df[columns + ['colour']]
    if limit is not None:
        df = df.sample(limit)
    parallel_coordinates(df, 'colour', colormap='prism', ax=ax)
    ax.yaxis.set_visible(False)
    plt.show()

columns = problem.names(('inputs', 'outputs', 'constraints'))
columns

par_coodrs(df,
           selector=(df['violation'] == 0) & (df['pareto-optimal']),
           columns=problem.names(('inputs', 'outputs', 'constraints')))


