# -*- coding: utf-8 -*-
import math
import numpy as np
import main as mmm


#Rastrigin関数（評価関数）
def rastrigin_score(para):
    k = 0
    for x in para:
        k += 10 + (x*x - 10 * math.cos(2*math.pi*x))
    return k



#パラメータ範囲
para_range = np.ones((15, 2)) * 5.12
para_range[:, 0] *= -1
print(para_range)

#GAで最適化
para, score = mmm.vcopt().rcGA(para_range,                           #para_range
                            rastrigin_score,                     #score_func
                            0.00,                                 #aim
                            show_pool_func='print')  #show_para_func='bar', 'print', 'plot')

#結果の表示
print(para)
print(score)