# coding: utf-8
#!/usr/bin/python
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import sys
import pandas as pd
import numpy as np
import xgboost as xgb
import argparse
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score
import math
import re
from .uni_variable_analysis import *
#----------------------------------------------------------------------------------
'''
xgb_train：封装了常规的xgboost的训练流程
参数设置：
save_path(str):保存模型的路径，不要添加模型的名字，模型会命名为xgb_model和lr_model
dtrain(DMatrixs):训练集数据
dtest(DMatrixs):测试集数据
parameter(dict):xgboost的参数集，存在默认设置
train_round(int):训练轮数，默认设置100轮
early_stopping(int):提前终止轮数，默认设置10
lr_flag(bool):是否融合LR模型标志位
y_train(list/Serise):LR训练数据的标签，本函数中是dtrain的标签

返回值：
bst(xgboost model):xgboost模型文件
lr_clf(LR model)：LR模型文件
'''
def xgb_train(save_path, dtrain, dtest, parameter = None, train_round = 100, early_stopping=10, lr_flag = False, y_train = None):
    if parameter:
        param = parameter
    else:
        param = {'max_depth':3, 
                 'eta':0.05,
                 'min_child_weight':4,
                 'gamma':0, 
                 'subsample':0.8,
                 'colsample_bytree':0.8,
                 'scale_pos_weight':0.8,
                 'silent':1, 
                 'objective':'binary:logistic',
                 'eval_metric': 'auc'
                  }
    param['nthread'] = -1
    
    plst = param.items()
    
    watchlist = [ (dtrain,'train') ,(dtest,'test')]  
    
    #训练保存模型
    bst = xgb.train(plst, dtrain, train_round, watchlist, early_stopping_rounds=early_stopping, verbose_eval=True)
    bst.save_model(save_path + 'xgb_model')
    if lr_flag:
        if not y_train:
            print('if lr_flag is True, then y_train can not be empty')
            print('lr train process will be pass')
        else:
            #每个样本在每棵树上的叶子的ID
            train_xgb_pred_mat = bst.predict(dtrain,pred_leaf =True)
            #编码成One-hot编码
            one_hot_encoder = OneHotEncoder()
            train_lr_feature_mat = one_hot_encoder.fit_transform(train_xgb_pred_mat)
            
            #入LR模型进行训练
            lr_clf = LogisticRegression(penalty='l1',C= 0.05, n_jobs=4)
            lr_clf.fit(train_lr_feature_mat,y_train)
            #保存lr模型
            joblib.dump(lr_clf, save_path + 'lr_model')
            return bst, lr_clf
            print ('----------------xgb&lr trained successfully!----------------')
    print ('----------------xgb trained successfully!----------------')
    return bst

#----------------------------------------------------------------------------------
    

#----------------------------------------------------------------------------------
'''
cal_auc_ks：封装了计算模型预测的auc和ks的功能
参数设置：
y_true(list):待测试样本的标签list
y_pred(list):待测试样本经过模型的预测list
name(str):标识结果的字段
save(bool)：保存标识位
online(bool):在线计算标志位,如果为True,auc/ks的计算将只是用python原生代码

返回值：
auc(double):模型分auc
ks(double)：模型分ks
'''
   
def cal_auc_ks(y_true, y_pred, name = None, save=False, online=False):
    if name:
        pass
    else:
        name = ''
    
    if not online:
        sample = name + " Sample : %s" % len(y_true)
        auc = name + ' test_set auc : %0.3f' % roc_auc_score(y_true, y_pred)
        ks = name + ' test_set ks  : %0.3f' % cal_ks(y_true,y_pred)
    else:
        sample = name + " Sample : %s" % len(y_true)
        auc = name + ' test_set auc : %0.3f' % auc_calculate(y_pred,y_true)
        ks = name + ' test_set ks  : %0.3f' % cal_ks(y_pred,y_true) 

    print (sample)
    print (auc)
    print (ks)
    print ('----------------cal_auc_ks process successfully!----------------')
    if save:
        with open(name + '_auc&ks.txt', 'a+') as f:
            f.write(sample + '\n' + auc + '\n' + ks + '\n' + '------------------------------------' + '\n' )
            print ('----------------cal_auc_ks save successfully!----------------')
    return roc_auc_score(y_true, y_pred), cal_ks(y_true,y_pred) 
    
