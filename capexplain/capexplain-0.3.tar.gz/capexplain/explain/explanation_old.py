#!/usr/bin/python
# -*- coding:utf-8 -*- 

import sys, getopt
import pandas
import csv
#import statsmodels.formula.api as smf
from sklearn import preprocessing
import math
import time
from heapq import *
import logging
from capexplain.similarity.category_similarity_matrix import *
from capexplain.similarity.category_network_embedding import *
from capexplain.utils import *
from capexplain.pattern_model.LocalRegressionPattern import *
from capexplain.cl.cfgoption import DictLike

# setup logging
log = logging.getLogger(__name__)

#********************************************************************************
# Configuration for Explanation generation
class ExplConfig(DictLike):

    DEFAULT_RESULT_PATH = './input/query_res.csv'
    DEFAULT_QUESTION_PATH = './input/user_question.csv'
    DEFAULT_CONSTRAINT_PATH = './input/CONSTRAINTS'
    EXAMPLE_NETWORK_EMBEDDING_PATH = './input/NETWORK_EMBEDDING'
    EXAMPLE_SIMILARITY_MATRIX_PATH = './input/SIMILARITY_DEFINITION'
    DEFAULT_AGGREGATE_COLUMN = 'count'
    DEFAULT_CONSTRAINT_EPSILON = 0.05
    TOP_K = 5
    REGRESSION_PACKAGES = [ 'scikit-learn', 'statsmodels' ]
    
    def __init__(self,
                 query_result_file = DEFAULT_RESULT_PATH,
                 constraint_file = DEFAULT_CONSTRAINT_PATH,
                 user_question_file = DEFAULT_QUESTION_PATH,
                 outputfile = '',
                 constraint_epsilon = DEFAULT_CONSTRAINT_EPSILON,
                 aggregate_column = DEFAULT_AGGREGATE_COLUMN,
                 regression_package = 'statsmodels'
    ):
        self.query_result_file = query_result_file
        self.constraint_file = constraint_file
        self.user_question_file = user_question_file
        self.outputfile = outputfile
        self.constraint_epsilon = constraint_epsilon
        self.aggregate_column = aggregate_column
        self.regression_package = regression_package

    def __str__(self):
        return self.__dict__.__str__()

