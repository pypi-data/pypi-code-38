#!/usr/bin/python
# -*- coding:utf-8 -*- 

import psycopg2
import sys, getopt
import pandas
import csv
#import statsmodels.formula.api as smf
from sklearn import preprocessing
import math
import time
from heapq import *
import re
import itertools
import bisect

from capexplain.similarity.category_similarity_matrix import *
from capexplain.similarity.category_network_embedding import *
from capexplain.utils import *
from capexplain.pattern_model.LocalRegressionPattern import *


DEFAULT_QUESTION_PATH = './input/user_question_crime.csv'

DEFAULT_QUERY_RESULT_TABLE = 'crime_2017_2'
# DEFAULT_PATTERN_TABLE = 'pub_select'
DEFAULT_PATTERN_TABLE = 'crime_2017_2'
DEFAULT_USER_QUESTION_NUMBER = 5
EXAMPLE_NETWORK_EMBEDDING_PATH = './input/NETWORK_EMBEDDING'
EXAMPLE_SIMILARITY_MATRIX_PATH = './input/SIMILARITY_DEFINITION'
DEFAULT_AGGREGATE_COLUMN = '*'
DEFAULT_EPSILON = 0.25
TOP_K = 5

def build_local_regression_constraint(data, column_index, t, con, epsilon, agg_col, regression_package):
    """Build local regression constraint from Q(R), t, and global regression constraint

    Args:
        data: result of Q(R)
        column_index: index for values in each column
        t: target tuple in Q(R)
        con: con[0] is the list of fixed attributes in Q(R), con[1] is the list of variable attributes in Q(R)
        epsilon: threshold for local regression constraint
        regression_package: which package is used to compute regression 
    Returns:
        A LocalRegressionConstraint object whose model is trained on \pi_{con[1]}(Q_{t[con[0]]}(R))
    """
    tF = get_F_value(con[0], t)
    local_con = LocalRegressionConstraint(con[0], tF, con[1], agg_col, epsilon)
    train_data = {agg_col: []}
    for v in con[1]:
        train_data[v] = []
    # for index, row in data['df'].iterrows():
    #     if get_F_value(con[0], row) == tF:
    #         for v in con[1]:
    #             train_data[v].append(row[v])
    #         train_data[agg_col].append(row[agg_col])

    
    for idx in column_index[con[0][0]][tF[0]]:
        row = data['df'].loc[data['df']['index'] == idx]
        row = row.to_dict('records')[0]
        #print row
        if get_F_value(con[0], row) == tF:
            for v in con[1]:
                train_data[v].append(row[v])
            train_data[agg_col].append(row[agg_col])
    if regression_package == 'scikit-learn':
        train_x = {}
        for v in con[1]:
            if v in data['le']:
                train_data[v] = data['le'][v].transform(train_data[v])
                train_data[v] = data['ohe'][v].transform(train_data[v].reshape(-1, 1))
                #print data['ohe'][v].transform(train_data[v].reshape(-1, 1))
                train_x[v] = train_data[v]
            else:
                if v != agg_col:
                    train_x[v] = np.array(train_data[v]).reshape(-1, 1)
        train_y = np.array(train_data[agg_col]).reshape(-1, 1)
        train_x = np.concatenate(list(train_x.values()), axis=-1)
        local_con.train_sklearn(train_x, train_y)
    else:
        #train_data = pandas.DataFrame(train_data)
        formula = agg_col + ' ~ ' + ' + '.join(con[1])
        local_con.train(train_data, formula)
    return local_con

        
def tuple_similarity(t1, t2, var_attr, cat_sim, num_dis_norm, agg_col):
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
    sim = 0.0
    cnt = 0
    for v_col in var_attr:
        col = v_col.replace(' ', '')
        
        if t1[col] is None or t2[col] is None:
            continue
        if cat_sim.is_categorical(col):
            t1_key = t1[col].replace("'", '').replace(' ', '')
            t2_key = t2[col].replace("'", '').replace(' ', '')
            s = cat_sim.compute_similarity(col, t1_key, t2_key, agg_col)
            # print(s)
            sim += s
        else:
            # print( num_dis_norm[col]['range'])
            if num_dis_norm[col]['range'] is None:
                if t1[col] == t2[col]:
                    sim += 1
            else:
                if col != agg_col and col != 'index':
                    temp = abs(t1[col] - t2[col]) / num_dis_norm[col]['range']
                    sim += 1-temp
        cnt += 1
    # print(t1, t2, sim)
    return sim / cnt

