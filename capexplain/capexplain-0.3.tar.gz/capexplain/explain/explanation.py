#!/usr/bin/python
# -*- coding:utf-8 -*- 

import sys, getopt
import pandas, psycopg2
import csv
#import statsmodels.formula.api as smf
from sklearn import preprocessing
import math
import time
from heapq import *
import logging
from capexplain.similarity.category_similarity_matrix import *
from capexplain.similarity.category_similarity_naive import *
from capexplain.similarity.category_network_embedding import *
from capexplain.utils import *
from capexplain.pattern_model.LocalRegressionPattern import *
from capexplain.cl.cfgoption import DictLike
from capexplain.explanation_model.explanation_model import *
#from build.lib.capexplain.database.dbaccess import DBConnection
# setup logging
# log = logging.getLogger(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s line %(lineno)d: %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


TEST_ID = ''
#********************************************************************************
# Configuration for Explanation generation
class ExplConfig(DictLike):

    DEFAULT_RESULT_TABLE = 'pub_large_no_domain'
    # DEFAULT_RESULT_TABLE = 'crime_clean_100000_2'
    DEFAULT_PATTERN_TABLE = 'dev.pub'
    # DEFAULT_PATTERN_TABLE = 'dev.crime_clean_100000'
    DEFAULT_QUESTION_PATH = './input/user_question.csv'

    EXAMPLE_NETWORK_EMBEDDING_PATH = './input/NETWORK_EMBEDDING'
    EXAMPLE_SIMILARITY_MATRIX_PATH = './input/SIMILARITY_DEFINITION'
    DEFAULT_AGGREGATE_COLUMN = '*'
    DEFAULT_EPSILON = 0.25
    DEFAULT_LAMBDA = 0.5
    TOP_K = 10
    PARAMETER_DEV_WEIGHT = 1.0
    # global MATERIALIZED_CNT
    MATERIALIZED_CNT = 0
    # global MATERIALIZED_DICT
    MATERIALIZED_DICT = dict()
    # global VISITED_DICT
    VISITED_DICT = dict()

    REGRESSION_PACKAGES = [ 'scikit-learn', 'statsmodels' ]
    
    def __init__(self,
                 query_result_table = DEFAULT_RESULT_TABLE,
                 pattern_table = DEFAULT_PATTERN_TABLE,
                 user_question_file = DEFAULT_QUESTION_PATH,
                 outputfile = '',
                 aggregate_column = DEFAULT_AGGREGATE_COLUMN,
                 regression_package = 'statsmodels'
    ):
        self.pattern_table = pattern_table
        self.query_result_table = query_result_table
        self.user_question_file = user_question_file
        self.outputfile = outputfile
        self.aggregate_column = aggregate_column
        self.regression_package = regression_package
        self.global_patterns =None
        self.schema = None
        self.global_patterns_dict = None
        self.conn = self.cur = None
#         try:
#             self.conn = psycopg2.connect(dbname=DBConn.db,
#                                          user=DBConn.user,
#                                          host=DBConn.host,
#                                          port=DBConn.port,
#                                          password=DBConn.password)
#             self.pattern_table = DBConn.local_table[:-6]
#             self.cur = self.conn.cursor()
#         except psycopg2.OperationalError:
#             print('Fail to connect to the database!')


    def __str__(self):
        return self.__dict__.__str__()

class TopkHeap(object):
    def __init__(self, k):
        self.topk = k
        self.data = []
 
    def Push(self, elem):
        if len(self.data) < self.topk:
            heappush(self.data, elem)
        else:
            # topk_small = self.data[0]
            # if elem[0] > topk_small[0]:
            #     heapreplace(self.data, elem)
            topk_small = self.data[0]
            if elem.score > topk_small.score:
                heapreplace(self.data, elem)
    def MinValue(self):
        # return min(list(map(lambda x: x[0], self.data)))
        return min(list(map(lambda x: x.score, self.data)))
    def MaxValue(self):
        # return max(list(map(lambda x: x[0], self.data)))
        return max(list(map(lambda x: x.score, self.data)))
    def TopK(self):
        return [x for x in reversed([heappop(self.data) for x in range(len(self.data))])]
    def HeapSize(self):
        return len(self.data)


def predict(local_pattern, t):
    if local_pattern[4] == 'const':
        # predictY = float(local_pattern[7][1:-1])
        predictY = float(local_pattern[6][1:-1].split(',')[0])
    elif local_pattern[4] == 'linear':
        # print(local_pattern, t)
        v = get_V_value(local_pattern[2], t)
        if isinstance(local_pattern[7], str):
            params_str = local_pattern[7].split('\n')
            params_dict = {}
            for i in range(0, len(params_str)-1):
                p_cate = re.compile(r'(.*)\[T\.\s*(.*)\]\s+(-?\d+\.\d+)')
                cate_res = p_cate.findall(params_str[i])
                if len(cate_res) != 0:
                    cate_res = cate_res[0]
                    v_attr = cate_res[0]
                    v_val = cate_res[1]
                    param = float(cate_res[2])
                    if v_attr not in params_dict:
                        params_dict[v_attr] = {}
                    params_dict[v_attr][v_val] = param
                else:
                    p_nume = re.compile(r'([^\s]+)\s+(-?\d+\.\d+)')
                    nume_res = p_nume.findall(params_str[i])
                    if len(nume_res) == 0:
                        continue
                    nume_res = nume_res[0]
                    v_attr = nume_res[0]
                    param = float(nume_res[1])
                    params_dict[v_attr] = param
        else:
            params_dict = local_pattern[7]
        predictY = params_dict['Intercept']
        for v_attr in t:
            v_key = '{}[T.{}]'.format(v_attr, t[v_attr])
            if v_key in params_dict:
                predictY += params_dict[v_key]
            else:
                if v_attr in params_dict:
                    predictY += params_dict[v_attr] * float(t[v_attr])
            
    return predictY


        
def tuple_distance(t1, t2, var_attr, cat_sim, num_dis_norm, agg_col):
    """Compute the similarity between two tuples t1 and t2 on their attributes var_attr

    Args:
        t1, t2: two tuples
        var_attr: variable attributes
        cat_sim: the similarity measure for categorical attributes
        num_dis_norm: normalization terms for numerical attributes
        agg_col: the column of aggregated value
    Returns:
        the Gower similarity between t1 and t2
    """
    dis = 0.0
    cnt = 0
    if var_attr is None:
        var_attr = t1.keys()
    max_dis = 0.0

    for v_col in var_attr:
        col = v_col.replace(' ', '')
        
        if col not in t1 and col not in t2:
            if col == 'name':
                dis += 10000
                cnt += 1
            continue
        if col not in t1 or col not in t2:
            if col == 'name':
                dis += 10000
                cnt += 1
            #     if 1 > max_dis:
            #         max_dis = 1
            # else:
            #     dis += 1
            #     cnt += 1
            #     if 1 > max_dis:
            #         max_dis = 1
            continue
        if col == 'name':
            if t1[col] != t2[col]:
                dis += 10000
            cnt += 1
            continue

        if col == 'venue' or col == 'pubkey':
            if t1[col] != t2[col]:
                dis += 0.25
            cnt += 1
            continue

        if cat_sim.is_categorical(col):
            t1_key = str(t1[col]).replace("'", '').replace(' ', '')
            t2_key = str(t2[col]).replace("'", '').replace(' ', '')
            s = 0
            if t1[col] == t2[col]:
                s = 1
            else:
                if col == 'venue':
                    s = 0.5
            s = cat_sim.compute_similarity(col, t1_key, t2_key, agg_col)
            if s == 0:
                dis += 1
                max_dis = 1
            else:
                dis += (((1.0/s)) * ((1.0/s))) / 100
                # dis += (1-s) * (1-s)
                if math.sqrt((((1.0/s)) * ((1.0/s)) - 1) / 100) > max_dis:
                    max_dis = math.sqrt((((1.0/s)) * ((1.0/s)) - 1) / 100)
            cnt += 1
        else:
            # print( num_dis_norm[col])
            # if col not in num_dis_norm or num_dis_norm[col]['range'] is None:
            #     if t1[col] == t2[col]:
            #         dis += 0
            #     else:
            #         dis += 1
            # else:
            #     if col != agg_col and col != 'index':
            #         # temp = abs(t1[col] - t2[col]) / (num_dis_norm[col]['range'])
            #         temp = abs(t1[col] - t2[col])
            #         # dis += 0.5 * math.pow(temp, 4)
            #         dis += math.pow(temp, 8)
            #     cnt += 1

            if col not in num_dis_norm or num_dis_norm[col]['range'] is None:
                if t1[col] == t2[col]:
                    dis += 0
                else:
                    dis += 1
            else:
                if col != agg_col and col != 'index':
                    # temp = (t1[col] - t2[col]) * (t1[col] - t2[col]) / (num_dis_norm[col]['range'] * num_dis_norm[col]['range'])
                    # temp = abs(t1[col] - t2[col]) / (num_dis_norm[col]['range'])
                    if isinstance(t1[col], datetime.date):
                        # print(398, t1, t2)
                        # print(col, t1[col], t2[col])
                        diff = datetime.datetime(t1[col].year, t1[col].month, t1[col].day) - datetime.datetime.strptime(t2[col], "%Y-%m-%d")
                        temp = diff.days
                    else:
                        # print(398, t1, t2)
                        # print(col, t1[col], t2[col])
                        temp = abs(float(t1[col]) - float(t2[col]))
                    # if temp != 0:
                    #     temp = 1/(1+(math.exp(-temp+2)))

                    dis += 0.5 * math.pow(temp, 8)
                    if temp > max_dis:
                        max_dis = temp
                cnt += 1
            
    return math.pow(dis, 0.5)
    # return max_dis

