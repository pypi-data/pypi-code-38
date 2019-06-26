import re

def format(template, prefix, suffix, **varDict):
    """
    由于标准的 `str.format` 需要对于 `{`, `}` 转义：`{` 要写成 `{{`，`}` 要写成 `}}`
    因此本函数仅适用于大量使用`{` `}`的字符串模板场合，其他场合皆应使用标准的 `str.format`
    example:
        format('123 $(name) def $(name)d', '$(', ')', name='x') == '123 x def xd'
    """
    s = template
    for k, v in varDict.items():
        s = s.replace(prefix+k+suffix, v)
    return s


# deprecated, replace with textwrap.indent(s, prefix)
def prefixM(prefix, s):
    """为字符串添加前缀，对于多行字符串，每行都添加前缀"""
    if '\n' not in s:
        return prefix+s

    ret = ''
    lines = s.split('\n')
    lineCount = len(lines)
    for index in range(lineCount):
        ret += prefix
        ret += lines[index]
        if index != lineCount-1:  # 最后一行不要添加换行符
            ret += '\n'
    return ret


def replace(s, replaceMap, useRegex=False, regexFlags=0):
    """将s用replaceMap进行替换，并返回替换后的字符串
    若id(返回值) == id(s)表示没有发生任何替换
    """
    for k, v in replaceMap.items():
        if useRegex:
            pattern = re.compile(k, regexFlags)
            s, replacedCount = pattern.subn(v , s)
        else:
            if k in s:
                s = s.replace(k, v)
    return s
