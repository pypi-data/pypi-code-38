# -*- coding: utf-8 -*-
import copy
import numpy as np
from vcopt import vcopt
import matplotlib.pyplot as plt
import main as mmm

#============================
#パラメータ
#============================
#購入意向商品ファイル
p_file = 'p_rate.txt'
#代替意向商品ファイル
ap_file = 'ap_rate.txt'
#並べる商品の数
space=19

print('並べる商品の数:{}'.format(space))

#============================
#購入意向率の読み込み
#============================
#ファイル名
file = open(p_file, 'r')
#１行目はラベルなのでカラ読み
file.readline()
#２行目以降を読み込む
p_data = []
while 1:
    tmp = file.readline().split()
    if len(tmp) > 1:
        p_data.append(tmp)
    else:
        break
file.close()

#print('購入意向率リスト数:{}'.format(len(p_data)))
#print('購入意向率リスト:{}'.format(p_data))

#============================
#代替購入率の読み込み
#============================
#ファイル名
file = open(ap_file, 'r')
#１行目のラベルを読み込む
ap_label = file.readline().split()[:20] #空の一列目はsplit()で除かれる
#２行目以降を読み込む
ap_data = []
while 1:
    tmp = file.readline().split()[1:] #一列目は商品名なので除く
    if len(tmp) > 1:
        ap_data.append(tmp)
    else:
        break
file.close()

#print('代替購入率リスト数:{}'.format(len(ap_data)))
#print('代替購入率リスト:{}'.format(ap_data))

#============================
#評価関数
#============================
def p_score(para):
    
    #paraは商品IDが並んだ[1,5,9,11,18]のような形で与えられる
    
    #並ばない商品のリストを作っておく    
    #全商品IDリスト
    all = list(range(1, len(p_data) + 1)) #全商品ID
    #並ばない商品IDのリスト
    non_s = list(set(all) - set(para)) #paraに含まれない商品ID

    #重複は除く
    para = list(set(para))
    
    #スコア計算
    score = 0
    for i in para:                         
        #意向商品売上計算
        score += (float(p_data[i-1][1]) * float(p_data[i-1][2]))
        #代替商品売上計算 （価格×j商品を買いたい割合×その人がi商品を買う割合）
        for j in non_s:
           score = score + (float(p_data[i-1][1]) * float(p_data[j-1][2]) * float(ap_data[j-1][i-1]))
    return score


#テスト用
para = [1,15]
score = p_score(para)
print(score)

#============================
#poolの可視化関数
#============================
def p_show_pool(pool, **info):
    
    #GA中の諸情報はinfoという辞書に格納されて渡されます
    #これらを受け取って使用することができます
    gen = info['gen']
    #best_index = info['best_index']
    best_score = info['best_score']
    mean_score = info['mean_score']
    #mean_gap = info['mean_gap']
    time = info['time']
    
    #各poolのスコアを計算（100体まで）
    scores = []
    for para in pool[:100]:
        scores.append(p_score(para))
    
    #棒グラフでプロット（100体まで）
    plt.figure(figsize=(12, 6))
    plt.bar(range(len(pool[:100])), scores)
    #タイトルをつけて表示
    plt.title('gen={}, best={} mean={} time={}'.format(gen, best_score, mean_score, time))
    plt.ylim([0, 130])
    #plt.savefig('save/{}.png'.format(gen))
    plt.show()
    print()


#============================
#最適化実行
#============================
#パラメータ範囲
para_range = [i for i in range(1, len(p_data) + 1)]
para_range = np.array(para_range)
#GAで最適化
para, score = mmm.vcopt().setGA(para_range,                  #para_range
                            space,                       #set_num
                            p_score,                     #score_func
                            110,                       #aim
                            show_pool_func='print',  #show_para_func=None
                            seed=1,                   #seed=None
                            pool_num=200,
                            max_gen=None)                  

#結果表示
print('期待売上:{:.3f}円'.format(score))
for i in para:
    print('{0}.{1} '.format(i,ap_label[i - 1]), end='')
print()