# -*- coding:utf-8 -*-

__author__ = 'denishuang'

import pandas as pd
import numpy as np
from sklearn import tree, ensemble, model_selection


class BaseForcaster(object):
    def __init__(self, dimensions=None, field_map={}, exclude=[]):
        self.id_field = field_map.get('id', 'id')
        self.value_field = field_map.get('value', 'value')
        self.exclude = exclude + [self.id_field, self.value_field]
        self.predict_field = field_map.get('predict_value', 'predict_value')
        self.dimensions = dimensions

        # self.normalize()

    # def split_train_test(self):
    #     df = self.data
    #     # X, X_test, Y, Y_test = model_selection.train_test_split(df[self.dimensions], df[self.value_field], test_size=self.test_rate, random_state=1)
    #     df['set'] = [(g < self.train_rate and 'train' or 'test') for g in df['group']]
    #     # df['set'] = [(g < 53608 and 'test' or 'train') for g in range(len(df))]
    #     return df[df['set'] == 'train'], df[df['set'] == 'test']

    def detect_dimensions(self, df):
        if not self.dimensions:
            self.dimensions = [c for c in df.columns if c not in self.exclude and df[c].dtype != np.dtype('<M8[ns]')]

    def normalize(self, df):
        self.detect_dimensions(df)
        return df.fillna(0)
        # df['group'] = df[self.id_field] % 10

    def train(self, df, Y=None):
        raise Exception("unimplemented!")

    def predict(self, df):
        raise Exception("unimplemented!")

    def performance(self, df):
        return df[['set', 'group', self.value_field, self.predict_field]].groupby(['set', 'group']).sum()

    def run(self):
        self.train()
        return self.performance(self.predict(self.data))


class DecisionTreeForcaster(BaseForcaster):
    def __init__(self, **kwargs):
        super(DecisionTreeForcaster, self).__init__(**kwargs)
        self.tree = tree.DecisionTreeRegressor()

    def normalize(self, df):
        df = super(DecisionTreeForcaster, self).normalize(df)
        cats = {}
        for d in self.dimensions:
            if df[d].dtype == 'object':
                cc = pd.Categorical(df[d])
                cats[d] = cc.categories
                df[d] = cc.codes
        self.categories = cats
        return df

    def train(self, df, Y=None):
        if Y is None:
            Y = df[self.value_field]
            X = df[self.dimensions]
        else:
            X = df
        self.tree.fit(X, Y)

    def predict(self, df, need_categorical=False, predict_field=None):
        if need_categorical:
            df.fillna(0, inplace=True)
            for d in self.dimensions:
                if df[d].dtype == 'object':
                    cc = pd.Categorical(df[d], self.categories.get(d))
                    df[d] = cc.codes
        df[predict_field or self.predict_field] = self.tree.predict(df[self.dimensions])
        return df

    def export_graph(self, out_file):
        dot_data = tree.export_graphviz(self.tree, out_file=out_file)
        return dot_data

    def show_tree(self, dot_data):
        import pydotplus
        from IPython.display import Image
        graph = pydotplus.graph_from_dot_data(dot_data)
        Image(graph.create_png())


class DecisionTreeClassifier(DecisionTreeForcaster):
    def __init__(self, data, **kwargs):
        super(DecisionTreeForcaster, self).__init__(data, **kwargs)
        self.tree = tree.DecisionTreeClassifier(max_depth=4, max_leaf_nodes=100)

    def normalize(self):
        super(DecisionTreeClassifier, self).normalize()
        df = self.data
        df[self.value_field] = pd.Categorical(df[self.value_field]).codes


class GradientBoostingForcaster(DecisionTreeForcaster):
    def __init__(self, data, **kwargs):
        super(DecisionTreeForcaster, self).__init__(data, **kwargs)
        self.tree = ensemble.GradientBoostingRegressor(n_estimators=200, loss='ls')

