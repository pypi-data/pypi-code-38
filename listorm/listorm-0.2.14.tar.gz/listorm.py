from itertools import chain, groupby, tee 
from operator import itemgetter
from heapq import nlargest, nsmallest
from io import BytesIO, StringIO
from collections import namedtuple, Counter, OrderedDict, defaultdict
from functools import partial
import csv, re

import xlrd, xlsxwriter


def str2float(value):
    try:
        ret = float(value)
    except:
        return value
    else:
        return ret

def round_try(value, round_to=2):
    try:
        if not isinstance(value, int):
            r = float(value)
        r = value
    except:
        return value
    else:
        return round(r, round_to)



class Scheme(dict):

    __getattr__ = dict.get

    def __init__(self, *args, **kwargs):
        super(Scheme, self).__init__(*args, **kwargs)

    def __add__(self, other):
        cp = Scheme(self)
        for k in cp.keys() & other.keys():
            other[k] = cp[k] or other[k]
        cp.update(other)
        return cp
        
    def __iadd__(self, other):
        self = self + other
        return self

    def __sub__(self, other):
        keys = self.keys() - other.keys()
        return Scheme({k:self[k] for k in keys})

    def __isub__(self, other):
        self =self-other
        return self

    def __hash__(self):
        return hash(tuple(sorted(self.items())))

    def _filter_invalid_keys(self, *keys):
        return (k for k in keys if k in self)

    def select(self, *keys, values=True):
        keys = self._filter_invalid_keys(*keys)
        return tuple(self[key] for key in keys) if values else {key:self[key] for key in keys}

    def delete(self, *keys):
        for key in keys:
            if key in self:
                self.pop(key)
        return self

    def rename(self, **key_map):
        for key in self:
            for ori, new in key_map.items():
                if ori in self:
                    value = self.pop(ori)
                    self[new]=value
        return self

    def row_update(self, apply_to_record=True, insert_new=False, **key_apply_set):
        for key, func in key_apply_set.items():
            if key in self or insert_new:
                try:
                    updated = func(self) if apply_to_record else func(self[key])
                except Exception as e:
                    continue
                else:
                    self[key] = updated
        return self

    def set_index(self, *keys, index_name=None):
        keys = self._filter_invalid_keys(*keys)
        if index_name in self:
            index_name += '__index'
        self[index_name] = ''.join(filter(None, (self[k] for k in keys)))
        return self

    def number_format(self, **key_examples):

        for key, format_example in key_examples.items():
            fmtfunc = type(format_example)
            val_ori = self.get(key)
            try:
                val_formated = fmtfunc(val_ori)
            except:
                val_ori = str2float(self.get(key))
                try:
                    val_formated = fmtfunc(val_ori)
                except:
                    val_formated = format_example
            finally:
                if key in self:
                    self[key] = val_formated
        return self

def diffkeys(src:dict, dest:dict):
    common_keys = src.keys() | dest.keys()
    diff_keys = []
    for key in common_keys:
        src_val = src.get(key)
        dest_val = dest.get(key)
        if src_val != dest_val:
            diff_keys.append(key)
    return diff_keys


