"""
用于 XML 电子表格 (2003) (*.xml)
xml应以UTF-8编码
"""
import xml.etree.ElementTree as ET
from . import AError


ROW_NUMBER_SIGN = '#'  # 行号标识
TITLE_ROW_INDEX = 1  # 第一行为标题行
ROW_DISABLE_TAG = '<%%下架%%>'


class Workbook_Error(AError.Error):
    pass


class Workbook_InvalidColumnError(Workbook_Error):
    def __init__(self, sheet, title):
        self.sheet = sheet
        self.title = title

    def __str__(self):
        return "'%s' 表，'%s' 列不存在" % (self.sheet.name, self.title)


class Workbook_UniqueCheckError(Workbook_Error):
    def __init__(self, sheet, title, row1, row2):
        self.sheet = sheet
        self.title = title
        self.row1 = row1
        self.row2 = row2

    def __str__(self):
        return "'%s' 表，'%s' 列：第 %d 行 和 第 %d 行包含重复数据" % (self.sheet.name, self.title, self.row1['#'], self.row2['#'])


class Row:
    def __init__(self, sheet, row):
        self.sheet = sheet
        self.row = row

    def __getitem__(self, title):
        return self.get(title)
    
    def get(self, title):
        try:
            cellIndex = self.sheet._titleToCellIndexMap[title]
        except KeyError:
            raise Workbook_InvalidColumnError(self.sheet, title)
        return self.row[cellIndex]
    
    @property
    def enabled(self):
        if ROW_DISABLE_TAG not in self.sheet._titleToCellIndexMap:
            return True
        return self[ROW_DISABLE_TAG] != ROW_DISABLE_TAG