def cal_ks(label,score):
    fpr,tpr,thresholds= roc_curve(label,score)
    return max(tpr-fpr)

def auc_calculate(preds,labels,n_bins=100):
    postive_len=0
    for i in range(len(labels)):
        if int(labels[i])==1:
            postive_len=postive_len+1
    negative_len = len(labels) - postive_len
    total_case = postive_len * negative_len
    pos_histogram = [0 for _ in range(n_bins)]
    neg_histogram = [0 for _ in range(n_bins)]
    bin_width = 1.0 /float(n_bins)
    for i in range(len(labels)):
        nth_bin = int(float(preds[i])/float(bin_width))
        if int(labels[i])==1:
            pos_histogram[nth_bin] += 1
        else:
            neg_histogram[nth_bin] += 1
    accumulated_neg = 0
    satisfied_pair = 0
    for i in range(n_bins):
        satisfied_pair += (pos_histogram[i]*accumulated_neg + pos_histogram[i]*neg_histogram[i]*0.5)
        accumulated_neg += neg_histogram[i]
    return satisfied_pair / float(total_case)


def quantile_p(data, p):
    pos = (len(data) + 1)*p
    pos_integer = int(math.modf(pos)[1])
    pos_decimal = pos - pos_integer
    Q = float(data[pos_integer - 1]) + (float(data[pos_integer]) - float(data[pos_integer - 1]))*pos_decimal
    return Q

def ks_calculate(preds, labels, seg=10):
    segPoint=[(1/float(seg))*i for i in range(1,seg)]
    segValue=[]
    for point in segPoint:
        segValue.append(quantile_p(preds,point))
    #tp、fp每个分段内累计1和0的样本个数
    #这里必须加float，不然会整数除法

    tp=[]
    fp=[]
    for a in segValue:
        tp_temp=0
        fp_temp=0
        for i in range(0,len(preds)):
            if float(preds[i])<=a and int(labels[i])==1:
                tp_temp=tp_temp+1
            elif float(preds[i])<=a and int(labels[i])==0:
                fp_temp=fp_temp+1
        tp.append(float(tp_temp))
        fp.append(float(fp_temp))

    #ts,fs
    ts=0
    fs=0
    for i in range(0,len(labels)):
        if int(labels[i])==1:
            ts=ts+1
        else:
            fs=fs+1

        
    #calculate
    ksList=[]
    for i in range(0,len(tp)):
        temp=abs(tp[i]/float(ts)-fp[i]/float(fs))
        ksList.append(temp)
    ks=max(ksList)
    return ks
#----------------------------------------------------------------------------------

#----------------------------------------------------------------------------------
'''
imp_report:封装了输出特征重要程度的功能
参数设置：
model(xgboost model file):输入模型，不能使模型文件的地址，必须先读入模型后传入
data_columns(list/array/Serise)：输入到模型的数据特征列名，若无列名输出的是对应的列编号
whole_column(list/array/Serise):数据集的全部列名，大多数时候输入到模型的数据和源数据表维度上有差异，因此设置这个参数，当然，如果没有差异也可以传入trainData.columns

返回值：
feat_import(DataFrame):按照whole_column顺序的特征重要度，没选中的重要度是0
'''
def imp_report(model, data_columns, whole_column):
    #模型输出的特征编号和特征表的是不对应的，他是从0开始的连续性index，需要做一个转换对应
    #modelFeat的index是模型输出特征的index，而对应的value是特征表的列名
    column = list(whole_column)
    modelFeat = list(data_columns)
    
    #输出重要变量得分
    #xgb.plot_importance(bst)
    imp = model.get_fscore()
    imp_temp = {}
    
    #把重要的特征的key转换为特征表的key
    for key, value in imp.items():
        k = int(key[1:])
        imp_temp[modelFeat[k]] = value
    imp = imp_temp
    temp = []
    
    for index, value in enumerate(column):
        if value in imp.keys():
            temp.append(imp[value])
        else:
            temp.append(0)
    
