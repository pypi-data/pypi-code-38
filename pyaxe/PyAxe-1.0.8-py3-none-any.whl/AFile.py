import os
import re
from . import AError, AOS, AStr

class File_Error(AError.Error):
    pass


def readStripedLines(filePath, *args, **kwargs):
    """
    每次返回一个非空行，并且去除了行首尾的空白.
    :param 和系统的open()函数一致
    """
    with open(filePath, 'r', *args, **kwargs) as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            yield line


def replaceContent(filePath, replaceMap, useRegex=False, regexFlags=0, encoding=None, newline=None):
    """
    使用replaceMap对文件内容进行替换
    useRegex: replaceMap是否使用正则表达式
    """
    try:
        with open(filePath, encoding=encoding, newline=newline) as fp:
            s = fp.read()
            newStr = AStr.replace(s, replaceMap, useRegex, regexFlags)

        if id(newStr) != id(s):  # changed
            with open(filePath, 'w', encoding=encoding, newline=newline) as fp:
                fp.write(newStr)

    except Exception as e:
        raise File_Error('replaceFileContent(%s) failure: %s' % (filePath, e))


def replaceContentInDir(dir, replaceMap, fileMatchRule=None, useRegex=False, regexFlags=0, encoding=None, newline=None):
    """
    对目录dir下面所有满足条件的文件使用replaceMap进行内容替换
    fileMatchRule(fileName, filePath)是一个函数: 用于决定文件是否要参与替换
    useRegex: replaceMap是否使用正则表达式
    """
    for _, filePath in AOS.walkFiles(dir, fileMatchRule=fileMatchRule):
        replaceContent(filePath, replaceMap, useRegex, regexFlags, encoding, newline)


def isNewer(aPath, bPath):
    """
    a是否比b新
    若a不存在，返回False
    若a存在但b不存在，返回True
    若a，b都存在则比较最后修改时间
    """
    try:
        aStat = os.stat(aPath)
    except:
        return False

    try:
        bStat = os.stat(bPath)
    except:
        return True

    return aStat.st_mtime > bStat.st_mtime


def write(filePath, content, encoding=None, newline=None):
    with open(filePath, 'w', encoding=encoding, newline=newline) as fp:
        fp.write(content)


def tryWrite(filePath, content, encoding=None, newline=None):
    """如果文件内容发生变化则写入之（返回True），否则不做任何事情（返回False）"""
    if os.path.isfile(filePath):
        with open(filePath, encoding=encoding, newline=newline) as fp:
            if fp.read() == content:
                return False
    write(filePath, content, encoding=encoding, newline=newline)
    return True


def isEncodingWith(filePath, encoding):
    """
    已知问题
    1. 若文件编码为UTF8-BOM，isEncodingWith(GBK)返回True
    """
    def isUTF8(encoding):
        return encoding.lower() in ('utf8', 'utf-8', 'utf_8', 'u8')

    def isUTF8WithBOM(encoding):
        return encoding.lower() in ('utf_8_sig')

    """
    注意utf8和utf_8_sig都能打开带BOM和不带BOM的UTF8文件
    - utf8返回的文件内容不会去掉BOM标识
    - utf_8_sig返回的文件内容会自动去掉BOM标识
    """
    if isUTF8(encoding) or isUTF8WithBOM(encoding):
        try:
            with open(filePath, encoding='utf8') as fp:
                s = fp.read(1)
                if s == '\ufeff':
                    return isUTF8WithBOM(encoding)
                else:
                    return isUTF8(encoding)
        except UnicodeDecodeError:
            return False
        except Exception as e:
            raise

    try:
        with open(filePath, encoding=encoding) as fp:
            fp.read()
            return True
    except Exception:
        return False


def convertEncoding(filePath, encodingFrom, encodingTo, newline=None):
    with open(filePath, encoding=encodingFrom, newline=newline) as fp:
        s = fp.read()

    with open(filePath, 'w', encoding=encodingTo, newline=newline) as fp:
        fp.write(s)
