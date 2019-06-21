# -*- coding: utf-8 -*-
"""
Created on Tue May  7 09:45:54 2019

@author: wanghu5
"""
import os
import time
import pandas as pd
from .Eval.CfMetric import CfMetric
from .Eval.Metric import Metric
import numpy as np
import sys
sys.dont_write_bytecode = True

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
'''

def feat_split_label_cross(ofname, data, select_titles=None, missing_value=-1, group_list = None, group_column = None, 
                           month_list = None, month_column = None, label_column = None, good_label = 1):
    print('\n\n*** uni_variable analyzing... ***')
    print('output path: %s\n' % ofname)
    
    dat0 = data
    
    if isinstance(month_list,list):
        psi_title = ''
        avg_title = ',avg'+month_list[0]
        for i in range(1, len(month_list)):
            psi_title += ',psi' + month_list[i]
            avg_title += ',avg' + month_list[i]
    else:
        psi_title = ''
        avg_title = ''
        
    outfile = open(ofname,'w')
    outfile.write('id,group,feat,desc,bin,miss_rate,lowbound,upbound,average,' \
               + 'total,good,bad,user_rate,bad_rate,ks,iv'
               + psi_title + avg_title + '\n')
    ids = 0
    
    #如果没有传group_list默认进行全部的分析
    all_group = ['all',[]]
    if group_list:
        group_list.insert(0,all_group)
    else:
        group_list=[all_group]
        
    for g in group_list:
        k,v = g
        if k == 'all':
            dat = dat0
        else:
            assert group_column, "If you wanna analysis split by group, a group column name list should be given"
            dat = dat0[dat0[group_column].isin(v)]
        
        if select_titles is None:
            print ("Need input columns name that you want to analysis!")
            return 0
        print ("\n================= GROUP "+str(k)+" =================")
        # 整体
        n_tot = len(dat)
        n_god = len(dat[dat[label_column]==good_label])
        n_bad = n_tot - n_god
        for t in select_titles:
            print ("[" + str(t) + "]")
            # 缺失统计
            n_t_mis_god = len(dat[np.logical_and(dat[t] == missing_value, dat[label_column]==1)])
            n_t_mis_bad = len(dat[np.logical_and(dat[t] == missing_value, dat[label_column]==0)])
            n_mis  = n_t_mis_god + n_t_mis_bad
            mis_rate = 0.0 if n_tot==0 else n_mis*1.0/n_tot
            bad_rate = 0.0 if n_tot==0 else n_bad*100.0/n_tot
            
            dat_t = dat[dat[t]!=missing_value]
            vavg = dat_t[t].mean()
            vmin = dat_t[t].min()
            vmax = dat_t[t].max()
            # ks,iv,psi
            ks, iv = (-1, -1)
            if len(dat_t) > 1 and len(set(dat_t[label_column].values)) == 2:
                try:
                    # print('debug:\n', dat_t[label_column].values, dat_t[t].values)
                    met = CfMetric(y_true=dat_t[label_column].values, y_score=dat_t[t].values, seg=10)
                    ks = met.ks
                    iv = met.iv
                except IndexError:
                    pass
            
            psi_str = ''
            avg_str = ''
            if month_list and len(month_list)>=2:
                mt = Metric(dat_t, label_name=label_column, score_name=t)
                psi_on_given_splits = mt.get_psi_given_splits(month_list, split_name = month_column)
                tmp = dat_t[dat_t[month_column] == month_list[0]]
                if len(tmp) > 0:
                    avg_str +=  ',%g' % (tmp[t].mean())
                else:
                    avg_str += ','
                for i in range(1, len(month_list)):
                    if month_list[i] in psi_on_given_splits:
                        psi_str += ',%g' % psi_on_given_splits[month_list[i]]
                    else:
                        psi_str += ','
                    tmp = dat_t[dat_t[month_column] == month_list[i]]
                    if len(tmp) > 0:
                        avg_str +=  ',%g' % (tmp[t].mean())
                    else:
                        avg_str += ','
            else:
                psi_str += ','
                avg_str += ','
            
            ids += 1
            outfile.write('%d,%s,%s,,ALL,%.3f,%g,%g,%g,%d,%d,%d,,%.3f,%.2f,%.3f%s%s\n' % \
                       (ids, k, t, mis_rate, vmin, vmax, vavg, n_tot, n_god, 
                        n_bad, bad_rate, ks, iv, psi_str, avg_str))
            ids += 1
            bad_rate = 0.0 if n_mis==0 else n_t_mis_bad*100.0/n_mis
            outfile.write('%d,%s,%s,,MISS,,,,,%d,%d,%d,,%.3f\n' % \
                       (ids, k, t, n_mis, n_t_mis_god, n_t_mis_bad, bad_rate))
            v_set = set(dat_t[t].values)
            ## 分组分析，如果取值较少，则每个值分一组；否则用 qcut 十分位分析
            if len(v_set) < 4:
                i = 0
                for vv in v_set:
                    i += 1
                    n_t_v_god = len(dat_t[(dat_t[t] == vv) & (dat_t[label_column]==1)])
                    n_t_v_bad = len(dat_t[(dat_t[t] == vv) & (dat_t[label_column]==0)])
                    n_t_v  = n_t_v_god + n_t_v_bad
                    ids += 1
                    use_rate = 0.0 if n_tot==0.0 else n_t_v*100.0/n_tot
                    bad_rate = 0.0 if n_t_v==0.0 else n_t_v_bad*100.0/n_t_v
                    outfile.write('%d,%s,%s,,%d,,%g,,,%d,%d,%d,%.3f,%.3f\n' % \
                               (ids, k, t, i, vv, n_t_v, 
                                n_t_v_god, n_t_v_bad, use_rate, bad_rate))
            else:
                _, bins = pd.qcut(dat_t[t], 10, duplicates='drop', retbins=True)
                # print('bins', bins)
                for i in range(1,len(bins)):
                    tmp = dat_t[(dat_t[t]>bins[i-1]) & (dat_t[t]<=bins[i])]
                    vavg = tmp[t].mean()
                    n_t_i = len(tmp)
                    n_t_i_god = len(tmp[tmp[label_column]==1])
                    n_t_i_bad = n_t_i - n_t_i_god
                    ids += 1
                    use_rate = 0.0 if n_tot==0.0 else n_t_i*100.0/n_tot
                    bad_rate = 0.0 if n_t_i==0.0 else n_t_i_bad*100.0/n_t_i
                    outfile.write('%d,%s,%s,,%d,,%f,%f,%g,%d,%d,%d,%.3f,%.3f\n' % \
                               (ids, k, t, i, bins[i-1], bins[i], vavg, n_t_i, 
                                n_t_i_god, n_t_i_bad, use_rate, bad_rate))
            outfile.flush()
    outfile.close()
    
        
if __name__ == "__main__":
    prefix = time.strftime('%Y%m%d_%H%M',time.localtime(time.time()))
    outdir = './analysis/'
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    ofname = outdir + ('log.feat_split_label_cross.%s.csv' % prefix)

    data = 'load data to here'
    data = pd.read_csv('test.csv',sep=',',encoding='utf-8')
    
    select_titles = ['card_attr','flag_card_high_end','cna_score']
    group_list = [['new',[1]],['std',[2]]]
    
    month_list=['2018-11','2018-12']
    
    feat_split_label_cross(ofname, data, select_titles=select_titles, missing_value=-1, group_list = group_list, group_column = 'group', 
                           month_list = month_list, month_column = 'month', label_column = 'label', good_label = 1)
    
