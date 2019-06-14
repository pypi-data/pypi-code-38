import os
import sys
import sqlite3
import csv
import locale
import random
import string
import signal
import logging
from contextlib import contextmanager
from itertools import groupby
from inspect import signature

import coloredlogs
import psutil
import pandas as pd
from sas7bdat import SAS7BDAT
from graphviz import Digraph
from more_itertools import spy, chunked
from pathos.multiprocessing import ProcessingPool as Pool
from tqdm import tqdm
from shutil import copyfile
from openpyxl import Workbook

from .util import listify, _build_keyfn


_locale = 'English_United States.1252' if os.name == 'nt' else 'en_US.UTF-8'

_CONFIG = {
    'ws': '',
    'max_workers': psutil.cpu_count(logical=False),
    'locale': _locale,
    'msg': True,
    'refresh': None,
    'export': None
}

_filename, _ = os.path.splitext(os.path.basename(sys.argv[0]))
_DBNAME = _filename + '.db'
_GRAPH_NAME = _filename + '.gv'
_JOBS = {}
# folder name (in workspace) for temporary databases for parallel work
_TEMP = "_temp"
_CONN = [None] 
# sqlite3 keywords
_RESERVED_KEYWORDS = {
    "ABORT", "ACTION", "ADD", "AFTER", "ALL", "ALTER", "ANALYZE", "AND", "AS",
    "ASC", "ATTACH", "AUTOINCREMENT", "BEFORE", "BEGIN", "BETWEEN", "BY",
    "CASCADE", "CASE", "CAST", "CHECK", "COLLATE", "COLUMN", "COMMIT",
    "CONFLICT", "CONSTRAINT", "CREATE", "CROSS", "CURRENT", "CURRENT_DATE",
    "CURRENT_TIME", "CURRENT_TIMESTAMP", "DATABASE", "DEFAULT", "DEFERRABLE",
    "DEFERRED", "DELETE", "DESC", "DETACH", "DISTINCT", "DO", "DROP", "EACH",
    "ELSE", "END", "ESCAPE", "EXCEPT", "EXCLUSIVE", "EXISTS", "EXPLAIN",
    "FAIL", "FILTER", "FOLLOWING", "FOR", "FOREIGN", "FROM", "FULL", "GLOB",
    "GROUP", "HAVING", "IF", "IGNORE", "IMMEDIATE", "IN", "INDEX", "INDEXED",
    "INITIALLY", "INNER", "INSERT", "INSTEAD", "INTERSECT", "INTO", "IS",
    "ISNULL", "JOIN", "KEY", "LEFT", "LIKE", "LIMIT", "MATCH", "NATURAL",
    "NO", "NOT", "NOTHING", "NOTNULL", "NULL", "OF", "OFFSET", "ON", "OR",
    "ORDER", "OUTER", "OVER", "PARTITION", "PLAN", "PRAGMA", "PRECEDING",
    "PRIMARY", "QUERY", "RAISE", "RANGE", "RECURSIVE", "REFERENCES", "REGEXP",
    "REINDEX", "RELEASE", "RENAME", "REPLACE", "RESTRICT", "RIGHT", "ROLLBACK",
    "ROW", "ROWS", "SAVEPOINT", "SELECT", "SET", "TABLE", "TEMP", "TEMPORARY",
    "THEN", "TO", "TRANSACTION", "TRIGGER", "UNBOUNDED", "UNION", "UNIQUE",
    "UPDATE", "USING", "VACUUM", "VALUES", "VIEW", "VIRTUAL", "WHEN", "WHERE",
    "WINDOW", "WITH", "WITHOUT"
}

