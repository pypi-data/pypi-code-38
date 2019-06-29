# -*- coding: utf-8 -*-
import numpy as np
import numpy.random as nr
import matplotlib.pyplot as plt
import main as mmm

#巡回セールスマン問題の作成
def create_tsp(town_num):
    
    #町のx座標とy座標の配列を作成
    town_x = nr.rand(town_num)
    town_y = nr.rand(town_num)
    
    return town_x, town_y

#巡回セールスマン問題の評価関数
def tsp_score(para):
    
    #スコアの計算（今回は直接returnする）
    
    return np.sum(((town_x[para][:-1] - town_x[para][1:])**2 + (town_y[para][:-1] - town_y[para][1:])**2)**0.5)


#巡回セールスマン問題のpoolの可視化
def tsp_show_pool(pool, **info):
    
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
    #poolを100個まで薄い黒でプロット
    for para in pool[:100]:
        plt.plot(town_x[para], town_y[para], 'ok-', alpha=(2.0/len(pool[:100])))
    #エリートは赤でプロット     
    plt.plot(town_x[pool[best_index]], town_y[pool[best_index]], 'or-')
    #タイトルをつけて表示
    plt.xlabel('x'); plt.ylabel('y')
    plt.xlim([0, 1]); plt.ylim([0, 1])
    plt.title('gen={}, best={} mean={} time={}'.format(gen, best_score, mean_score, time))
    #plt.savefig('save/{}.png'.format(gen_num))
    plt.show()
    print()


#巡回セールスマン問題の作成
nr.seed(1)
town_num = 20
town_x, town_y = create_tsp(town_num)

#パラメータ範囲
para_range = np.arange(town_num)

#GAで最適化
para, score = mmm.vcopt().tspGA(para_range,                    #para_range
                            tsp_score,                     #score_func
                            0.0,                           #aim
                            show_pool_func='print',  #show_pool_func=None
                            seed=1,
                            pool_num=100,
                            max_gen=None)                        #seed=None

#結果の表示
print(para)
print(score)

'''
#巡回セールスマン問題の作成
nr.seed(1)
town_num = 5
town_x, town_y = create_tsp(town_num)

#パラメータ範囲
para_range = [1, 2, 3, 4]

#GAで最適化
para, score = mmm.vcopt().tspGA(para_range,                    #para_range
                            tsp_score,                     #score_func
                            0.0,                           #aim
                            show_pool_func='print',  #show_pool_func=None
                            seed=1,
                            pool_num=100,
                            max_gen=None)                        #seed=None

#結果の表示
print(para)
print(score)'''