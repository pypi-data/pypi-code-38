from . import (AError, ATab, ALog, ACollection)
import copy
import time


class Util_Error(AError.Error):
    pass
    

class Util_DuplicateInputChoiceKeyError(Util_Error):
    def __init__(self, key, choices):
        self.key = key
        self.choices = choices

    def __str__(self):
        return 'Duplicate input choice key(%s)' % self.key


class Util_CycleDependsError(Util_Error):
    def __init__(self, lst):
        self.lst = lst

    def __str__(self):
        return 'Cycle depends in: %s' % self.lst


def inputYesNo(title='', defaultValue='yes'):
    """回车返回defaultValue"""
    if defaultValue.lower() in ('y', 'yes'):
        defaultValue = 'yes'
    else:
        defaultValue = 'no'
            
    s = input('%s (yes/no) [%s]: ' % (title, defaultValue))
    if s == '':
        return defaultValue

    if s.lower() in ('y', 'yes'):
        return 'yes'

    return 'no'


def inputChoice(choices, title='', choiceCountPerLine=3):
    """
    choices = [
        ('1', '重新编译', ...), 
        ('2': '编译', ...),
        ...
    ]
    返回选中的choice条目：比如('1', '重新编译', ...)
    """
    def checkChoices():
        map = {}
        for index, item in enumerate(choices):
            key = item[0]
            if key in map:
                raise Util_DuplicateInputChoiceKeyError(key, choices)
            map[key] = index
        return map
        
    indexMap = checkChoices()
    
    while True:
        if title != '':
            print(title)
        
        if title != '':
            lineStart = '  '
        else:
            lineStart = ''

        data = []
        for index, item in enumerate(choices):
            if index % choiceCountPerLine == 0:
                line = []
                data.append(line)
            line.append('%s: %s' % (item[0], item[1]))
        
        # 最后一行补齐
        while len(line) < choiceCountPerLine:
            line.append('')
        
        for line in ATab.spaceTabData(0, data, sameColumnWidth=True).splitlines():
            print(lineStart+line)
        
        s = input('\n请选择> ')
        print('')
        
        if s in indexMap:
            return choices[indexMap[s]]


def test_inputChoice():
    choices = [
        ('1',   '重新编译',  '你选择了Rebuild'),
        ('2',   '编译',      '你选择了Build'),
        ('3',   '清理',      '你选择了Clean'),
        ('4',   '打包',      '你选择了Packing'),
        ('5',   '部署',      '你选择了Deploy'),
    ]
    index = inputChoice(choices, '*** 编译方式 ***')
    print(choices[index][2])


def adjustOrderByDependency(lst, dependDict, asc=True):
    """
    根据依赖字典调整顺序，并返回新的列表（和原列表长度一致，顺序不一致）
    :param lst: 原始列表
    :param dependDict: 依赖关系字典，键为依赖者，值为被依赖者列表
    :param asc: True表示升序（依赖性越低的越靠前），False表示降序（依赖性越低的越靠后）
    """
    depends = copy.deepcopy(dependDict)

    for depender, dependees in depends.items():
        # 被依赖者若不在lst，则从依赖关系中删除
        for dependee in dependees[:]:  # 注意迭代中移除
            if dependee not in lst:
                dependees.remove(dependee)

        # 删除重复的依赖项
        ACollection.listUnique(dependees)

    # 删除依赖项为空的条目
    dependers = list(depends.keys())
    for depender in dependers:
        if len(depends[depender]) == 0:
            del depends[depender]

    def removeDepend(depends, item):
        """把item从依赖者的依赖列表中删除"""
        for k, v in depends.items():
            ACollection.listRemoveAll(v, item)

        # 检查所有的依赖项，删除无依赖的项
        for k in list(depends.keys()):
            if len(depends[k]) == 0:
                depends.pop(k)

    left = lst[:]
    pending = []

    ret = []
    while True:
        for item in left:
            if item in depends:  # has depend
                pending.append(item)
            else:  # no depend
                removeDepend(depends, item)
                if asc:
                    ret.append(item)
                else:
                    ret.insert(0, item)

        if len(pending) == 0:
            return ret
        elif len(pending) == len(left):
            raise Util_CycleDependsError(pending)
        else:
            left = pending
            pending = []


def fixLibDepends(lst, dependDict):
    # 为所有缺依赖的库自动添加依赖，并按照依赖顺序重排，越底层的库越靠后
    def complete(lst, item):
        if item not in dependDict:
            return
        for dependLib in dependDict[item]:
            if dependLib not in lst:
                lst.append(dependLib)

    for item in lst:
        complete(lst, item)

    return adjustOrderByDependency(lst, dependDict, False)


def test_fixLibDepends():
    dependDict = {
        'mariadb': ['zlib', 'axe'],
        'RanaSrv' : ['rana'],
        'rana' : ['lua'],
        'axe' : ['RanaSrv'],
        'zlib' : ['lua'],
        # 'lua' : ['RanaSrv'],  # Util_CycleDependsError 
    }
    import os
    if os.name != 'nt':
        dependDict['mariadb'].append('m', 'dl', 'pthread')

    print(fixLibDepends(['zlib', 'mariadb', 'rana', 'RanaSrv'], dependDict))



def infoTitle(fmt, *args):
    ALog.info(ALog.BRIGHT_AQUA + '================================================')
    ALog.info(ALog.BRIGHT_AQUA + fmt, *args)
    ALog.info(ALog.BRIGHT_AQUA + '================================================')


def infoSubTitle(fmt, *args):
    s = fmt % args
    ALog.info(ALog.BRIGHT_AQUA + s)
    ALog.info(ALog.BRIGHT_AQUA + ('=' * ATab.getStrScreenWidth(s)))


class decorate_logStepTimeCost:
    """ 日志每个步骤（以 `yield 0` 分隔）的耗时（单位默认为分钟）
    :param stepLog(stepCostSeconds, totalCostSeconds)
    :param doneLog(totalCostSeconds)
    【示例】
    @decorate_logStepTimeCost
    def steps():
        print('1')
        yield 0

        print('2')
        yield 0

    steps()
    """
    def __init__(self, stepLog=None, doneLog=None):
        self.stepLog = stepLog
        self.doneLog = doneLog

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            beginTime = time.time()
            endTime = time.time()
            for _ in func(*args, **kwargs):
                stepCostSeconds = time.time() - endTime
                totalCostSeconds = time.time() - beginTime
                if self.stepLog is None:
                    ALog.info('步骤耗时: %.3f 分钟；总耗时 %.3f 分钟', stepCostSeconds/60.0, totalCostSeconds/60.0)
                else:
                    self.stepLog(stepCostSeconds, totalCostSeconds)
                endTime = time.time()

            totalCostSeconds = endTime - beginTime
            if self.doneLog is None:
                ALog.info(ALog.BRIGHT_GREEN + '!!! DONE !!!')
                ALog.info(ALog.BRIGHT_GREEN + '耗时: %.3f 分钟', totalCostSeconds/60.0)
            else:
                self.doneLog(totalCostSeconds)

        return wrapper
