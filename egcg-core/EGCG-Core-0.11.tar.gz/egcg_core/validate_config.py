import re
import sys
from os.path import abspath, dirname, basename

table = str.maketrans('', '', '\'" []')


class ConfigRef:
    def __init__(self, ref, lineno):
        self.ref = ref
        self.lineno = lineno

    def __repr__(self):
        return '%s at line %s' % ('/'.join(self.ref), self.lineno)


def find_config_references(file):
    getitems = []
    gets = []
    queries = []
    imports = _config_import_references(file)
    lineno = 0

    with open(file) as f:
        for line in f:
            lineno += 1
            for i in imports:
                for l, m in (
                    (getitems, _find_get_item),
                    (gets, _find_gets),
                    (queries, _find_query)
                ):
                    refs = m(line, i, lineno)
                    if refs:
                        l.extend(refs)

    return getitems, gets, queries


def _find_gets(line, cfg_pointer, lineno):
    return [ConfigRef(x, lineno) for x in re.findall(cfg_pointer + '\.get\([\'"]([a-z]+)[\'"]\)', line)]


def _find_query(line, cfg_pointer, lineno):
    f = re.findall(cfg_pointer + '\.query\(([^\)]+)\)', line)
    if f:
        l = []
        for x in f[0].split(','):
            x = x.translate(table)
            if len(x) > 3 and '.' not in x:
                l.append(x)
        return [ConfigRef(l, lineno)]


def _find_get_item(line, cfg_pointer, lineno):
    f = re.findall(cfg_pointer + '(\[.+\])', line)
    if f:
        l = [x.translate(table) for x in f[0].split(']')]
        return [ConfigRef([x for x in l if x], lineno)]


def _config_import_references(file):
    refs = []
    with open(file) as f:
        for line in f:
            if line.startswith('import') or (line.startswith('from') and 'import' in line):
                if 'config' in line:
                    refs.append(line.strip().split(' ')[-1])
    return refs


def validate_main_config(cfg, file):
    print('_' * 36)
    print('Searching for missing configs in %s:' % basename(file))
    getitems, gets, queries = find_config_references(file)
    for i in getitems + queries:
        if not cfg.query(*i.ref):
            print(i)

    for i in gets:
        if not cfg.get(i):
            print(i)
    print('_' * 36)


def main():
    sys.path.append(dirname(dirname(abspath(__file__))))
    from egcg_core.config import cfg

    config_file = sys.argv[1]
    source_code = sys.argv[2]

    cfg.load_config_file(config_file)
    validate_main_config(cfg, source_code)


if __name__ == '__main__':
    main()