def get_local_patterns(F, Fv, V, agg_col, model_type, t, conn, cur, pat_table_name, res_table_name):
    local_patterns = []
    local_patterns_dict = {}
        
    if model_type is not None:
        mt_predicate = " AND model='{}'".format(model_type)
    else:
        mt_predicate = ''
    if Fv is not None:
        local_pattern_query = '''SELECT * FROM {} WHERE array_to_string(fixed, ', ')='{}' AND 
            REPLACE(array_to_string(fixed_value, ', '), '"', '') LIKE '%{}%' AND 
            array_to_string(variable, ', ') = '{}' AND
            agg='{}'{};'''.format(
                pat_table_name + '_local' + TEST_ID, str(F).replace("\'", '').replace('[', '').replace(']', ''), 
                str(Fv).replace("\'", '').replace('[', '').replace(']', ''),
                str(V).replace("\'", '').replace('[', '').replace(']', ''), 
                agg_col, mt_predicate
            )
        # print(406, Fv, local_pattern_query)
    else:
        tF = get_F_value(F, t)
        # local_pattern_query = '''SELECT * FROM {} WHERE array_to_string(fixed, ', ')='{}' AND 
        #     REPLACE(array_to_string(fixed_value, ', '), '"', '') = REPLACE('{}', '"', '') AND array_to_string(variable, ', ')='{}' AND
        #     agg='{}'{};'''.format(
        #         pat_table_name + '_local' + TEST_ID, str(F).replace("\'", '').replace('[', '').replace(']', ''), 
        #         str(tF).replace("\'", '"').replace('[', '').replace(']', ''),
        #         str(V).replace("\'", '').replace('[', '').replace(']', ''), 
        #         agg_col, mt_predicate
        #     )
        local_pattern_query = '''SELECT * FROM {} WHERE array_to_string(fixed, ', ')='{}' AND
            REPLACE(array_to_string(fixed_value, ', '), '"', '') LIKE '%{}%' AND array_to_string(variable, ', ')='{}' AND
            agg='{}'{};'''.format(
                pat_table_name + '_local'+TEST_ID, str(F).replace("\'", '').replace('[', '').replace(']', ''),
                '%'.join(list(map(str, tF))),
                str(V).replace("\'", '').replace('[', '').replace(']', ''),
                agg_col, mt_predicate
            )
    # print(293, local_pattern_query)
    cur.execute(local_pattern_query)
    local_patterns = cur.fetchall()
        
    return local_patterns


def get_tuples_by_F(local_pattern, f_value, cur, table_name, cat_sim):
    def tuple_column_to_str_in_where_clause_2(col_value):
        # print(col_value, cat_sim.is_categorical(col_value[0]))
        if cat_sim.is_categorical(col_value[0]):
            # return "like '%" + str(col_value[1]) + "%'"
            return "= '" + str(col_value[1]) + "'"
        else:
            if is_float(col_value[1]):
                return '=' + str(col_value[1])
            else:
                # return "like '%" + str(col_value[1]) + "%'"
                return "= '" + str(col_value[1]) + "'"

    F = str(local_pattern[0]).replace("\'", '')[1:-1]
    V = str(local_pattern[2]).replace("\'", '')[1:-1]
    F_list = F.split(', ')
    V_list = V.split(', ')
    where_clause = ' AND '.join(list(map(lambda x: "{} {}".format(x[0], x[1]), zip(local_pattern[0], map(tuple_column_to_str_in_where_clause_2, zip(F_list, f_value))))))
    tuples_query = '''SELECT {},{},{} as {} FROM {} WHERE {} GROUP BY {}, {};'''.format(
            F, V, local_pattern[3].replace('_', '(') + ')', local_pattern[3], table_name, where_clause, F, V
        )
    # tuples_query = "SELECT * FROM {} WHERE {};".format(table_name, where_clause)
    
    # column_name_query = "SELECT column_name FROM information_schema.columns where table_name='{}';".format(table_name)
    # print(column_name_query)
    # cur.execute(column_name_query)
    # column_name = cur.fetchall()
    column_name = F_list + V_list + [local_pattern[3]]
    cur.execute(tuples_query)
    # print(tuples_query)
    tuples = []
    res = cur.fetchall()
    min_agg = 1e10
    max_agg = -1e10
    for row in res:
        min_agg = min(min_agg, row[-1])
        max_agg = max(max_agg, row[-1])
        tuples.append(dict(zip(map(lambda x: x, column_name), row)))
        # row_data = {}
        # cnt = 0 
        # for f_attr in F_list:    
        #     if is_float(row[cnt]):
        #         row_data[f_attr] = float(row[cnt])
        #     elif is_integer(row[cnt]):
        #         row_data[f_attr] = float(int(row[cnt]))
        #     else:
        #         row_data[f_attr] = t[cnt]
        #     cnt += 1
        # for v_attr in V_list:
        #     if is_float(row[cnt]):
        #         row_data[v_attr] = float(row[cnt])
        #     elif is_integer(row[cnt]):
        #         row_data[v_attr] = float(int(row[cnt]))
        #     else:
        #         row_data[v_attr] = row[cnt]
        #     cnt += 1
        # row_data[pat[4] + '(' + pat[3] + ')'] = row[-1]
        # tuples.append(row_data)
    return tuples, max_agg - min_agg

def get_tuples_by_F_V2(lp1, lp2, f_value, v_value, conn, cur, table_name, cat_sim):
    def tuple_column_to_str_in_where_clause_2(col_value):
        # print(col_value, cat_sim.is_categorical(col_value[0]))
        if cat_sim.is_categorical(col_value[0]):
            # return "like '%" + str(col_value[1]) + "%'"
            return "= '" + str(col_value[1]) + "'"
        else:
            if is_float(col_value[1]):
                return '=' + str(col_value[1])
            else:
                # return "like '%" + str(col_value[1]) + "%'"
                return "= '" + str(col_value[1]) + "'"

    F1 = str(lp1[0]).replace("\'", '')[1:-1]
    V1 = str(lp1[2]).replace("\'", '')[1:-1]
    F1_list = F1.split(', ')
    V1_list = V1.split(', ')
    # print(lp1)
    # print(lp2)
    F2 = str(lp2[0]).replace("\'", '')[1:-1]
    V2 = str(lp2[2]).replace("\'", '')[1:-1]
    F2_list = F2.split(', ')
    V2_list = V2.split(', ')
    where_clause = ' AND '.join(list(map(lambda x: "{} {}".format(x[0], x[1]), zip(lp1[0], map(tuple_column_to_str_in_where_clause_2, zip(F1_list, f_value))))))
    where_clause += ' AND ' 
    where_clause += ' AND '.join(list(map(lambda x: "{} {}".format(x[0], x[1]), zip(lp1[2], map(tuple_column_to_str_in_where_clause_2, zip(V1_list, v_value))))))
    tuples_query = '''SELECT {},{},{} as {} FROM {} WHERE {} GROUP BY {}, {};'''.format(
            F2, V2, lp2[3].replace('_', '(') + ')', lp2[3], table_name, where_clause, F2, V2
        )
    
    column_name = F2_list + V2_list + [lp2[3]]
    cur.execute(tuples_query)
    # print(tuples_query)
    tuples = []
    res = cur.fetchall()
    min_agg = 1e10
    max_agg = -1e10
    for row in res:
        min_agg = min(min_agg, row[-1])
        max_agg = max(max_agg, row[-1])
        tuples.append(dict(zip(map(lambda x: x, column_name), row)))
        
    return tuples, max_agg - min_agg


