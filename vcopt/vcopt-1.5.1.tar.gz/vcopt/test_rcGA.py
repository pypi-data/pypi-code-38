# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import math
import numpy as np
import numpy.random as nr
import matplotlib.pyplot as plt
import main as mmm





#Rastrigin関数（評価関数）
def rastrigin_score(para):
    k = 0
    for x in para:
        k += 10 + (x*x - 10 * math.cos(2*math.pi*x))
    return k

#poolの可視化
def rastrigin_show_pool(pool, **info):
    
    #GA中の諸情報はinfoという辞書に格納されて渡されます
    #これらを受け取って使用することができます
    gen = info['gen']
    best_index = info['best_index']
    best_score = info['best_score']
    mean_score = info['mean_score']
    mean_gap = info['mean_gap']
    time = info['time']
    
    #プロット
    plt.figure(figsize=(6, 6))
    #次元の数だけ横線を引く
    for dim in range(len(pool[0])):
        plt.plot([-5, 5], [dim, dim], 'k-')
    #poolを次元ごとに100個まで薄い黒でプロット
    for dim in range(len(pool[0])):
        plt.plot(pool[:100, dim], [dim]*len(pool[:100]), 'ok', markersize=8, alpha=(2.0/len(pool[:100])))
    #エリートは赤でプロット
    plt.plot(pool[best_index, :], range(len(pool[0])), 'or', markersize=8)
    #タイトルをつけて表示
    plt.xlabel('para'); plt.ylabel('dim')
    plt.title('gen={}, best={} mean={} time={}'.format(gen, best_score, mean_score, time))
    #plt.savefig('save/{}.png'.format(gen_num))
    plt.show()
    print()


#パラメータ範囲
para_range = np.ones((15, 2)) * 5.12
para_range[:, 0] *= -1
print(para_range)

#GAで最適化
para, score = mmm.vcopt().rcGA(para_range,                           #para_range
                            rastrigin_score,                     #score_func
                            0.00,                                 #aim
                            show_pool_func='print',  #show_para_func=None
                            seed=1,
                            pool_num=None,
                            max_gen=None)                           #seed=None

#結果の表示
print(para)
print(score)