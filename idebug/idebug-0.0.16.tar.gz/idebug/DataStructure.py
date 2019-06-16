
import inspect
import pprint
pp = pprint.PrettyPrinter(indent=2)
import pandas as pd
import copy
import json
import sys

#============================================================
# df
#============================================================

def dframe(_df, title='_None', invisible_cols=['_id']):
    print(f"\n{'*'*60}\n Debug dataframe : {title}\n")
    df = _df.copy()
    print(f"\n df.info() :\n")
    pp.pprint(df.info())

    cols = list(df.columns)
    visible_cols = [e for e in cols if e not in invisible_cols]
    df = df.reindex(columns=visible_cols)
    print(f"\n df :\n\n{df}\n")

def eachcolumn_unqvalue_count(df, grouping_impossible_cols=['_id'], shown_glen=10):
    print(f"\n{'='*60} 컬럼별 유일한 자료개수\n")
    # 그루핑할 필요없는 id 또는 그루핑시 무시되는 None값에 대한 예외처리.
    cols = list(df.columns)
    cols = [col for col in cols if col not in grouping_impossible_cols]
    print(f"\n grouping_possible_cols : {cols}\n")
    df = df.reindex(columns=cols)
    df = df.fillna('_None')
    for col in cols:
        df1 = df.reindex(columns=[col])
        df1 = df1.assign(seq= True)
        gr = df1.groupby(col).count().sort_values(by='seq', ascending=False)
        if len(gr) > shown_glen:
            print(f"\n grouped_len : {len(gr)}")
        else:
            print(f"\n grouped :\n\n{gr}")

def cols_dtype(df):
    print(f"\n{'='*60} 첫번째 문서의 컬럼별 데이터타입\n")
    df.index = range(len(df))
    dic = df.loc[:1, ].to_dict('records')[0]
    cols = list(dic.keys())
    df_grouping_possible_cols = []
    for col in cols:
        TF = inspect_data(col, dic[col])
        if TF is True: df_grouping_possible_cols.append(col)
    return df_grouping_possible_cols

#============================================================
# class, function
#============================================================

def obj(object, title='_None', selective=True):
    print(f"\n dir(object) :\n {dir(object)}")
    print(f"\n object.__module__ : {object.__module__}")
    print(f"\n object.__class__ : {object.__class__}")
    print(f"\n object.__class__.__name__ : {object.__class__.__name__}")
    print(f"\n object.__doc__ : {object.__doc__}")
    print(f"\n{'*'*60}\n Debug object : {object.__class__} | {title}\n")
    if '__dict__' in dir(object):
        for attr, value in object.__dict__.items():
            print(f"{'-'*60}\n {attr} : {value}")

#============================================================
# list, dict, tuple, set
#============================================================

def docs(obj):
    print(f"\n{'*'*60}\n Debug docs : {obj.__class__}\n")

    print(f"\n obj.docs :\n")
    pp.pprint(obj.docs)

    print(f"\n obj.docs.brief :")
    print(f"\n len(obj.docs): {len(obj.docs)}")
    df = obj.get_df()
    print(f"\n obj.docs.cols : {df.columns}\n")

def dics(dics, title='_None'):
    print(f"\n{'*'*60}\n Debug dics : {title}\n")
    pp.pprint(dics)
    if isinstance(dics, list):
        print(f"\n len(dics) : {len(dics)}\n")

def dic(d, title='_None', invisibles=[]):
    print(f"\n{'*'*60}\n Debug dic : {title}\n")
    if isinstance(d, dict):
        _d = d.copy()
        for key in invisibles:
            del(_d[key])
        pp.pprint(_d)

        dics = []
        for k, v in d.items():
            dics.append({'key':k, 'type(v)':type(v), 'getsizeof(v)':sys.getsizeof(v)})
            #print(f"\n key : {k}")
            #print(f" type(v) : {type(v)}")
            #print(f" getsizeof(v) : {sys.getsizeof(v)}")
        df = pd.DataFrame(dics).reindex(columns=['key','type(v)','getsizeof(v)']).sort_values('key')
        dframe(df, '사전의 성분조사')
    else:
        print('\n 입력이 사전타입이 아니다.\n')

def _dic_example():
    dic = {'k1':[1,2,3], 'k2':{'k21':'이런', 'k22':'니미'}, 'k3':'씨발좃도', 'k4':'', 'k5':None}
    key_li = dic.keys()
    for k in key_li:
        print('-'*60+'키:{}'.format(k))
        print(type(v))
        print(len(v))

def li(_li, title='_None', shown_cnt=20):
    print(f"\n{'*'*60}\n Debug list : {title} | shown_cnt : {shown_cnt}\n")
    li = copy.copy(_li)
    print(f"\n len(li) : {len(li)}")
    li = li[:shown_cnt]
    print("\n li :\n")
    pp.pprint(sorted(li))

def json(js, caller='caller'):
    js_ = js
    if type(js_) is dict: pp.pprint({'sorted(js_.keys())':sorted(js_.keys())})
    elif type(js_) is list: pp.pprint({'len(js_)':len(js_)})
    else: pp.pprint({'type(js_)':type(js_)})