def get_tuples_by_F_V(lp1, lp2, f_value, v_value, conn, cur, table_name, cat_sim, ExplConfig):
    def tuple_column_to_str_in_where_clause_2(col_value):
        # print(col_value, cat_sim.is_categorical(col_value[0]))
        if cat_sim.is_categorical(col_value[0]):
            # return "like '%" + str(col_value[1]) + "%'"
            return "= '" + str(col_value[1]) + "'"
        else:
            if is_float(col_value[1]):
                return '=' + str(col_value[1])
            else:
                # return "like '%" + str(col_value[1]) + "%'"
                return "= '" + str(col_value[1]) + "'"
    def tuple_column_to_str_in_where_clause_3(col_value):
        # print(col_value, cat_sim.is_categorical(col_value[0]))
        if cat_sim.is_categorical(col_value[0]):
            # return "like '%" + str(col_value[1]) + "%'"
            return "= '" + str(col_value[1]) + "'"
        else:
            if is_float(col_value[1]):
                return '>=' + str(col_value[1])
            else:
                # return "like '%" + str(col_value[1]) + "%'"
                return "= '" + str(col_value[1]) + "'"

    def tuple_column_to_str_in_where_clause_4(col_value):
        # print(col_value, cat_sim.is_categorical(col_value[0]))
        if cat_sim.is_categorical(col_value[0]):
            # return "like '%" + str(col_value[1]) + "%'"
            return "= '" + str(col_value[1]) + "'"
        else:
            if is_float(col_value[1]):
                return '<=' + str(col_value[1])
            else:
                # return "like '%" + str(col_value[1]) + "%'"
                return "= '" + str(col_value[1]) + "'"

    F1 = str(lp1[0]).replace("\'", '')[1:-1]
    V1 = str(lp1[2]).replace("\'", '')[1:-1]
    F1_list = F1.split(', ')
    V1_list = V1.split(', ')

    F2 = str(lp2[0]).replace("\'", '')[1:-1]
    V2 = str(lp2[2]).replace("\'", '')[1:-1]
    F2_list = F2.split(', ')
    V2_list = V2.split(', ')
    G_list = sorted(F2_list + V2_list)
    G_key = str(G_list).replace("\'", '')[1:-1]
    f_value_key = str(f_value).replace("\'", '')[1:-1]
    if lp2[3] == 'count':
        agg_fun = 'count(*)'
    else:
        agg_fun = lp2[3].replace('_', '(') + ')'



    if G_key not in ExplConfig.MATERIALIZED_DICT:
        ExplConfig.MATERIALIZED_DICT[G_key] = dict()
        
    if f_value_key not in ExplConfig.MATERIALIZED_DICT[G_key]:
        ExplConfig.MATERIALIZED_DICT[G_key][f_value_key] = ExplConfig.MATERIALIZED_CNT
        dv_query = '''DROP VIEW IF EXISTS MV_{};'''.format(str(ExplConfig.MATERIALIZED_CNT))
        cur.execute(dv_query)
        # print(504, MATERIALIZED_CNT)
        cmv_query = '''
            CREATE VIEW MV_{} AS SELECT {}, {} as {} FROM {} WHERE {} GROUP BY {};
        '''.format(
            str(ExplConfig.MATERIALIZED_CNT), G_key, agg_fun, lp2[3], table_name,
            ' AND '.join(list(map(lambda x: "{} {}".format(x[0], x[1]), 
                zip(lp1[0], map(tuple_column_to_str_in_where_clause_2, zip(F1_list, f_value)))))),
            G_key
        )
        # print(585, cmv_query)
        cur.execute(cmv_query)
        conn.commit()
        ExplConfig.MATERIALIZED_CNT += 1


    where_clause = ' AND '.join(list(map(lambda x: "{} {}".format(x[0], x[1]), zip(lp1[0], map(tuple_column_to_str_in_where_clause_2, zip(F1_list, f_value))))))
    if v_value is not None:
        where_clause += ' AND ' 
        # print(593, v_value)
        v_range_l = map(lambda x: v_value[0][x] + v_value[1][x][0], range(len(v_value[0])))
        v_range_r = map(lambda x: v_value[0][x] + v_value[1][x][1], range(len(v_value[0])))
        where_clause += ' AND '.join(list(map(lambda x: "{} {}".format(x[0], x[1]), zip(lp1[2], 
            map(tuple_column_to_str_in_where_clause_3, zip(V1_list, v_range_l))))))
        where_clause += ' AND ' 
        where_clause += ' AND '.join(list(map(lambda x: "{} {}".format(x[0], x[1]), zip(lp1[2], 
            map(tuple_column_to_str_in_where_clause_4, zip(V1_list, v_range_r))))))
    tuples_query = '''SELECT {},{},{} FROM MV_{} WHERE {};'''.format(
            F2, V2, lp2[3], str(ExplConfig.MATERIALIZED_DICT[G_key][f_value_key]), where_clause
        )
    # print(604, tuples_query)
    column_name = F2_list + V2_list + [lp2[3]]
    cur.execute(tuples_query)
    # print(tuples_query)
    tuples = []
    tuples_dict = dict()
    res = cur.fetchall()
    min_agg = 1e10
    max_agg = -1e10
    for row in res:
        min_agg = min(min_agg, row[-1])
        max_agg = max(max_agg, row[-1])
        tuples.append(dict(zip(map(lambda x: x, column_name), row)))
        fv = get_F_value(lp2[0], tuples[-1])
        f_key = str(fv).replace('\'', '')[1:-1]
        if f_key not in tuples_dict:
            tuples_dict[f_key] = []
        tuples_dict[f_key].append(tuples[-1])
        
    return tuples, (min_agg, max_agg), tuples_dict


def get_tuples_by_gp_uq(gp, f_value, v_value, conn, cur, table_name, cat_sim, ExplConfig):
    def tuple_column_to_str_in_where_clause_2(col_value):
        # print(col_value, cat_sim.is_categorical(col_value[0]))
        if cat_sim.is_categorical(col_value[0]) or col_value[0] == 'year':
            # return "like '%" + str(col_value[1]) + "%'"
            return "= '" + str(col_value[1]) + "'"
        else:
            if is_float(col_value[1]):
                return '=' + str(col_value[1])
            else:
                # return "like '%" + str(col_value[1]) + "%'"
                return "= '" + str(col_value[1]) + "'"
    
    F1 = str(gp[0]).replace("\'", '')[1:-1]
    V1 = str(gp[1]).replace("\'", '')[1:-1]
    F1_list = F1.split(', ')
    V1_list = V1.split(', ')
    G_list = sorted(F1_list + V1_list)
    G_key = str(G_list).replace("\'", '')[1:-1]
    f_value_key = str(f_value).replace("\'", '')[1:-1]
    v_value_key = str(v_value).replace("\'", '')[1:-1]

    if gp[2] == 'count':
        agg_fun = 'count(*)'
    else:
        agg_fun = gp[2].replace('_', '(') + ')'

    
    if G_key not in ExplConfig.MATERIALIZED_DICT:
        ExplConfig.MATERIALIZED_DICT[G_key] = dict()
        
    if f_value_key not in ExplConfig.MATERIALIZED_DICT[G_key]:
        ExplConfig.MATERIALIZED_DICT[G_key][f_value_key] = ExplConfig.MATERIALIZED_CNT
        dv_query = '''DROP VIEW IF EXISTS MV_{};'''.format(str(ExplConfig.MATERIALIZED_CNT))
        cur.execute(dv_query)
        # print(504, MATERIALIZED_CNT)
        cmv_query = '''
            CREATE VIEW MV_{} AS SELECT {}, {} as {} FROM {} WHERE {} GROUP BY {};
        '''.format(
            str(ExplConfig.MATERIALIZED_CNT), G_key, agg_fun, gp[2], table_name,
            ' AND '.join(list(map(lambda x: "{} {}".format(x[0], x[1]), 
                zip(gp[0], map(tuple_column_to_str_in_where_clause_2, zip(F1_list, f_value)))))),
            G_key
        )
        # print(585, cmv_query)
        cur.execute(cmv_query)
        conn.commit()
        ExplConfig.MATERIALIZED_CNT += 1


    where_clause = ' AND '.join(
        list(map(lambda x: "{} {}".format(x[0], x[1]), zip(gp[0], map(
            tuple_column_to_str_in_where_clause_2, zip(F1_list, f_value)))))) + ' AND ' + \
        ' AND '.join(list(map(lambda x: "{} {}".format(x[0], x[1]), 
                zip(gp[1], map(tuple_column_to_str_in_where_clause_2, zip(V1_list, v_value))))))

    tuples_query = '''SELECT {} FROM MV_{} WHERE {};'''.format(
            gp[2], str(ExplConfig.MATERIALIZED_DICT[G_key][f_value_key]), where_clause
        )
    # print(530, tuples_query)
    cur.execute(tuples_query)
    res = cur.fetchall()
    return res[0]


def find_global_patterns_exact_match(global_patterns_dict, F_prime_set, V_set, agg_col, reg_type):
    gp_list = []
    for v_key in global_patterns_dict:
        # print(v_key, F_prime_set)
        F_key_set = set(f_key[1:-1].replace("'", '').split(', '))
        # print(545, f_key)
        # F_set = set(f_key)
        # print(579, f_key, F_set, t_set)
        if F_key_set != F_prime_set:
            continue
        
        for v_key in global_patterns_dict[f_key]:
            V_key_set = set(v_key[1:-1].replace("'", '').split(', '))
            if V_key_set != V_set:
                continue
            for pat in global_patterns_dict[f_key][v_key]:
                if pat[2] != agg_col or pat[3] != reg_type:
                    continue
                gp_list.append(pat)
    return gp_list

def find_patterns_refinement(global_patterns_dict, F_prime_set, V_set, agg_col, reg_type, ExplConfig):
    # pattern refinement can have different model types
    # e.g., JH’s #pub increases linearly, but JH’s #pub on VLDB remains a constant
    gp_list = []
    v_key = str(sorted(list(V_set)))
    for f_key in global_patterns_dict[0][v_key]:
        F_key_set = set(f_key[1:-1].replace("'", '').split(', '))
        if F_prime_set.issubset(F_key_set):
            for pat in global_patterns_dict[0][v_key][f_key]:
                if pat[2] == agg_col:
                    pat_key = f_key + '|,|' + v_key + '|,|' + pat[2] + '|,|' + pat[3]
                    
                    gp_list.append(pat)
                    if pat_key not in ExplConfig.VISITED_DICT:
                        ExplConfig.VISITED_DICT[pat_key] = True
    return gp_list


