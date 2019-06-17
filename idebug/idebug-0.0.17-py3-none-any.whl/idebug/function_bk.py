from idebug import *



"""

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