#********************************************************************************
# construct local patterns
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
        A LocalRegressionPattern object whose model is trained on \pi_{con[1]}(Q_{t[con[0]]}(R))
    """
    tF = get_F_value(con[0], t)
    local_con = LocalRegressionPattern(con[0], tF, con[1], agg_col, epsilon)
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
        print 
        local_con.train(train_data, formula)
    return local_con

def validate_local_regression_constraint(data, local_con, t, dir, agg_col, regression_package):
    """Check the validicity of the user question under a local regression constraint

    Args:
        data: data['df'] is the data frame storing Q(R)
            data['le'] is the label encoder, data['ohe'] is the one-hot encoder
        local_con: a LocalRegressionPattern object
        t: target tuple in Q(R)
        dir: whether user thinks t[agg(B)] is high or low
        agg_col: the column of aggregated value
        regression_package: which package is used to compute regression 
    Returns:
        the actual direction that t[agg(B)] compares to its expected value, and the expected value from local_con
    """
    test_tuple = {}
    for v in local_con.var_attr:
        test_tuple[v] = [t[v]]
    if regression_package == 'scikit-learn':
        for v in local_con.var_attr:
            if v in data['le']:
                test_tuple[v] = data['le'][v].transform(test_tuple[v])
                test_tuple[v] = data['ohe'][v].transform(test_tuple[v].reshape(-1, 1))
            else:
                test_tuple[v] = np.array(test_tuple[v]).reshape(-1, 1)
        
        test_tuple = np.concatenate(list(test_tuple.values()), axis=-1)
        predictY = local_con.predict_sklearn(test_tuple)
    else:
        predictY = local_con.predict(pandas.DataFrame(test_tuple))

    if t[agg_col] < (1-local_con.epsilon) * predictY[0]:
        return -dir, predictY[0]
    elif t[agg_col] > (1+local_con.epsilon) * predictY[0]:
        return dir, predictY[0]
    else:
        return 0, predictY[0]
        
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
    for col in var_attr:
        if t1[col] is None or t2[col] is None:
            continue
        if cat_sim.is_categorical(col):
            s = cat_sim.compute_similarity(col, t1[col], t2[col], agg_col)
            sim += s
        else:
            if col != agg_col and col != 'index':
                temp = abs(t1[col] - t2[col]) / num_dis_norm[col]['range']
                sim += 1-temp
        cnt += 1
    return sim / cnt

def find_explanation_regression_based(data, user_question_list, cons, cat_sim, num_dis_norm, cons_epsilon, agg_col, regression_package):

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
    index_building_time = 0
    constraint_building_time = 0
    question_validating_time = 0
    score_computing_time = 0
    result_merging_time = 0

    start = time.clock()
    column_index = dict()
    for column in data['df']:
        column_index[column] = dict()
    for index, row in data['df'].iterrows():
        for column in data['df']:
            val = row[column]
            if not val in column_index[column]:
                column_index[column][val] = []
            column_index[column][val].append(index)
    end = time.clock()
    index_building_time += end - start

    for j, uq in enumerate(user_question_list):
        dir = uq['dir']
        t = uq['target_tuple']
        print(uq)
        candidate_list = [[[] for i in range(len(data['df'].index))] for i in range(len(cons))]
        top_k_lists = [[(1e10,0,0) for i in range(len(data['df'].index))] for i in range(len(cons))]
        validate_res_list = []

        psi = []
        local_cons = []
        start = time.clock()
        for i in range(len(cons)):
            local_cons.append(build_local_regression_constraint(data, column_index, t, cons[i], cons_epsilon, agg_col, regression_package))
            local_cons[i].print_fit_summary()
        end = time.clock()
        constraint_building_time += end - start

        explanation_type = 0
        for i in range(0, len(local_cons)):
            psi.append(0)
            start = time.clock()
            validate_res, predicted_aggr = validate_local_regression_constraint(data, local_cons[i], t, dir, agg_col, regression_package)
            validate_res_list.append(validate_res)
            end = time.clock()
            question_validating_time += end - start

            if validate_res < -1:
                print ("The local regression constraint derived from the " + str(i+1) +
                        "th constraint and the target tuple does not hold")
                explanation_type = 1
            elif validate_res == -1:
                print ("The user question is invalid according to the local regression constraint derived from the "
                        + str(i+1) + "th constraint and the target tuple -- in the opposite direction")
                explanation_type = 2
            elif validate_res == 0:
                print ("The user question is invalid according to the local regression constraint derived from the "
                        + str(i+1) + "th constraint and the target tuple -- "
                        "the target tuple can be predicted by the constraint")
                explanation_type = 2
            else:
                print ("The user question is valid according to the local regression constraint derived from the "
                        + str(i+1) + "th constraint and the target tuple")
                explanation_type = 3
                #deviation = dir * (t[agg_col] - predicted_aggr) / predicted_aggr
                cnt = 0
                #for index, row in data['df'].iterrows():
                start = time.clock()
                f_value = get_F_value(local_cons[i].fix_attr, t)
                for idx in column_index[local_cons[i].fix_attr[0]][f_value[0]]:
                    row = data['df'].loc[data['df']['index'] == idx]
                    row = row.to_dict('records')[0]
                    if not local_cons[i].same_fixed_attributes(row):
                        continue
                    psi[-1] += row[agg_col]
                    t_sim = tuple_similarity(t, row, local_cons[i].var_attr, cat_sim, num_dis_norm, agg_col)
                    # print local_cons[i].var_attr, row
                    test_tuple = dict(zip(local_cons[i].var_attr, 
                                          map(lambda x:[x], get_V_value(local_cons[i].var_attr, row))))
                    predicted_aggr = []
                    if regression_package == 'scikit-learn':
                        for v in local_cons[i].var_attr:
                            if v in data['le']:
                                test_tuple[v] = data['le'][v].transform(test_tuple[v])
                                test_tuple[v] = data['ohe'][v].transform(test_tuple[v].reshape(-1, 1))
                            else:
                                test_tuple[v] = np.array(test_tuple[v]).reshape(-1, 1)
                        predicted_aggr = local_cons[i].predict_sklearn(np.concatenate(list(test_tuple.values()), axis=-1))
                    else:
                        predicted_aggr = local_cons[i].predict(pandas.DataFrame(test_tuple)).tolist()
                    deviation = (row[agg_col] - predicted_aggr[0]) / predicted_aggr[0]
                    #print get_F_value(local_cons[i].fix_attr, row), get_V_value(local_cons[i].var_attr, row), predicted_aggr[0], deviation, t_sim
                    candidate_list[i][cnt] = [deviation, t_sim, row['index'], predicted_aggr[0]]
                    print(row, predicted_aggr[0])
                    cnt += 1
                
                for k in range(cnt):
                    deviation = candidate_list[i][k][0]
                    t_sim = candidate_list[i][k][1]
                    predicted_aggr = candidate_list[i][k][3]
                    denominator = 10
                    #denominator = psi[-1] * psi[-1]
                    #denominator = psi[-1] * psi[-1] / (predicted_aggr * predicted_aggr)
                    score = math.sqrt(t_sim * t_sim + deviation * deviation / denominator)
                    #print score
                    top_k_lists[i][k] = (dir * deviation / abs(deviation) * score, i, candidate_list[i][k][2])

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
        for i in range(len(local_cons)):
            answer[j].append(sorted(top_k_lists[i], key=lambda x: x[0]))

        #answer[j] = top_k_lists


    print('Index building time: ' + str(index_building_time) + 'seconds')
    print('Constraint building time: ' + str(constraint_building_time) + 'seconds')
    print('Question validating time: ' + str(question_validating_time) + 'seconds')
    print('Score computing time: ' + str(score_computing_time) + 'seconds')
    #print('Result merging time: ' + str(result_merging_time) + 'seconds')
    return answer

def load_data(qr_file=ExplConfig.DEFAULT_RESULT_PATH):
    ''' 
        load query result
    '''
    df = pandas.read_csv(open(qr_file, 'r'), header=0, quotechar="'")
    le = {}
    ohe = {}
    for column in df:
        df[column] = df[column].apply(lambda x: x.replace('\'', '').strip())
        df[column] = df[column].apply(lambda x: float_or_integer(x))
        # if it is a categorical attribute, first encode each one into integers, and then use one-hot encoding
        if df[column].dtype.kind == 'S' or df[column].dtype.kind == 'O':
            le[column] = preprocessing.LabelEncoder()
            le[column].fit(df[column])
            ohe[column] = preprocessing.OneHotEncoder()
            le_col = le[column].transform(df[column])
            le_col = le_col.reshape(-1, 1)
            ohe[column] = preprocessing.OneHotEncoder(sparse=False)
            ohe[column].fit(le_col)
    df.insert(0, 'index', range(0, len(df))) 
    data = {'df':df, 'le':le, 'ohe':ohe}
    return data

def load_user_question(uq_path=ExplConfig.DEFAULT_QUESTION_PATH):
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
                print(k, v)
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

def load_constraints(cons_path=ExplConfig.DEFAULT_CONSTRAINT_PATH):
    '''
        load pre-defined constraints(currently only fixed attributes and variable attributes)
    '''
    inf = open(cons_path, 'r')
    cons = []
    while True:
        line = inf.readline()
        if not line:
            break
        cons.append([[],[]])
        cons[-1][0] = line.strip(' \r\n').split(',')
        line = inf.readline()
        cons[-1][1] = line.strip(' \r\n').split(',')
    inf.close()
    return cons

class ExplanationGenerator:

    def __init__(self, config : ExplConfig):
        self.config = config

    def doExplain(self):
        c=self.config
        log.info("start explaining ...")
        start = time.clock()
        data = load_data(c.query_result_file)
        log.debug("loaded query results from file")
        constraints = load_constraints(ExplConfig.DEFAULT_CONSTRAINT_PATH)
        log.debug("loaded patterns from file")
        Q = load_user_question(c.user_question_file)
        log.debug("loaded user question from file")
        category_similarity = CategorySimilarityMatrix(ExplConfig.EXAMPLE_SIMILARITY_MATRIX_PATH)
        #category_similarity = CategoryNetworkEmbedding(EXAMPLE_NETWORK_EMBEDDING_PATH, data['df'])
        num_dis_norm = normalize_numerical_distance(data['df'])
        end = time.clock()
        log.debug("done loading")
        print('Loading time: ' + str(end-start) + 'seconds')

        log.debug("start finding explanations ...")
        start = time.clock()
        #regression_package = 'scikit-learn'
        regression_package = 'statsmodels'
        explanations_list = find_explanation_regression_based(data, Q, constraints, category_similarity, 
                                                              num_dis_norm, c.constraint_epsilon, 
                                                              aggregate_column, regression_package)
        end = time.clock()
        print('Total querying time: ' + str(end-start) + 'seconds')
        log.debug("finding explanations ... DONE")
        
        ofile = sys.stdout
        if outputfile != '':
            ofile = open(outputfile, 'w')

        for i, top_k_list in enumerate(explanations_list):
            ofile.write('User question ' + str(i+1) + ':\n')
            for k, list_by_con in enumerate(top_k_list):
                for j in range(5):
                    e = list_by_con[j]
                    ofile.write('------------------------\n')
                    print_str = ''
                    e_tuple = data['df'].loc[data['df']['index'] == e[2]]
                    e_tuple_str = ','.join(e_tuple.to_string(header=False,index=False,index_names=False).split('  ')[1:])
                    ofile.write('Top ' + str(j+1) + ' explanation:\n')
                    ofile.write('Constraint ' + str(e[1]+1) + ': [' + ','.join(constraints[e[1]][0]) + ']' + '[' + ','.join(constraints[e[1]][1]) + ']')
                    ofile.write('\n')
                    #ofile.write('Score: ' + str(e[0]))
                    ofile.write('Score: ' + str(-e[0]))
                    ofile.write('\n')
                    ofile.write('(' + e_tuple_str + ')')
                    ofile.write('\n')
            
                ofile.write('------------------------\n')
        
        
def main(argv=[]):
    query_result_file = ExplConfig.DEFAULT_RESULT_PATH
    constraint_file = ExplConfig.DEFAULT_CONSTRAINT_PATH
    user_question_file = ExplConfig.DEFAULT_QUESTION_PATH
    outputfile = ''
    constraint_epsilon = ExplConfig.DEFAULT_CONSTRAINT_EPSILON
    aggregate_column = ExplConfig.DEFAULT_AGGREGATE_COLUMN
    try:
        opts, args = getopt.getopt(argv,"hq:c:u:o:e:a",["help","qfile=","cfile=","ufile=","ofile=","epsilon=","aggregate_column="])
    except getopt.GetoptError:
        print('explanation.py -q <query_result_file> -c <constraint_file> -u \
        <user_question_file> -o <outputfile> -e <epsilon> -a <aggregate_column>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('explanation.py -q <query_result_file> -c <constraint_file> -u \
            <user_question_file> -o <outputfile> -e <epsilon> -a <aggregate_column>')
            sys.exit(2)    
        elif opt in ("-q", "--qfile"):
            query_result_file = arg
        elif opt in ("-c", "--cfile"):
            constraint_file = arg
        elif opt in ("-u", "--ufile"):
            user_question_file = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-e", "--epsilon"):
            constraint_epsilon = float(arg)
        elif opt in ("-a", "--aggcolumn"):
            aggregate_column = arg

    print(opts)
    start = time.clock()
    data = load_data(query_result_file)
    constraints = load_constraints(ExplConfig.DEFAULT_CONSTRAINT_PATH)
    Q = load_user_question(user_question_file)
    category_similarity = CategorySimilarityMatrix(ExplConfig.EXAMPLE_SIMILARITY_MATRIX_PATH)
    #category_similarity = CategoryNetworkEmbedding(ExplConfig.EXAMPLE_NETWORK_EMBEDDING_PATH, data['df'])
    num_dis_norm = normalize_numerical_distance(data['df'])
    end = time.clock()
    print('Loading time: ' + str(end-start) + 'seconds')
    
    start = time.clock()
    #regression_package = 'scikit-learn'
    regression_package = 'statsmodels'
    explanations_list = find_explanation_regression_based(data, Q, constraints, category_similarity, 
                                                          num_dis_norm, constraint_epsilon, 
                                                          aggregate_column, regression_package)
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
        ofile.write('User question ' + str(i+1) + ':\n')
        for k, list_by_con in enumerate(top_k_list):
            for j in range(5):
                e = list_by_con[j]
                ofile.write('------------------------\n')
                print_str = ''
                e_tuple = data['df'].loc[data['df']['index'] == e[2]]
                e_tuple_str = ','.join(e_tuple.to_string(header=False,index=False,index_names=False).split('  ')[1:])
                ofile.write('Top ' + str(j+1) + ' explanation:\n')
                ofile.write('Constraint ' + str(e[1]+1) + ': [' + ','.join(constraints[e[1]][0]) + ']' + '[' + ','.join(constraints[e[1]][1]) + ']')
                ofile.write('\n')
                #ofile.write('Score: ' + str(e[0]))
                ofile.write('Score: ' + str(-e[0]))
                ofile.write('\n')
                ofile.write('(' + e_tuple_str + ')')
                ofile.write('\n')
            
            ofile.write('------------------------\n')

if __name__ == "__main__":
    main(sys.argv[1:])