class Listorm(list):

    def __init__(self, records=None, index=None, index_name=None, normalize=True, column_orders=None):
        self.index = index or []
        self.index_name = index_name

        to_normalize, to_init = tee(records or [])

        if normalize:
            uni_keys = self._union_keys(to_normalize)

        records = list(Scheme.fromkeys(uni_keys)+Scheme(record) if normalize else Scheme(record) for record in to_init if record)

        if column_orders:
            self.column_orders = column_orders
        elif isinstance(records, Listorm):
            self.column_orders = records.column_orders
        else:
            self.column_orders = sorted(records[0].keys()) if records else []

        super(Listorm, self).__init__(records)

        if isinstance(index, str):
            index = [index]
        if index and not index_name:
            self.set_index(*index)
        if index_name and not index:
            self.index_name = None                

    def __add__(self, other):
        return Listorm(super(Listorm, self).__add__(other), index=other.index)
        
    def __sub__(self, other):
        return Listorm(set(self)-set(other), column_orders=self.column_orders, index=self.index)
        
    def __or__(self, other):
       return Listorm(set(self)|set(other), column_orders=self.column_orders, index=self.index)

    def __and__(self, other):
       return Listorm(set(self)&set(other), column_orders=self.column_orders, index=self.index)
       
    def __xor__(self, other):
       return Listorm(set(self)^set(other), column_orders=self.column_orders, index=self.index)

    def _union_keys(self, records):
        return set(chain(*(record.keys() for record in records)))

    def _is_valid(self, row_value):
        if row_value and isinstance(row_value, dict):
            return True
        return False

    def _row_func(self, row, filter_and, **where):
        if filter_and:
            for key, val in where.items():
                    if row[key] != val:
                        return False
            return True
        else:
            for key, val in where.items():
                    if row[key] == val:
                        return True
            return False

    def append(self, row_value, sync_new=True):
        if self._is_valid(row_value):
            new_record = Scheme(row_value)
            if self:
                enough = new_record.keys() - self[-1].keys()
                deficiency = self[-1].keys() - new_record.keys()
                if enough:
                    if sync_new:
                        for record in self:
                            for key in enough:
                                record[key] = None
                    else:
                        new_record.delete(*enough)
                    self.column_orders += list(enough)
                for key in deficiency:
                    new_record[key] = None
            super(Listorm, self).append(new_record)

    @property
    def exists(self):
        return len(self) != 0

    def update(self, where=lambda row: True, to_rows=True, **updates):
        '''update record in where condition
           apply_to_record if True func in updates applies each row(record), else applies on each cell(value) 
           lst.update(name=lambda row: row.name + row.firstname, height=round, where=lamba row: row['age']>18)
        '''
        for record in self:
            if where(record):
                for column, apply in updates.items():
                    if column not in record:
                        print("Listorm.update-Warning: {} is not in this columns".format(column))
                        continue
                    if callable(apply):
                        record.row_update(apply_to_record=to_rows, **{column: apply})
                    else:
                        record[column] = apply
        return self

    def filter(self, where=lambda row: True):
        '''filtering by func apply to each record
           lst.filter(where = lambda row:row['price'] > 500)
        '''
        return Listorm((record for record in self if where(record)), normalize=False, column_orders=self.column_orders, index=self.index, index_name=self.index_name)

    def filterand(self, **where):
        '''filtering by value for each column in record
           lst.vfilter(a='1', b='2') , filtering as 'AND'
        '''
        rowfunc = partial(self._row_func, filter_and=True, **where)
        return Listorm(self, normalize=False).filter(rowfunc)

    def filteror(self, **where):
        '''filtering by value for each column in record
           lst.vfilter(a='1', b='2') , filtering as 'OR'
        '''
        rowfunc = partial(self._row_func, filter_and=False, **where)
        return Listorm(self, normalize=False).filter(rowfunc)
         
    def exclude(self, where=lambda row: True):
        '''filtering exclusively by func apply to each record
           lst.filter(where = lambda row:row['price'] > 500)
        '''
        return Listorm((record for record in self if not where(record)), normalize=False, column_orders=self.column_orders, index=self.index, index_name=self.index_name)

    def excludeand(self, **where):
        '''exclude when all where condition is true
        '''
        rowfunc = partial(self._row_func, filter_and=True, **where)
        return Listorm(self, normalize=False, index=self.index, index_name=self.index_name).exclude(rowfunc)

    def excludeor(self, **where):
        '''exclude when any where conditions is true
        '''
        rowfunc = partial(self._row_func, filter_and=False, **where)
        return Listorm(self, normalize=False, index=self.index, index_name=self.index_name).exclude(rowfunc)

    def select(self, *columns, values=False):
        '''select columns if you need
           lst.select('A', 'B', 'c')
           values: True, then returns 2dArray that only contains values
        '''
        records = (record.select(*columns, values=values) for record in self)
        column_orders = [column for column in columns if column in self.column_orders]
        return list(records) if values else Listorm(records, normalize=False, column_orders=column_orders)

    def drop(self, *columns):
        column_orders = [column for column in self.column_orders if column not in columns]
        lst = self.select(*column_orders)
        return lst

    def max(self, column):
        seq = list(filter(None, self.column_values(column)))
        if seq:
            return max(seq)

    def min(self, column):
        seq = list(filter(None, self.column_values(column)))
        if seq:
            return min(seq)

    @property
    def first(self):
        if self:
            return self[0]
        return Scheme()

    @property
    def last(self):
        if self:
            return self[-1]
        return Scheme()

    def row_values(self, *args, headers=False):
        '''returns 2dArray contains only value of self
        '''
        header = [list(args)] if headers else []
        return header+[[record[k] for k in args] for record in self.select(*args)]

    def column_values(self, column):
        '''Get virtical Values in List by column name
        '''
        return [record.get(column) for record in self]

    def orderby(self, *rules):
        '''lst.orderby('A', '-B') orderby A asc B desc
           lst = lst.orderby(lambda row: [row.name, row.age], lambda row: row.gender)
        '''
        for rule in reversed(rules):
            if isinstance(rule, str):
                rvs = rule.startswith('-')
                rule = rule.strip('-')
                super().sort(key=lambda x: x[rule], reverse=rvs)
            elif callable(rule):
                super().sort(key=rule)
        return self

    def distinct(self, *column, eliminate=False):
        '''remove duplicate by columns
           lst.distinct('A', 'B', 'C')
        '''
        ret = []
        for g, l in groupby(sorted(self, key=itemgetter(*column)), key=itemgetter(*column)):
            head, *body = l
            if eliminate and body:
                continue
            else:
                ret.append(head)
        return Listorm(ret, normalize=False, column_orders=self.column_orders, index=self.index, index_name=self.index_name)

    def groupby(self, *columns, extra_columns=None, renames=None, agg_float_round=2, set_name=None, **aggset):
        '''groupby('location', 'gender',
                extra_columns = ['age', 'phone'], # Any one Extra Value in Grouped, not recomanded
                gender=len, age=sum, # aggregate targets column and apply functions
                renames = {'gender': 'gender_count', 'age': 'age_sum'}  # prevent for overwriting of result column to original column
                agg_float_round: column's rounding point that applied by aggregate function
                when aggregation colunm overlaped with grouped columns name
                set_name: To containing sub record and column name for each sub record in grouped results. 
            )
        '''
        grouped = defaultdict(Listorm)
        renames = renames or {}
        ret_columns = list(chain(columns, extra_columns or [], aggset, renames.values()))

        ret = Listorm()

        if set_name:
            ret_columns.append(set_name)

        for record in self:
            g = tuple(record.get(key) for key in columns)
            grouped[g].append(record)

        for g, lst in grouped.items():
            head = {k:v for k, v in lst.first.items()}
            for column, aggfn in aggset.items():
                head[renames.get(column, column)] = round_try(lst.apply_column(column, aggfn), round_to=agg_float_round)
            if set_name:
                head[set_name] = lst
            ret.append(head, sync_new=False)

        return ret.select(*ret_columns)

    def set_number_type(self, **key_examples):
        '''set_number_format(A=0.0, B=0, C='0'), change number type to default value(if failed, example values are applied to default)
            A: '123' => 123.0, B: 123.2 => 123, C: 123.1 => '123.1' 
        '''
        records = map(lambda record: record.number_format(**key_examples), self)
        return Listorm(records, normalize=False, column_orders=self.column_orders, index=self.index, index_name=self.index_name)

    def apply_row(self, apply_to_record=True, **key_func_to_records):
        '''Function For one record
        '''
        records = map(lambda record: record.row_update(apply_to_record=apply_to_record, **key_func_to_records), self)
        return Listorm(records, normalize=False, column_orders=self.column_orders, index=self.index, index_name=self.index_name)

    def apply_column(self, column, func=lambda col:col):
        values = [e[0] for e in self.row_values(column)]
        return func(values)

    def map(self, **key_values):
        '''Function for one value in record
           value_map = {'M':'multy', 'K':'kill'}
           map(A=lambda val: value_map.get(val, val))
           map(A=value_map) -> same as above
        '''
        applies = {}
        lst = Listorm(self)
        for column, mapping in key_values.items():
            if isinstance(mapping, dict):
                f = lambda e: mapping.get(e,e)
                lst = self.apply_row(apply_to_record=False, **{column:f})
            else:
                applies[column] = mapping
        return lst.apply_row(apply_to_record=False, **applies)


    def rename(self, **key_map):
        '''change Columns name
           lst.rename(**{'OriginCol': 'ChangedCol', 'OriginCol2': 'ChangedCol2'})
        '''
        records = map(lambda record: record.rename(**key_map), self)
        colums = map(lambda e: key_map.get(e, e), self.column_orders)
        return Listorm(records, normalize=False, column_orders=list(colums), index=list(map(lambda e: key_map.get(e, e), self.index)), index_name=key_map.get(self.index_name, self.index_name))

    def add_columns(self, **kwargs):
        '''adding columns in current scheme by related funcion with neighborhood in record
           lst.add_columns(C=lambda row: row['A'] -  row['B'], B=lambda row: row['C']*row['D'])
        '''
        records = map(lambda record: record.row_update(insert_new=True, **kwargs), self)
        column_orders = self.column_orders + list(kwargs.keys())
        return Listorm(records, column_orders=column_orders, index=self.index, index_name=self.index_name)

    def top(self, *by, n=1):
        '''get top n record in current List, if 0<n<1, then n apply as percentage
           lst.top('age', 1) => returns a oldest peple's record
           lst.top('sellary', 0.1) => returns top 10% sellary's records in List
        '''
        index = round(len(self) * n) if n < 1 else n
        ret = Listorm(nlargest(index, self, key=itemgetter(*by)), column_orders=self.column_orders, index=self.index, index_name=self.index_name)
        return ret.first if n == 1 else ret

    def bottom(self, *by, n=1):
        '''get bottom n record in current List, if 0<n<1, then n apply as percentage
           lst.bottom('age', 1) => returns a youngest peple's record
           lst.bottom('sellary', 0.1) => returns bottom 10% sellary's records in List
        '''
        index = round(len(self) * n) if n < 1 else n
        ret = Listorm(nsmallest(index, self, key=itemgetter(*by)), column_orders=self.column_orders, index=self.index, index_name=self.index_name)
        return ret.first if n == 1 else ret

    def value_count(self, column):
        '''returns a Column's value count
        '''
        return Counter(row[column] for row in self)

    def unique(self, column):
        '''get column's unique values
        '''
        return set(self.apply_column(column))

    def isunique(self, column):
        column_values = self.apply_column(column)
        return len(column_values) == len(set(column_values))

    def set_index(self, *column, index_name='__index__'):
        '''set Index each record by column values
           lst.set_index('A', 'B', 'C')
        '''
        for record in self:
            index = record.set_index(*column, index_name=index_name)
        self.index_name = index_name
        self.index = column
        return self

    def join(self, other, **kwargs):
        ''' Join With two Listorm
            join(lst1, lst2, on='name', how='inner')
            how: 'inner'|'left'| 'right'|'outer'
        '''
        return join(self, other, **kwargs)

    def to_excel(self, filename=None, selects=None):
        '''If filnames is None, returns filecontents
        '''
        if not self:
            return
        selects = selects or self.column_orders

        error_columns = set(selects) - self[0].keys()

        for col in error_columns:
            selects.remove(col)

        for key, val in self[0].items():
            if isinstance(val, (Listorm, list)):
                selects.remove(key)

        output = BytesIO()
        wb = xlsxwriter.Workbook(output)
        ws = wb.add_worksheet()
        ws.write_row(0,0, selects)
        for r, row in enumerate(self, 1):
            row_values = [row[k] for k in selects]
            ws.write_row(r,0, row_values)
        wb.close()
        if filename:
            with open(filename, 'wb') as fp:
                fp.write(output.getvalue())
        else:
            return output.getvalue()

    def to_csv(self, filename=None, selects=None):
        if not self:
            return

        selects =  selects or self.column_orders

        error_columns = set(selects) - self[0].keys()
        for col in error_columns:
            selects.remove(col)

        for key, val in self[0].items():
            if isinstance(val, (Listorm, list)):
                selects.remove(key)

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames = selects, lineterminator='\n')
        writer.writeheader()
        for row in self:
            row_values = OrderedDict((k, row[k]) for k in selects)
            writer.writerow(row_values)

        if filename:
            with open(filename, 'w') as fp:
                fp.write(output.getvalue())
        else:
            return output.getvalue()
        
    def to_records(self):
        return [
            dict(row) for row in self
        ]

    def get_changes(self, other, pk):
        '''Comparison both Lists that has common keys
            lst.get_changes(recs2, pk='primaryKey') 
            pk: primarykey for both Lists
        '''
        if not other:
            return
            
        other = Listorm(other)

        common_keys = self[0].keys() & other[0].keys()

        if not common_keys:
            raise ValueError('Other Listorm Object has no common keys with this')

        if pk not in common_keys:
            raise ValueError('Index must exist in both!')

        origin_select = self.select(*common_keys)
        target_select = other.select(*common_keys)

        origin, target = {row[pk]: row for row in origin_select}, {row[pk]: row for row in target_select}

        missing_keys = origin.keys() - target.keys()
        extra_keys = target.keys() - origin.keys()
        common_keys = origin.keys() & target.keys()
        
        added, deleted, updated = [], [], []

        Added = namedtuple('Added', 'pk rows')
        Deleted = namedtuple('Deleted', 'pk rows')
        Updated = namedtuple('Updated', 'pk before after where')

        for key in extra_keys:
            added.append(Added(key, target[key]))

        for key in missing_keys:
            deleted.append(Deleted(key, origin[key]))

        for key in common_keys:
            diff = origin[key].items() ^ target[key].items()
            if diff:
                updated.append(Updated(key, origin[key], target[key], list(dict(diff))))

        Changes = namedtuple('Changes', 'added deleted updated')
        return Changes(added, deleted, updated)

    def filtersim(self, **where):
        result_set = {}
        splitby=['space', 'nospace', 'digit']
        for_filter = Listorm(self).select(*where)

        for colname, keywords in where.items():
            if isinstance(keywords, str):
                keywords = [keywords]
            elif keywords is None:
                keywords = []
            keyword_set = Listorm()
            for keyword in filter(None, keywords):
                lst = Listorm()
                for sep in splitby:
                    ismatch = lambda keyword, text: re.search(keyword, text)

                    if sep == 'space':
                        tokkens = re.split('\s+', keyword)
                    elif sep == 'nospace':
                        ismatch = lambda keyword, text: re.search(re.sub('\s+','', keyword), re.sub('\s+','', text))
                        tokkens = [keyword]
                    elif sep == 'digit':
                        tokkens = re.split('\d+', keyword) + re.findall('\d+', keyword)     

                    tokkens = list(filter(None, tokkens))
                    toklst = Listorm(for_filter)
                    for tok in tokkens:
                        toklst = toklst.filter(where= lambda row: ismatch(tok, row[colname])) 
                    lst|=toklst
                keyword_set|= lst
            result_set[colname] = keyword_set

        ret = Listorm(column_orders=self.column_orders, index=self.index, index_name=self.index_name)
        for colname, lst in result_set.items():
            filtered = lst.unique(colname)
            ret+=self.filter(lambda row: row[colname] in filtered)

        return ret

    def excludesim(self, **where):
        return self - self.filtersim(**where)                      