def get_local_patterns(global_patterns, t, cur, table_name):
    local_patterns = []
    local_patterns_dict = {}
    for pat in global_patterns:
        tF = get_F_value(pat[0], t)
        print(pat)
        local_pattern_query = '''SELECT * FROM {} WHERE REPLACE(fixed_value, ' ', '')=REPLACE('{}', ' ', '') AND variable='{}' AND in_a='{}' AND agg='{}' AND model='{}';'''.format(
                table_name + '_local', str(tF).replace("\'", '"'), str(pat[1]).replace("\'", ''), pat[2], pat[3], pat[4]
            )
        # local_pattern_query = '''SELECT * FROM {} WHERE REPLACE(fixed_value, ' ', '')=REPLACE('{}', ' ', '') AND variable='{}' AND in_a='{}' AND agg='{}' AND model='{}';'''.format(
        #           table_name + '_local', str(tF).replace("\'", ''), str(pat[1]).replace("\'", ''), pat[2], pat[3], pat[4]
        # )
        print(local_pattern_query)
        cur.execute(local_pattern_query)
        res = cur.fetchall()
        l_pat = []
        print('In get local patterns: ', res)
        if len(res) != 0:
            local_patterns_dict[str(res[0])] = True
            for i in range(3):
                l_pat.append(res[0][i][1:-1].split(','))
            l_pat[0] = list(map(lambda x: x.replace(' ', ''), l_pat[0]))
            l_pat[2] = list(map(lambda x: x.replace(' ', ''), l_pat[2]))
            for i in range(3, len(res[0])):
                l_pat.append(res[0][i])
            # print(l_pat)
            local_patterns.append(l_pat)
        else:
            l_pat.append(pat[0])
            l_pat.append(tF)
            for i in range(1, len(pat)):
                l_pat.append(pat[i])
            local_patterns.append({'hold': False, 'pattern': l_pat})


    for num_of_fix in range(1, min(len(t.keys()),4)):
        for possible_f_attr in itertools.combinations(list(t.keys())[:-1], num_of_fix):
            tF = get_F_value(possible_f_attr, t)
            local_pattern_query = '''SELECT * FROM {} WHERE REPLACE(fixed_value, ' ', '')=REPLACE('{}', ' ', '')'''.format(
                table_name + '_local', str(tF).replace("\'", '"'))
            # print(tF)
            print(local_pattern_query)
            cur.execute(local_pattern_query)
            res = cur.fetchall()
            # print('In get local patterns: ', res)
            for k in range(len(res)):
                l_pat = []
                if str(res[k]) in local_patterns_dict:
                    continue
                else:
                    local_patterns_dict[str(res[k])] = True
                for i in range(3):
                    l_pat.append(res[k][i][1:-1].split(','))
                l_pat[0] = list(map(lambda x: x.replace(' ', ''), l_pat[0]))
                l_pat[2] = list(map(lambda x: x.replace(' ', ''), l_pat[2]))
                for i in range(3, len(res[0])):
                    l_pat.append(res[0][i])
                # print(l_pat)
                if l_pat not in local_patterns:
                    local_patterns.append(l_pat)
    print('GET ', local_patterns)
    return local_patterns


def get_tuples_by_F(local_pattern, f_value, cur, table_name):
    
    where_clause = ' AND '.join(list(map(lambda x: "{} {}".format(x[0], x[1]), zip(local_pattern[0], map(tuple_column_to_str_in_where_clause, f_value)))))
    tuples_query = "SELECT * FROM {} WHERE {};".format(table_name, where_clause)
    
    column_name_query = "SELECT column_name FROM information_schema.columns where table_name='{}';".format(table_name)
    # print(column_name_query)
    cur.execute(column_name_query)
    column_name = cur.fetchall()
    cur.execute(tuples_query)
    # print(tuples_query)
    tuples = []
    res = cur.fetchall()
    for row in res:
        tuples.append(dict(zip(map(lambda x: x[0], column_name), row)))
    return tuples


def load_user_question(uq_path=DEFAULT_QUESTION_PATH):
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
            for k, v in enumerate(headers):
                # print(k, v)
                if v != 'direction':
                    if is_float(row[v]):
                        row_data[v] = float(row[v])
                    elif is_integer(row[v]):
                        row_data[v] = float(long(row[v]))
                    else:
                        row_data[v] = row[v]
            if row['direction'][0] == 'h':
                dir = 1
            else:
                dir = -1
            uq.append({'target_tuple': row_data, 'dir':dir})
    return uq

