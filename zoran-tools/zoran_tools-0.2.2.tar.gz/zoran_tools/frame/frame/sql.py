import re
import csv


from .exception import LengthException
from tools.prettytable import PrettyTable


class Square(object):
    def __init__(self, length=0, width=0):
        self.length = length
        self.width = width

    def __str__(self):
        return 'size: {} lines × {} columns'.format(self.length, self.width)

    def __repr__(self):
        return self.__str__()


class FakeFrame(object):
    def __init__(self):
        self._content = [Row(fields='_1', row=[''])]  # 这种设计太不省内存了
        self.name = None

    def __str__(self):
        return '<frame.sql.FakeFrame>,it has {} lines, \nits first row fields are {}' \
            .format(self.length, self.dtypes)

    def __repr__(self):
        return '<frame.sql.FakeFrame>,it has {} lines'.format(self.length)

    def __len__(self):
        return self._content.__len__()

    def __getitem__(self, item):
        # 如果对FakeFrame对象切片，则返回一个切片了的FakeFrame对象
        if isinstance(item, slice):
            fakeframe = FakeFrame()
            fakeframe._content = self._content.__getitem__(item)
            return fakeframe
        # 如果对FakeFrame对象索引求值，则返回FakeFrame对象的一个元素，即一个Row对象
        elif isinstance(item, int):
            return self._content.__getitem__(item)

    def __setitem__(self, key, value):
        return self._content.__setitem__(key, value)

    def __add__(self, other):
        fakefarame = FakeFrame()
        fakefarame._content = self.collection + other.collection
        return fakefarame

    @property
    def length(self):
        """
        :return: 返回长度，即对象的行数
        """
        return self.__len__()

    @property
    def width(self):
        """

        :return: 返回对象字段数最长的一行的长度（字段数）
        """
        return max([len(row) for row in self])

    @property
    def square(self):
        """

        :return: 返回表示对象长度、宽度的对象
        """
        return Square(length=self.length, width=self.width)

    @property
    def dtypes(self):
        """

        :return: 返回第一行的字段
        """
        return [(f, type(e)) for f, e in zip(self.first().fields, self.first().collection)]

    @property
    def collection(self):
        """

        :return: 返回一个列表，列表的每一个元素都是一个Row对象
        """
        return self._content

    def pure_content(self):
        """

        :return: 返回一个列表，列表的每一个元素都是一个列表
        """
        return [row.values for row in self]

    def first_row_fields(self):
        """

        :return: 返回第一行的字段
        """
        return self.first().fields

    def take(self, num=1):
        """
        :param num:
        :return: 如果num是int类型，则取出第num行；如果是切片，则取出切片。
        """
        return self[num]

    def show(self, num=None, printt=True):
        """
        以友好方式打印要预览的内容
        :param num:
        :param printt:
        :return:
        """
        if isinstance(num, (int, slice)):
            fakeframe = self[:num] if isinstance(num, int) else self[num]
            x = PrettyTable()
            x._set_field_names(fakeframe.first_row_fields())
            for row in fakeframe:
                x.add_row(row=row.collection)
            if printt:
                print(x)
            else:
                return x.__str__()
        else:
            print('show limit 10 lines')
            return self.show(num=10)

    def count(self):
        """
        :return: 返回对象的行数
        """
        return self.length

    def first(self):
        """
        :return: 返回对象的第一行
        """
        return self[0]

    def lengthies(self):
        """
        :return: 返回对象每一行的宽度
        """
        return [len(row) for row in self]

    def neat(self):
        """判断对象每一行宽度是否相等， 相等返回True，否则返回False"""
        return len(set(self.lengthies())) == 1

    def select(self, *items, new=False):
        """
        选择列
        :param items: 要选择的字段，可以list，也可以是一组字符串，也可以是包含多个字段信息的一个字符串
        :param new:
        :return: 返回一个FakeFrame对象
        """
        content = [row.select(items) for row in self]
        if new:
            fakeframe = FakeFrame()
            fakeframe._content = content
            return fakeframe
        else:
            self._content = content
            return self

    def _update(self, content, new=False):
        """重新生成一个有着全新_content的FakeFrame对象"""
        if new:
            fakeframe = FakeFrame()
            fakeframe._content = content
            return fakeframe
        else:
            self._content = content
            return self

    def delete(self, condition, new=False):
        """
        删除满足条件的行
        :param condition: 条件，一个返回真值的函数
        :param new: 新建一个FakeFrame对象还是在原对象上更新
        :return:
        """
        content = [row for row in self if not row.filter(condition)]
        return self._update(content, new)

    def remove(self, row):
        """移除指定的行，可能会产生未知的问题"""
        return self._content.remove(row)

    def filter(self, condition, new=False):
        """
        留下满足条件的行，参考delete方法
        :param condition:
        :param new:
        :return:
        """
        content = [row for row in self if row.filter(condition)]
        return self._update(content, new)

    def left_join(self, other_df, on_condition):
        pass

    def pop(self, index=None):
        """从对象中删除最后一行，并返回这一行"""
        if index:
            row = self._content.pop(index)
        else:
            row = self._content.pop()
        return row

    def set_fields(self, fields):
        """重设所有行的字段"""
        for row in self:
            row.fields = fields

    def with_incid(self, position=0, start=1):
        """为对象增加一个自增列"""
        for i, row in enumerate(self, start):
            row.with_element(key='id', value=i, position=position)

    def with_column(self, key, value, position=0):
        """
        对对象增加一列
        :param key: 增加的列的字段名
        :param value: 增加的列的值，可以是一个函数，也可以是固定的值
        :param position: 增加的列所在的位置，从0开始
        :return:
        """
        for row in self:
            row.with_element(key=key, value=value, position=position)

    def union(self, other):
        """把另一个FakeFrame对象追加到本对象后面"""
        self._content += other.collection

    def set(self, key):
        """
        返回某列的值的集合
        :param key: 列名
        :return:
        """
        return set([row.values[0] for row in self.select(key, new=True)])

    def count_key(self, key):
        """
        返回某列的值以及其出现的频次
        :param key: 列名
        :return:
        """
        values_set = set([row.values[0] for row in self.select(key, new=True)])
        ck = []
        for v in values_set:
            count = self.filter(condition=lambda row: row[key] == '{}'.format(v), new=True).count()
            ck.append((v, count))
        return ck

    def update_row_value(self, update, condition):
        """
        更新某些行的值
        :param update: 一个函数，用于修改行元素的值
        :param condition: 一个函数，用于选择要修改的行
        :return:
        """
        pass

    def to_csv(self, file, head=False, encoding='utf8', quoting=csv.QUOTE_ALL, mode='append'):
        """
        将对象内容写入CSV文件
        :param file: 要写入的文件名
        :param head: 是否要将列名写入
        :param encoding:
        :param quoting:
        :param mode:
        :return:
        """
        mode_dict = {'a+': 'a+', 'append': 'a+', 'write': 'w', 'overwrite': 'w'}
        mode = mode_dict.get(mode)

        with open(file, mode=mode, encoding=encoding, newline='') as f:
            f_csv = csv.writer(f, quoting=quoting)
            if head:
                f_csv.writerow(self.first_row_fields())
            f_csv.writerows(self.pure_content())

    def sort(self, key, new=False):
        new_content = sorted(self._content, key=key)
        if new:
            fakeframe = FakeFrame()
            fakeframe._content = new_content
            return fakeframe
        else:
            self._content = new_content
            return self