def score_of_explanation(t1, t2, cat_sim, num_dis_norm, dir, denominator = 1, lp1 = None, lp2 = None):
    if lp1 is None:
        return 1.0
    else:
        #print(lp1, lp2, t1, t2)
        agg_col = lp1[3]
        t1fv = dict(zip(lp1[0] + lp1[2], map(lambda x:x, get_F_value(lp1[0] + lp1[2], t1))))
        t2fv = dict(zip(lp2[0] + lp2[2], map(lambda x:x, get_F_value(lp2[0] + lp2[2], t2))))
        # if lp1 == lp2:
        #     t_sim = tuple_similarity(t1fv, t2fv, lp1[2], cat_sim, num_dis_norm, agg_col)
        # else:
        #     t_sim = tuple_similarity(t1fv, t2fv, None, cat_sim, num_dis_norm, agg_col)
        # t_sim = tuple_similarity(t1fv, t2fv, None, cat_sim, num_dis_norm, agg_col)
        t_dis = tuple_distance(t1fv, t2fv, None, cat_sim, num_dis_norm, agg_col)
        cnt1 = 0
        cnt2 = 0
        for a1 in t1:
            if a1 != 'lambda' and a1 != agg_col:
                cnt1 += 1
        for a2 in t2:
            if a2 != 'lambda' and a2 != agg_col:
                cnt2 += 1
        
        if len(t1.keys()) + 1 != len(t2.keys()):
            diff = len(t2.keys()) - len(t1.keys()) - 1
            if 'lambda' not in t2:
                diff += 1
            w = 1
            if 'name' in t2 and 'name' not in t1:
                w = 10000
            t_dis = math.sqrt(t_dis * t_dis + w * diff * diff)
            
            # print(488, t1, t2)
        # print local_cons[i].var_attr, row
        t1v = dict(zip(lp1[2], map(lambda x:x, get_V_value(lp1[2], t1))))        
        predicted_agg1 = predict(lp1, t1v)
        t2v = dict(zip(lp2[2], map(lambda x:x, get_V_value(lp2[2], t2))))        
        predicted_agg2 = predict(lp2, t2v)
        # deviation - counterbalance_needed 
        deviation = float(t1[agg_col]) - predicted_agg1
        counterbalance = t2[agg_col] - predicted_agg2
        # deviation_normalized = (t1[agg_col] - predicted_agg1) / predicted_agg1
        # influence = -deviation / counterbalance
        #score = (deviation + counterbalance) * t_sim
        #score = deviation * (math.exp(t_sim) - 1)
        

        # if t_sim == 1:
        #     score = deviation * -dir
        # else:
        #     score = deviation * math.exp(t_sim) * -dir
        if t_dis == 0:
            score = deviation * -dir
        else:
            score = deviation / t_dis * -dir
        
        # score = deviation * t_sim * -dir * 1 / (1 + math.exp(-(influence - 0.5)))
        # score *= math.log(deviation_normalized + 3)
        # score /= counterbalance
        # print(414, t1fv, t2fv)
        # print(t_dis, deviation, score)
        # return score / float(denominator) * cnt1 / cnt2
        return [100 * score / float(denominator), t_dis, 0, deviation, float(denominator)]

def compare_tuple(t1, t2):
    flag1 = True
    for a in t1:
        if (a != 'lambda' and a.find('_') == -1):
            if a not in t2:
                flag1 = False
            elif t1[a] != t2[a]:
                return 0
    flag2 = True
    for a in t2:
        if (a != 'lambda' and a.find('_') == -1):
            if a not in t1:
                flag2 = False
            elif t1[a] != t2[a]:
                return 0
    
    if flag1 and flag2:
        return -1
    elif flag1:
        return -1
    else:
        return 0

def DrillDown(global_patterns_dict, local_pattern, F_set, U_set, V_set, t_prime_coarser, t_coarser, t_prime, target_tuple,
        conn, cur, pat_table_name, res_table_name, cat_sim, num_dis_norm, 
        dir, query_result, norm_lb, dist_lb, tkheap, ExplConfig):
    reslist = []
    F_prime_set = F_set.union(U_set)
    agg_col = local_pattern[3]
    # gp2_list = find_global_patterns_exact_match(global_patterns_dict, F_prime_set, V_set, local_pattern[3], local_pattern[4])
    # gp2_list = find_patterns_refinement(global_patterns_dict, F_prime_set, V_set, local_pattern[3], local_pattern[4])
    gp2_list = find_patterns_refinement(global_patterns_dict, F_set, V_set, local_pattern[3], local_pattern[4], ExplConfig)
    # print(714, F_set, V_set, gp2_list)
    if len(gp2_list) == 0:
        return []
    for gp2 in gp2_list:
        # if random.random() < 0.3:
        #     continue
        # print(693, gp2)
        if dir == 1:
            dev_ub = abs(gp2[7])
        else:
            dev_ub = abs(gp2[6])
        # dev_ub = agg_maxmin[0][0] - agg_maxmin[0][1]
        k_score = tkheap.MinValue()
        # print(888, dev_ub, k_score, 100 * float(dev_ub) / (dist_lb * float(norm_lb)))
        if tkheap.HeapSize() == ExplConfig.TOP_K and 100 * float(dev_ub) / (dist_lb * float(norm_lb)) <= k_score:
            # print(890, dev_ub, dist_lb, norm_lb, gp2[0], gp2[1])
            continue
        # lp2_list = get_local_patterns(gp2[0], None, gp2[1], gp2[2], None, t_prime, conn, cur, pat_table_name, res_table_name)
        # print(731, t_prime)
        lp2_list = get_local_patterns(gp2[0], None, gp2[1], gp2[2], gp2[3], t_prime, conn, cur, pat_table_name, res_table_name)
        # print(733, lp2_list)
        if len(lp2_list) == 0:
            continue
        lp2 = lp2_list[0]
        
        f_value = get_F_value(local_pattern[0], t_prime)
        tuples_same_F, agg_range, tuples_same_F_dict = get_tuples_by_F_V(local_pattern, lp2, f_value, 
            # [get_V_value(local_pattern[2], t_prime), [[-3, 3]]],
            None,
            conn, cur, res_table_name, cat_sim,
            ExplConfig)
        lp3_list = get_local_patterns(lp2[0], f_value, lp2[2], lp2[3], lp2[4], t_prime, conn, cur, pat_table_name, res_table_name)
        # tuples_same_F, agg_range = get_tuples_by_F(local_pattern, lp2, f_value, 
        #     conn, cur, res_table_name, cat_sim)
        # tuples_same_F, agg_range, tuples_same_F_dict = get_tuples_by_F_V(local_pattern, lp2, f_value, None,
        #     conn, cur, res_table_name, cat_sim)
        # print(725, local_pattern[0], local_pattern[1], local_pattern[2], lp2[0], lp2[1], lp2[2])
        # print(725, len(tuples_same_F), len(lp3_list))
        for lp3 in lp3_list:
            if dir == 1:
                dev_ub = abs(lp3[9])
            else:
                dev_ub = abs(lp3[8])
            # dev_ub = agg_maxmin[0][0] - agg_maxmin[0][1]
            k_score = tkheap.MinValue()
            print(919, dev_ub, k_score, 100 * float(dev_ub) / (dist_lb * float(norm_lb)))
            if tkheap.HeapSize() == ExplConfig.TOP_K and 100 * float(dev_ub) / (dist_lb * float(norm_lb)) <= k_score:
                print(921, dev_ub, dist_lb, norm_lb, lp3[0], lp3[1])
                continue
            f_key = str(lp3[1]).replace('\'', '')[1:-1]
            if f_key in tuples_same_F_dict:
                for idx, row in enumerate(tuples_same_F_dict[f_key]):
                    for idx2, row2 in enumerate(t_coarser):
                        if get_V_value(local_pattern[2], row2) == get_V_value(local_pattern[2], row):
                            s = score_of_explanation(row, target_tuple, cat_sim, num_dis_norm, dir, float(row2[agg_col]), lp3, lp2)
                            break
                
                    # e.g. U = {Venue}, u = {ICDE}, do not need to check whether {Author, Venue} {Year} holds on (JH, ICDE)
                    # expected values are replaced with the average across year for all (JH, ICDE, year) tuples
                    #s = score_of_explanation(row, t_prime, cat_sim)
                    cmp_res = compare_tuple(row, target_tuple)
                    if cmp_res == 0: # row is not subset of target_tuple, target_tuple is not subset of row
                        # print(551, row, target_tuple, s)
                        # reslist.append([s[0], s[1:], dict(row), local_pattern, lp3, 1])  
                        reslist.append(Explanation(1, s[0], s[1], s[2], s[3], dir, dict(row), ExplConfig.TOP_K, local_pattern, lp3))
                    # else:
                    #     reslist.append([-s[0], s[1:], dict(row), local_pattern, lp3, 1])  
            # for f_key in tuples_same_F_dict:
            # # commented finer pattern holds only
            # if gp2 does not hold on (t[F], u):
            #     continue
            # e.g.{Author, venue} {Year} holds on (JH, ICDE)
            # lp3 = (F', (t[F], u), V, agg, a, m3)
            # s = score_of_explanation((t[F],u,t[V]), t, lp3, lp2)
            # f_prime_value = f_key.split(', ')
            # v_prime_value = get_V_value(lp2[0], row)
            # if v_prime_value[0]
            # f_prime_value = get_F_value(lp2[0], row)
            # lp3 = get_local_patterns(lp2[0], f_prime_value, lp2[2], lp2[3], lp2[4], row, conn, cur, pat_table_name, res_table_name)
            # lp3 = get_local_patterns(lp2[0], f_prime_value, lp2[2], lp2[3], lp2[4], tuples_same_F_dict[f_key][0], conn, cur, pat_table_name, res_table_name)

            # print(791, f_key, f_prime_value, len(lp3))
            # if len(lp3) == 0:
            #     continue
            # for row in tuples_same_F_dict[f_key]:
            #     s = score_of_explanation(row, target_tuple, cat_sim, num_dis_norm, dir, float(t_coarser[agg_col]), lp3[0], lp2)
            
            #     # e.g. U = {Venue}, u = {ICDE}, do not need to check whether {Author, Venue} {Year} holds on (JH, ICDE)
            #     # expected values are replaced with the average across year for all (JH, ICDE, year) tuples
            #     #s = score_of_explanation(row, t_prime, cat_sim)
            #     if not equal_tuple(row, target_tuple):
            #         # print(551, row, target_tuple, s)
            #         reslist.append([s[0], s[1:], dict(row), local_pattern, lp3[0], 1])

    
    return reslist

