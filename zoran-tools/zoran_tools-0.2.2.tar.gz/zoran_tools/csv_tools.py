import csv


from zoran_tools.path_tools import create_father_dir


def readcsv(filename: str, encoding: str='utf8', delimiter: str=',', quotechar: str=None, li: bool=True):
    """
    接收一个CSV文件名, 返回其内容, 可能返回<list>也可能返回<generator>
    :param filename: 要读取的CSV路径
    :param encoding:
    :param delimiter:
    :param quotechar:
    :param li: 指定返回的数据格式, 为True时返回列表, 为False时返回生成器
    :return:
    """
    with open(file=filename, mode='r', encoding=encoding, newline='') as f:
        if quotechar:
            f_csv = csv.reader(f, delimiter=delimiter, quotechar=quotechar)
        else:
            f_csv = csv.reader(f, delimiter=delimiter)
        if li:
            return list(f_csv)
        else:
            for row in f_csv:
                yield row


def write_csv(filename: str, row_or_rows: list, mode: str='a+', encoding: str='utf8', newline: str='',
              delimiter: str=',', quotechar: str='"', quoting: str='all'):
    """
    接收一个文件名(路径)和一个列表, 将列表写入该文件
    :param filename: <str> 要写入的文件名
    :param row_or_rows: <list> 要写入的列表
    :param mode:
    :param encoding:
    :param newline:
    :param delimiter:
    :param quotechar:
    :param quoting: <csv.QUOTE_MINIMAL, csv.QUOTE_ALL, csv.QUOTE_NONNUMERIC, csv.QUOTE_NONE>
        csv.QUOTE_MINIMAL 仅当字段中包含分隔符时才用引号括起,
        csv.QUOTE_ALL 任何情况下都将字段用引号括起,
        csv.QUOTE_NONNUMERIC 括起非数字字段, 数字不括起,
        csv.QUOTE_NONE 不括起任何字段
    """
    create_father_dir(filename)

    quoting_dict = {
        'minimal': csv.QUOTE_MINIMAL,
        'nonnumeric': csv.QUOTE_NONNUMERIC,
        'all': csv.QUOTE_ALL,
        'none': csv.QUOTE_NONE,
    }
    quoting = quoting_dict.get(quoting.lower(), csv.QUOTE_NONE)

    with open(file=filename, mode=mode, encoding=encoding, newline=newline) as f:
        sp = csv.writer(f, delimiter=delimiter, quotechar=quotechar, quoting=quoting)
        if all([isinstance(e, (list, tuple)) for e in row_or_rows]):
            sp.writerows(row_or_rows)
        else:
            sp.writerow(row_or_rows)


def write_csv_row(file: str, row: list, mode: str='a+', encoding: str='utf8', newline: str=''):
    with open(file, mode=mode, encoding=encoding, newline=newline) as f:
        csv.writer(f).writerow(row)
