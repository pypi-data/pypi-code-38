# -*- coding: utf-8 -*-
import numpy as np
import numpy.random as nr
import math, time
from copy import deepcopy
#import matplotlib.pyplot as plt
np.set_printoptions(threshold=np.inf, precision=8, suppress=True, floatmode='maxprec')



class vcopt:
    def __init__(self):
        pass
    def __del__(self):
        pass
    
    #setting 1
    def setting_1(self, para_range, score_func, aim, show_pool_func, seed):
        self.para_range = para_range # para_rangeはそのままの形式で用いる
        self.para_num = len(para_range)
        self.score_func = score_func
        self.aim = aim
        self.show_pool_func = show_pool_func
        self.seed = seed
        nr.seed(self.seed)
        self.start = time.time()
    
    #setting 2
    def setting_2(self, pool_num, parent_num, child_num):
        self.pool_num = pool_num
        self.parent_num = parent_num
        self.child_num = child_num
        self.family_num = parent_num + child_num
    
    #setting 3
    def setting_3(self, dtype):
        self.pool, self.pool_score = np.zeros((self.pool_num, self.para_num), dtype=dtype), np.zeros(self.pool_num)
        self.parent, self.parent_score = np.zeros((self.parent_num, self.para_num), dtype=dtype), np.zeros(self.parent_num)
        self.child, self.child_score = np.zeros((self.child_num, self.para_num), dtype=dtype), np.zeros(self.child_num)
        self.family, self.family_score = np.zeros((self.family_num, self.para_num), dtype=dtype), np.zeros(self.child_num)

    #score pool
    def score_pool(self):        
        for i in range(self.pool_num):
            self.pool_score[i] = self.score_func(self.para_range[self.pool[i]])
    def score_pool_dc(self):
        for i in range(self.pool_num):
            para = []
            for j in range(self.para_num):
                para.append(self.para_range[j][self.pool[i, j]])
            para = np.array(para)
            self.pool_score[i] = self.score_func(para)
    def score_pool_rc(self):        
        for i in range(self.pool_num):
            self.pool_score[i] = self.score_func(self.pool[i])
    
    #score child
    def score_child(self):        
        for i in range(self.child_num):
            self.child_score[i] = self.score_func(self.para_range[self.child[i]])
    def score_child_dc(self):        
        for i in range(self.child_num):
            para = []
            for j in range(self.para_num):
                para.append(self.para_range[j][self.child[i, j]])
            para = np.array(para)
            self.child_score[i] = self.score_func(para)
    def score_child_rc(self):        
        for i in range(self.child_num):
            self.child_score[i] = self.score_func(self.child[i])
    
    #save best and mean
    def save_best_mean(self):
        #best
        self.best_index = np.argmin(np.abs(self.aim - self.pool_score))
        #save
        self.pool_best = deepcopy(self.pool[self.best_index])
        self.pool_score_best = deepcopy(self.pool_score[self.best_index])
        
        #mean
        self.pool_score_mean = np.mean(self.pool_score)
        self.mean_gap = np.mean(np.abs(self.aim - self.pool_score))
        #save
        self.pool_score_mean_save = deepcopy(self.pool_score_mean)
        self.mean_gap_save = deepcopy(self.mean_gap)

    #make parent
    def make_parent(self, it):
        self.pool_select = it
        self.parent = self.pool[self.pool_select]
        self.parent_score = self.pool_score[self.pool_select]

    #make family
    def make_family(self):
        self.family = np.vstack((self.child, self.parent))
        self.family_score = np.hstack((self.child_score, self.parent_score))
    
    #JGG
    def JGG(self):
        #np.argpartition(-array, K)[:K] returns max K index
        #np.argpartition(array, K)[:K] returns min K index
        self.family_select = np.argpartition(np.abs(self.aim - self.family_score), self.parent_num)[:self.parent_num]
        #return to pool
        self.pool[self.pool_select] = self.family[self.family_select]
        self.pool_score[self.pool_select] = self.family_score[self.family_select]

    #end check
    def end_check(self):
        self.mean_gap = np.mean(np.abs(self.aim - self.pool_score))
        if self.mean_gap < self.mean_gap_save:
            return False
        else:
            return True
        
    def show_pool(self, n):
        info = {'gen':n, 'best_index':self.best_index,\
                'best_score':round(self.pool_score_best, 4),\
                'mean_score':round(self.pool_score_mean, 4),\
                'mean_gap':round(self.mean_gap, 4),\
                'time':round(time.time() - self.start, 2)}
        self.show_pool_func(self.para_range[self.pool], **info)
    def show_pool_dc(self, n):
        info = {'gen':n, 'best_index':self.best_index,\
                'best_score':round(self.pool_score_best, 4),\
                'mean_score':round(self.pool_score_mean, 4),\
                'mean_gap':round(self.mean_gap, 4),\
                'time':round(time.time() - self.start, 2)}
        pool = []
        for i in range(self.pool_num):
            para = []
            for j in range(self.para_num):
                para.append(self.para_range[j][self.pool[i, j]])
            pool.append(para)
        pool = np.array(pool)
        self.show_pool_func(pool, **info)
    def show_pool_rc(self, n):
        info = {'gen':n, 'best_index':self.best_index,\
                'best_score':round(self.pool_score_best, 4),\
                'mean_score':round(self.pool_score_mean, 4),\
                'mean_gap':round(self.mean_gap, 4),\
                'time':round(time.time() - self.start, 2)}
        self.show_pool_func(self.pool, **info)
    '''
    #print bar
    def print_bar(self, n):
        n0 = int(20*n/(self.maxgen+1)) + 1
        n1 = 20 - n0
        t = time.time() - self.start
        bar = '\r{}% [{}{}] time:{}s gen:{}  φ(□　□;)'.format(str((n*100//self.maxgen)).rjust(3), '#'*n0, ' '*n1, np.round(t, 1), n)
        print(bar, end='')
        #print(bar)
        

    
    #print bar final
    def print_bar_final(self, n):
        n0 = int(20*n/(self.maxgen+1)) + 1
        n1 = 20 - n0
        t = time.time() - self.start
        bar = '\r{}% [{}{}] time:{}s gen:{}  φ(□　□*)!!'.format(str((n*100//self.maxgen)).rjust(3), '#'*n0, ' '*n1, np.round(t, 1), n)
        #print(bar, end='')
        print(bar)
    '''
    
    #2-opt
    def opt2(self, para, score_func, aim, show_para_func=None, seed=None, step_max=float('inf')):
        #
        para, score = np.array(para), score_func(para)
        kwargs = {}
        if seed != 'pass': nr.seed(seed)
        step = 0
        #
        if show_para_func != None:
            kwargs.update({'step_num':step, 'score':round(score, 3)})
            show_para_func(para, **kwargs)
        #opt
        while 1:
            update = False
            if step >= step_max:
                #print('stop')
                break
            
            i_set = np.arange(0, len(para)-1)
            nr.shuffle(i_set)
            for i in i_set:
                #continue check
                if update == True: break
                
                j_set = np.arange(i + 1, len(para))
                nr.shuffle(j_set)
                for j in j_set:
                    #continue check
                    if update == True: break
                    
                    #try
                    para_tmp = np.hstack((para[:i], para[i:j+1][::-1], para[j+1:]))
                    score_tmp = score_func(para_tmp)
                    
                    #check and update
                    if np.abs(aim - score_tmp) < np.abs(aim - score):
                        para, score = para_tmp, score_tmp
                        step += 1
                        if show_para_func != None:
                            kwargs.update({'step_num':step, 'score':round(score, 3)})
                            show_para_func(para, **kwargs)
                        update = True
            if update == False:
                #print('end')
                break
        return para, score

    #2-opt for tspGA()
    def opt2_tspGA(self, para, score, step_max=float('inf')):
        #
        para, score = para, score
        step = 0
        #opt
        while 1:
            update = False
            if step >= step_max:
                break
            
            i_set = np.arange(0, self.para_num - 1)
            nr.shuffle(i_set)
            for i in i_set:
                #continue check
                if update == True: break
                
                j_set = np.arange(i + 1, self.para_num)
                nr.shuffle(j_set)
                for j in j_set:
                    #continue check
                    if update == True: break
                    
                    #try
                    para_tmp = np.hstack((para[:i], para[i:j+1][::-1], para[j+1:]))
                    score_tmp = self.score_func(self.para_range[para_tmp])
                    
                    #check and update
                    if np.abs(self.aim - score_tmp) < np.abs(self.aim - score):
                        para, score = para_tmp, score_tmp
                        step += 1
                        update = True
            if update == False:
                #print('end')
                break
        return para, score



    #######################################################################################################################
    #######################################################################################################################
    def tspGA(self, para_range, score_func, aim, show_pool_func=None, seed=None, pool_num=None):
        #setting
        self.setting_1(para_range, score_func, aim, show_pool_func, seed)
        self.setting_2(self.para_num*10, 2, 2)
        if pool_num != None: self.setting_2(pool_num, 2, 2)
        self.setting_3(int)
        
        #specific para
        self.para_index = np.arange(self.para_num)
        self.opt2_num = 1
        
        #gen 1 pool
        for i in range(self.pool_num):
            self.pool[i] = deepcopy(self.para_index)
            nr.shuffle(self.pool[i])
        
        #mini 2-opt
        for i in range(self.pool_num):
            self.pool[i], self.pool_score[i] = self.opt2_tspGA(self.pool[i], self.pool_score[i], step_max=self.opt2_num)
        
        #
        self.score_pool()
        self.save_best_mean()
        
        #show
        if self.show_pool_func != None:
            self.show_pool(0)
        
        #gen 2-
        count = 0
        for n in range(1, 1000000 + 1):
            #
            self.opt2_num = n // 10
            
            #iteration
            iteration = np.arange(self.pool_num)
            nr.shuffle(iteration)
            iteration = iteration.reshape((self.pool_num//self.parent_num), self.parent_num)
            for it in iteration:
                #
                self.make_parent(it)
            
                #辺に着目したヒュリスティック操作
                #==============================================================
                #ex_parent
                self.ex_parent = np.hstack((self.parent[:, -2:].reshape(self.parent_num, 2), self.parent, self.parent[:, :2].reshape(self.parent_num, 2)))
                
                #child
                for i in range(self.child_num):
                    #first para
                    s = self.parent[nr.randint(self.parent_num), 0]
                    if nr.rand() < (1.0 / self.para_num):
                        s = nr.choice(self.para_index)
                    self.child[i, 0] = s
                    #following para
                    for j in range(1, self.para_num):
                        
                        mask_1 = np.zeros((self.parent_num, self.para_num + 4), dtype=bool)
                        mask_2 = np.zeros((self.parent_num, self.para_num + 4), dtype=bool)
                        
                        mask_1[:, 1:-3] += (self.parent == s)
                        mask_1[:, 3:-1] += (self.parent == s)
                        mask_2[:, 0:-4] += (self.parent == s)
                        mask_2[:, 4:] += (self.parent == s)
                        
                        #p
                        p = np.ones(self.para_num) * (1.0 / self.para_num)
                        for k in self.ex_parent[mask_1]:
                            p[np.where(self.para_index==k)[0]] += 1.0 / self.parent_num
                        for k in self.ex_parent[mask_2]:
                            p[np.where(self.para_index==k)[0]] += 0.1 / self.parent_num
                        
                        #mask passed para
                        for k in self.child[i, 0:j]:
                            p[np.where(self.para_index==k)[0]] = 0.0
                        #print(p)
                        #choice
                        p *= 1.0 / np.sum(p)
                        s = nr.choice(self.para_index, p=p)
                        #child
                        self.child[i, j] = s
                #==============================================================
                #
                self.score_child()
                self.make_family()
                
                #mini 2-opt
                for i in range(self.family_num):
                    self.family[i], self.family_score[i] = self.opt2_tspGA(self.family[i], self.family_score[i], step_max=self.opt2_num)
                
                self.JGG()
            
            #end check
            if self.end_check():
                count += 1
            if count >= 1:
                break
            
            self.save_best_mean()
            
            #show
            if self.show_pool_func != None:
                self.show_pool(n * self.pool_num)
        
        return self.para_range[self.pool_best], self.pool_score_best
    
    
    
    
    #==============================================================#==============================================================
    #==============================================================#==============================================================
    def dcGA(self, para_range, score_func, aim, show_pool_func=None, seed=None, pool_num=None):
        #setting
        self.setting_1(para_range, score_func, aim, show_pool_func, seed)
        self.setting_2(self.para_num*10, 2, 8)
        if pool_num != None: self.setting_2(pool_num, 2, 8)
        self.setting_3(int)
        
        #specific para
        self.para_index = []
        for i in range(self.para_num):
            self.para_index.append(np.arange(len(self.para_range[i])))
        self.choice = np.array([[0,0,1],[0,1,0],[0,1,1],[1,0,0],[1,0,1],[1,1,0]], dtype=int)
        
        #gen 1 pool
        for i in range(self.pool_num):
            for j in range(self.para_num):
                self.pool[i, j] = nr.choice(self.para_index[j])
        
        #
        self.score_pool_dc()
        self.save_best_mean()
        
        #show
        if self.show_pool_func != None:
            self.show_pool_dc(0)

        #gen 2-
        count = 0
        for n in range(1, 1000000 + 1):
            #
            #iteration
            iteration = np.arange(self.pool_num)
            nr.shuffle(iteration)
            iteration = iteration.reshape((self.pool_num//self.parent_num), self.parent_num)
            for it in iteration:
                #
                self.make_parent(it)            
            
                #2-point cross
                #==============================================================
                #cross point
                cross_point = nr.choice(range(1, self.para_num), 2, replace=False)
                if cross_point[0] > cross_point[1]:
                    cross_point[0], cross_point[1] = cross_point[1], cross_point[0]
                #child
                for i in range(len(self.choice)):
                    self.child[i] = np.hstack((self.parent[self.choice[i, 0], :cross_point[0]],
                                               self.parent[self.choice[i, 1], cross_point[0]:cross_point[1]],
                                               self.parent[self.choice[i, 2], cross_point[1]:]))
                #==============================================================
                #uniform cross
                #==============================================================
                #child
                for i in [6, 7]:
                    mask = nr.randint(0, 2, self.para_num)
                    self.child[i][mask==0] = self.parent[0][mask==0]
                    self.child[i][mask==1] = self.parent[1][mask==1]
                #==============================================================
                #mutation
                #==============================================================
                for ch in self.child:
                    for j in range(self.para_num):
                        if nr.rand() < (1.0 / self.para_num):
                            ch[j] = nr.choice(self.para_index[j])
                #==============================================================
                #
                self.score_child_dc()
                self.make_family()
                self.JGG()
            
            #end check
            if self.end_check():
                count += 1
            if count >= 1:
                break
            
            self.save_best_mean()
            
            #show
            if self.show_pool_func != None:
                self.show_pool_dc(n * self.pool_num)
        
        para = []
        for j in range(self.para_num):
            para.append(self.para_range[j][self.pool[self.best_index, j]])
        para = np.array(para)
             
        return para, self.pool_score_best
        
        

    #==============================================================#==============================================================
    #==============================================================#==============================================================
    def setGA(self, para_range, set_num, score_func, aim, show_pool_func=None, seed=None, pool_num=None):
        #setting
        self.setting_1(para_range, score_func, aim, show_pool_func, seed)
        #specific para
        self.para_range = np.array(para_range) # para_rangeはnp形式で用いる
        self.set_num = set_num
        self.para_num = self.set_num
        #
        self.setting_2(self.para_num*10, 2, 4)
        if pool_num != None: self.setting_2(pool_num, 2, 4)
        self.setting_3(int)
        
        #specific para
        self.para_index = np.arange(len(self.para_range))
        
        #gen 1 pool
        for i in range(self.pool_num):
            self.pool[i] = nr.choice(self.para_index, self.set_num, replace=False)
            self.pool[i] = np.sort(self.pool[i])
        
        #
        self.score_pool()
        self.save_best_mean()
        
        #show
        if self.show_pool_func != None:
            self.show_pool(0)

        #gen 2-
        count = 0
        for n in range(1, 1000000 + 1):
            #
            #iteration
            iteration = np.arange(self.pool_num)
            nr.shuffle(iteration)
            iteration = iteration.reshape((self.pool_num//self.parent_num), self.parent_num)
            for it in iteration:
                #
                self.make_parent(it)            
            
                #subtour exchange cross
                #==============================================================
                #common part
                common_part = set(self.parent[0]) & set(self.parent[1])
                #rand index
                rand_index = set(self.para_index) - common_part
                #child
                for i in range(len(self.child)):
                    rand_part = nr.choice(np.array(list(rand_index)), self.set_num - len(common_part), replace=False)

                    self.child[i, :len(common_part)] = np.array(list(common_part))
                    self.child[i, len(common_part):] = rand_part
                    
                    self.child[i] = np.sort(self.child[i])
                #mutation
                #==============================================================
                for ch in self.child[2:]:
                    for j in range(self.set_num):
                        if nr.rand() < (1.0 / self.set_num):
                            akak = nr.choice(self.para_index)
                            if akak not in ch:
                                ch[j] = akak
                #==============================================================
                #
                self.score_child()
                self.make_family()
                self.JGG()
            
            #end check
            if self.end_check():
                count += 1
            if count >= 1:
                break
            
            self.save_best_mean()
            
            #show
            if self.show_pool_func != None:
                self.show_pool(n * self.pool_num)
             
        return self.para_range[self.pool_best], self.pool_score_best



        
    #==============================================================#==============================================================
    #==============================================================#==============================================================
    def rcGA(self, para_range, score_func, aim, show_pool_func=None, seed=None, pool_num=None):
        #setting
        self.setting_1(para_range, score_func, aim, show_pool_func, seed)
        self.setting_2(self.para_num*10, self.para_num*1, self.para_num*10)
        if pool_num != None: self.setting_2(pool_num, self.para_num*1, self.para_num*10)
        self.setting_3(float)
        
        #specific para
        self.sd = 1.0*0.9 / math.sqrt(self.parent_num)
        
        #gen 1 pool
        for j in range(self.para_num):
            self.pool[:, j] = nr.rand(self.pool_num) * (self.para_range[j, 1] - self.para_range[j, 0]) + self.para_range[j, 0]
        
        #
        self.score_pool_rc()
        self.save_best_mean()
        
        #show
        if self.show_pool_func != None:
            self.show_pool_rc(0)
        
        #gen 2-
        count = 0
        for n in range(1, 1000000 + 1):
            #
            #iteration
            iteration = np.arange(self.pool_num)
            nr.shuffle(iteration)
            iteration = iteration.reshape((self.pool_num//self.parent_num), self.parent_num)
            for it in iteration:
                #
                self.make_parent(it)            

                #REX
                #==============================================================
                #parant average
                ave = np.mean(self.parent, axis=0)
                #child
                self.child[:, :] = float('inf')
                for i in range(self.child_num):
                    for j in range(self.para_num):
                        while self.child[i, j] < self.para_range[j, 0] or self.para_range[j, 1] < self.child[i, j]:
                            #average
                            self.child[i, j] = ave[j]
                            #perturbation
                            for k in range(self.parent_num):
                                self.child[i, j] += nr.normal(0, self.sd) * (self.parent[k][j] - ave[j])
                #==============================================================
                #
                self.score_child_rc()
                self.make_family()
                self.JGG()
            
            #end check
            if np.max(np.std(self.pool, axis=0) / (self.para_range[:, 1] - self.para_range[:, 0])) < 0.001:
                count += 1
            if count >= 1:
                break
            
            self.save_best_mean()
            
            #show
            if self.show_pool_func != None:
                self.show_pool_rc(n * self.pool_num)

        return self.pool_best, self.pool_score_best
    
    






if __name__ == '__main__':
    pass
