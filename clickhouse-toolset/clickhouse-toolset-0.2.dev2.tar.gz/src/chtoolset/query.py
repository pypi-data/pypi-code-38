from chtoolset._query import _replace_tables, format, tables, table_if_is_simple_query
from collections import defaultdict
from toposort import toposort

def tables_or_sql(sql):
    try:
        return set(tables(sql))
    except:
        return set([('', sql)])

def replace_tables(sql, replacements):
    if not replacements:
        return format(sql)

    _replacements = {}
    for k, r in replacements.items():
        table = table_if_is_simple_query(r)
        rk = k if isinstance(k, tuple) else ('', k)
        _replacements[rk] = table[1] if table else r

    deps = defaultdict(set)
    for k, r in _replacements.items():
        deps[k] |= tables_or_sql(r)
    deps_sorted = list(reversed(list(toposort(deps))))

    query = sql
    for current_deps in deps_sorted:
        current_replacements = {}
        for r in current_deps:
            if r in _replacements:
                current_replacements[r] = _replacements[r]
        query = _replace_tables(query, current_replacements)
    return query
