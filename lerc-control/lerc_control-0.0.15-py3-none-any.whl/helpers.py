
class TablePrinter(object):
    """Print a list of dicts as a table.

    :param fmt: list of tuple(heading, key, width)
    :param sep: string, separation between columns
    :param ul: string, character to underline column label, or None for no underlining
    :return: A string representation of the table, ready to be printed

    Each tuple in the fmt list of tuples is like so:

    :heading: str, column label
    :key: dictionary key to value to print
    :width: int, column width in chars
    """
    def __init__(self, fmt, sep=' ', ul=None):
        super(TablePrinter,self).__init__()
        self.fmt   = str(sep).join('{lb}{0}:{1}{rb}'.format(key, width, lb='{', rb='}') for heading,key,width in fmt)
        self.head  = {key:heading for heading,key,width in fmt}
        self.ul    = {key:str(ul)*width for heading,key,width in fmt} if ul else None
        self.width = {key:width for heading,key,width in fmt}

    def row(self, data):
        return self.fmt.format(**{ k:str(data.get(k,''))[:w] for k,w in self.width.items() })

    def __call__(self, dataList):
        _r = self.row
        res = [_r(data) for data in dataList]
        res.insert(0, _r(self.head))
        if self.ul:
            res.insert(1, _r(self.ul))
        return '\n'.join(res)
