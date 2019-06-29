# -*- coding: utf-8 -*-
import numpy as np
import numpy.random as nr
import matplotlib.pyplot as plt
#from numba import jit
import main as mmm


#ナップザック問題の評価関数
#@jit
def money_score(para):
    
    money = para[0]*10000
    
    #スコアの計算（直接returnする）
    return money




#パラメータ範囲
para_range = [[i for i in range(10)] for j in range(2)]
#para_range = [i for i in range(10)]
print(para_range)

#para_range = [para_range]
#print(para_range)


#GAで最適化
para, score = mmm.vcopt().dcGA(para_range,                      #para_range
                           money_score,                     #score_func
                           -0.1,                             #aim
                           show_pool_func='print',  #show_para_func=None
                           seed=2,
                           pool_num=20,
                           max_gen=None)                       #seed=None

#結果の表示
print(para)
print(score)
