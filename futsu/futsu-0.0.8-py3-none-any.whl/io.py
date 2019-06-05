def read_line_list(fn, encoding='utf-8'):
    with open(fn,'rt',encoding=encoding) as fin:
        ret = fin.readlines()
    ret = [ i.strip('\n') for i in ret ]
    return ret

def write_line_list(fn, txt_list, encoding='utf-8'):
    with open(fn, mode='wt', encoding=encoding) as fout:
        for txt in txt_list:
            fout.write('{}\n'.format(txt))