# class Forcaster(object):
#     def __init__(self, data, dimensions=None, train_rate=5, field_map={}):
#         self.data = data
#         self.data.rename(columns=field_map, inplace=True)
#         self.dimensions = dimensions or [c for c in data.columns if c not in STATIC_FIELDS]
#         self.train_rate = train_rate
#         self.normalize()
#         self.dimension_values = {}
#         self.train_set, self.test_set = self.split_train_test()
#         self.base_corr = 0
#         self.base_value = 0
#
#     def split_train_test(self):
#         df = self.data
#         return df[df['gid'] < 5], df[df['gid'] >= 5]
#
#     def normalize(self):
#         df = self.data
#         df['value'].fillna(0, inplace=True)
#         df['reg_count'] = 1
#         df['gid'] = df['id'] % 10
#         df['paid'] = df['value'].apply(lambda x: x > 0 and 1 or 0)
#         for d in self.dimensions:
#             df[d] = df[d].astype(object)
#
#     def cal_reg_pament(self, df):
#         return (df['value'] / df['reg_count']).agg('average')
#
#     def cal_corr(self, df):
#         return df.corr().iloc[0, 1]
#
#     def train(self):
#         df = self.train_set
#         dimensions = self.dimensions
#         m = self.dimension_values
#         gsum = df[['gid', 'reg_count', 'value']].groupby('gid').sum()
#         self.base_corr = self.cal_corr(gsum)
#         if self.base_corr < 0:
#             self.base_corr = 0
#         self.base_value = self.cal_reg_pament(gsum)
#         for d in dimensions:
#             r = df[[d, 'gid', 'reg_count', 'value', 'paid']].groupby([d, 'gid']).sum()
#             for a in r.index.levels[0]:
#                 b = r.loc[a]
#                 corr = self.cal_corr(b)
#                 if corr <= 0 or np.isnan(corr):
#                     continue
#                 m["%s:%s" % (d, a)] = dict(
#                     reg_payment=self.cal_reg_pament(b),
#                     corr=corr,
#                     groups=len(b),
#                     reg_count=b['reg_count'].sum(),
#                     pay_count=b['paid'].sum()
#                 )
#                 # print d, a
#         return m
#
#     def predict_object(self, obj):
#         tc = self.base_corr
#         a = 0
#         facts = []
#         fs = [('base', self.base_value, self.base_corr)]
#         for d in self.dimensions:
#             k = '%s:%s' % (d, obj[d])
#             vs = self.dimension_values.get(k)
#             if vs:
#                 corr = vs.get('corr')
#                 val = vs.get('reg_payment')
#                 fs.append((k, val, corr))
#                 tc += corr
#         if tc == 0:
#             tc = 1
#             fs = [('base', self.base_value, 1)]
#         for d, v, c in fs:
#             w = c / tc
#             f = v * w
#             a += f
#             facts.append("%s %.2f*%.2f=%.2f" % (d, v, w, f))
#         return a, obj.id, ' | '.join(facts)
#
#     def predict(self, df):
#         return pd.DataFrame(
#             [(row.gid, self.predict_object(row)[0], row.value) for index, row in df.iterrows()],
#             columns=['gid', 'predict', 'actual'])
#
#     def score(self, result):
#         d1 = result.sum()
#         d2 = result.groupby('gid').sum()
#         return d1['predict'] / d1['actual'], d2['predict'] / d2['actual']
#
#     def fit(self):
#         self.train()
#         print 'train:', self.score(self.predict(self.train_set))
#         print 'test:', self.score(self.predict(self.test_set))
#
#     def sample(self, size=10):
#         ds = [self.predict_object(row) for index, row in self.test_set.iterrows()]
#         ds.sort(reverse=True)
#         l = len(ds)
#
#         def output(start):
#             print "\n##############", start, "###########\n"
#             for p, id, s in ds[start:start + size]:
#                 print "%.2f" % p, id, s
#
#         output(0)
#         output(l / 2)
#         output(l - size)
#
#
# def tree_fit(data, rate=2, exclude=[]):
#     a = len(data) / 2
#     dt = data  # data[dims]
#     for d in exclude:
#         dt = dt.drop(d, 1)
#     dt = dt.fillna(0)
#     cats = {}
#     for d in dt.columns:
#         if dt[d].dtype == 'object':
#             cc = pd.Categorical(dt[d])
#             cats[d] = cc.categories
#             dt[d] = cc.codes
#     train = dt[dt[u'资源编号'] % rate != 0]
#     test = dt[dt[u'资源编号'] % rate == 0]
#     Y = train[u'成单金额'].fillna(0)
#     YT = test[u'成单金额'].fillna(0)
#     X = train
#     X = X.drop(u'资源编号', 1).drop(u'成单金额', 1)
#     test = test.drop(u'资源编号', 1).drop(u'成单金额', 1)
#     mode = tree.DecisionTreeRegressor()
#     mode.fit(X, Y)
#     r = mode.predict(test)
#     return r, YT, test, cats
#
#
# def csv_correlation(fname):
#     return pd.read_csv(fname).corr().iloc[0, 1]