class Sheet:
    def __init__(self):
        self._name = ''
        self._titles = []  # 标题列表
        self._rows = [] # 行对象列表(不含标题行）
        self._titleToCellIndexMap = {}  # 标题对应列索引（包含系统产生的标题 ROW_NUMBER_SIGN)

    def __iter__(self):
        return iter(self._rows)

    @property
    def name(self):
        return self._name

    @property
    def titles(self):
        return self._titles

    def parseFromXMLNode(self, node):
        tableNode = node.find('{urn:schemas-microsoft-com:office:spreadsheet}Table')
        if tableNode is None:
            raise Workbook_Error('解析 Table 节点失败')

        """ 二维矩阵（第 0 行为标题行，第 0 列为行号）
        # 标题1 标题2
        1 内容1 内容2
        2 内容3 内容4
        """
        rows = []

        lastRowIndex = 0
        rowIndex = 0
        lastFullBlankRowNumber = -1
        for rowNode in tableNode.iterfind('{urn:schemas-microsoft-com:office:spreadsheet}Row'):
            try:
                rowIndex = rowNode.attrib['{urn:schemas-microsoft-com:office:spreadsheet}Index']
            except KeyError:
                rowIndex += 1

            if isinstance(rowIndex, str):
                try:
                    rowIndex = int(rowIndex)
                except:
                    raise Workbook_Error('XML包含无效数据：Row包含无效Index(%s), LastRow(%d)' % (rowIndex, lastRowIndex))

            if rowIndex < lastRowIndex + 1:
                raise Workbook_Error('XML包含无效数据：RowIndex(%s) < LastRow(%d)+1' % (rowIndex, lastRowIndex))

            if rowIndex > lastRowIndex + 1:
                lastFullBlankRowNumber = rowIndex - 1

            # 产生新行数据
            row = []

            # 第0列存储行号
            if rowIndex == TITLE_ROW_INDEX:
                row.append(ROW_NUMBER_SIGN)
            else:
                row.append(rowIndex)

            lastCellIndex = 0
            cellIndex = 0

            isFullBlankRow = True  # 当前行是否为完全空行（可能只包括Style信息或空白）
            for cellNode in rowNode.iterfind('{urn:schemas-microsoft-com:office:spreadsheet}Cell'):
                try:
                    cellIndex = cellNode.attrib['{urn:schemas-microsoft-com:office:spreadsheet}Index']
                except KeyError:
                    cellIndex += 1

                if isinstance(cellIndex, str):
                    try:
                        cellIndex = int(cellIndex)
                    except:
                        raise Workbook_Error('XML包含无效数据：Cell包含无效Index(%s), LastRow(%d), LastCell(%d)' % (cellIndex, lastRowIndex, lastCellIndex))

                if cellIndex < lastCellIndex + 1:
                    raise Workbook_Error('第 %d 行 第 %d 列，XML包含无效数据：无效的列索引' % (rowIndex, cellIndex))

                # 缺失的列自动填充为空
                for index in range(lastCellIndex+1, cellIndex):
                    if rowIndex == TITLE_ROW_INDEX:
                        raise Workbook_Error('第 %d 行 第 %d 列，标题行不能包含空列' % (rowIndex, index))
                    else:
                        row.append('')
                lastCellIndex = cellIndex

                dataText = ''
                dataNode = cellNode.find('{urn:schemas-microsoft-com:office:spreadsheet}Data')
                if dataNode is not None:
                    dataText = dataNode.text.strip()
                    if dataText:
                        isFullBlankRow = False
                row.append(dataText)

            if lastFullBlankRowNumber > 0:
                if not isFullBlankRow:
                    raise Workbook_Error('第 %d 行不能为空行' % lastFullBlankRowNumber)
            else:
                if isFullBlankRow:
                    lastFullBlankRowNumber = row[0]  # 允许最后的几行为空行（这些行会被丢弃）
                else:
                    rows.append(row)

            lastRowIndex = rowIndex
            
        if len(rows) == 0:
            raise Workbook_Error('标题行(第 %d 行)必须存在' % TITLE_ROW_INDEX)
        titleRow = rows[0]
        self._titles = titleRow[1:]

        for index, title in enumerate(titleRow):
            self._titleToCellIndexMap[title] = index

        # 缺失的列自动填充为空，使行长度等于标题行长度
        for rowIndex in range(1, len(rows)):
            row = rows[rowIndex]
            for _ in range(len(row), len(titleRow)):
                row.append('')

        # generate Row objects
        self._rows = []
        for rowIndex in range(1, len(rows)):
            row = Row(self, rows[rowIndex])
            if row.enabled:
                self._rows.append(row)

    def find(self, title, value):
        """
        找到title列值为value所在的行
        """
        for row in self._rows:
            if row[title] == value:
                return row
        return None

    def uniqueCheck(self, title, skipValue=None):
        """
        检测某列是否包含重复值，若值为skipValue则跳过检测
        """
        values = {}
        for row in self._rows:
            curValue = row[title]
            if skipValue is not None and curValue == skipValue:
                continue
            if curValue in values:
                raise Workbook_UniqueCheckError(self, title, values[curValue], row)
            else:
                values[curValue] = row


def readXML(xmlPath):
    book = {}

    try:
        tree = ET.ElementTree(file=xmlPath)
    except ET.ParseError as e:
        raise Workbook_Error("解析XML文件 '%s' 失败: %s" % (xmlPath, e))

    sheetCount = 0
    for sheetNode in tree.iterfind('{urn:schemas-microsoft-com:office:spreadsheet}Worksheet'):
        sheetCount += 1
        sheet = Sheet()
        try:
            sheetName = sheetNode.attrib['{urn:schemas-microsoft-com:office:spreadsheet}Name']
        except Exception as e:
            raise Workbook_Error("第 %d 张表，解析名称失败：%s" % (sheetCount, e))
        sheet._name = sheetName
        book[sheetName] = sheet

        try:
            sheet.parseFromXMLNode(sheetNode)
        except Exception as e:
            raise Workbook_Error("解析 '%s' 表失败：%s" % (sheetName, e))

    return book