def find_explanation_regression_based(user_question_list, global_patterns, global_patterns_dict, 
    cat_sim, num_dis_norm, agg_col, conn, cur, pat_table_name, res_table_name, ExplConfig):

    """Find explanations for user questions

    Args:
        data: data['df'] is the data frame storing Q(R)
            data['le'] is the label encoder, data['ohe'] is the one-hot encoder
        user_question_list: list of user questions (t, dir), all questions have the same Q(R)
        cons: list of fixed attributes and variable attributes of global constraints
        cat_sim: the similarity measure for categorical attributes
        num_dis_norm: normalization terms for numerical attributes
        cons_epsilon: threshold for local regression constraints
        agg_col: the column of aggregated value
        regression_package: which package is used to compute regression 
    Returns:
        the top-k list of explanations for each user question
    """
    answer = [[] for i in range(len(user_question_list))]
    local_pattern_loading_time = 0
    question_validating_time = 0
    score_computing_time = 0
    score_computing_time_list = []
    result_merging_time = 0
    local_patterns_list = []
    # print(792, global_patterns)

    for j, uq in enumerate(user_question_list):
        dir = uq['dir']
        topK_heap = TopkHeap(ExplConfig.TOP_K)
        marked = {}

        t = dict(uq['target_tuple'])
        start = time.time()
        
        
        end = time.time()
        local_pattern_loading_time += end - start

        uq['global_patterns'] = find_patterns_relevant(
                global_patterns_dict, uq['target_tuple'], conn, cur, res_table_name, pat_table_name, cat_sim)

        # print(811, len(uq['global_patterns']))
        candidate_list = [[] for i in range(len(uq['global_patterns']))]
        top_k_lists = [[] for i in range(len(uq['global_patterns']))]
        validate_res_list = []
        # local_patterns_list.append(local_patterns)
        local_patterns = []
        
        psi = []
        
        ExplConfig.VISITED_DICT = dict()
        score_computing_time_cur_uq = 0
        score_computing_start = time.time()
        explanation_type = 0
        for i in range(0, len(uq['global_patterns'])):
            top_k_lists[i] = [4, uq['global_patterns'][i], t, []]
            local_patterns.append(None)
            F_key = str(sorted(uq['global_patterns'][i][0]))
            V_key = str(sorted(uq['global_patterns'][i][1]))
            pat_key = F_key + '|,|' + V_key + '|,|' + uq['global_patterns'][i][2] + '|,|' + uq['global_patterns'][i][3]
            if pat_key in ExplConfig.VISITED_DICT:
                continue
            ExplConfig.VISITED_DICT[pat_key] = True

            
            tF = get_F_value(uq['global_patterns'][i][0], t)
            local_pattern_query_fixed = '''SELECT * FROM {} 
                    WHERE array_to_string(fixed, ', ')='{}' AND 
                    array_to_string(fixed_value, ', ')='{}' AND
                    array_to_string(variable, ', ')='{}' AND 
                    agg='{}' AND model='{}'
                ORDER BY theta;
            '''.format(
                pat_table_name + '_local' + TEST_ID, 
                str(uq['global_patterns'][i][0]).replace("\'", '').replace('[', '').replace(']', ''),
                str(tF)[1:-1].replace("\'", ''),
                str(uq['global_patterns'][i][1]).replace("\'", '').replace('[', '').replace(']', ''), 
                uq['global_patterns'][i][2], uq['global_patterns'][i][3] 
            )
            cur.execute(local_pattern_query_fixed)
            res_fixed = cur.fetchall()
            if len(res_fixed) == 0:
                continue
            local_patterns[i] = res_fixed[0]
            # if len(local_patterns[i][2]) > 1 or local_patterns[i][2][0] != 'year':
            #     continue
            T_set = set(t.keys()).difference(set(['lambda', uq['global_patterns'][i][2]]))
            psi.append(0)
            agg_col = local_patterns[i][3]
            start = time.time()
            # print('PAT', i, local_patterns[i])
            # t_coarser_list, agg_range, t_coarser_dict = get_tuples_by_F_V(local_patterns[i], local_patterns[i], 
            #     get_F_value(local_patterns[i][0], t), [get_V_value(local_patterns[i][2], t), [[0, 0]]],
            #     conn, cur, res_table_name, cat_sim)
            t_t_list, agg_range, t_t_dict = get_tuples_by_F_V(local_patterns[i], local_patterns[i], 
                get_F_value(local_patterns[i][0], t), 
                #[get_V_value(local_patterns[i][2], t), [[-3, 3]]],
                None,
                conn, cur, res_table_name, cat_sim,
                ExplConfig)
            # print(t_t_list)
            dist_lb = 1e10
            dev_ub = 0
            for t_t in t_t_list:
                if compare_tuple(t_t, t) == 0:
                    s = score_of_explanation(t_t, t, cat_sim, num_dis_norm, dir, t_t[agg_col], local_patterns[i], local_patterns[i])
                    if str(t_t) not in marked:
                        marked[str(t_t)] = True
                        # topK_heap.Push([s[0], s[1:], 
                        #     list(map(lambda y: y[1], sorted(t_t.items(), key=lambda x: x[0]))), 
                        #     local_patterns[i], None, 0])
                        topK_heap.Push(Explanation(0, s[0], s[1], s[2], s[3], uq['dir'],
                            # list(map(lambda y: y[1], sorted(t_t.items(), key=lambda x: x[0]))), 
                            dict(t_t),
                            ExplConfig.TOP_K, local_patterns[i], None))
                    # top_k_lists[i][-1].append([s[0], s[1:], dict(t_t), local_patterns[i], None, 0])
                    top_k_lists[i][-1].append(Explanation(0, s[0], s[1], s[2], s[3], uq['dir'],
                            dict(t_t),
                            ExplConfig.TOP_K, local_patterns[i], None))
                    if s[1] < dist_lb:
                        dist_lb = s[1]
                    if abs(s[3]) > dev_ub:
                        dev_ub = abs(s[3])
            if dist_lb < 1e-10:
                dist_lb = 0.01

            
            end = time.time()
            question_validating_time += end - start

            
            F_set = set(local_patterns[i][0])
            V_set = set(local_patterns[i][2])
            
            # if 'venue' in local_patterns[i][0] and 'name' not in local_patterns[i][0]:
            #     continue
            # if 'pubkey' in local_patterns[i][0] and 'name' not in local_patterns[i][0]:
            #     continue
            # F union V \subsetneq G            
            
            # print(t_coarser)
            t_coarser_copy = list(t_t_list)
            # t_coarser_copy[agg_col] = 1
            # if len(local_patterns[i][0]) + len(local_patterns[i][2]) < len(t.keys()) -2:
                # if 'pubkey' in local_patterns[i][0] and 'name' not in local_patterns[i][0]:
                #     continue
            # if 'venue' in local_patterns[i][0] and 'name' not in local_patterns[i][0]:
            #     continue

            # dev_ub_list = get_dev_upper_bound(local_patterns[i])
            # dev_ub = agg_range[1] - agg_range[0]
            norm_lb = min(list(map(lambda x: x[agg_col], t_coarser_copy)))
            # cur_top_k_res = topK_heap.TopK()
            # k_score = min(map(lambda x:x[0], cur_top_k_res))
            k_score = topK_heap.MinValue()
            # k_score = topK_heap.MaxValue()
            print(1124, k_score, 100 * float(dev_ub) / (dist_lb * float(norm_lb)))
            if topK_heap.HeapSize() == ExplConfig.TOP_K and 100 * float(dev_ub) / (dist_lb * float(norm_lb)) <= k_score:
                print(1126, dev_ub, dist_lb, norm_lb, local_patterns[i][0], local_patterns[i][1])
                continue
            top_k_lists[i][-1] += DrillDown(global_patterns_dict, local_patterns[i], 
                F_set, T_set.difference(F_set.union(V_set)), V_set, t_coarser_copy, t_coarser_copy, t, t,
                conn, cur, pat_table_name, res_table_name, cat_sim, num_dis_norm,
                dir, uq['query_result'],
                norm_lb, dist_lb, topK_heap, ExplConfig)
            for tk in top_k_lists[i][-1]:
                # print(937, tk.to_string())
                # if str(tk[2]) not in marked:
                if str(tk.tuple_value) not in marked:
                    # marked[str(tk[2])] = True
                    marked[str(tk.tuple_value)] = True
                    # topK_heap.Push([tk[0], tk[1], 
                    #     list(map(lambda y: y[1], sorted(tk[2].items(), key=lambda x: x[0]))), 
                    #     tk[3], tk[4], tk[5]])
                    topK_heap.Push(tk)
            

            end = time.time()
            
            score_computing_time += end - start
                
                
        score_computing_end = time.time()             
        score_computing_time_cur_uq = score_computing_end - score_computing_start
        # uses heapq to manipulate merge of explanations from multiple constraints
        start = time.time()
        # complementary_explanation_list = []
        # heapify(complementary_explanation_list)
        # refute_explanation_list = []
        # for i in range(len(local_patterns)):
        #     if len(top_k_lists[i]) > 3 and len(top_k_lists[i][3]) > 0:
        #         for idx, tk in enumerate(top_k_lists[i][3]):
        #             top_k_lists[i][3][idx][0] = -tk[0]
        #             top_k_lists[i][3][idx][2] = list(map(lambda y: y[1], sorted(tk[2].items(), key=lambda x: x[0])))
        #         print(top_k_lists[i])
        #         heapify(top_k_lists[i][-1])
        #         # print(top_k_lists[i])
        #         poped_tuple = list(heappop(top_k_lists[i][-1]))
        #         poped_tuple.append(i)
        #         heappush(complementary_explanation_list, poped_tuple)
        #     else:
        #         refute_explanation_list.append(top_k_lists[i])
        answer[j] = [{} for i in range(ExplConfig.TOP_K)]

        # cnt = 0
        # while cnt < TOP_K and len(complementary_explanation_list) > 0:
        #     poped_tuple = heappop(complementary_explanation_list)
        #     if str(poped_tuple[2]) not in marked:
        #         marked[str(poped_tuple[2])] = True
        #         answer[j][cnt] = (poped_tuple[0], poped_tuple[1], poped_tuple[2], poped_tuple[3], poped_tuple[4], poped_tuple[5])
        #         cnt += 1
        #     if len(top_k_lists[poped_tuple[-1]][3]) == 0:
        #         for i in range(len(local_patterns)):
        #             if len(top_k_lists[i]) > 3 and len(top_k_lists[i][-1]) > 0:
        #                 poped_tuple2 = list(heappop(top_k_lists[i][-1]))
        #                 poped_tuple2.append(i)
        #                 heappush(complementary_explanation_list, poped_tuple2)
                        
        #         heapify(complementary_explanation_list)
        #     else:
        #         # for tk in top_k_lists[poped_tuple[3]][3]:
        #         #     print(tk)

        #         poped_tuple2 = list(heappop(top_k_lists[poped_tuple[-1]][-1]))
        #         poped_tuple2.append(poped_tuple[-1])
        #         heappush(complementary_explanation_list, poped_tuple2)
        answer[j] = topK_heap.TopK()
        end = time.time()
        result_merging_time += end - start
        score_computing_time_list.append([t, score_computing_time_cur_uq])
        # print(749, answer[j])
        # print(topK_heap)

        # for i in range(len(local_patterns)):
        #     # print("TOP K: ", top_k_lists[i])
        #     if len(top_k_lists[i]) > 3:
        #         print(top_k_lists[i])
        #         answer[j].append(sorted(top_k_lists[i][-1], key=lambda x: x[1], reverse=True)[0:TOP_K])
        #     else:
        #         answer[j].append(top_k_lists[i])
        #     # print(len(answer[j][-1]))



    print('Local pattern loading time: ' + str(local_pattern_loading_time) + 'seconds')
    print('Question validating time: ' + str(question_validating_time) + 'seconds')
    print('Score computing time: ' + str(score_computing_time) + 'seconds')
    print('Result merging time: ' + str(result_merging_time) + 'seconds')
    return answer, local_patterns_list, score_computing_time_list