#    imp = np.array(temp)
    imp = temp
    feat_import = pd.DataFrame(columns=['feat','imp'])
    feat_import['feat'] = column
    feat_import['imp'] = imp
    print ('----------------imp_feat process successfully!----------------')
    return feat_import    
#----------------------------------------------------------------------------------

#----------------------------------------------------------------------------------
'''    
cal_feat_ks:封装了计算单变量ks的功能
参数设置：
df(DataFrame):读入所有变量数据的DataFrame
valueCol(str)：df中要计算ks的列名，这里只支持单值传入，计算多个变量请用list的for循环传入
labelCol(str):df中的标签列名
seg(int):ks分组数，默认10组

返回值：
ksList(list):各分组的ks中间计算值
ks(double):单变量ks的值
'''
def cal_feat_ks(df, valueCol, labelCol, seg=10):
    segPoint=[(1/float(seg))*i for i in range(1,seg+1)]
    segValue=[]
    for point in segPoint:
        segValue.append(df[valueCol].quantile(point))
    #tp、fp每个分段内累计1和0的样本个数
    #这里必须加float，不然会整数除法
    tp=[float(df[(df[valueCol]<=a)&(df[labelCol]==1)][labelCol].count()) for a in segValue]
    fp=[float(df[(df[valueCol]<=a)&(df[labelCol]==0)][labelCol].count()) for a in segValue]
    #left：分段内累计样本数
    left=[df[(df[valueCol]<=a)][labelCol].count() for a in segValue]
    #tp_r：大于分段的逾期为1的样本数
    tp_r=[df[(df[valueCol]>a)&(df[labelCol]==1)][labelCol].count() for a in segValue]
    #right：大于分段所有样本
    right=[df[(df[valueCol]>a)][labelCol].count() for a in segValue]
    #所有逾期=1的样本数
    ts=df[df[labelCol]==1][labelCol].count()
    #所有逾期=0的样本数
    fs=df[df[labelCol]==0][labelCol].count()    
    
    ksList = abs((tp/ts)-(fp/fs))
    ks = max(ksList)
    return ksList,ks

#----------------------------------------------------------------------------------

#----------------------------------------------------------------------------------
'''    
cal_feat_iv:封装了计算单变量ks的功能
参数设置：
df(DataFrame):读入所有变量数据的DataFrame
valueCol(str)：df中要计算ks的列名，这里只支持单值传入，计算多个变量请用list的for循环传入
labelCol(str):df中的标签列名
seg(int):ks分组数，默认10组

返回值：
woe(list):单变量woe值
ks(double):单变量ks的值
'''

def cal_feat_iv(df, valueCol, labelCol, seg=10):
    segPoint=[(1/float(seg))*i for i in range(1,seg+1)]
    segValue=[]
    for point in segPoint:
        segValue.append(df[valueCol].quantile(point))
    #tp、fp每个分段内累计1和0的样本个数
    #这里必须加float，不然会整数除法
    tp=[float(df[(df[valueCol]<=a)&(df[labelCol]==1)][labelCol].count()) for a in segValue]
    fp=[float(df[(df[valueCol]<=a)&(df[labelCol]==0)][labelCol].count()) for a in segValue]
    #left：分段内累计样本数
    left=[df[(df[valueCol]<=a)][labelCol].count() for a in segValue]
    #tp_r：大于分段的逾期为1的样本数
    tp_r=[df[(df[valueCol]>a)&(df[labelCol]==1)][labelCol].count() for a in segValue]
    #right：大于分段所有样本
    right=[df[(df[valueCol]>a)][labelCol].count() for a in segValue]
    #所有逾期=1的样本数
    ts=df[df[labelCol]==1][labelCol].count()
    #所有逾期=0的样本数
    fs=df[df[labelCol]==0][labelCol].count()    
    
    weight = (tp/ts)-(fp/fs)
    woe = []
    for i in range(seg):
       woe.append(math.log((tp[i]/ts)/(fp[i]/fs)))
    iv = 0
    for i in range(seg):
        iv += weight[i] * woe[i]
    return woe,iv
#----------------------------------------------------------------------------------

