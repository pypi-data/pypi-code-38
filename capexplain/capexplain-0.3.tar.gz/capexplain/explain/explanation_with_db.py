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

from capexplain.similarity.category_similarity_matrix import *
from capexplain.similarity.category_network_embedding import *
from capexplain.utils import *
from capexplain.pattern_model.LocalRegressionPattern import *



DEFAULT_QUERY_RESULT_TABLE = 'crime_2017_2'
# DEFAULT_PATTERN_TABLE = 'pub_select'
DEFAULT_PATTERN_TABLE = 'crime_2017_2'
DEFAULT_QUESTION_PATH = './input/user_question_crime.csv'
DEFAULT_USER_QUESTION_NUMBER = 5
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

def predict(local_pattern, t):
    # print('In predict ', local_pattern)
    if local_pattern[5] == 'const':
        # predictY = float(local_pattern[-1][1:-1])
        predictY = float(local_pattern[-2][1:-1].split(',')[0])
    elif local_pattern[5] == 'linear':
        # print(local_pattern, t)
        v = get_V_value(local_pattern[2], t)
        # params = list(map(float, local_pattern[-1][1:-1].split(',')))
        params_str = local_pattern[-1].split('\n')
        # params = list(map(float, ))
        # print(params_str, v)
        params_dict = {}
        for i in range(0, len(params_str)-1):
            # print(params_str[i])
            # p_cate = re.compile(r'(.*)\[T\.\s+(.*)\]\s+(-?\d+\.\d+)')
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
                nume_res = p_nume.findall(params_str[i])[0]
                # print(nume_res)
                v_attr = nume_res[0]
                param = float(nume_res[1])
                params_dict[v_attr] = param

        predictY = 0.0
        # print(params_dict)
        for v_attr, v_dict in params_dict.items():
            # print(v_attr, v_dict, t)
            if v_attr == 'Intercept':
                predictY += v_dict
            else:
                if isinstance(v_dict, dict):
                    v_key = t[v_attr].replace('\'', '').replace(' ', '')
                    # print(v_attr, v_key)
                    # print(v_dict.keys())
                    if v_key in v_dict:
                        predictY += v_dict[v_key]
                else:
                    if v_attr in t:
                        predictY += v_dict * t[v_attr]

        # predictY = sum(map(lambda x: x[0]*x[1], zip(params[:-1], v))) + params[-1]

    return predictY

def validate_local_regression_pattern(local_pattern, epsilon, t, dir, agg_col, cur, table_name):
    """Check the validicity of the user question under a local regression constraint

    Args:
        local_pattern:
        t: target tuple in Q(R)
        dir: whether user thinks t[agg(B)] is high or low
        agg_col: the column of aggregated value
    Returns:
        the actual direction that t[agg(B)] compares to its expected value, and the expected value from local_con
    """
    test_tuple = {}
    print('PAT', local_pattern)
    if isinstance(local_pattern, dict):
        return -2, 0
    for v in local_pattern[2]:
        test_tuple[v] = t[v.replace(' ', '')]
    # if regression_package == 'scikit-learn':
    #     for v in local_con.var_attr:
    #         if v in data['le']:
    #             test_tuple[v] = data['le'][v].transform(test_tuple[v])
    #             test_tuple[v] = data['ohe'][v].transform(test_tuple[v].reshape(-1, 1))
    #         else:
    #             test_tuple[v] = np.array(test_tuple[v]).reshape(-1, 1)
        
    #     test_tuple = np.concatenate(list(test_tuple.values()), axis=-1)
    #     predictY = local_con.predict_sklearn(test_tuple)
    # else:
    #     predictY = local_con.predict(pandas.DataFrame(test_tuple))

    predictY = predict(local_pattern, test_tuple)
    if t[agg_col] < (1-epsilon) * predictY:
        # print(test_tuple, predictY)
        return -dir, predictY
    elif t[agg_col] > (1+epsilon) * predictY:
        # print(test_tuple, predictY)
        return dir, predictY
    else:
        return 0, predictY
        
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