def load_query_result(t, cur, query_result_table, agg_col):
    agg_arr = agg_col.split('_')
    agg = agg_arr[0]
    a = agg_arr[1]
    group_arr = list(t.keys())
    group_arr.remove('lambda')
    group_arr.remove('direction')
    group_arr.remove('agg_col')
    group = ', '.join(group_arr)
    aggregate_query = 'SELECT {}, {}({}) as {} FROM {} GROUP BY {};'.format(
            group, agg, a, agg_col, query_result_table, group
        )
    cur.execute(aggregate_query)
    res = cur.fetchall()
    qr = list(map(lambda y: dict(zip(map(lambda x: x, column_name), y)), res))
    
    return qr

def find_patterns_relevant(global_patterns_dict, t, conn, cur, query_table_name, pattern_table_name, cat_sim):
    
    g_pat_list = []
    l_pat_list = []
    res_list = []
    t_set = set(t.keys())
    # print(1036, global_patterns_dict[0].keys())
    for v_key in global_patterns_dict[0]:
        # print(pat, pat[0])
        V_set = set(v_key[1:-1].replace("'", '').split(', '))
        # print(545, f_key)
        # F_set = set(f_key)
        # print(579, v_key, V_set, t_set)
        if not V_set.issubset(t_set):
            continue
        
        for f_key in global_patterns_dict[0][v_key]:
            for pat in global_patterns_dict[0][v_key][f_key]:
                # F_set = set(f_key.split(','))
                F_set = set(f_key[1:-1].replace("'", '').split(', '))
                # print(587, f_key, F_set, V_set, t_set)
                if not F_set.issubset(t_set):
                    continue
                # print(1053, pat, t)
                if pat[2] not in t and pat[2] + '_star' not in t:
                    continue

                agg_value = get_tuples_by_gp_uq(pat, get_F_value(pat[0], t), get_V_value(pat[1], t), 
                    conn, cur, query_table_name, cat_sim,
                    ExplConfig)
                res_list.append([pat, agg_value[0]])

                
    res_list = sorted(res_list, key = lambda x: (len(x[0][0]) + len(x[0][1]), x[1]))
    g_pat_list = list(map(lambda x: x[0], res_list))
    # print(1065, g_pat_list)
    return g_pat_list


def load_user_question_from_file(global_patterns, global_patterns_dict, uq_path, schema=None, conn=None, cur=None, pattern_table='', query_result_table='', pf=None, cat_sim=None):
    '''
        load user questions
    '''
    uq = []
    with open(uq_path, 'rt') as uqfile:
        reader = csv.DictReader(uqfile, quotechar='\'')
        headers = reader.fieldnames
        #temp_data = csv.reader(uqfile, delimiter=',', quotechar='\'')
        #for row in temp_data:
        for row in reader:
            row_data = {}
            raw_row_data = {}
            agg_col = None
            for k, v in enumerate(headers):
                # print(k, v)
                if schema is None or v not in schema:
                    if v != 'direction':
                        if is_float(row[v]):
                            row_data[v] = float(row[v])
                        elif is_integer(row[v]):
                            row_data[v] = float(long(row[v]))
                        else:
                            row_data[v] = row[v]
                    if v not in schema and v != 'lambda' and v != 'direction':
                        agg_col = v
                else:
                    if row[v] != '*':
                        if v.startswith('count_') or v.startswith('sum_'):
                            agg_col = v 
                        if schema[v] == 'integer':
                            row_data[v] = int(row[v])
                            raw_row_data[v] = int(row[v])
                        elif schema[v].startswith('double') or schema[v].startswith('float'):
                            row_data[v] = float(row[v])
                            raw_row_data[v] = float(row[v])
                        else:    
                            row_data[v] = row[v]
                            raw_row_data[v] = row[v]

            if row['direction'][0] == 'h':
                dir = 1
            else:
                dir = -1
            # print(615, schema, raw_row_data, row_data)
            uq.append({'target_tuple': row_data, 'dir':dir})
            # uq[-1]['global_patterns'], uq[-1]['local_patterns'] = find_patterns_relevant(
            #     global_patterns_dict, uq[-1]['target_tuple'], cur, pattern_table
            # )
            # uq[-1]['global_patterns'] = find_patterns_relevant(
            #     global_patterns_dict, uq[-1]['target_tuple'], conn, cur, query_result_table, pattern_table, cat_sim)

            
            # print(739, j, g_pat_cnt_by_theta[j])
            # print(list(map(lambda x: str(x[0]) + ' ' + str(x[1]) + '     ', g_pat_list_by_theta[j][0])))
            # print(list(map(lambda x: str(x[0]) + ' ' + str(x[1]) + '     ' if len(x) > 1 else '   empty   ', g_pat_list_by_theta[j][1])))
    
            # uq[-1]['query_result'] = load_query_result(uq[-1]['target_tuple'], cur, query_result_table, agg_col)
            uq[-1]['query_result'] = []
    # print(992, uq[-1])
    return uq, global_patterns, global_patterns_dict


