
from idebug import *

"""
============================== 성능 ==============================
"""
class LoopReporter:
    def __init__(self, title, len):
        self.title = title
        self.starttime = datetime.now()
        self.count = 1
        self.len = len

    def report(self, period=None):
        if self.count <= self.len:
            cum_runtime = (datetime.now() - self.starttime).total_seconds()
            avg_runtime = cum_runtime / self.count
            expected_total_runtime = avg_runtime * self.len
            expected_remaining_runtime = avg_runtime * (self.len - self.count)

            tpls = [
                ('평균실행시간', avg_runtime),
                ("누적실행시간", cum_runtime),
                ('전체실행시간', expected_total_runtime),
                ('잔여실행시간', expected_remaining_runtime)
            ]
            print('\n\n' + '*'*60)
            print(f"반복명 : {self.title}\n반복횟수현황 : {self.count}/{self.len}")
            for tpl in tpls:
                print_converted_timeunit(title=tpl[0], seconds=tpl[1])
            self.count+=1
            return True


def print_converted_timeunit(title, seconds):
    timeexp, unit = convert_timeunit(seconds)
    print(f"{title} : {timeexp}")


def convert_timeunit(seconds):
    sec = 1
    msec = sec / 1000
    min = sec * 60
    hour = min * 60

    t = seconds
    if t < sec:
        unit = 'msec'
        t = t / msec
    elif sec <= t <= min:
        unit = 'secs'
    elif min < t <= hour:
        unit = 'mins'
        t = t / min
    else:
        unit = 'hrs'
        t = t / hour

    return f"{round(t, 1)}_[{unit}]", unit


def runtimelog(start_t, title):
    import inumber as nmbr
    """
    ===== 사용법 =====
    runtimelog(start_t=start_t, title='')
    """
    t = (datetime.now() - start_t).total_seconds()
    t, unit = nmbr.convert_timeunit(t)
    print('\n {}_시간{} : {}\n'.format(title, unit, t))


def looplog(loopname, rpt_strt_t, rpt_cnt, rpt_len):
    """
    반복_실행시간_보고
    ===== 용어정의 =====
    loopname : 반복대상의 이름
    rpt_strt_t : 반복최초시작시간
    rpt_cnt : 반복수
    rpt_len : 반복길이
    ===== 사용법 =====
    looplog(loopname, rpt_strt_t=XX_rpt_strt_t, rpt_cnt=i, rpt_len=len)
    """
    반복n회_누적실행시간 = (datetime.now() - rpt_strt_t).total_seconds()
    반복1회_평균실행시간 = 반복n회_누적실행시간 / rpt_cnt
    전체반복_예상실행시간 = 반복1회_평균실행시간 * rpt_len
    잔여반복_예상실행시간 = 반복1회_평균실행시간 * (rpt_len - rpt_cnt)
    t0 = 반복1회_평균실행시간
    t1 = 반복n회_누적실행시간
    t2 = 전체반복_예상실행시간
    t3 = 잔여반복_예상실행시간

    d = {}
    for nm, t in zip(['반복1회_평균실행시간', '반복n회_누적실행시간', '전체반복_예상실행시간', '잔여반복_예상실행시간'], [t0, t1, t2, t3]):
        t, unit = inumber.convert_timeunit(t)
        d.update({nm + unit:t})

    print('\n 보고 :\n')
    pp.pprint(d)


def errlog(caller, err, addt_i={}, dbgon=True):
    whoami = whoami(sys.modules[__name__].__file__, inspect.stack()[0][3], dbgon)
    inputs = inputs(inspect.currentframe(), dbgon)
    """
    ===== 사용법 =====
    errlog(caller=inspect.stack()[0][3], err=e, addt_i={})
    """
    inputs['err'] = str(err)
    inputs['발생일시'] = datetime.now()
    inputs.update(addt_i)
    pp.pprint({'\n err_log':inputs})
    db['errlog'].insert_one(document=inputs)
