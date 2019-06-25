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
from besos import config
from besos import eppy_funcs as ef
from besos import sampling
from besos.evaluator import EvaluatorEP, AdaptiveSR
from besos.parameters import RangeParameter, expand_plist, wwr, Parameter, FieldSelector, FilterSelector
from besos.problem import EPProblem
from besos.objectives import clear_outputs

from pyKriging.krige import kriging  

import pandas as pd
# -

class KrigingEval(AdaptiveSR):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.problem.num_outputs != 1:
            raise ValueError('This model cannont handle multiobjective problems.')
        if self.problem.num_constraints != 0:
            raise ValueError('This model cannont handle constrained problems.')
        
    def train(self):
        self.model = kriging(self.data.values[:,:-1], self.data.values[:,-1])
        self.model.train()
        
    def eval_single(self, values):
        return ((self.model.predict(list(values)),), ())
    
    def get_infill(self, num_datapoints, **kwargs):
        return self.model.infill(num_datapoints, **kwargs)
    
    def update_model(self, new_data, old_data = None) -> None:
        for index, *row in new_data.itertuples():
            inputs = row[:self.problem.num_inputs]
            output = row[-1]
            assert len(row) == self.problem.num_inputs + self.problem.num_outputs
            self.model.addPoint(inputs, output)
        self.model.train()

# +
building = ef.get_building()
clear_outputs(building)

parameters=expand_plist(
    {
        'Mass NonRes Wall Insulation':
        {'Thickness': (0.01, 0.99)},
        'NonRes Fixed Assembly Window':
        {'U-Factor':(0.1,5),
         'Solar Heat Gain Coefficient':(0.01,0.99)},
        'Roof Membrane':
        {'Thickness': (0.003, 0.02)},
        'AtticFloor NonRes Insulation':
        {'Thickness': (0.01, 0.99)},
    })

if config.energy_plus_mode == 'idf':
    def select_zone_infiltration(idf, air_change):
        return [o for o in idf.idfobjects['ZONEINFILTRATION:DESIGNFLOWRATE']
                if (o.Air_Changes_per_Hour) == air_change]
elif config.energy_plus_mode == 'json':
    def select_zone_infiltration(building, air_change):
        return [o for name,o in building['ZoneInfiltration:DesignFlowRate'].items()
                if ('air_changes_per_hour' in o) == air_change]

parameters.extend([
    Parameter(FilterSelector(get_objects=lambda b:select_zone_infiltration(b, True),
                                 field_name='Air Changes per Hour'),
                  RangeParameter(min_val=0, max_val=1),),
    Parameter(FilterSelector(get_objects=lambda b:select_zone_infiltration(b, False),
                                 field_name='Flow per Exterior Surface Area',),
                  RangeParameter(min_val=0, max_val=0.001),
                  name='Infiltration/Area'),
    wwr(),
    Parameter(FieldSelector('Lights', '*', 'Watts per Zone Floor Area'),
                  RangeParameter(1, 20), name='Lights Watts/Area'),
    Parameter(FieldSelector('Lights', '*', 'Fraction Radiant'),
                  RangeParameter(0, 0.8)),
    # note that these fractions are a possible use case for multi-variable parameters,
    # or a valid use of error_value
    Parameter(FieldSelector('ElectricEquipment', '*', 'Watts per Zone Floor Area'),
                  RangeParameter(1, 20), name='Equipment Watts/Area'),
    Parameter(FieldSelector('ElectricEquipment', '*', 'Fraction Radiant'),
                  RangeParameter(0, 1)),
                 ])

problem = EPProblem(parameters)

evaluator = EvaluatorEP(problem, building)

train = sampling.dist_sampler(sampling.lhs, problem, 10)
train = sampling.add_extremes(train, problem)
# this helps this specific evaluator auto-detect the min/max correctly

test = sampling.dist_sampler(sampling.random, problem, 10)
answers = evaluator.df_apply(test)
# -

evaluator.df_apply(test, keep_input=True)

k = KrigingEval(reference=evaluator)
k.do_infill(train)

predictions_before = k.df_apply(test)

predictions_before

k.infill(10)

predictions_after = k.df_apply(test)

dfs = [answers, predictions_before, predictions_after]
names = ['answers', 'before', 'after']
for df, name in zip(dfs, names):
    if name not in df:
        df[name] = df['Electricity:Facility']
        del df['Electricity:Facility']
results = pd.concat(dfs, axis=1)

from sklearn.metrics import r2_score
r2_b = r2_score(results['answers'], results['before'])
r2_a = r2_score(results['answers'], results['after'])
print('before:', r2_b, 'after:', r2_a, 'change in r2:', r2_a - r2_b)

# In the past few runs, adding 10 datapoints have suggested that adding datapoints has resulted in slightly weaker models. This may be due to the model overfitting to values at the extremes of the range, but the change in r2 is very small ( <0.03)

from sklearn.metrics import r2_score
r2_b = r2_score(results['answers'], results['before'])
r2_a = r2_score(results['answers'], results['after'])
print('before:', r2_b, 'after:', r2_a, 'change in r2:', r2_a - r2_b)

results

k.data


