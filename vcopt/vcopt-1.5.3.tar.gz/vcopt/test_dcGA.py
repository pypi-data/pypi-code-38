# -*- coding: utf-8 -*-
import numpy as np
import numpy.random as nr
import matplotlib.pyplot as plt
#from numba import jit
import main as mmm


#ナップザック問題の評価関数
#@jit
def money_score(para):
    
    money = para[0]*10000 + para[1]*5000 + para[2]*1000 + para[3]*500 + para[4]*100 + para[5]*50 + para[6]*10
    num = np.sum(para)
    
    #スコアの計算（直接returnする）
    return (abs(65860 - money) + 1) * num**2
    #return abs(65860 - money) * num

#ナップザック問題のpoolの可視化
def money_show_pool(pool, **info):
    
    #GA中の諸情報はinfoという辞書に格納されて渡されます
    #これらを受け取って使用することができます
    gen = info['gen']
    best_index = info['best_index']
    best_score = info['best_score']
    mean_score = info['mean_score']
    mean_gap = info['mean_gap']
    time = info['time']
    
    #プロット（および保存）
    plt.figure(figsize=(6, 6))
    #poolを100個まで積み上げ棒グラフでプロット
    x = np.arange(len(pool[:100]))
    plt.bar(x, pool[:100, 0]*10000)
    plt.bar(x, pool[:100, 1]*5000, bottom=pool[:, 0]*10000)
    plt.bar(x, pool[:100, 2]*1000, bottom=pool[:, 0]*10000 + pool[:, 1]*5000)
    plt.bar(x, pool[:100, 3]*500,  bottom=pool[:, 0]*10000 + pool[:, 1]*5000 + pool[:, 2]*1000)
    plt.bar(x, pool[:100, 4]*100,  bottom=pool[:, 0]*10000 + pool[:, 1]*5000 + pool[:, 2]*1000 + pool[:, 3]*500)
    plt.bar(x, pool[:100, 5]*50,   bottom=pool[:, 0]*10000 + pool[:, 1]*5000 + pool[:, 2]*1000 + pool[:, 3]*500 + pool[:, 4]*100)
    plt.bar(x, pool[:100, 6]*10,   bottom=pool[:, 0]*10000 + pool[:, 1]*5000 + pool[:, 2]*1000 + pool[:, 3]*500 + pool[:, 4]*100 + pool[:, 5]*50)
    #タイトルをつけて表示
    plt.title('gen={}, best={} mean={} time={}'.format(gen, best_score, mean_score, time))
    plt.ylim([0, 80000])
    #plt.savefig('save/GA_{}.png'.format(gen_num))
    plt.show()
    print()


#パラメータ範囲
para_range = [[i for i in range(10)] for j in range(7)]

#GAで最適化
para, score = mmm.vcopt().dcGA(para_range,                      #para_range
                           money_score,                     #score_func
                           -0.1,                             #aim
                           show_pool_func='print',  #show_para_func=None
                           seed=2,
                           pool_num=2000,
                           max_gen=None)                       #seed=None

#結果の表示
print(para)
print(score)