def difflist(src:list, dest:list, nodiffs=None, common=True):
    if not src or not dest:
        return

    lst_src, lst_dest = Listorm(src), Listorm(dest)

    if set(lst_src.column_orders) != set(lst_dest.column_orders):
        if common:
            common_keys = lst_src.first.keys() & lst_dest.first.keys()
        else:
            common_keys = lst_src.first.keys() | lst_dest.first.keys()
        lst_src = lst_src.select(*common_keys)
        lst_dest = lst_dest.select(*common_keys)

    src_counter = Counter([{'row': row} for row in lst_src])
    dest_counter = Counter([{'row': row} for row in lst_dest])
    diff_counter_keys = src_counter.keys() ^ dest_counter.keys()
    common_counter_keys = src_counter.keys() & dest_counter.keys()

    added = []
    removed = []

    for key in common_counter_keys:
        src_row_count = src_counter[key]
        dest_row_count = dest_counter[key]
        count_diff = dest_row_count - src_row_count
        if count_diff > 0:
            target = added
        elif count_diff < 0:
            target = removed
        for _ in range(abs(count_diff)):
            target.append(key)

    for key in diff_counter_keys:
        src_row_count = src_counter.get(key, 0)
        dest_row_count = dest_counter.get(key, 0)
        
        target = added if dest_row_count else removed

        for _ in range(src_row_count+dest_row_count):
            target.append(key)

    return added, removed