def load_patterns(cur, pat_table_name):
    '''
        load pre-defined constraints(currently only fixed attributes and variable attributes)
    '''
    global_pattern_table = pat_table_name + '_global'
    load_query = "SELECT * FROM {};".format(global_pattern_table)
    cur.execute(load_query)
    res = cur.fetchall()
    patterns = []
    for pat in res:
        patterns.append(list(pat))
        patterns[-1][0] = patterns[-1][0][1:-1].replace(' ', '').split(',')
        patterns[-1][1] = patterns[-1][1][1:-1].replace(' ', '').split(',')
    
    return patterns


def get_local_patterns(global_patterns, t, cur, table_name):
    local_patterns = []
    local_patterns_dict = {}
    for pat in global_patterns:
        
        F_set = set(pat[0])
        V_set = set(pat[1])
        t_set = set(t.keys())
        FV_set = F_set.union(V_set)
        if not (FV_set.issubset(t_set) and len(FV_set) == len(t_set) - 1 
            and '{}({})'.format(pat[3], pat[2]) in t):
        # if F_set.union(V_set) != t_set:
            continue
        # print(pat[0], t)
        local_patterns.append(get_local_pattern(pat, t, cur, table_name))

        
def count_gloabl_patterns(global_patterns, t, cur, table_name):
    local_patterns = []
    local_patterns_dict = {}
    g_pat_cnt_by_theta = [0 for i in range(21)]
    for pat in global_patterns:
        
        F_set = set(pat[0])
        V_set = set(pat[1])
        t_set = set(t.keys())
        FV_set = F_set.union(V_set)
        # print(pat, t)
        # print(FV_set, t_set, pat[3], pat[2])
        if not (FV_set.issubset(t_set) and len(FV_set) == len(t_set) - 2
            and '{}({})'.format(pat[3], pat[2]) in t):
        # if F_set.union(V_set) != t_set:
            continue
        # print(pat[0], t)
        # if float(pat[-1]) >= t['lambda']:
        local_pattern_query = '''SELECT theta FROM {} 
            WHERE fixed='{}' AND variable='{}' AND 
                in_a='{}' AND agg='{}' AND model='{}'
            ORDER BY theta;
        '''.format(
            table_name + '_local', str(pat[0]).replace("\'", ''), str(pat[1]).replace("\'", ''), pat[2], pat[3], pat[4] 
        )

        cur.execute(local_pattern_query)
        res = list(map(lambda x:x[0], cur.fetchall()))
        # print(res)
        for the_i in range(2, 21):
            j = bisect.bisect_left(res, the_i * 0.05)
            if len(res) - j >= t['lambda'] * len(res):
                g_pat_cnt_by_theta[the_i] += 1 
    print(g_pat_cnt_by_theta)

def main(argv=[]):
    query_result_table = DEFAULT_QUERY_RESULT_TABLE
    pattern_table = DEFAULT_PATTERN_TABLE
    user_question_file = DEFAULT_QUESTION_PATH
    outputfile = ''
    epsilon = DEFAULT_EPSILON
    aggregate_column = DEFAULT_AGGREGATE_COLUMN
    try:
        # conn = psycopg2.connect("host=216.47.152.61 port=5432 dbname=postgres user=antiprov password=test")
        # conn = psycopg2.connect("host=localhost port=5432 dbname=antiprov")
        conn = psycopg2.connect("host=localhost port=5432 dbname=antiprov user=zjmiao password=keertijeff")
        cur = conn.cursor()
    except psycopg2.OperationalError:
        print('数据库连接失败！')

    try:
        opts, args = getopt.getopt(argv,"hq:p:u:o:e:a",["qtable=", "ptable=", "ufile=","ofile=","epsilon=","aggregate_column="])
    except getopt.GetoptError:
        print('explanation.py -q <query_result_table> -p <pattern_table> -u <user_question_file> -o <outputfile> -e <epsilon> -a <aggregate_column>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('explanation.py -q <query_result_table> -p <pattern_table> -u <user_question_file> -o <outputfile> -e <epsilon> -a <aggregate_column>')
            sys.exit(2)    
        elif opt in ("-q", "--qtable"):
            query_result_table = arg
        elif opt in ("-p", "--ptable"):
            pattern_table = arg
        elif opt in ("-u", "--ufile"):
            user_question_file = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-e", "--epsilon"):
            epsilon = float(arg)
        elif opt in ("-a", "--aggcolumn"):
            aggregate_column = arg

    start = time.clock()
    global_patterns = load_patterns(cur, pattern_table)
    end = time.clock()
    print('Loading time: ' + str(end-start) + 'seconds')

    Q = load_user_question(user_question_file)
    print(global_patterns)
    print(Q)
    for uq in Q:
        count_gloabl_patterns(global_patterns, uq['target_tuple'], cur, pattern_table)
    
    
 

if __name__ == "__main__":
    main(sys.argv[1:])