class Row(object):
    def __init__(self, fields=None, row=None):
        self._fields = fields
        self._row = row

    def __iter__(self):
        return self._row.__iter__()

    def __setitem__(self, key, value):
        for i, f in enumerate(self._fields):
            if f == key:
                self._row[i] = value

    def __str__(self):
        return 'Row{}'.format(['"{}": {}'.format(f, e) for f, e in zip(self._fields, self._row)].__str__())

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        if isinstance(item, str) and item in self._fields:
            item = self._fields.index(item)

        if isinstance(item, (int, slice)):
            return self._row.__getitem__(item)
        else:
            raise TypeError

    def __len__(self):
        return self._row.__len__()

    def __add__(self, other):
        fields = ['left' + field for field in self.fields] + ['right' + field for field in other.fields]
        row = self.collection + other.collection
        return Row(fields=fields, row=row)

    def filter(self, condition):
        return condition(self)

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, fields):
        if isinstance(fields, (list, tuple)):
            if len(fields) == len(self.fields):
                self._fields = fields
            else:
                raise LengthException
        else:
            raise TypeError

    @property
    def values(self):
        return self.collect()

    def collect(self):
        return self._row

    @property
    def collection(self):
        return self.collect()

    def select(self, items):
        if isinstance(items, tuple):
            if len(items) == 1:
                items = items[0]
            else:
                items = list(items)

        if isinstance(items, str):
            items = re.sub('\s', '', items).split(',')

        if not isinstance(items, list):
            raise TypeError

        if set(items).issubset(self._fields):
            row = [self[e] for e in items]
            return Row(fields=items, row=row)
        else:
            print(items)
            raise IndexError

    def dict(self):
        d = dict()
        for f, v in zip(self.fields, self.collection):
            d[f] = v
        return d

    def with_element(self, key, value='', position=0):
        if hasattr(value, '__call__'):
            value = value(self)

        self._fields.insert(position, key)
        self._row.insert(position, value)

    def update_row_value(self, update):
        pass