def load_patterns(cur, pat_table_name, query_table_name):
    '''
        load pre-defined constraints(currently only fixed attributes and variable attributes)
    '''
    global_pattern_table = pat_table_name + '_global'
    load_query = "SELECT * FROM {};".format(global_pattern_table)
    # load_query = "SELECT * FROM {} WHERE fixed = '[primary_type]' AND variable = '[community_area, arrest, week]';".format(global_pattern_table)
    
    cur.execute(load_query)
    res = cur.fetchall()
    patterns = []
    pattern_dict = [{}, {}]
    for pat in res:
        if 'name' in pat[1] or 'venue' in pat[1]:
            continue
        patterns.append(list(pat))
        # print(pat)
        # print(patterns[-1])
        # patterns[-1][0] = patterns[-1][0][1:-1].replace(' ', '').split(',')
        # patterns[-1][1] = patterns[-1][1][1:-1].replace(' ', '').split(',')
        f_key = str(sorted(patterns[-1][0]))
        # f_key = str(patterns[-1][0])
        # print(694, f_key)
        v_key = str(sorted(patterns[-1][1]))
        # v_key = str(patterns[-1][1])
        if v_key not in pattern_dict[0]:
            pattern_dict[0][v_key] = {}
        if f_key not in pattern_dict[0][v_key]:
            pattern_dict[0][v_key][f_key] = []
        pattern_dict[0][v_key][f_key].append(patterns[-1])
        if f_key not in pattern_dict[1]:
            pattern_dict[1][f_key] = {}
        if v_key not in pattern_dict[1][f_key]:
            pattern_dict[1][f_key][v_key] = []
        pattern_dict[1][f_key][v_key].append(patterns[-1])
    schema_query = '''select column_name, data_type, character_maximum_length
        from INFORMATION_SCHEMA.COLUMNS where table_name=\'{}\'
    '''.format(query_table_name);
    cur.execute(schema_query)
    res = cur.fetchall()
    schema = {}
    for s in res:
        schema[s[0]] = s[1]
    
    # logger.debug('patterns')
    # logger.debug(patterns)
    return patterns, schema, pattern_dict