#----------------------------------------------------------------------------------
'''    
format_time:封装了转换秒数为时分秒的函数
参数设置：
seconds(float):秒数

返回值：
hours(int)
minutes(int)
seconds(float)
'''
def format_time(seconds):
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = seconds % 60
    return hours, minutes, seconds
#----------------------------------------------------------------------------------

#----------------------------------------------------------------------------------
'''
xgb_serialization:可以将xgboost dump下来的树模型解析文件进行序列化
参数设置：
xgb_dump_file(string):dump文件目录

返回值:
tree_lists(3d-list):三维list, 每棵树是一个2d list, N颗数组成，变成3d list
'''
def xgb_serialization(xgb_dump_file):
    # model = xgb.Booster(model_file='{0}'.format(ufile))
    # model.dump_model('tmp_dump.txt')
    filestr=''
    for line in file('{0}'.format(xgb_dump_file)):
        filestr+=line
    tree_lists = []
    pattern = re.compile(r'(\d+):')
    treestrs = filestr.split('booster')
    for treestr in treestrs:
        if re.match('\[\d+\]', treestr):
            node_num = max([int(i) for i in pattern.findall(treestr)])
            tree_list = [0]*(node_num+1)
            for line in treestr.split('\n'):
                if re.match(r'\t*(\d+):leaf=(.*)', line):
                    m = re.match(r'\t*(\d+):leaf=(.*)', line)
                    index, prob = m.groups()
                    tree_list[int(index)] = ['none',prob]
                elif re.match(r'\t*(\d+):\[(.*?)<(.*?)\] yes=(\d+),no=(\d+),missing=(\d+)', line):
                    m = re.match(r'\t*(\d+):\[(.*?)<(.*?)\] yes=(\d+),no=(\d+),missing=(\d+)', line)
                    index, featname, value, yesindex, noindex, missingindex = m.groups()
                    tree_list[int(index)] = [featname,value,yesindex, noindex, missingindex]
            tree_lists.append(tree_list)
    return tree_lists

#----------------------------------------------------------------------------------
'''
xgb_online_predict:通过序列化xgb的模型解析文件，进行原生python的在线打分
参数设置：
feature_dict(dict):类似libsvm格式的特征字典key:value, key(string),例如'f729'，value(float)
xgbtree(3d-list):xgb模型解析文件的序列化数据

返回值:
score(float):单条样本的打分
'''
def xgb_online_predict(feature_dict, xgbtree):
    pred = []
    for tree in xgbtree:
        pred.append(get_predict_value(feature_dict, tree))
    score = 1/(1+math.exp(-sum(pred)))
    return score
    
'''
get_predict_value:xgb_online_predict的依赖函数，利用递归达到叶子节点
参数设置：
feature_dict(dict):类似libsvm格式的特征字典key:value, key(string),例如'f729'，value(float)
xgbtree(3d-list):xgb模型解析文件的序列化数据得到的单颗数
index:树递归的方向，非in参数

返回值:
pred(float):单条样本的叶子节点
'''     
def get_predict_value(feature_dict, tree, index=0):
    if tree[index][0] == 'none':
        return float(tree[index][1])
    elif tree[index][0] not in feature_dict:
        return get_predict_value(feature_dict, tree, int(tree[index][4]))
    elif feature_dict[tree[index][0]] < float(tree[index][1]):
        return get_predict_value(feature_dict, tree, int(tree[index][2]))
    else:
        return get_predict_value(feature_dict, tree, int(tree[index][3]))
        
#----------------------------------------------------------------------------------


#----------------------------------------------------------------------------------
'''
ofname(str)：结果导出路径
select_titles(list)：进行分析的列名
missing_value(int)：缺失值定义
group_list(list-2d like [["cate_name",[cate_value]],["cate_name",[cate_value]]...])：分组列表
group_column(string)：待分析的DataFrame中用于分组主键的列名
month_list(list)：按月分组的列表
month_column(str)：月份字段在DataFrame中的列名
label_column(str)：待分析的DataFrame中用于标签的列名
good_label(int)：好人的标签

def feat_split_label_cross(ofname, data, select_titles=None, missing_value=-1, group_list = None, group_column = None, 
                           month_list = None, month_column = None, label_column = None, good_label = 1)
'''
#----------------------------------------------------------------------------------