coloredlogs.DEFAULT_FIELD_STYLES['levelname']['color'] = 'cyan'
coloredlogs.install(
    fmt='%(asctime)s %(levelname)s %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


class FeebeeError(Exception):
    pass


class NoRowToInsert(FeebeeError):
    pass


class NoRowToWrite(FeebeeError):
    pass


class InvalidGroup(FeebeeError):
    pass


class UnknownConfig(FeebeeError):
    pass


class ReservedKeyword(FeebeeError):
    pass


class InvalidColumns(FeebeeError):
    pass


class TableDuplication(FeebeeError):
    pass


class TableNotExist(FeebeeError):
    pass


@contextmanager
def _connect(dbfile):
    conn = _Connection(dbfile)
    try:
        yield conn
    finally:
        # Trying to make closing atomic to handle multiple ctrl-cs
        # Imagine the first ctrl-c have the process enter the 'finally block'
        # and the second ctrl-c interrupts the block in the middle
        # so that the database is corrupted
        with _delayed_keyboard_interrupts():
            # should I close the cursor?
            conn._cursor.close()
            conn._conn.commit()
            conn._conn.close()


@contextmanager
def _delayed_keyboard_interrupts():
    signal_received = []

    def handler(sig, frame):
        nonlocal signal_received
        signal_received = (sig, frame)
        logger.debug('SIGINT received. Delaying KeyboardInterrupt.')
    old_handler = signal.signal(signal.SIGINT, handler)

    try:
        yield
    finally:
        signal.signal(signal.SIGINT, old_handler)
        if signal_received:
            old_handler(*signal_received)


class _Connection:
    def __init__(self, dbfile):
        if not _CONFIG['ws']:
            _CONFIG['ws'] = os.getcwd()
        dbfile = os.path.join(_CONFIG['ws'], dbfile)
        locale.setlocale(locale.LC_ALL, _CONFIG['locale'])
        logger.propagate = _CONFIG['msg']

        self._conn = sqlite3.connect(dbfile)
        self._conn.row_factory = _dict_factory
        self._cursor = self._conn.cursor()
        # DO NOT re_CONFIGure pragmas. Defaults are defaults for a reason.
        # You could make it faster but with a cost. It could corrupt the disk
        # image of the database.

    def fetch(self, query, by=None):
        if by and isinstance(by, list) and by != ['*'] and\
                all(isinstance(c, str) for c in by):
            query += " order by " + ','.join(by)
        rows = self._conn.cursor().execute(query)
        if by:
            if isinstance(by, list):
                rows1 = (list(rs) for _, rs in groupby(rows, _build_keyfn(by)))
            elif isinstance(by, int):
                rows1 = chunked(rows, by)
            else:
                raise InvalidGroup(by)
            yield from rows1
        else:
            yield from rows

    def insert(self, rs, name):
        r0, rs = spy(rs)
        if r0 == []:
            raise NoRowToInsert(name)

        cols = list(r0[0])
        for x in [name] + cols:
            if _is_reserved(x):
                raise ReservedKeyword(x)

        try:
            self._cursor.execute(_create_statement(name, cols))
            istmt = _insert_statement(name, r0[0])
            self._cursor.executemany(istmt, rs)
        except sqlite3.OperationalError:
            raise InvalidColumns(cols)
    
    def load(self, filename, name, delimiter=None, quotechar='"',
             encoding='utf-8', newline="\n", fn=None):
        total = None
        if isinstance(filename, str):
            _, ext = os.path.splitext(filename)
            if ext.lower() == '.xlsx' or ext.lower() == ".xls":
                seq = _read_excel(filename)
            elif ext.lower() == '.sas7bdat':
                seq = _read_sas(filename)
            elif ext.lower() == ".dta":
                seq = _read_stata(filename)
            else:
                # default delimiter is ","
                delimiter = delimiter or\
                    ("\t" if ext.lower() == ".tsv" else ",")
                seq = _read_csv(filename, delimiter=delimiter,
                                quotechar=quotechar, encoding=encoding,
                                newline=newline)
                total = _line_count(filename, encoding, newline)
        else:
            # iterator, since you can pass an iterator
            # functions of 'load' should be limited
            seq = filename

        if fn:
            seq = _flatten(fn(rs) for rs in seq)
        self.insert(tqdm(seq, total=total), name)

    def get_tables(self):
        query = self._cursor.\
            execute("select * from sqlite_master where type='table'")
        return [row['name'] for row in query]

    def drop(self, tables):
        tables = listify(tables)
        for table in tables:
            if _is_reserved(table):
                raise ReservedKeyword(table)
            self._cursor.execute(f'drop table if exists {table}')

    def join(self, tinfos, name):
        # check if a colname is a reserved keyword
        newcols = []
        for _, _cols, _ in tinfos:
            _cols = [c.upper() for c in listify(_cols)]
            for c in _cols:
                if 'AS' in c:
                    newcols.append(c.split('AS')[-1])
        for x in [name] + newcols:
            if _is_reserved(x):
                raise ReservedKeyword(x)

        tname0, _, mcols0 = tinfos[0]
        join_clauses = []
        for i, (tname1, _, mcols1) in enumerate(tinfos[1:], 1):
            eqs = []
            for c0, c1 in zip(listify(mcols0), listify(mcols1)):
                if c1:
                    # allows expression such as 'col + 4' for 'c1',
                    # for example. somewhat sneaky though
                    eqs.append(f't0.{c0} = t{i}.{c1}')
            join_clauses.\
                append(f"left join {tname1} as t{i} on {' and '.join(eqs)}")
        jcs = ' '.join(join_clauses)

        allcols = []
        for i, (_, cols, _) in enumerate(tinfos):
            for c in listify(cols):
                if c == '*':
                    allcols += [f't{i}.{c1}'
                                for c1 in self.
                                _cols(f'select * from {tinfos[i][0]}')]
                else:
                    allcols.append(f't{i}.{c}')

        # create indices
        ind_tnames = []
        for tname, _, mcols in tinfos:
            mcols1 = [c for c in listify(mcols) if c]
            ind_tname = tname + _random_string(10)
            # allows expression such as 'col + 4' for indexing, for example.
            # https://www.sqlite.org/expridx.html
            self._cursor.execute(f"""
            create index {ind_tname} on {tname}({', '.join(mcols1)})""")

        query = f"""
        create table {name} as select
        {', '.join(allcols)} from {tname0} as t0 {jcs}
        """
        self._cursor.execute(query)
        # drop indices, not so necessary
        for ind_tname in ind_tnames:
            self._cursor.execute(f"drop index {ind_tname}")

    def export(self, tables):
        for table in listify(tables):
            table, ext = os.path.splitext(table)
            if ext.lower() == '.xlsx':
                rs = self.fetch(f'select * from {table}')
                book = Workbook()
                sheet = book.active 
                r0, rs = spy(rs)
                header = list(r0[0])
                sheet.append(header)
                for r in rs:
                    sheet.append(list(r.values()))
                book.save(f'{table}.xlsx')

            else:
                with open(os.path.join(_CONFIG['ws'], table + '.csv'), 'w',
                          encoding='utf-8', newline='') as f:
                    rs = self.fetch(f'select * from {table}')
                    r0, rs = spy(rs)
                    if r0 == []:
                        raise NoRowToWrite
                    fieldnames = list(r0[0])
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for r in rs:
                        writer.writerow(r)
                
    def _cols(self, query):
        return [c[0] for c in self._cursor.execute(query).description]

    def _size(self, table):
        self._cursor.execute(f"select count(*) as c from {table}")
        return self._cursor.fetchone()['c']


def get(tname, cols=None):
    """Get a list of rows (the whole table) ordered by cols

    :param tname: table name
    :param cols: comma separated string

    :returns: a list of rows
    """
    tname = tname.strip()
    c = _CONN[0]
    if tname in c.get_tables():
        if cols:
            seq = c.fetch(f"""select * from {tname} 
                              order by {','.join(listify(cols))}""")
        else:
            seq = c.fetch(f"select * from {tname}")
        return list(seq)
    else:
        raise TableNotExist(tname)

 
def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def _flatten(seq):
    for x in seq:
        if isinstance(x, dict):
            yield x
        elif x is not None:
            yield from x


def _applyfn(fn, seq):
    yield from _flatten(fn(rs) for rs in seq)


def _tqdm(seq, total, by):
    if by:
        with tqdm(seq, total=total) as pbar:
            for rs in seq:
                yield rs
                pbar.update(len(rs))
    else:
        with tqdm(seq, total=total) as pbar:
            for r in seq:
                yield r
                pbar.update(1)


def _execute(c, job):
    cmd = job['cmd']
    if cmd == 'load':
        c.load(job['file'], job['output'], delimiter=job['delimiter'],
               quotechar=job['quotechar'], encoding=job['encoding'],
               fn=job['fn'])

    elif cmd == 'map':
        tsize = c._size(job['inputs'][0])
        job['evaled_fn'] = job['fn']() if _is_thunk(job['fn']) else job['fn']

        if job['parallel']:
            max_workers = int(job['parallel'])\
                if job['parallel'] >= 2 else _CONFIG['max_workers']
            max_workers = min(max_workers, psutil.cpu_count())
        if job['parallel'] and\
            (job['by'].strip() != '*' if job['by'] else True) and\
                max_workers > 1 and tsize >= max_workers:
            logger.info(
                f"processing {job['cmd']}: {job['output']}"
                f" (multiprocessing: {max_workers})")
            _exec_parallel_map(c, job, max_workers, tsize)
        else:
            logger.info(f"processing {job['cmd']}: {job['output']}")
            seq = c.fetch(f"select * from {job['inputs'][0]}",
                          listify(job['by']))
            seq1 = _applyfn(job['evaled_fn'], _tqdm(seq, tsize, job['by']))
            c.insert(seq1, job['output'])

    # The only place where 'insert' is not used
    elif cmd == 'join':
        c.join(job['args'], job['output'])

    elif cmd == 'low':
        sqls = []
        for tbl, cols in job['tables']:
            if cols:
                sqls.append(f"""select * from {tbl}
                                order by {','.join(listify(cols))}""")
            else:
                sqls.append(f"select * from {tbl}")
        c.insert(tqdm(job['fn'](*(c.fetch(sql) for sql in sqls))),
                 job['output'])


def _line_count(fname, encoding, newline):
    with open(fname, encoding=encoding, newline=newline) as f:
        for i, _ in enumerate(f):
            pass
    # header implied, hence not i + 1
    return i


# sqlite3 in osx can't handle multiple connections properly.
def _exec_parallel_map(c, job, max_workers, tsize):
    itable = job['inputs'][0]
    tdir = os.path.join(_CONFIG['ws'], _TEMP)
    if not os.path.exists(tdir):
        os.makedirs(tdir)
    dbfiles = [os.path.join(_TEMP, _random_string(10))
               for _ in range(max_workers)]

    tcon = 'con' + _random_string(9)
    ttable = "tbl" + _random_string(9)
    # Rather expensive
    breaks = [int(i * tsize / max_workers) for i in range(1, max_workers)]
    bys = listify(job['by']) if job['by'] else None
    exe = Pool(len(dbfiles))

    def _proc(dbfile, cut):
        query = f"""select * from {ttable}
        where _ROWID_ > {cut[0]} and _ROWID_ <= {cut[1]}"""
        with _connect(dbfile) as c1:
            n = cut[1] - cut[0]
            seq = _applyfn(job['evaled_fn'], 
                           _tqdm(c1.fetch(query, by=bys), n, by=bys))
            try:
                c1.insert(seq, job['output'])
            except NoRowToInsert:
                pass

    def _collect_tables(dbfiles):
        succeeded_dbfiles = []
        for dbfile in dbfiles:
            with _connect(dbfile) as c1:
                if job['output'] in c1.get_tables():
                    succeeded_dbfiles.append(dbfile)

        if succeeded_dbfiles == []:
            raise NoRowToInsert

        with _connect(succeeded_dbfiles[0]) as c1:
            ocols = c1._cols(f"select * from {job['output']}")
        c._cursor.execute(_create_statement(job['output'], ocols))

        # collect tables from dbfiles
        for dbfile in succeeded_dbfiles:
            c._cursor.execute(f"attach database '{dbfile}' as {tcon}")
            c._cursor.execute(f"""
            insert into {job['output']} select * from {tcon}.{job['output']}
            """)
            c._conn.commit()
            c._cursor.execute(f"detach database {tcon}")

    def _delete_dbfiles(dbfiles):
        with _delayed_keyboard_interrupts():
            for dbfile in dbfiles:
                if os.path.exists(dbfile):
                    os.remove(dbfile)

    # condition for parallel work by group
    if bys:
        try:
            c._cursor.execute(f"attach database '{dbfiles[0]}' as {tcon}")
            c._cursor.execute(f"""
            create table {tcon}.{ttable} as select * from {itable}
            order by {','.join(bys)}
            """)
            c._conn.commit()
            c._cursor.execute(f"detach database {tcon}")

            with _connect(dbfiles[0]) as c1:
                def nth_gcols(n):
                    c1._cursor.execute(f"""select * from {ttable}
                    where _ROWID_ == {n} limit 1""")
                    r = c1._cursor.fetchone()
                    return [r[c] for c in bys]

                def where1(br):
                    return ' and '.join(f"{c} = {repr(v)}"
                                        for c, v in zip(bys, nth_gcols(br)))

                def build_wheres(breaks):
                    return ' or '.join(where1(br) for br in breaks)

                newbreaks = [list(r.values())[0] for r in c1._cursor.
                             execute(f"""select _ROWID_ from {ttable}
                                      where {build_wheres(breaks)} group by
                                      {','.join(bys)} having MAX(_ROWID_)""")]\
                    + [tsize]
            for dbfile in dbfiles[1:]:
                copyfile(dbfiles[0], dbfile)

            exe.map(_proc, dbfiles, zip([0] + newbreaks, newbreaks))
            _collect_tables(dbfiles)
        finally:
            _delete_dbfiles(dbfiles)

    # non group parallel work
    else:
        try:
            c._cursor.execute(f"attach database '{dbfiles[0]}' as {tcon}")
            c._cursor.execute(f"""create table {tcon}.{ttable}
             as select * from {itable}""")
            c._conn.commit()
            c._cursor.execute(f"detach database {tcon}")
            for dbfile in dbfiles[1:]:
                copyfile(dbfiles[0], dbfile)

            exe.map(_proc, dbfiles, zip([0] + breaks, breaks + [tsize]))
            _collect_tables(dbfiles)
        finally:
            _delete_dbfiles(dbfiles)


def load(file=None, fn=None, delimiter=None, quotechar='"', encoding='utf-8'):
    return {'cmd': 'load',
            'file': file,
            'fn': fn,
            'delimiter': delimiter,
            'quotechar': quotechar,
            'encoding': encoding,
            'inputs': []}


def map(fn=None, data=None, by=None, parallel=False):
    return {
        'cmd': 'map',
        'fn': fn,
        'inputs': [data],
        'by': by,
        'parallel': parallel
    }


def join(*args):
    inputs = [arg[0] for arg in args]
    return {
        'cmd': 'join',
        'inputs': inputs,
        'args': args
    }


def low(fn=None, data=None):
    """Sometimes you have to load the whole table(s) on memory
    which can be inefficient.

    :param fn: function (or generator) that accepts iterator(s) as args
    :param data: 
        'tname1, tname2, tname3' 
        or
        ['tname1', ('tname2', 'col1, col2'), 'tname3'] 
        'col1, col2' represents sorting columns
    """
    def handle_data(xs):
        if isinstance(xs, str):
            return [(x, None) for x in listify(xs)]
        return [(x, None) if isinstance(x, str) else x for x in xs]

    data = handle_data(data)
    return {
        'cmd': 'low',
        'fn': fn,
        'inputs': [tbl for tbl, _ in data],
        'tables': data
    }


def register(**kwargs):
    """Register processes as keyword args.

    .. highlight:: python
    .. code-block:: python

        import feebee as fb

        fb.register(
            table_name = fb.load('sample.csv'),
            table_name1 = fb.map(simple_process, 'table_name'),
        )

        fb.run()
    """
    for k, _ in kwargs.items():
        if _JOBS.get(k, False):
            raise TableDuplication(k)
    _JOBS.update(kwargs)


def run(**kwargs):
    """Run registered processes, only those that are not in the database and
    also that depend on those missing processes.

    :param ws: working space, the default is where the script is.
    :type ws: path as str
    :param max_workers: maxinum workers for parallel work. The default is the
        number of physical cores of your CPU.
    :type max_workers: int
    :param locale: The default is en_US.UTF-8
        (English_United States.1252 for Windows)
    :param msg: You may not want visual noises in the terminal.
    :param refresh: You may want to rerun the script over and over again,
        changing the code a bit. It could be tedious to delete the table
        everytime in those circumstances.

        Pass table names in string, for example 'table1, table2'.
    :type refresh: comma separated string of table names
    :param export: Export tables in csv. for example 'table1, table2'
        Those CSVs will be in the workspace as table1.csv, table2.csv.
    :type export: comma separated string of table names
    :returns: Actually returns something for testing purposes,
        but not relavant.
    """
    global _CONFIG
    try:
        default_configs = {k: v for k, v in _CONFIG.items()}
        for k, v in kwargs.items():
            if k not in _CONFIG:
                raise UnknownConfig(k)
            _CONFIG[k] = v
        return _run()
    finally:
        _CONFIG = default_configs


def _run():
    def append_output(kwargs):
        for k, v in kwargs.items():
            v['output'] = k
        return [v for _, v in kwargs.items()]

    def find_required_tables(jobs):
        tables = set()
        for job in jobs:
            for table in job['inputs']:
                tables.add(table)
            tables.add(job['output'])
        return tables

    # depth first search
    def dfs(graph, path, paths=[]):
        datum = path[-1]
        if datum in graph:
            for val in graph[datum]:
                new_path = path + [val]
                paths = dfs(graph, new_path, paths)
        else:
            paths += [path]
        return paths

    # graph: {input: [out1, out2, ...]}
    def build_graph(jobs):
        graph = {}
        for job in jobs:
            for ip in job['inputs']:
                if graph.get(ip):
                    graph[ip].add(job['output'])
                else:
                    graph[ip] = {job['output']}
        for x in graph:
            graph[x] = list(graph[x])
        return graph

    def render_graph(graph, jobs):
        dot = Digraph()
        for k, v in graph.items():
            dot.node(k, k)
            if k != v:
                for v1 in v:
                    dot.edge(k, v1)
        for job in jobs:
            if job['cmd'] == 'load':
                dot.node(job['output'], job['output'])
        dot.render(_GRAPH_NAME)

    jobs = append_output(_JOBS)
    required_tables = find_required_tables(jobs)
    with _connect(_DBNAME) as c:
        _CONN[0] = c

        def delete_after(missing_table, paths):
            for path in paths:
                if missing_table in path:
                    for x in path[path.index(missing_table):]:
                        c.drop(x)

        def get_missing_tables():
            existing_tables = c.get_tables()
            return [table for table in required_tables
                    if table not in existing_tables]

        def find_jobs_to_do(jobs):
            missing_tables = get_missing_tables()
            result = []
            for job in jobs:
                for table in job['inputs'] + [job['output']]:
                    if table in missing_tables:
                        result.append(job)
                        break
            return result

        def is_doable(job):
            missing_tables = get_missing_tables()
            return all(table not in missing_tables for table in job['inputs'])\
                and job['output'] in missing_tables

        graph = build_graph(jobs)
        try:
            render_graph(graph, jobs)
        except Exception:
            pass

        # delete tables in 'refresh'
        if _CONFIG['refresh']:
            c.drop(listify(_CONFIG['refresh']))

        starting_points = [job['output']
                           for job in jobs if job['cmd'] == 'load']
        paths = []
        for sp in starting_points:
            paths += dfs(graph, [sp], [])

        for mt in get_missing_tables():
            delete_after(mt, paths)

        jobs_to_do = find_jobs_to_do(jobs)
        initial_jobs_to_do = list(jobs_to_do)
        logger.info(f'To Create: {[j["output"] for j in jobs_to_do]}')

        while jobs_to_do:
            cnt = 0
            for i, job in enumerate(jobs_to_do):
                if is_doable(job):
                    try:
                        if job['cmd'] != 'map':
                            logger.info(
                                f"processing {job['cmd']}: {job['output']}")
                        _execute(c, job)

                    except Exception as e:
                        if isinstance(e, TableNotExist) and\
                          e.args[0] in required_tables:
                            continue

                        logger.error(f"Failed: {job['output']}")
                        logger.error(f"{type(e).__name__}: {e}", exc_info=True)

                        try:
                            c.drop(job['output'])
                        except Exception:
                            pass

                        logger.warning(
                            f"Unfinished: "
                            f"{[job['output'] for job in jobs_to_do]}")
                        return (initial_jobs_to_do, jobs_to_do)
                    del jobs_to_do[i]
                    cnt += 1
            # No jobs can be done anymore
            if cnt == 0:
                for j in jobs_to_do:
                    logger.warning(f'Unfinished: {j["output"]}')
                    for t in j['inputs']:
                        if t not in c.get_tables():
                            logger.warning(f'Table not found: {t}')
                return (initial_jobs_to_do, jobs_to_do)
        # All jobs done well
        if _CONFIG['export']:
            c.export(listify(_CONFIG['export']))

        return (initial_jobs_to_do, jobs_to_do)


def _random_string(nchars):
    "Generates a random string of lengh 'n' with alphabets and digits. "
    chars = string.ascii_letters + string.digits
    return ''.join(random.SystemRandom().choice(chars)
                   for _ in range(nchars))


# primary keys are too much for non-experts
def _create_statement(name, colnames):
    """create table if not exists foo (...)

    Note:
        Every type is numeric.
        Table name and column names are all lowercased
    """
    # every col is numeric, this may not be so elegant but simple to handle.
    # If you want to change this, Think again
    schema = ', '.join([col + ' ' + 'numeric' for col in colnames])
    return "create table if not exists %s (%s)" % (name, schema)


# column can contain spaces. So you must strip them all
def _insert_statement(name, d):
    "insert into foo values (:a, :b, :c, ...)"
    keycols = ', '.join(":" + c.strip() for c in d)
    return "insert into %s values (%s)" % (name, keycols)


def _read_csv(filename, delimiter=',', quotechar='"',
              encoding='utf-8', newline="\n"):
    with open(os.path.join(_CONFIG['ws'], filename),
              encoding=encoding, newline=newline) as f:
        header = [c.strip() for c in f.readline().split(delimiter)]
        yield from csv.DictReader(f, fieldnames=header,
                                  delimiter=delimiter, quotechar=quotechar)


def _read_sas(filename):
    filename = os.path.join(_CONFIG['ws'], filename)
    with SAS7BDAT(filename) as f:
        reader = f.readlines()
        header = [c.strip() for c in next(reader)]
        for line in reader:
            yield {k: v for k, v in zip(header, line)}


def _read_df(df):
    cols = df.columns
    header = [c.strip() for c in df.columns]
    for _, r in df.iterrows():
        yield {k: v for k, v in zip(header, ((str(r[c]) for c in cols)))}


# this could be more complex but should it be?
def _read_excel(filename):
    filename = os.path.join(_CONFIG['ws'], filename)
    # it's OK. Excel files are small
    df = pd.read_excel(filename, keep_default_na=False)
    yield from _read_df(df)


# raises a deprecation warning
def _read_stata(filename):
    filename = os.path.join(_CONFIG['ws'], filename)
    chunk = 10_000
    for xs in pd.read_stata(filename, chunksize=chunk):
        yield from _read_df(xs)


def _is_reserved(x):
    return x.upper() in _RESERVED_KEYWORDS


def _is_thunk(fn):
    return len(signature(fn).parameters) == 0
