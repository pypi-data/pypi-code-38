#-*- coding: utf-8 -*-
import basis as b
from scipy.sparse import coo_matrix, eye
import numpy as np
import copy
from math import factorial as fact

class A():

    def __init__(self, mc, n_max, Ud, Vcd, gamma_bd, ec, eb, mu, delta = 1.0, calc = False):
        '''
        Ud - кулоновское отталкивание на узле,
        Vcd - величина перескока с кластера на фермионную ванну и обратно,
        gamma_bd - величина электрон-фононного взаимодействия,
        ec - узельная энергия электронов на фермионной ванне,
        eb - узельная энергия на бозонной ванне,
        md - число узлов в кластере,
        mc - число узлов в Ферми ванне, 
        mb - число узлов в Бозе ванне,
        n_max - максимум частиц на узле в Бозе ванне
        mu - химический потенциал
        '''
        self.md, self.mc, self.mb, self.n_max = 1, mc, 1, n_max
        self.f_sites = 2 * (self.md + self.mc)
        self.ec = ec
        self.Vcd = Vcd
        self.Ud = Ud
        self.eb = eb
        self.mu = mu
        self.gamma_bd = gamma_bd
        self.delta = delta
        
        self.fb = self.full_basis()
        self.wf = self._make_dict()
        self.comb_n = [b.limit_basis(2, i, self.f_sites // 2) for i in range(self.f_sites + 1)]
        self.cdag_up = self.mtx_comp(self.calc, self.up, 0) # self.md - 1
        self.cdag_down = self.mtx_comp(self.calc_down, self.up, self.f_sites / 2)
        self.bdag = self.mtx_comp(self.calc_bose, self.b_up, self.f_sites)
        self.bm = self.mtx_comp(self.calc_bose, self.b_down, self.f_sites)
        self.nup = self.cdag_up.dot(self.c_up())
        self.ndown = self.cdag_down.dot(self.c_down())
        self._hamiltonian_not_changed_parts()
        if calc:
            self.init_calc()
            
    def init_calc(self):
        self._hamiltonian_changed_parts()
        self.H = self._assemble_hamiltonian()
        self.div_dict = self._divide_h()
        self.div_list = self._make_list()
          
    def full_basis(self):
        '''
        Возвращает базис системы с несохраняющимся числом частиц fb :: array.       
        '''
        fb = []
        # comb_b содержит все сочетания числа фермионов с разными спинами [spin_up, spin_down]
        self.comb_n = [b.limit_basis(2, i, self.f_sites // 2) for i in range(self.f_sites + 1)]
        for state in self.comb_n:
            for inner in state:
                temp_basis = b.full_basis_save(self.md, self.mc, self.mb, inner[1], inner[0], self.n_max)
                for i in temp_basis: # Flatten 2d -> 1d
                    fb.append(i)
        return np.array(fb, dtype=np.int8)
    
    def _make_dict(self):
        '''
        Возвращает словарь словарь собственных функций 
        dict = {wave_function : index in mtx}
        '''
        key = [''.join(map(str, map(int, i))) for i in self.fb]
        value = range(len(key))
        return dict(zip(key, value))
    
    def up(self, number_to_up, func):
        '''
        Ферми оператор рождения.
        Функция возвращает коэффициент и новую волновую функцию
        '''
        function = copy.copy(func)
        if function[number_to_up] == 1:
            return [0,function]
        else:
            coef_up = np.sqrt(function[number_to_up] + 1, dtype=np.float64)
            function[number_to_up] = function[number_to_up] + 1
            return [coef_up, function]

    def down(self, number_to_down, func): 
        '''
        Ферми оператор уничтожения.
        Функция возвращает коэффициент и новую волновую функцию
        '''
        function = copy.copy(func)
        if function[number_to_down] == 0:
            return [0, function]
        else:
            coef_down = np.sqrt(function[number_to_down], dtype=np.float64)
            function[number_to_down] = function[number_to_down] - 1
            return [coef_down, function]

    def b_up(self, number_to_up, function, index):
            '''
            Бозе оператор рождения.
            Функция возвращает коэффициент и индекс
            '''
            if function[number_to_up] == self.n_max:
                return [0, index]
            else:
                coef_up = np.sqrt(function[number_to_up] + 1, dtype=np.float64)
                return [coef_up, (index + (self.n_max + 1) ** (self.f_sites + self.mb - number_to_up - 1))]

    def b_down(self, number_to_down, function, index):
        '''
        Бозе оператор уничтожения.
        Функция возвращает коэффициент и индекс
        '''
        if function[number_to_down] == 0:
            return [0, index]
        else:
            coef_down = np.sqrt(function[number_to_down], dtype=np.float64)
            return [coef_down, (index - (self.n_max + 1) ** (self.f_sites + self.mb - number_to_down - 1))]      

    def sign(self, left_edge, right_edge, func):
        '''Функция определяет знак перескока'''
        left_edge,right_edge = min(left_edge,right_edge), max(left_edge,right_edge)
        if sum(func[left_edge+1:right_edge]) % 2 == 0:
            return 1
        else:
            return -1
   
    def calc(self, n, operator, p):
        '''
        Собирает блок матрицы оператора рождения спин - вверх
        '''
        n_up, n_down = n[0], n[1]

        #  Число состояний 
        R_up = (fact(self.mc + self.md) / fact(n_up) / fact(self.mc + self.md - n_up))
        R_down = (fact(self.mc + self.md) / fact(n_down) / fact(self.mc + self.md - n_down))
        R_bose = (self.n_max + 1)**self.mb   
        for i in range(0, R_bose * R_up * R_down, R_bose * R_down): # Перебираем функции, у которых части со спином вверх отличаются
            coef, function = operator(p, self.fb[i + self.s_out])
            index = self.wf[''.join(map(str, function))]
            if coef != 0:
                self.line[self.s0:self.s0 + R_bose * R_down] = range(i + self.s_out, i + self.s_out + R_bose * R_down)
                self.col[self.s0:self.s0 + R_bose * R_down] = range(index, index + R_bose * R_down)
                self.data[self.s0:self.s0 + R_bose * R_down] = coef * self.sign(p, 0, self.fb[i + self.s_out])
                self.s0 += R_bose * R_down
        self.s_out += R_up * R_down * R_bose
    
    def calc_down(self, n, operator, p):
        ''' Собирает блок матрицы оператора рождения спин - вниз '''
        n_up, n_down = n[0], n[1]

        #  Число состояний 
        R_up = (fact(self.mc + self.md) / fact(n_up) / fact(self.mc + self.md - n_up))
        R_down = (fact(self.mc + self.md) / fact(n_down) / fact(self.mc + self.md - n_down))
        R_bose = (self.n_max + 1)**self.mb
        if self.mc + self.md > n_down:    
            R_down1 = (fact(self.mc + self.md) / fact(n_down + 1) / fact(self.mc + self.md - n_down - 1))          
            for i in range(0, R_bose * R_down, R_bose):
                # перескок с ванны на кластер
                coef, function = operator(p, self.fb[i + self.s_out])
                index = self.wf[''.join(map(str, function))]
                if coef != 0:
                    s0 = self.s0 
                    for T in range(0, R_bose * R_up * R_down, R_bose * R_down): # Т вводится из-за того, что волновые функции с одиноковой частью со спином вниз идут не подряд
                        self.line[s0: s0 + R_bose] = range(i + T + self.s_out, i + T + R_bose + self.s_out)
                        s0 += R_bose
                    for T1 in range(0, R_bose * R_up * R_down1, R_bose * R_down1):
                        self.col[self.s0: self.s0 + R_bose] = range(index + T1,index + T1 + R_bose)
                        self.data[self.s0: self.s0 + R_bose] = coef * self.sign(p, -1, self.fb[i + self.s_out])
                        self.s0 += R_bose 
        self.s_out += R_up * R_down * R_bose
    
     # Бозоны
    def calc_bose(self, n, operator, q):
        ''' Собирает блок матрицы бозе операторов''' 
        n_up, n_down = n[0], n[1]
        R_up = (fact(self.mc + self.md) / fact(n_up) / fact(self.mc + self.md - n_up))
        R_down = (fact(self.mc + self.md) / fact(n_down) / fact(self.mc + self.md - n_down))
        R_bose = (self.n_max + 1)**self.mb
        for i in range(R_bose):
            coef, index = operator(q, self.fb[i + self.s_out], i + self.s_out)
            if coef != 0:
                self.line[self.s0:self.s0+R_up*R_down] = range(i + self.s_out, i + R_up * R_down * R_bose + self.s_out, R_bose)
                self.col[self.s0:self.s0+R_up*R_down] = range(index, index + R_up * R_down * R_bose, R_bose)
                self.data[self.s0:self.s0+R_up*R_down] = coef
                self.s0 += R_up * R_down
        self.s_out += R_up * R_down * R_bose
    
    def mtx_comp(self, func, operator, p):
        '''
        Вычисление матрицы оператора рождения со спином вверх
        '''
        R = self.fb.shape[0]        
        self.line = np.zeros(R)
        self.col = np.zeros(R)
        self.data = np.zeros(R , dtype=np.float64)
        self.s_out = self.s0 = 0 #s_out - сдвиг по блоку, s0 - сдвиг до свободного места в массивах line, col, data
        for i in self.comb_n:
            for j in i:
                func(j, operator, p)
        return coo_matrix((self.data, (self.col, self.line)), shape=(R, R), dtype=np.float64)
    
    def _divide_h(self):
        '''
        Разбивает Гамильтониан системы по числу частиц и по суммарному спину
        --------------
        Returns dict[dict] = mtx
        ------------
        ------------
        Example: 
            blocks[num_of_particle :: str][full_spin :: str] = mtx
            blocks['1']['-0.5'] = ...
        '''
        
        blocks = {}
        R_bose = (self.n_max + 1) ** self.mb
        spin = lambda x: str(0.5 * (x[0] - x[1])) # Helpful function : compute full spin
        s0 = 0
        self.indexes = []
        for block in self.comb_n:
            inner = {}
            for n in block:
                R_up = (fact(self.mc + self.md) / fact(n[0]) / fact(self.mc + self.md - n[0])) # n[0] - spin up; n[1] - spin down
                R_down = (fact(self.mc + self.md) / fact(n[1]) / fact(self.mc + self.md - n[1]))
                inner[spin(n)] = self.get_H()[s0 : s0 + R_up * R_down * R_bose, s0 : s0 + R_up * R_down * R_bose]
                self.indexes.append(np.arange(s0,s0 + R_up * R_down * R_bose))
                s0 += R_up * R_down * R_bose
            blocks[str(sum(n))] = inner
        
        return blocks
    def _hamiltonian_changed_parts(self):
        '''Расчитывает гамильтонову матрицу'''
         #Затравочная энергия фермионной ванны
        self.h1 = sum([self.ec[i] * (self.a_dag_up[i].dot(self.a_up[i]) + self.a_dag_down[i].dot(self.a_down[i])) for i in range(self.mc)])
        #Энергия перескоков с ванны на кластер и обратно
        self.h2 = sum([self.Vcd[i] * (self.cdag_up.dot(self.a_up[i]) + self.a_dag_up[i].dot(self.c_up()) +
                 self.cdag_down.dot(self.a_down[i]) + self.a_dag_down[i].dot(self.c_down())) for i in range(self.mc)])
        #Вклад от хим. потенциала
        self.h6 = -self.mu * (self.n_up() + self.n_down())
         
    def _hamiltonian_not_changed_parts(self):
        '''Расчитывает гамильтонову матрицу'''       
        # Опереторы рождения и уничтожения с кластера на ферми ванну
        self.a_dag_up = [self.mtx_comp(self.calc, self.up, i) for i in range(self.md, self.mc + self.md)]
        self.a_up = [i.transpose() for i in self.a_dag_up]
        self.a_dag_down = [self.mtx_comp(self.calc_down, self.up, i) for i in range(self.mc + 2 * self.md, 2 * (self.mc + self.md))]
        self.a_down = [i.transpose() for i in self.a_dag_down]
        
        #Энергия кулоновского взаимодействия на кластере
        self.h3 = self.Ud * self.n_up().dot(self.n_down())
        #Затравочная энергия бозонной ванны
        self.h4 = self.eb * self.b_dag().dot(self.b())
        #Энергия электрон-фононного взаимодействия
        self.h5 = self.gamma_bd * ((self.b_dag() +  self.b()).dot(self.n_up()  + self.n_down())) -  self.gamma_bd * self.delta * ((self.b_dag() +  self.b()))
        
    
    def _assemble_hamiltonian(self):
        '''Собирает гамильтонову матрицу''' 
        return sum([self.h1, self.h2, self.h3, self.h4, self.h5, self.h6])
    
    def _make_list(self):
        '''Создает список блоков Гамильтоновой матрицы'''
        outer = sorted(map(int, self.div_dict.keys()))
        f = lambda x : sorted(map(float, x))
        return [self.div_dict[str(i)][str(j)] for i in outer for j in f(self.div_dict[str(i)].keys())]
    
    def c_dag_up(self):
        '''Оператор рождения спин - вверх'''
        return self.cdag_up
    
    def n_up(self):
        '''Оператор рождения спин - вверх'''
        return self.nup
    
    def n_down(self):
        '''Оператор рождения спин - вверх'''
        return self.ndown
    
    def c_up(self):
        '''Оператор уничтожения спин - вверх'''
        return self.cdag_up.transpose()
    
    def c_dag_down(self):
        '''Оператор рождения спин - вниз'''
        return self.cdag_down
    
    def c_down(self):
        '''Оператор уничтожения спин - вниз'''
        return self.cdag_down.transpose()
    
    def b_dag(self):
        '''Бозе оператор рождения'''
        return self.bdag
    
    
    def b(self):
        '''Бозе оператор уничтожения'''
        return self.bm
    
    def get_H(self):
        '''Возвращает гамильтонову матрицу'''
        return self.H
    
    def get_dict(self):
        '''Словарь блоков Гамильтоновой матрицы'''
        return self.div_dict
    
    def get_list(self):
        '''Список блоков Гамильтоновой матрицы'''
        return self.div_list
    
    def get_blocks(self):
        '''Список из массивов индексов блоков Гамильтоновой матрицы'''
        return self.indexes
            