"""
============================== df ==============================
"""
def df_structure(df, col_unq_val=False):
    def cols_dtype(df):
        df.index = range(len(df))
        dic = df.loc[:1, ].to_dict('records')[0]
        cols = list(dic.keys())
        df_grouping_possible_cols = []
        for col in cols:
            TF = inspect_data(col, dic[col])
            if TF is True: df_grouping_possible_cols.append(col)
        return df_grouping_possible_cols

    def cols_groupbycount(df, df_grouping_possible_cols, shown_glen=10):
        start_t = datetime.now()
        # 그루핑할 필요없는 id 또는 그루핑시 무시되는 None값에 대한 예외처리.
        df = df.loc[:, df_grouping_possible_cols]
        df = df.fillna('_None')
        cols = list(df.columns)
        if '_id' in cols: cols.remove('_id')
        print(f"\n cols : {cols}\n")

        l = LoopReporter(title='cols', len=len(cols))
        for col in cols:
            print('\n' + '- '*30 + f"{l.count}/{l.len}")
            df1 = df.loc[:, [col]]
            df1 = df1.assign(seq= True)
            gr = df1.groupby(col).count().sort_values(by='seq', ascending=False)
            if len(gr) > shown_glen: print(f"\n gr_len : {len(gr)}")
            else: print(f"\n grouped :\n\n{gr}")
            l.count+=1

        runtimelog(start_t=start_t, title='')
    """."""
    f = FuncReporter(inspect.currentframe(), True)
    print('\n' + '= '*30 + '개요')
    print(df.info())
    if len(df) is not 0:
        print('\n' + '= '*30 + '첫번째 문서의 컬럼별 데이터타입')
        df_grouping_possible_cols = cols_dtype(df)
        if col_unq_val is True:
            print('\n' + '= '*30 + '컬럼별 유일한 자료개수')
            cols_groupbycount(df, df_grouping_possible_cols)
        print("\n" + "= "*30 + f"df :\n\n{df}")
        f.report()
"""
============================== 자료구조 ==============================
"""
def res(r):
    print(f"\n r : {r}")
    print(f"\n type(r) : {type(r)}")
    print(f"\n dir(r) :\n\n {dir(r)}")
    print(f"\n r.__dir__() :\n\n {r.__dir__()}")
    print(f"\n r.__attrs__ :\n\n {r.__attrs__}")
    print(f"\n r.__dict__ :\n")
    pp.pprint(r.__dict__)

    for attr, value in r.__dict__.items():
        print(f"\n attr : {attr}")
        print(f" type : {type(value)}")
        print(f" bytes : {sys.getsizeof(value)}")
        print(f" value : {value}")
        if attr is 'raw': print(f" r.raw.read() : {value.read()}")
        if attr is 'headers': pp.pprint(dict(value))

    print(f"\n attr : text")
    print(f" type : {type(r.text)}")
    print(f" bytes : {sys.getsizeof(r.text)}")
    print(f" value : {r.text}")


def inspect_data(dataname, data):
    print(f"\n\n dataname : {dataname}")
    print(f" type : {type(data)}")

    # df에서 그루핑이 가능한 데이터타입 일 경우, True 반환.
    if (isinstance(data, list)) or (isinstance(data, tuple)):
        print(f" len : {len(data)}")
        return False
    elif isinstance(data, dict):
        print(f" keys : {data.keys()}")
        return False
    else:
        print(f" value : {data}")
        return True


def tbl_structure(tbl, query=None, projection=None):
    print('\n' + '='*60 + whoami(sys.modules[__name__].__file__, inspect.stack()[0][3]))
    inputs = inputs(inspect.currentframe(), dbgon=True)
    """
    테이블에 대한 자료구조를 확인한다.
    tbl : collection_obj.
    find_one : {'반복1회_평균실행시간_초': 0.003278, '잔여반복_예상실행시간_초': 0.0, '전체반복_예상실행시간_초': 0.003278}
    find.limit : {'반복1회_평균실행시간_초': 0.005471, '잔여반복_예상실행시간_초': 0.0, '전체반복_예상실행시간_초': 0.005471}
    ===== 사용법 =====
    tbl_structure(db=DB, tbl=TBL, query=None, projection=None, dbgon=True)
    """
    start_t = datetime.now()

    #df = mg.find_limit(db=DB, tbl=tbl, query=query, projection=projection, limit_cnt=1, dbgon=dbgon, 컬럼순서li=[], df보고형태='df')
    cursor = tbl.find(filter=None).limit(1)
    df = pd.DataFrame(list(cursor))
    #df = pd.DataFrame(list( db[tbl].find_one(filter=None) ))
    caller = sys.modules[__name__].__file__ + '_:_' + inspect.stack()[0][3]
    funclog(caller=caller, start_t=start_t, addt_i={}, RunTimeout=10)
    df_structure(df)


