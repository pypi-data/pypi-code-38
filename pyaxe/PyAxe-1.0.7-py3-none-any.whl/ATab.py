from . import AStr

_ORD_WIDTH_TABLE = (
    (126,    1), (159,    0), (687,     1), (710,   0), (711,   1),
    (727,    0), (733,    1), (879,     0), (1154,  1), (1161,  0),
    (4347,   1), (4447,   2), (7467,    1), (7521,  0), (8369,  1),
    (8426,   0), (9000,   1), (9002,    2), (11021, 1), (12350, 2),
    (12351,  1), (12438,  2), (12442,   0), (19893, 2), (19967, 1),
    (55203,  2), (63743,  1), (64106,   2), (65039, 1), (65059, 0),
    (65131,  2), (65279,  1), (65376,   2), (65500, 1), (65510, 2),
    (120831, 1), (262141, 2), (1114109, 1),
)


def getCharScreenWidth(c):
    """Return the screen column width for unicode ordinal o.
    SEE:
        Urwid
            http://urwid.org/
        Python中计算字符宽度
            http://blog.csdn.net/zhangxinrun/article/details/7526044
    """
    o = ord(c)
    if o == 0xe or o == 0xf:
        return 0
    for num, width in _ORD_WIDTH_TABLE:
        if o <= num:
            return width
    return 1


def getStrScreenWidth(s):
    ret = 0
    for c in s:
        ret += getCharScreenWidth(c)
    return ret


def spaceStr(spaceCount, fmt, *args):
    return spaceCount * ' ' + fmt % args


class TabObj:
    def __init__(self, tab='\t'):
        self.tab = tab

    def tabStr(self, tabCount, fmt, *args):
        return tabCount * self.tab + fmt % args


    def tabLine(self, tabCount, format, *args):
        return self.tabStr(tabCount, format, *args) + '\n'


    def tabStrM(self, tabCount, format, *args):
        return AStr.prefixM(tabCount * self.tab, format % args)


    def tabLineM(self, tabCount, format, *args):
        return self.tabStrM(tabCount, format, *args) + '\n'


tabObj = TabObj()
spaceTabObj = TabObj(' ' * 4)

tabStr = tabObj.tabStr
tabLine = tabObj.tabLine
tabStrM = tabObj.tabStrM
tabLineM = tabObj.tabLineM

spaceTabStr = spaceTabObj.tabStr
spaceTabLine = spaceTabObj.tabLine
spaceTabStrM = spaceTabObj.tabStrM
spaceTabLineM = spaceTabObj.tabLineM

def spaceTabData(tabCount, data, sameColumnWidth=False):
    SPACE_TAB_WIDTH = 4
    """
    用Tab均匀填充二维数据块data
    data的行可以是单个字符串也可以是字符串数组
    如果是字符串数组，则所有数组的长度应该相同

    sameColumnWidth: 所有列保持相同宽度
    """
    def calcMaxColumnWidth(data):
        maxLen = 0
        for row in data:
            if type(row) != list:
                continue
            for column in row:
                len_of_s = getStrScreenWidth(column)
                if len_of_s > maxLen:
                    maxLen = len_of_s
        return maxLen

    def fillTabs(data, maxColumnWidth):
        columnCount = 0
        for row in data:
            if type(row) == list:
                columnCount = len(row)
                break

        columnIndex = 0
        while columnIndex < columnCount-1:
            # 计算当前列的最大宽度
            maxLen = 0
            if maxColumnWidth is None:
                for row in data:
                    if type(row) != list:
                        continue
                    s = row[columnIndex*2]
                    len_of_s = getStrScreenWidth(s)
                    if len_of_s > maxLen:
                        maxLen = len_of_s
            else:
                maxLen = maxColumnWidth

            # 当前列占用的空格数
            spaceCount = (maxLen//SPACE_TAB_WIDTH + 1) * SPACE_TAB_WIDTH

            # 为每行插入Tab
            for row in data:
                if type(row) == list:
                    s = row[columnIndex*2]
                    fixSpaceCount = spaceCount - getStrScreenWidth(s)  # 当前元素后面需要补充的空格数
                    row.insert(columnIndex*2+1, fixSpaceCount)
            columnIndex += 1
        return columnCount * 2 -1  # 返回填充Tab后的列数

    if sameColumnWidth:
        maxColumnWidth = calcMaxColumnWidth(data)
    else:
        maxColumnWidth = None

    maxColumnCount = fillTabs(data, maxColumnWidth)
    s = ''
    for row in data:
        if type(row)==list:
            s += spaceTabStr(tabCount, '%s', row[0])
            columnIndex = 1
            while columnIndex < maxColumnCount:
                s += row[columnIndex] * ' ' + row[columnIndex+1]
                columnIndex +=2
            s += '\n'
        else:
            s += '%s\n' % row
    return s