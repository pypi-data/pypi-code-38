import re


class Table:

    def __init__(self):
        self.columns = []
        self.rows = []

    def log(self):
        print '\t'.join(self.columns)
        for line in self.rows:
            print '\t'.join(line)

    def save(self, file):
        file = open(file, 'w')
        file.write('\t'.join(self.columns) + '\n')
        for line in self.rows:
            file.write('\t'.join(line) + '\n')

    def select(self, column):
        if column in self.columns:
            column = self.columns.index(column)
        else:
            print 'table have not parameter [%s]' % column
            return []
        result = []
        for line in self.rows:
            result.append(line[column])
        return result

    def count_if(self, column, equal):
        count = 0
        index = self.columns.index(column)
        for row in self.rows:
            value = row[index]
            if eval(equal.format(value)):
                count += 1
        return count

    def remove_if(self, column, equal):
        rows = []
        index = self.columns.index(column)
        for row in self.rows:
            value = row[index]
            if not eval(equal.format(value)):
                rows.append(row)
        self.rows = rows

    def max(self, column):
        values = self.select(column)
        max_value = -9999
        for value in values:
            if value.isdigit():
                max_value = max(max_value, int(value))
        return max_value


def parse_params(params):
    result = {}
    pairs = params.split(';')
    for pair in pairs:
        name = pair.split(':')[0].strip()
        value = pair.split(':')[1].strip()
        result[name] = value
    return result


def parse(file):
    table = []
    columns = []
    lines = open(file).readlines()
    lines = lines[1:]
    for line in lines:
        l = line.find('{')
        r = line.rfind('}')
        if l != -1 and r != -1:
            params = line[l + 1:r]
            params = parse_params(params)
            table.append(params)
            for name in params:
                if name not in columns:
                    columns.append(name)

    result_table = Table()
    result_table.columns = columns
    for line in table:
        nline = []
        for name in columns:
            value = line[name] if name in line else ''
            nline.append(value)
        result_table.rows.append(nline)
    return result_table


def parse_all(file):
    tables = {}
    columns = []
    lines = open(file).readlines()
    lines = lines[1:]
    for line in lines:
        event = re.findall(r'"[\w\s,:]+",\d+.(\w+)', line)
        if event:
            event = event[0]
        if event not in tables:
            tables[event] = []
        l = line.find('{')
        r = line.rfind('}')
        if l != -1 and r != -1:
            params = line[l + 1:r]
            params = parse_params(params)
            tables[event].append(params)
            for name in params:
                if name not in columns:
                    columns.append(name)

    result = {}
    for event in tables:
        result[event] = Table()
        result[event].columns = columns
        for line in tables[event]:
            nline = []
            for name in columns:
                value = line[name] if name in line else ''
                nline.append(value)
            result[event].rows.append(nline)
    return result

if __name__ == '__main__':
    file = 'Syndicate3-(2017-08-08T02_37_10.527Z-2017-09-07T02_37_10.527Z)-(PurchaseSuccessful)-eventsLog.csv'
    parse(file).log()