def dicli(dicli, caller='caller', shown_cnt=10, 검색할key명=None):
    print('\n' + '='*60 + whoami(sys.modules[__name__].__file__, inspect.stack()[0][3]))
    inputs = inputs(inspect.currentframe(), dbgon=True)
    """
    ===== 사용법 =====
    _dicli(dicli, caller=inspect.stack()[0][3], shown_cnt=10, 검색할key명=None)
    """
    dic = dicli[0]
    d_keyli = dic.keys()
    pp.pprint({'dic.keys()':dic.keys()})
    d_keyli_len = len(d_keyli)

    dicli_len = len(dicli)
    i=1
    for d in dicli:
        print('\n' + '-'*60 + '{}/{}'.format(i, dicli_len))
        j=1
        for k in d_keyli:
            print('\n'+'- '*30+'{}/{}'.format(j, d_keyli_len))

            j+=1
        pp.pprint({'d.keys()':d.keys()})
        pp.pprint(d)
        if 검색할key명 is not None:

            pp.pprint(d[검색할key명])
        i+=1


def dic(d, caller='caller', vlen=20):
    whoami = whoami(sys.modules[__name__].__file__, inspect.stack()[0][3], dbgon=True)
    inputs = inputs(inspect.currentframe(), dbgon=True)
    """
    사전에 대한 전반적인 검사
    ===== 사용법 =====
    dic(d, caller)
    ===== 교훈 =====
    pp.pprint({'dic.__name__':dic.__name__})
    AttributeError: 'dict' object has no attribute '__name__'
    """
    if isinstance(d, dict):
        key_li = list(d.keys())
        key_li_len = len(key_li)
        i=1
        for k in key_li:
            print('\n' + '-'*60 + '{}/{}, 키 : {}'.format(i, key_li_len, k))
            if d[k] is None: print('\n if d[k] is None:\n')
            else:
                v = d[k]
                print('\n type(v) : {}'.format(type(v)))
                print('\n len(v) : {}'.format(len(v)))
                if len(v) <= vlen:
                    print('\n v : {}'.format(v))
            i+=1
    else:
        print('\n 입력이 사전타입이 아니다.\n')


def _dic_example():
    dic = {'k1':[1,2,3], 'k2':{'k21':'이런', 'k22':'니미'}, 'k3':'씨발좃도', 'k4':'', 'k5':None}
    key_li = dic.keys()
    for k in key_li:
        print('-'*60+'키:{}'.format(k))
        print(type(v))
        print(len(v))


def li(li, caller='caller', shown_cnt=None):
    print('\n' + '='*60 + whoami(sys.modules[__name__].__file__, inspect.stack()[0][3]))
    inputs = inputs(inspect.currentframe(), dbgon=True)
    """
    리스트에 대한 전반적인 검사
    """

    pp.pprint({'len(li)':len(li)})
    if shown_cnt is not None:
        li = li[:shown_cnt]
    pp.pprint({'li':li})


def json(js, caller='caller'):
    print('\n' + '='*60 + whoami(sys.modules[__name__].__file__, inspect.stack()[0][3]))
    inputs = inputs(inspect.currentframe(), dbgon=True)
    """
    JSON 에 대한 전반적인 검사
    """

    js_ = js
    if type(js_) is dict: pp.pprint({'sorted(js_.keys())':sorted(js_.keys())})
    elif type(js_) is list: pp.pprint({'len(js_)':len(js_)})
    else: pp.pprint({'type(js_)':type(js_)})
