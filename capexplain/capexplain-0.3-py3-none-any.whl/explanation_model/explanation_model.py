import sys
import pprint
import logging
import pandas as pd
from itertools import combinations, permutations
from time import sleep
import statsmodels.formula.api as sm
from psycopg2.extras import Json
from sklearn.linear_model import LinearRegression
from scipy.stats import chisquare, mode
from numpy import percentile, mean
from inspect import currentframe, getframeinfo
from tqdm import tqdm
from capexplain.utils import printException, CombinationsWithLen, progress_iter, PermutationsWithLen
from capexplain.pattern_miner.permtest import *
from capexplain.fd.fd import closure
from capexplain.cl.cfgoption import DictLike
from capexplain.cl.instrumentation import ExecStats


# setup logging
log = logging.getLogger(__name__)

class Explanation(object):
    expl_type = -1
    user_question_direction = 0
    tuple_value = dict()
    top_k_expl = -1
    relevent_pattern = None
    refinement_pattern = None
    score = -1
    distance = -1
    deviation = -1
    denominator = -1

    def __lt__(self, o):
        return self.score < o.score

    def __eq__(self, o):
        return self.score == o.score

    def __init__(self, et, score, distance, deviation, denominator, uqd, tv, top_k_expl, relevent_pattern, refinement_pattern):
        self.expl_type = et
        self.score = score
        self.distance = distance
        self.deviation = deviation
        self.denominator = denominator
        self.user_question_direction = uqd
        self.tuple_value = tv
        self.top_k_expl = top_k_expl
        self.relevent_pattern = relevent_pattern
        self.refinement_pattern = refinement_pattern
        # log.debug("created explanation:\n")

    def ordered_tuple_string(self):
        value_str = ''
        agg = ''
        for key in sorted(self.tuple_value.keys()):
            if key.startswith('count') or key.startswith('sum'):
                agg = key
            else:
                value_str += str(self.tuple_value[key]) + ','
        if agg in self.tuple_value:
            value_str += str(self.tuple_value[agg])
        return value_str

    def to_string(self):
        e_tuple_str = ','.join(map(str, self.tuple_value.values()))
        # res_str = 'Top ' + str(j+1) + ' explanation:\n'
        res_str = ''
        if self.expl_type == 1:
            res_str += 'From local pattern' + ': [' + ','.join(self.relevent_pattern[0]) + ']' +\
                '[' + ','.join(list(map(str, self.relevent_pattern[1]))) + ']' + \
                '[' + ','.join(list(map(str, self.relevent_pattern[2]))) + ']' +\
                '[' + self.relevent_pattern[4] + ']' + \
                (('[' + str(self.relevent_pattern[6].split(',')[0][1:]) + ']') if self.relevent_pattern[4] == 'const' else ('[' + str(self.relevent_pattern[7]) + ']'))
            res_str += '\ndrill down to\n' + ': [' + ','.join(self.refinement_pattern[0]) + ']' + \
                '[' + ','.join(list(map(str, self.refinement_pattern[1]))) + ']' + \
                '[' + ','.join(list(map(str, self.refinement_pattern[2]))) + ']' + \
                '[' + self.refinement_pattern[4] + ']' + \
                (('[' + str(self.refinement_pattern[6].split(',')[0][1:]) + ']') if self.refinement_pattern[4] == 'const' else ('[' + str(self.refinement_pattern[7]) + ']'))
        else:
            res_str += 'Directly from local pattern ' + ': [' + ','.join(self.relevent_pattern[0]) + ']' + \
                '[' + ','.join(list(map(str, self.relevent_pattern[1]))) + ']' + \
                '[' + ','.join(list(map(str, self.relevent_pattern[2]))) + ']' + \
                '[' + self.relevent_pattern[4] + ']' +  \
                (('[' + str(self.relevent_pattern[6].split(',')[0][1:]) + ']') if self.relevent_pattern[4] == 'const' else ('[' + str(self.relevent_pattern[7]) + ']'))
        res_str += '\n'
        res_str += 'Score: ' + str(self.score)
        res_str += '\n'
        res_str += 'Distance: ' + str(self.distance)
        res_str += '\n'
        # res_str += 'Simialriry: ' + str(e[1][1]))
        # res_str += '\n')
        res_str += 'Outlierness: ' + str(self.deviation)
        res_str += '\n'
        res_str += 'Denominator: ' + str(self.denominator)
        res_str += '\n'
        res_str += '(' + e_tuple_str + ')'
        res_str += '\n'
        
        return res_str