class ExplanationGenerator:

    def __init__(self, config : ExplConfig, user_input_config = None):
        self.config = config 
        if user_input_config is not None:
            if 'pattern_table' in user_input_config:
                self.config.pattern_table = user_input_config['pattern_table']
            if 'query_result_table' in user_input_config:
                self.config.query_result_table = user_input_config['query_result_table']
            if 'user_question_file' in user_input_config:
                self.config.user_question_file = user_input_config['user_question_file']
            if 'outputfile' in user_input_config:
                self.config.outputfile = user_input_config['outputfile']
            if 'aggregate_column' in user_input_config:
                self.config.aggregate_column = user_input_config['aggregate_column']
                

    def initialize(self):
        ecf = self.config
        query_result_table = ecf.query_result_table
        pattern_table = ecf.pattern_table
        user_question_file = ecf.DEFAULT_QUESTION_PATH
        outputfile = ''
        aggregate_column = ecf.aggregate_column
        conn = ecf.conn
        cur = ecf.cur
        logger.debug(ecf)
        logger.debug("pattern_table is")
        logger.debug(pattern_table)

        logger.debug("query_result_table is")
        logger.debug(query_result_table)

        # print(opts)
        start = time.clock()
        logger.info("start explaining ...")
        self.global_patterns, self.schema, self.global_patterns_dict = load_patterns(cur, pattern_table, query_result_table)
        logger.debug("loaded patterns from database")

        if query_result_table.find('crime') == -1:
            self.category_similarity = CategorySimilarityNaive(cur=cur, table_name=query_result_table)
        else:
            self.category_similarity = CategorySimilarityNaive(cur=cur, table_name=query_result_table, embedding_table_list=[('community_area', 'community_area_loc')])
        # category_similarity = CategoryNetworkEmbedding(EXAMPLE_NETWORK_EMBEDDING_PATH, data['df'])
        #num_dis_norm = normalize_numerical_distance(data['df'])
        self.num_dis_norm = normalize_numerical_distance(cur=cur, table_name=query_result_table)
        end = time.clock()
        print('Loading time: ' + str(end-start) + 'seconds')


    def wrap_user_question(self, global_patterns, global_patterns_dict, uq_tuple, schema=None):
        '''
            wrap user questions
        '''
        row_data = {}
        agg_col = None
        if 'lambda' not in uq_tuple:
            uq_tuple['lambda'] = 0.1
        for k, v in enumerate(uq_tuple):
            # print(k, v)
            if schema is None or v not in schema:
                if v != 'direction':
                    if is_float(uq_tuple[v]):
                        row_data[v] = float(uq_tuple[v])
                    elif is_integer(uq_tuple[v]):
                        row_data[v] = float((uq_tuple[v]))
                    else:
                        row_data[v] = uq_tuple[v]
                if v not in schema and v != 'lambda' and v != 'direction':
                    agg_col = v
            else:
                if uq_tuple[v] != '*':
                    if v.startswith('count_') or v.startswith('sum_'):
                        agg_col = v 
                    if schema[v] == 'integer':
                        row_data[v] = int(uq_tuple[v])
                    elif schema[v].startswith('double') or schema[v].startswith('float'):
                        row_data[v] = float(uq_tuple[v])
                    else:    
                        row_data[v] = uq_tuple[v]

        if uq_tuple['direction'][0] == 'h':
            dir = 1
        else:
            dir = -1

        if 'count_*' in row_data:
            row_data['count'] = row_data['count_*']
        uq = {'target_tuple': row_data, 'dir':dir, 'query_result': []}

        logger.debug("uq is")
        logger.debug(uq)

        return [uq]


    def do_explain_online(self, uq_tuple):

        ecf = self.config
        query_result_table = ecf.query_result_table
        pattern_table = ecf.pattern_table
        outputfile = ''
        aggregate_column = ecf.aggregate_column
        conn = ecf.conn
        cur = ecf.cur

        logger.debug("pattern_table is")
        logger.debug(pattern_table)

        logger.debug("query_result_table is")
        logger.debug(query_result_table)
        
        Q = self.wrap_user_question(self.global_patterns, self.global_patterns_dict, uq_tuple, self.schema)

        logger.debug("start finding explanations ...")
        
        start = time.clock()
        #regression_package = 'scikit-learn'
        regression_package = 'statsmodels'

        explanations_list, local_patterns_list, score_computing_time_list = find_explanation_regression_based(
            Q, self.global_patterns, self.global_patterns_dict, self.category_similarity, self.num_dis_norm,
            aggregate_column, conn, cur, 
            pattern_table, query_result_table, ecf
        )
            
        end = time.clock()
        # print('Total querying time: ' + str(end-start) + 'seconds')
        logger.debug("finding explanations ... DONE")

        # for g_key in ecf.MATERIALIZED_DICT:
        #     for fv_key in ecf.MATERIALIZED_DICT[g_key]:
        #         dv_query = '''DROP VIEW IF EXISTS MV_{};'''.format(str(ecf.MATERIALIZED_DICT[g_key][fv_key]))
        #         cur.execute(dv_query)
        #         conn.commit()
        return explanations_list[0]


    def doExplain(self):
        # c=self.config
        # logger.info("start explaining ...")
        # start = time.clock()
        # data = load_data(c.query_result_file)
        # logger.debug("loaded query results from file")
        # constraints = load_constraints(ExplConfig.DEFAULT_CONSTRAINT_PATH)
        # logger.debug("loaded patterns from file")
        # Q = load_user_question(c.user_question_file)
        # logger.debug("loaded user question from file")
        # category_similarity = CategorySimilarityMatrix(ExplConfig.EXAMPLE_SIMILARITY_MATRIX_PATH)
        # #category_similarity = CategoryNetworkEmbedding(EXAMPLE_NETWORK_EMBEDDING_PATH, data['df'])
        # num_dis_norm = normalize_numerical_distance(data['df'])
        # end = time.clock()
        # logger.debug("done loading")
        # print('Loading time: ' + str(end-start) + 'seconds')

        # logger.debug("start finding explanations ...")
        # start = time.clock()
        # #regression_package = 'scikit-learn'
        # regression_package = 'statsmodels'
        # explanations_list = find_explanation_regression_based(data, Q, constraints, category_similarity, 
        #                                                       num_dis_norm, c.constraint_epsilon, 
        #                                                       aggregate_column, regression_package)
        # end = time.clock()
        # print('Total querying time: ' + str(end-start) + 'seconds')
        # logger.debug("finding explanations ... DONE")
        
        # ofile = sys.stdout
        # if outputfile != '':
        #     ofile = open(outputfile, 'w')

        # for i, top_k_list in enumerate(explanations_list):
        #     ofile.write('User question ' + str(i+1) + ':\n')
        #     for k, list_by_con in enumerate(top_k_list):
        #         for j in range(5):
        #             e = list_by_con[j]
        #             ofile.write('------------------------\n')
        #             print_str = ''
        #             e_tuple = data['df'].loc[data['df']['index'] == e[2]]
        #             e_tuple_str = ','.join(e_tuple.to_string(header=False,index=False,index_names=False).split('  ')[1:])
        #             ofile.write('Top ' + str(j+1) + ' explanation:\n')
        #             ofile.write('Constraint ' + str(e[1]+1) + ': [' + ','.join(constraints[e[1]][0]) + ']' + '[' + ','.join(constraints[e[1]][1]) + ']')
        #             ofile.write('\n')
        #             #ofile.write('Score: ' + str(e[0]))
        #             ofile.write('Score: ' + str(-e[0]))
        #             ofile.write('\n')
        #             ofile.write('(' + e_tuple_str + ')')
        #             ofile.write('\n')
            
        #         ofile.write('------------------------\n')

        ecf = self.config
        query_result_table = ecf.DEFAULT_RESULT_TABLE
        pattern_table = ecf.DEFAULT_PATTERN_TABLE
        user_question_file = ecf.DEFAULT_QUESTION_PATH
        outputfile = ''
        aggregate_column = ecf.DEFAULT_AGGREGATE_COLUMN
        conn = ecf.conn
        cur = ecf.cur
        
        # print(opts)
        start = time.clock()
        logger.info("start explaining ...")
        global_patterns, schema, global_patterns_dict = load_patterns(cur, pattern_table, query_result_table)
        logger.debug("loaded patterns from database")
        # category_similarity = CategorySimilarityMatrix(ecf.EXAMPLE_SIMILARITY_MATRIX_PATH, schema)
        category_similarity = CategorySimilarityNaive(cur=cur, table_name=query_result_table)
        # category_similarity = CategoryNetworkEmbedding(EXAMPLE_NETWORK_EMBEDDING_PATH, data['df'])
        #num_dis_norm = normalize_numerical_distance(data['df'])
        num_dis_norm = normalize_numerical_distance(cur=cur, table_name=query_result_table)

        # pf = PatternFinder(engine.connect(), query_result_table, fit=True, theta_c=0.5, theta_l=0.25, lamb=DEFAULT_LAMBDA, dist_thre=0.9,  supp_l=10,supp_g=1)
        Q, global_patterns, global_patterns_dict = load_user_question_from_file(
            global_patterns, global_patterns_dict, user_question_file, 
            schema, conn, cur, pattern_table, query_result_table, None, category_similarity)
        logger.debug("loaded user question from file")

        end = time.clock()
        print('Loading time: ' + str(end-start) + 'seconds')

        logger.debug("start finding explanations ...")
        
        start = time.clock()
        #regression_package = 'scikit-learn'
        regression_package = 'statsmodels'
        
        explanations_list, local_patterns_list, score_computing_time_list = find_explanation_regression_based(
            Q, global_patterns, global_patterns_dict, category_similarity, num_dis_norm,
            aggregate_column, conn, cur, 
            pattern_table, query_result_table, ecf
        )
        expl_end = time.time()
            
        end = time.clock()
        print('Total querying time: ' + str(end-start) + 'seconds')
        logger.debug("finding explanations ... DONE")

        ofile = sys.stdout
        if outputfile != '':
            ofile = open(outputfile, 'w')

        for i, top_k_list in enumerate(explanations_list):
            ofile.write('User question {} in direction {}: {}\n'.format(
                str(i+1), 'high' if Q[i]['dir'] > 0 else 'low', str(Q[i]['target_tuple']))
            )

            # print(1300, len(top_k_list))
            for j, e in enumerate(top_k_list):
                ofile.write('------------------------\n')
                ofile.write('Top ' + str(j+1) + ' explanation:\n')
                ofile.write(e.to_string())
                ofile.write('------------------------\n')
            #     print_str = ''
            #     # e_tuple_str = ','.join(e_tuple.to_string(header=False,index=False,index_names=False).split('  ')[1:])
            #     # print(e)
            #     if isinstance(e, dict):
            #         continue
            #     e_tuple_str = ','.join(map(str, e[2]))
            #     ofile.write('Top ' + str(j+1) + ' explanation:\n')
            #     # ofile.write('Constraint ' + str(e[1]+1) + ': [' + ','.join(global_patterns[e[1]][0]) + ']' + '[' + ','.join(global_patterns[e[1]][1]) + ']')
            #     # print(827, e[1], local_patterns_list[i][e[1]][0])
            #     # print(828, local_patterns_list[i][e[1]][1])
            #     # print(829, local_patterns_list[i][e[1]][2])
            #     # ofile.write('Constraint ' + str(e[1]+1) + ': [' + ','.join(local_patterns_list[i][e[1]][0]) + ']' + 
            #     #     '[' + ','.join(list(map(str, local_patterns_list[i][e[1]][1]))) + ']' +
            #     #     '[' + ','.join(list(map(str, local_patterns_list[i][e[1]][2]))) + ']')
                
            #     if e[5] == 1:
            #         ofile.write('From local pattern' + ': [' + ','.join(e[3][0]) + ']' + 
            #             '[' + ','.join(list(map(str, e[3][1]))) + ']' +
            #             '[' + ','.join(list(map(str, e[3][2]))) + ']' +
            #             '[' + e[3][4] + ']' + 
            #             (('[' + str(e[3][6].split(',')[0][1:]) + ']') if e[3][4] == 'const' else ('[' + str(e[3][7]) + ']'))
            #         )
            #         ofile.write('\ndrill down to\n' + ': [' + ','.join(e[4][0]) + ']' + 
            #             '[' + ','.join(list(map(str, e[4][1]))) + ']' +
            #             '[' + ','.join(list(map(str, e[4][2]))) + ']' + 
            #             '[' + e[4][4] + ']' + 
            #             (('[' + str(e[4][6].split(',')[0][1:]) + ']') if e[4][4] == 'const' else ('[' + str(e[4][7]) + ']'))
            #         )
            #     else:
            #         ofile.write('Directly from local pattern ' + ': [' + ','.join(e[3][0]) + ']' + 
            #             '[' + ','.join(list(map(str, e[3][1]))) + ']' +
            #             '[' + ','.join(list(map(str, e[3][2]))) + ']' +
            #             '[' + e[3][4] + ']' + 
            #             (('[' + str(e[3][6].split(',')[0][1:]) + ']') if e[3][4] == 'const' else ('[' + str(e[3][7]) + ']'))
            #         )
            #     ofile.write('\n')
            #     ofile.write('Score: ' + str(e[0]))
            #     ofile.write('\n')
            #     ofile.write('Distance: ' + str(e[1][0]))
            #     ofile.write('\n')
            #     # ofile.write('Simialriry: ' + str(e[1][1]))
            #     # ofile.write('\n')
            #     ofile.write('Outlierness: ' + str(e[1][2]))
            #     ofile.write('\n')
            #     ofile.write('Denominator: ' + str(e[1][3]))
            #     ofile.write('\n')
            #     ofile.write('(' + e_tuple_str + ')')
            #     ofile.write('\n')
            # # else:
            #     #     ofile.write('------------------------\n')
            #     #     ofile.write('Explanation:\n')
            #     #     ofile.write(str(list_by_pat) + '\n')
            # ofile.write('------------------------\n\n')
        ofile.close()

        for g_key in ecf.MATERIALIZED_DICT:
            for fv_key in ecf.MATERIALIZED_DICT[g_key]:
                dv_query = '''DROP VIEW IF EXISTS MV_{};'''.format(str(ecf.MATERIALIZED_DICT[g_key][fv_key]))
                cur.execute(dv_query)
                conn.commit()
        ecf.MATERIALIZED_DICT = dict()
        ecf.MATERIALIZED_CNT = 0

        
def main(argv=[]):
    try:
        opts, args = getopt.getopt(argv,"h:p:q:u:o:a",["help","ptable=","qtable=","ufile=","ofile=","aggregate_column="])
    except getopt.GetoptError:
        print('explanation.py -p <pattern_table> -q <query_result_table>  -u <user_question_file>\
         -o <outputfile> -a <aggregate_column>')
        sys.exit(2)
    # user_input_config = dict()
    user_input_config = ExplConfig()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('explanation.py -p <pattern_table> -q <query_result_table> -u <user_question_file> \
                -o <outputfile> -a <aggregate_column>')
            sys.exit(2)    
        elif opt in ("-p", "--ptable"):
            user_input_config['pattern_table'] = arg
        elif opt in ("-q", "--qtable"):
            user_input_config['query_result_table'] = arg
        elif opt in ("-u", "--ufile"):
            user_input_config['user_question_file'] = arg
        elif opt in ("-o", "--ofile"):
            user_input_config['outputfile'] = arg
        elif opt in ("-a", "--aggcolumn"):
            user_input_config['aggregate_column'] = arg

    

    eg = ExplanationGenerator(user_input_config)
    # eg.doExplain()
    eg.initialize()
    # elist = eg.do_explain_online({'name': 'Jiawei Han', 'venue': 'kdd', 'year': 2007, 'sum_pubcount': 1, 'lambda': 0.2, 'direction': 'low'})
    # elist = eg.do_explain_online({'name': 'Kirsten Bergmann', 'venue': 'iva', 'sum_pubcount': 6.0, 'direction': 'high', 'lambda': 0.2})

    # elist = eg.do_explain_online({'primary_type': 'BATTERY', 'community_area': '26', 'year': '2011', 'count': 16, 'lambda': 0.2, 'direction': 'low'})
    for e in elist:
        print(e.to_string())


if __name__ == "__main__":
    main(sys.argv[1:])


