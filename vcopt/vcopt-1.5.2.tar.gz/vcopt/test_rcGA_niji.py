# -*- coding: utf-8 -*-
import numpy as np
import main as mmm

#二次関数（評価関数）
def niji_kansu(para):
    y = para**2
    return y

#パラメータ範囲（パラメータ１つだけでも2次元配列にする必要がある）
para_range = [-5, 5]
print(para_range)

#GAで最適化
para, score = mmm.vcopt().rcGA(para_range,              #para_range
                           niji_kansu,              #score_func
                           0.00,                    #aim
                           show_pool_func='print')  #show_para_func=None, 'bar', 'print', 'plot'

#結果の表示
print(para)
print(score)