"""
============================== 함수실행 디버거 ==============================
"""
class FuncReporter:

    def __init__(self, currentframe, dbgon=False):
        frameinfo = inspect.getframeinfo(frame=currentframe)
        self.filename = frameinfo.filename
        self.function = frameinfo.function
        #inputs = inspect.getargvalues(frame=currentframe).locals
        self.inputs = remove_big_arg(currentframe.f_locals)
        self.starttime = datetime.now()
        self.funcpath = self.filename.replace(".py", f".{self.function}()")
        if dbgon == True:
            print('\n\n' + '='*60 + f"\n{self.funcpath}\n")

    def report(self, RunTimeout=60):
        self.runtime = (datetime.now() - self.starttime).total_seconds()

        print('\n\n' + '~'*60 + f"\n함수실행보고\n{self.funcpath}\n")
        timeexp, unit = convert_timeunit(seconds=self.runtime)
        pp.pprint({
            'StartTime':self.starttime,
            'Runtime':timeexp
        })
        print('>'*60)

        if self.runtime > RunTimeout:
            db['함수실행로그'].insert_one(document=fn)


def funclog(caller, start_t, addt_i={}, RunTimeout=30, dbgon=True):
    whoami = whoami(sys.modules[__name__].__file__, inspect.stack()[0][3], dbgon)
    inputs = inputs(inspect.currentframe(), dbgon)
    """
    주목적 : 함수실행시간 체크.
    - 함수실행시간에 영향을 미치는 입력 파라미터는 무엇인지 나중에 조사하기 위함.

    딕셔너리 값 들 중, 모듈, 클래스 등의 오브젝트는 제거.
    - https://docs.python.org/3/library/functions.html#isinstance
    - https://www.w3schools.com/python/ref_func_isinstance.asp

    ===== 용어정의 =====
    start_t : caller의 시작시간
    RunTimeout : 실행초과시간
    addt_i : 추가정보_dic
    running_t : 함수실행시간

    ===== 사용법 =====
    whoami = whoami(sys.modules[__name__].__file__, inspect.stack()[0][3])
    start_t = datetime.now()
    funclog(caller=whoami, start_t=start_t, addt_i={}, RunTimeout=60)
    """
    # 주목적 : 함수실행시간 체크.
    running_t = (datetime.now() - start_t).total_seconds()
    t, unit = inumber.convert_timeunit(running_t)
    print('\n 함수실행시간{} : {}\n'.format(unit, t))

    # - 함수실행시간에 영향을 미치는 입력 파라미터는 무엇인지 나중에 조사하기 위함.
    del(inputs['addt_i'])
    inputs.update(addt_i)
    inputs.update({'running_t':running_t})

    # 딕셔너리 값 들 중, 모듈, 클래스 등의 오브젝트는 제거.
    inputs_keys = list(inputs.keys())
    for key in inputs_keys:
        if isinstance(inputs[key], str): pass
        elif isinstance(inputs[key], int): pass
        elif isinstance(inputs[key], float): pass
        elif isinstance(inputs[key], list): pass
        elif isinstance(inputs[key], dict): pass
        else: del(inputs[key])

    print('\n 보고 :\n')
    pp.pprint(inputs)

    if running_t > RunTimeout:
        db['함수실행로그'].insert_one(document=inputs)


def funcinit(currentframe):
    """함수가 시작되었음을 알리는 구분선과 입력변수를 프린트."""
    filename = inspect.getframeinfo(frame=currentframe).filename
    inputs = inspect.getargvalues(frame=currentframe).locals
    inputs = remove_big_arg(inputs)
    print('\n' + '='*60 + filename + f"\n\n inputs : {inputs}")
    return {'filename':filename, 'inputs':inputs, 'start_t':datetime.now()}


def funcfin(fn, RunTimeout=60):
    """함수실행시간 체크, 함수실행시간에 영향을 미치는 입력 파라미터는 무엇인지 나중에 조사."""
    runtime = (datetime.now() - fn['start_t']).total_seconds()
    fn.update({'runtime':runtime})

    print('\n 함수실행보고 :\n')
    t, unit = inumber.convert_timeunit(runtime)
    pp.pprint({
        'funcpath':fn['funcpath'],
        'start_t':fn['start_t'],
        f"runtime{unit}":t
    })

    if runtime > RunTimeout:
        db['함수실행로그'].insert_one(document=fn)


def whoami(sys_mod_file, ins_stack, dbgon=False):
    """
    ===== 사용법 =====
    whoami = whoami(sys.modules[__name__].__file__, inspect.stack()[0][3], dbgon)
    """
    whoami = sys_mod_file.replace('/Users/sambong/p/', '').replace('.py', '.' + ins_stack)
    if dbgon == True: print('\n' + '='*60 + whoami)
    return whoami