def find_explanation_regression_based(user_question_list, global_patterns, cat_sim, num_dis_norm, epsilon, agg_col, cur, pat_table_name, res_table_name):

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
    result_merging_time = 0

    local_patterns_list = []


    for j, uq in enumerate(user_question_list):
        dir = uq['dir']
        t = uq['target_tuple']
        print(uq)

        start = time.clock()
        local_patterns = get_local_patterns(global_patterns, t, cur, res_table_name)
        end = time.clock()
        local_pattern_loading_time += end - start

        candidate_list = [[] for i in range(len(local_patterns))]
        top_k_lists = [[] for i in range(len(local_patterns))]
        validate_res_list = []
        local_patterns_list.append(local_patterns)
        
        psi = []
        

        explanation_type = 0
        for i in range(0, len(local_patterns)):
            psi.append(0)
            start = time.clock()
            # print('PAT', i, local_patterns[i])
            validate_res, predicted_aggr = validate_local_regression_pattern(local_patterns[i], epsilon, t, dir, agg_col, cur, res_table_name)
            validate_res_list.append(validate_res)
            end = time.clock()
            question_validating_time += end - start

            if validate_res < -1:
                print ("The local regression constraint derived from the " + str(i+1) +
                        "th constraint and the target tuple does not hold")
                explanation_type = 1
                top_k_lists[i] = [1, local_patterns[i]]
            elif validate_res == -1:
                print ("The user question is invalid according to the local regression constraint derived from the "
                        + str(i+1) + "th constraint and the target tuple -- in the opposite direction")
                explanation_type = 2
                top_k_lists[i] = [-2, local_patterns[i], t]
            elif validate_res == 0:
                print ("The user question is invalid according to the local regression constraint derived from the "
                        + str(i+1) + "th constraint and the target tuple -- "
                        "the target tuple can be predicted by the constraint")
                explanation_type = 2
                top_k_lists[i] = [2, local_patterns[i], t]
            else:
                print ("The user question is valid according to the local regression constraint derived from the "
                        + str(i+1) + "th constraint and the target tuple")
                explanation_type = 3
                #deviation = dir * (t[agg_col] - predicted_aggr) / predicted_aggr
                cnt = 0
                #for index, row in data['df'].iterrows():
                start = time.clock()
                f_value = get_F_value(local_patterns[i][0], t)

            ### replace with db query
                tuples_same_F_value = get_tuples_by_F(local_patterns[i], f_value, cur, res_table_name)

                
                for row in tuples_same_F_value:
                    psi[-1] += row[agg_col]
                    t_sim = tuple_similarity(t, row, local_patterns[i][2], cat_sim, num_dis_norm, agg_col)
                    # print local_cons[i].var_attr, row
                    test_tuple = dict(zip(local_patterns[i][2],
                                          map(lambda x:x, get_V_value(local_patterns[i][2], row))))
                    predicted_aggr = []
                    
                
                    predicted_aggr = predict(local_patterns[i], test_tuple)
                    # if abs(predicted_aggr) < 1e-8:
                    #     # print(local_patterns[i], test_tuple)
                    #     deviation = 0
                    # else:
                    #     deviation = (row[agg_col] - predicted_aggr) / predicted_aggr

                    if abs(row[agg_col] - predicted_aggr) < 1e-8:
                        sign = 0
                    elif row[agg_col] > predicted_aggr:
                        sign = 1
                    else:
                        sign = -1
                    deviation = sign * abs(row[agg_col] - t[agg_col]) / abs(t[agg_col] + 0.01)
                    candidate_list[i].append([deviation, t_sim, row, predicted_aggr])
                    # print(row, predicted_aggr)
                    cnt += 1
                # print(len(candidate_list[i]), cnt)

                # print('In scoring: ', local_patterns[i])

                for k in range(cnt):
                    deviation = candidate_list[i][k][0]
                    t_sim = candidate_list[i][k][1]
                    predicted_aggr = candidate_list[i][k][3]
                    denominator = 20


                    
                    score = math.sqrt(t_sim * t_sim + deviation * deviation / denominator)
                    # score = abs(deviation)
                    # print(deviation, t_sim, score, candidate_list[i][k][2])
                    if deviation == 0:
                        top_k_lists[i].append((-1e10, i, candidate_list[i][k][2]))
                    else:
                        top_k_lists[i].append((-dir * deviation / abs(deviation) * score, i, candidate_list[i][k][2]))

                end = time.clock()
                score_computing_time += end - start
                    
        # uses heapq to manipulate merge of explanations from multiple constraints
        # start = time.clock()
        # merge_top_k_list = []
        # marked = {}
        # for i in range(len(cons)):
        #     heapify(top_k_lists[i])
        #     heappush(merge_top_k_list, heappop(top_k_lists[i]))

        # answer[j] = [{} for i in range(TOP_K)]
        # cnt = 0
        # while cnt < TOP_K:
        #     poped_tuple = heappop(merge_top_k_list)
        #     if poped_tuple[2] in marked:
        #         continue
        #     marked[poped_tuple[2]] = True
        #     answer[j][cnt] = (-poped_tuple[0], poped_tuple[1], poped_tuple[2])
        #     heappush(merge_top_k_list, heappop(top_k_lists[poped_tuple[1]]))
        #     cnt += 1
        # end = time.clock()
        # result_merging_time += end - start

        for i in range(len(local_patterns)):
            # print("TOP K: ", top_k_lists[i])
            if len(top_k_lists[i]) > 3:
                answer[j].append(sorted(top_k_lists[i], key=lambda x: x[0], reverse=True)[0:TOP_K])
            else:
                answer[j].append(top_k_lists[i])
            # print(len(answer[j][-1]))

        #answer[j] = top_k_lists


    print('Local pattern loading time: ' + str(local_pattern_loading_time) + 'seconds')
    print('Question validating time: ' + str(question_validating_time) + 'seconds')
    print('Score computing time: ' + str(score_computing_time) + 'seconds')
    #print('Result merging time: ' + str(result_merging_time) + 'seconds')
    return answer, local_patterns_list

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

        
def main(argv=[]):
    query_result_table = DEFAULT_QUERY_RESULT_TABLE
    pattern_table = DEFAULT_PATTERN_TABLE
    user_question_file = DEFAULT_QUESTION_PATH
    outputfile = ''
    epsilon = DEFAULT_EPSILON
    aggregate_column = DEFAULT_AGGREGATE_COLUMN
    try:
        # conn = psycopg2.connect("host=216.47.152.61 port=5432 dbname=postgres user=antiprov password=test")
        conn = psycopg2.connect("host=localhost port=5432 dbname=antiprov")
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
    Q = load_user_question(user_question_file)
    category_similarity = CategorySimilarityMatrix(EXAMPLE_SIMILARITY_MATRIX_PATH)
    # category_similarity = CategoryNetworkEmbedding(EXAMPLE_NETWORK_EMBEDDING_PATH, data['df'])
    #num_dis_norm = normalize_numerical_distance(data['df'])
    num_dis_norm = normalize_numerical_distance(cur=cur, table_name=query_result_table)
    end = time.clock()
    print('Loading time: ' + str(end-start) + 'seconds')
    
    start = time.clock()
    #regression_package = 'scikit-learn'
    regression_package = 'statsmodels'
    explanations_list, local_patterns_list = find_explanation_regression_based(Q, global_patterns, category_similarity, 
                                                          num_dis_norm, epsilon, 
                                                          aggregate_column, cur, pattern_table, query_result_table)
    end = time.clock()
    print('Total querying time: ' + str(end-start) + 'seconds')

    ofile = sys.stdout
    if outputfile != '':
        ofile = open(outputfile, 'w')

    # for i, explanations in enumerate(explanations_list):
    #     ofile.write('User question ' + str(i+1) + ':\n')
    #     for j, e in enumerate(explanations):
    #         print_str = ''
    #         e_tuple = data['df'].loc[data['df']['index'] == e[2]]
    #         e_tuple_str = ','.join(e_tuple.to_string(header=False,index=False,index_names=False).split('  ')[1:])
    #         ofile.write('Top ' + str(j+1) + ' explanation:\n')
    #         ofile.write('Constraint ' + str(e[1]+1) + ': [' + ','.join(constraints[e[1]][0]) + ']' + '[' + ','.join(constraints[e[1]][1]) + ']')
    #         ofile.write('\n')
    #         ofile.write('Score: ' + str(e[0]))
    #         ofile.write('\n')
    #         ofile.write('(' + e_tuple_str + ')')
    #         ofile.write('\n')
    #     ofile.write('------------------------\n')

    for i, top_k_list in enumerate(explanations_list):
        ofile.write('User question {}: {}\n'.format(str(i+1), str(Q[i])))
        print(len(top_k_list))
        for k, list_by_pat in enumerate(top_k_list):
            if k < len(global_patterns):
                ofile.write('Globally held pattern: {}\n'.format(str(local_patterns_list[i][k])))
            else:
                ofile.write('Locally held pattern: {}\n'.format(str(local_patterns_list[i][k])))
            print(len(list_by_pat))
            if isinstance(list_by_pat[0], int):
                if list_by_pat[0] == 1:
                    ofile.write("The local regression constraint derived from the " + str(i+1) +
                        "th constraint and the target tuple does not hold\n")
                elif list_by_pat[0] == -2:
                    ofile.write("The user question is invalid according to the local regression constraint derived from the "
                            + str(i+1) + "th constraint and the target tuple -- in the opposite direction\n")
                elif list_by_pat[0] == 2:
                    ofile.write("The user question is invalid according to the local regression constraint derived from the "
                            + str(i+1) + "th constraint and the target tuple -- the target tuple can be predicted by the constraint\n")
            else:

                if len(list_by_pat) > 2:
                    for j in range(TOP_K):
                        e = list_by_pat[j]
                        if e[0] < 0:
                            break
                        ofile.write('------------------------\n')
                        print_str = ''
                        e_tuple = list(e[2].values())
                        # e_tuple_str = ','.join(e_tuple.to_string(header=False,index=False,index_names=False).split('  ')[1:])
                        e_tuple_str = ','.join(map(str, e_tuple))
                        ofile.write('Top ' + str(j+1) + ' explanation:\n')
                        # ofile.write('Constraint ' + str(e[1]+1) + ': [' + ','.join(global_patterns[e[1]][0]) + ']' + '[' + ','.join(global_patterns[e[1]][1]) + ']')
                        ofile.write('Constraint ' + str(e[1]+1) + ': [' + ','.join(local_patterns_list[i][e[1]][0]) + ']' + 
                            '[' + ','.join(local_patterns_list[i][e[1]][1]) + ']' +
                            '[' + ','.join(local_patterns_list[i][e[1]][2]) + ']')
                        ofile.write('\n')
                        ofile.write('Score: ' + str(e[0]))
                        ofile.write('\n')
                        ofile.write('(' + e_tuple_str + ')')
                        ofile.write('\n')
                else:
                    ofile.write('------------------------\n')
                    ofile.write('Explanation:\n')
                    ofile.write(str(list_by_pat) + '\n')


                
            ofile.write('------------------------\n\n\n------------------------\n')

if __name__ == "__main__":
    main(sys.argv[1:])