def join(left, right, left_on=None, right_on=None, on=None, how='inner'):
    '''Join With two Listorm
        join(lst1, lst2, on='name', how='inner')
        join(lst1, lst2, left_on='name', right_on='name' how='inner')
        on: if both index names are same else each index names are needed at left_on, right_on
        how: 'inner'|'left'|'right'|'outer'
    '''
    left_on = left_on or left.index_name
    right_on = right_on or right.index_name

    if not (left_on and right_on or on):
        print("Listorm.join: has no index for join")
        return

    left_on_index, right_on_index = defaultdict(list), defaultdict(list)

    left = Listorm(left, column_orders=left.column_orders, index=left.index)
    right = Listorm(right, column_orders=right.column_orders, index=right.index)

    for record in left:
        key = record.get(left_on or on)
        left_on_index[key].append(record)

    for record in right:
        key = record.get(right_on or on)
        right_on_index[key].append(record)

    ret = []
    
    if how == 'left':
        index_on = left_on_index.keys()
    elif how=='right':
        index_on = right_on_index.keys()
    elif how=='outer':
        index_on = left_on_index.keys() | right_on_index.keys()
    else:
        index_on = left_on_index.keys() & right_on_index.keys()

    for index in index_on:
        left_scheme = Scheme.fromkeys(left[0])
        right_scheme = Scheme.fromkeys(right[0])
        left_list = left_on_index.get(index, [left_scheme])
        rights_list = right_on_index.get(index, [right_scheme])
        
        for left_record in left_list:
            for right_record in rights_list:
                row = left_record+right_record
                ret.append(row)

    column_orders = list(OrderedDict.fromkeys(left.column_orders+right.column_orders))
    return Listorm(ret, column_orders=column_orders, index=left.index)


def read_excel(file_name=None, file_contents=None, sheet_index=0, start_row=0, index=None):
    '''Excel File or byte Content of Excel to Listorm object
    '''
    wb = xlrd.open_workbook(filename=file_name, file_contents=file_contents)
    ws = wb.sheet_by_index(sheet_index)
    fields = ws.row_values(start_row)
    records = [dict(zip(fields, map(str, ws.row_values(r)))) for r in range(start_row+1, ws.nrows)]
    return Listorm(records, index=index, column_orders=fields)


def read_csv(filename=None, encoding='utf-8',  fp=None, index=None):
    '''CSV file or filepointer of CSV to Listorm object
    '''
    csvfp = None
    if filename:
        csvfp = open(filename, encoding=encoding)
    elif fp:
        csvfp = fp
    else:
        return
    csv_reader = csv.reader(csvfp)
    fields = next(csv_reader)
    records = [dict(zip(fields, map(str, row))) for row in csv_reader]
    csvfp.close()
    return Listorm(records, index=index, column_orders=fields)