def inputs(insp_currframe, dbgon=False):
    """
    ===== 사용법 =====
    inputs = inputs(inspect.currentframe(), dbgon)
    """
    inputs = inspect.getargvalues(insp_currframe).locals
    if dbgon == True:
        inputs = remove_big_arg(inputs)
        print('\n 입력변수 :\n')
        pp.pprint(inputs)
        print('\n\n')
    return inputs


def remove_big_arg(inputs, dbgon=False):
    import re
    """
    input_param_중에_list를_포함한_query는_프린트하지않는다
    """
    reg_li = ['^query', 'df|df\d+', '.+li', '^r$', '^whoami', '^soup', '^js']
    inputs_keys = list(inputs.keys())
    elem_li = []

    for reg in reg_li:
        if dbgon == True: print('\n' + '-'*60 + 'reg : {}'.format(reg))
        p = re.compile(pattern=reg)
        for key in inputs_keys:
            m = p.match(string=key)
            if dbgon == True: print('\n m :\n{}'.format(m))
            if m is not None: elem_li.append(key)

    if dbgon == True: print('\n elem_li :\n\n{}'.format(elem_li))

    for key in elem_li:
        if key == 'query':
            v = str(inputs['query'])
            m = re.search(pattern='\$in|\$nin', string=v)
            if dbgon == True: print('\n m :\n{}'.format(m))
            if m is not None: del(inputs['query'])
        else:
            del(inputs[key])

    return inputs
"""
============================== __pymongo ==============================
"""
def UpdateResult(r):
    """
    https://api.mongodb.com/python/current/api/pymongo/results.html#pymongo.results.UpdateResult
    """
    f = FuncReporter(inspect.currentframe(), True)
    print(f"\n\n matched_count : {r.matched_count}\n modified_count : {r.modified_count}\n raw_result : {r.raw_result}\n upserted_id : {r.upserted_id}")


def InsertManyResult(r):
    """
    https://api.mongodb.com/python/current/api/pymongo/results.html#pymongo.results.InsertManyResult
    """
    f = FuncReporter(inspect.currentframe(), True)
    print(f"\n\n acknowledged : {r.acknowledged}\n len(inserted_ids) : {len(r.inserted_ids)}")
"""
============================== 기타 ==============================
"""
def data_size_report():
    print('\n' + '='*60 + whoami(sys.modules[__name__].__file__, inspect.stack()[0][3]))
    from bson.objectid import ObjectId
    """
    data_size_report()
    """
    def PrintDataSize(x):
        pp.pprint({"len(x.encode('utf-8'))":len(x.encode('utf-8'))})
        pp.pprint({"sys.getsizeof(x)":sys.getsizeof(x)})

    print('\n' + '= '*30 + 'string')
    s = '삼성전자'
    PrintDataSize(s)


    print('\n' + '= '*30 + 'datetime')
    date_iso = '2018-09-28'
    PrintDataSize(date_iso)
    print('\n datetime.strptime(~) :')
    date = datetime.strptime(date_iso, '%Y-%m-%d')
    pp.pprint({"sys.getsizeof(date)":sys.getsizeof(date)})


    print('\n' + '= '*30 + 'ObjectId')
    obj_id = '5bb69217dc958f260ea3a1e9'
    PrintDataSize(obj_id)
    obj_id = ObjectId(obj_id)
    print('\n ObjectId(obj_id) :')
    pp.pprint({"sys.getsizeof(obj_id)":sys.getsizeof(obj_id)})


def query_attrs_표시길이제한(query, shown_cnt=10):
    print('\n' + '='*60 + whoami(sys.modules[__name__].__file__, inspect.stack()[0][3]))
    """
    입력값 디버그시에 query 내부 리스트의 길이가 너무 길면 단축 표시한다.
    """

    fake_q = query.copy()
    q_keyli = fake_q.keys()
    q_keyli_len = len(q_keyli)
    i=1
    for k in q_keyli:
        print('\n'+'-'*60)
        if type(k) is list:
            if len(q_keyli(k)) > shown_cnt:
                attr_cut = q_keyli(k)[:shown_cnt]
                attr_len = len(q_keyli(k))
        i+=1
    #return {'attr_cut':attr_cut, 'attr_len':attr_len}
