""" Defines the phonon SQLite 3 Database """
from __future__ import absolute_import, print_function
import os
import json
import numbers
import sqlite3
import struct
import sys

import numpy as np

from ase.data import atomic_numbers
from ase.db.core import ops, now, invop
from ase.db.sqlite import SQLite3Database, index_statements, float_if_not_none
from ase.io import jsonio
from ase.utils import basestring

from hilde.phonon_db.phonon_db import PhononDatabase
from hilde.phonon_db.row import PhononRow

# Preamble modified from the sqlite database from ASE
if sys.version >= "3":
    buffer = memoryview

VERSION = 8
init_statements = [
    """CREATE TABLE systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID's, timestamps and user name
    unique_id TEXT UNIQUE,
    ctime REAL,
    mtime REAL,
    username TEXT,
    numbers BLOB,  -- stuff that defines an Atoms object
    positions BLOB,
    cell BLOB,
    pbc INTEGER,
    initial_magmoms BLOB,
    initial_charges BLOB,
    masses BLOB,
    tags BLOB,
    momenta BLOB,
    constraints TEXT,  -- constraints and calculator
    calculator TEXT,
    calculator_parameters TEXT,
    energy REAL,  -- calculated properties
    free_energy REAL,
    forces BLOB,
    stress BLOB,
    dipole BLOB,
    magmoms BLOB,
    magmom REAL,
    charges BLOB,
    natoms_in_sc_2 INTEGER,
    natoms_in_sc_3 INTEGER,
    sc_matrix_2 TEXT,
    sc_matrix_3 TEXT,
    force_2 BLOB,
    force_3 BLOB,
    displacement_dataset_2 TEXT,
    displacement_dataset_3 TEXT,
    qmesh TEXT,
    phonon_dos_fp TEXT,
    qpoints TEXT,
    phonon_bs_fp TEXT,
    tp_ZPE REAL,
    tp_high_T_S REAL,
    tp_T TEXT,
    tp_A TEXT,
    tp_S TEXT,
    tp_Cv TEXT,
    tp_kappa TEXT,
    symprec FLOAT,
    key_value_pairs TEXT,  -- key-value pairs and data as json
    data TEXT,
    natoms INTEGER,  -- stuff for making queries faster
    fmax REAL,
    smax REAL,
    volume REAL,
    mass REAL,
    charge REAL)""",
    """CREATE TABLE species (
    Z INTEGER,
    n INTEGER,
    id INTEGER,
    FOREIGN KEY (id) REFERENCES systems(id))""",
    """CREATE TABLE keys (
    key TEXT,
    id INTEGER,
    FOREIGN KEY (id) REFERENCES systems(id))""",
    """CREATE TABLE text_key_values (
    key TEXT,
    value TEXT,
    id INTEGER,
    FOREIGN KEY (id) REFERENCES systems(id))""",
    """CREATE TABLE number_key_values (
    key TEXT,
    value REAL,
    id INTEGER,
    FOREIGN KEY (id) REFERENCES systems(id))""",
    """CREATE TABLE information (
    name TEXT,
    value TEXT)""",
    "INSERT INTO information VALUES ('version', '{}')".format(VERSION),
]

check_keys = [
    "id",
    "energy",
    "magmom",
    "ctime",
    "user",
    "calculator",
    "natoms",
    "pbc",
    "unique_id",
    "fmax",
    "smax",
    "volume",
    "mass",
    "charge",
    "sc_matrix_2",
    "sc_matrix_3",
]


def hexify(array):
    """
    Converts a numpy array into a hex string representing the big endian
    byte encoding of the array
    Args:
        array: np.ndarray
            The array to be converted
    Returns:
        hexstr: str
            The hex string representing the bytestring of the array
    """
    if array is None:
        return None
    if array.size == 0:
        array = np.zeros(0)
    hexstr = ""
    zero = "0x0000000000000000"
    if array.dtype is np.int64:
        for val in array.flatten():
            hexstr += (
                hex(struct.unpack(">Q", struct.pack(">q", val))[0])
                if val != 0
                else zero
            )
    elif array.dtype is np.int32:
        array = array.astype(np.int64)
        for val in array.flatten():
            hexstr += (
                hex(struct.unpack(">Q", struct.pack(">q", val))[0])
                if val != 0
                else zero
            )
    else:
        for val in array.flatten():
            hexstr += (
                hex(struct.unpack(">Q", struct.pack(">d", val))[0])
                if val != 0.0
                else zero
            )
    return hexstr


def dehexify(hexstr, dtype=np.float64, shape=None):
    """
    Converts a hex string representation of an array into a numpy array
    Args:
        hexstr: str
            the hex string to be converted
        dtype: numpy data type
            the data type of the array
        shape: tuple or ints
            The shape of an array
    Returns:
        array:  The array the hex string represents
    """
    if hexstr is None:
        return None
    elif not hexstr:
        return np.zeros(0, dtype)
    if dtype is np.int64 or dtype is np.int32 or dtype is int:
        to_ret = [
            struct.unpack(">q", struct.pack(">Q", int(hh, 16)))[0]
            for hh in hexstr.split("0x")[1:]
        ]
    else:
        to_ret = [
            struct.unpack(">d", struct.pack(">Q", int(hh, 16)))[0]
            for hh in hexstr.split("0x")[1:]
        ]
    return np.array(to_ret).astype(dtype).reshape(shape)


class PhononSQLite3Database(PhononDatabase, SQLite3Database, object):
    """
    Modification of the SQLite3 database from ASE to include phonopy objects
    See ase.db.sqlite3 for missing function definitions
    """

    type = "db"
    initialized = False
    _allow_reading_old_format = False
    default = "NULL"  # used for autoincrement id
    connection = None
    version = None
    columnnames = [
        line.split()[0].lstrip() for line in init_statements[0].splitlines()[1:]
    ]

    def blob(self, array):
        """Convert array to blob/buffer object."""
        if array is None:
            return None
        array = np.array(array)
        if len(array) == 0:
            array = np.zeros(0)
        if array.dtype == np.int64:
            array = array.astype(np.int32)
        if not np.little_endian:
            array = array.byteswap()
        return buffer(np.ascontiguousarray(array))

    def deblob(self, buf, dtype=float, shape=None):
        """Convert blob/buffer object to ndarray of correct dtype and shape.

        (without creating an extra view)."""
        if buf is None:
            return None
        if len(buf) == 0:
            array = np.zeros(0, dtype)
        else:
            array = np.frombuffer(buf, dtype)
            if not np.little_endian:
                array = array.byteswap()
        if shape is not None:
            array.shape = shape
        return array

    def _write(self, row, key_value_pairs, data, id):
        """
        Writes a phonopy object to the database. Modifications from ASE are related to phonopy
        Args:
            row: PhononRow object
                The PhononRow object to be added to the database
            key_values_pairs: dict
                additional keys to be added to the database
            data: str
                Additional data to be included
            id: int
                ID for the phonopy object in the database
        Returns:
            id: the id of the row
        """
        PhononDatabase._write(self, row, key_value_pairs, data)
        encode = self.encode
        con = self.connection or self._connect()
        self._initialize(con)
        cur = con.cursor()
        mtime = now()
        blob = self.blob
        text_key_values = []
        number_key_values = []
        if id:
            self._delete(
                cur, [id], ["keys", "text_key_values", "number_key_values", "species"]
            )
        else:
            if not key_value_pairs:
                key_value_pairs = row.key_value_pairs
        constraints = row._constraints
        if constraints:
            if isinstance(constraints, list):
                constraints = encode(constraints)
        else:
            constraints = None

        values = (
            row.unique_id,
            row.ctime,
            mtime,
            row.user,
            blob(row.get("numbers")),
            blob(row.positions),
            blob(row.cell),
            int(np.dot(row.pbc, [1, 2, 4])),
            blob(row.get("initial_magmoms")),
            blob(row.get("initial_charges")),
            blob(row.get("masses")),
            blob(row.get("tags")),
            blob(row.get("momenta")),
            constraints,
        )
        if "calculator" in row:
            values += (row.calculator, encode(row.calculator_parameters))
        else:
            values += (None, None)
        if not data:
            data = row._data
        if not isinstance(data, basestring):
            data = encode(data)
        values += (
            row.get("energy"),
            row.get("free_energy"),
            blob(row.get("forces")),
            blob(row.get("stress")),
            blob(row.get("dipole")),
            blob(row.get("magmoms")),
            row.get("magmom"),
            blob(row.get("charges")),
            row.get("natoms_in_sc_2"),
            row.get("natoms_in_sc_3"),
            encode(row.get("sc_matrix_2")),
            encode(row.get("sc_matrix_3")),
            blob(row.get("forces_2")),
            blob(row.get("forces_3")),
            encode(row.get("displacement_dataset_2")),
            encode(row.get("displacement_dataset_3")),
            encode(row.get("qmesh")),
            encode(row.get("phonon_dos_fp")),
            encode(row.get("qpoints")),
            encode(row.get("phonon_bs_fp")),
            row.get("tp_ZPE"),
            row.get("tp_high_T_S"),
            hexify(row.get("tp_T")),
            hexify(row.get("tp_A")),
            hexify(row.get("tp_S")),
            hexify(row.get("tp_Cv")),
            hexify(row.get("tp_kappa")),
            row.get("symprec"),
            encode(key_value_pairs),
            data,
            len(row.numbers),
            float_if_not_none(row.get("fmax")),
            float_if_not_none(row.get("smax")),
            float_if_not_none(row.get("volume")),
            float(row.mass),
            float(row.charge),
        )
        if id is None:
            q = self.default + ", " + ", ".join("?" * len(values))
            cur.execute("INSERT INTO systems VALUES ({})".format(q), values)
            id = self.get_last_id(cur)
        else:
            q = ", ".join(name + "=?" for name in self.columnnames[1:])
            cur.execute("UPDATE systems SET {} WHERE id=?".format(q), values + (id,))

        count = row.count_atoms()
        if count:
            species = [(atomic_numbers[symbol], n, id) for symbol, n in count.items()]
            cur.executemany("INSERT INTO species VALUES (?, ?, ?)", species)
        text_key_values = []
        number_key_values = []
        for key, value in key_value_pairs.items():
            if isinstance(value, (numbers.Real, np.bool_)):
                number_key_values.append([key, float(value), id])
            else:
                assert isinstance(value, basestring)
                text_key_values.append([key, value, id])
        cur.executemany("INSERT INTO text_key_values VALUES (?, ?, ?)", text_key_values)
        cur.executemany(
            "INSERT INTO number_key_values VALUES (?, ?, ?)", number_key_values
        )
        cur.executemany(
            "INSERT INTO keys VALUES (?, ?)", [(key, id) for key in key_value_pairs]
        )
        if self.connection is None:
            con.commit()
            con.close()
        return id

    def _convert_tuple_to_row(self, values):
        """
        Converts the database's data into a Phonon Row object
        Args:
            values: Database encoded data list
                data from the database
        Returns
            PhononRow of the database data for object
        """
        deblob = self.deblob
        decode = self.decode

        values = self._old2new(values)
        dct = {
            "id": values[0],
            "unique_id": values[1],
            "ctime": values[2],
            "mtime": values[3],
            "user": values[4],
            "numbers": deblob(values[5], dtype=np.int32),
            "positions": deblob(values[6], shape=(-1, 3)),
            "cell": deblob(values[7], shape=(3, 3)),
        }
        if values[8] is not None:
            dct["pbc"] = (values[8] & np.array([1, 2, 4])).astype(bool)
        if values[9] is not None:
            dct["initial_magmoms"] = deblob(values[9])
        if values[10] is not None:
            dct["initial_charges"] = deblob(values[10])
        if values[11] is not None:
            dct["masses"] = deblob(values[11])
        if values[12] is not None:
            dct["tags"] = deblob(values[12], np.int32)
        if values[13] is not None:
            dct["momenta"] = deblob(values[13], shape=(-1, 3))
        if values[14] is not None:
            dct["constraints"] = values[14]
        if values[15] is not None:
            dct["calculator"] = values[15]
        if values[16] is not None:
            dct["calculator_parameters"] = decode(values[16])
        if values[17] is not None:
            dct["energy"] = values[17]
        if values[18] is not None:
            dct["free_energy"] = values[18]
        if values[19] is not None:
            dct["forces"] = deblob(values[19], shape=(-1, 3))
        if values[20] is not None:
            dct["stress"] = deblob(values[20])
        if values[21] is not None:
            dct["dipole"] = deblob(values[21])
        if values[22] is not None:
            dct["magmoms"] = deblob(values[22])
        if values[23] is not None:
            dct["magmom"] = values[23]
        if values[24] is not None:
            dct["charges"] = deblob(values[24])
        if values[25] is not None:
            dct["natoms_in_sc_2"] = values[25]
        if values[26] is not None:
            dct["natoms_in_sc_3"] = values[26]
        if values[27] is not None:
            dct["sc_matrix_2"] = jsonio.decode(values[27])
        if values[28] is not None:
            dct["sc_matrix_3"] = jsonio.decode(values[28])
        if values[29] is not None:
            dct["forces_2"] = deblob(values[29], shape=(-1, values[25], 3))
        if values[30] is not None:
            dct["forces_3"] = deblob(values[30], shape=(-1, values[26], 3))
        if values[31] is not None:
            dct["displacement_dataset_2"] = decode(values[31])
        if values[32] is not None:
            dct["displacement_dataset_3"] = decode(values[32])
        if values[33] is not None:
            dct["qmesh"] = jsonio.decode(values[33])
        if values[34] is not None:
            dct["phonon_dos_fp"] = decode(values[34])
        if values[35] is not None:
            dct["qpoints"] = decode(values[35])
        if values[36] is not None:
            dct["phonon_bs_fp"] = decode(values[36])
        if values[37] is not None:
            dct["tp_ZPE"] = values[37]
        if values[38] is not None:
            dct["tp_high_T_S"] = values[38]
        if values[39] is not None:
            dct["tp_T"] = dehexify(values[39])
        if values[40] is not None:
            dct["tp_A"] = dehexify(values[40])
        if values[41] is not None:
            dct["tp_S"] = dehexify(values[41])
        if values[42] is not None:
            dct["tp_Cv"] = dehexify(values[42])
        if values[43] is not None:
            dct["tp_kappa"] = dehexify(values[43], shape=(-1, 6))
        if values[44] is not None:
            dct["symprec"] = values[44]
        if values[len(self.columnnames) - 8] != "{}":
            dct["key_value_pairs"] = decode(values[len(self.columnnames) - 8])
        if (
            len(values) >= len(self.columnnames) - 6
            and values[len(self.columnnames) - 7] != "null"
        ):
            dct["data"] = decode(values[len(self.columnnames) - 7])
        return PhononRow(dct)

    def create_select_statement(
        self, keys, cmps, sort=None, order=None, sort_table=None, what="systems.*"
    ):
        """
        Creates a string that represents a select command in SQLite 3
        Args:
            keys: list of strs
                relevant keys to be included in the where part of the select commands
            cmps: list of tuples (key, op, val)
                a list of tuples representing what the where conditions for the query are
            sort: str
                Sort rows after key.  Prepend with minus sign for a decending sort.
            order:
                the order for the sort table
            sort_table:
                sort table for the query
            what: str
                The table to be accessed
        Returns:
            sql: A lsit of SQL commands
            args: arguments for the SQL commands
        """
        tables = ["systems"]
        where = []
        args = []
        for key in keys:
            if key == "forces":
                where.append("systems.fmax IS NOT NULL")
            elif key == "strain":
                where.append("systems.smax IS NOT NULL")
            elif key in ["energy", "fmax", "smax", "constraints", "calculator"]:
                where.append("systems.{} IS NOT NULL".format(key))
            else:
                if "-" not in key:
                    q = "systems.id in (select id from keys where key=?)"
                else:
                    key = key.replace("-", "")
                    q = "systems.id not in (select id from keys where key=?)"
                where.append(q)
                args.append(key)

        # Special handling of "H=0" and "H<2" type of selections:
        bad = {}
        for key, op, value in cmps:
            if isinstance(key, int):
                bad[key] = bad.get(key, True) and ops[op](0, value)
        temp = None
        for key, op, value in cmps:
            if key == "tp_T":
                if op != "=":
                    raise ValeError("For temperature searches the operator must be =")
                else:
                    temp = hex(struct.unpack(">Q", struct.pack(">d", value))[0])
        for key, op, value in cmps:
            if key == "tp_T":
                continue
            elif key in check_keys:
                if key == "user" and self.version >= 2:
                    key = "username"
                elif key == "pbc":
                    assert op in ["=", "!="]
                    value = int(np.dot([x == "T" for x in value], [1, 2, 4]))
                elif key == "magmom":
                    assert self.version >= 6, "Update your db-file"
                elif key == "sc_matrix_2":
                    value = self.encode(list(np.asarray(value).flatten()))
                elif key == "sc_matrix_3":
                    value = self.encode(list(np.asarray(value).flatten()))
                where.append("systems.{}{}?".format(key, op))
                args.append(value)
            elif key in ["tp_A", "tp_S", "tp_Cv", "tp_kappa"]:
                if temp is None:
                    raise ValeError(
                        "If selecting with a thermal property a temperature must also be given."
                    )
                op_actual = op
                if value < 0.0:
                    if op == "<":
                        op_actual = ">"
                    elif op == ">":
                        op_actual = "<"
                    elif op == "<=":
                        op_actual = ">="
                    elif op == ">=":
                        op_actual = "<="
                if self.type == "postgresql":
                    where.append(
                        "SUBSTR({}, POSITION('{}' IN systems.tp_T), 18){}?".format(
                            key, temp, op_actual
                        )
                    )
                else:
                    where.append(
                        "SUBSTR({}, INSTR(systems.tp_T,'{}'), 18){}?".format(
                            key, temp, op_actual
                        )
                    )
                args.append(hex(struct.unpack(">Q", struct.pack(">d", value))[0]))
            elif key in ["hashes", "hash"]:
                if key == "hashes":
                    assert isinstance(value, list)
                elif key == "hash":
                    if isinstance(value, str):
                        value = [value]
                if self.type == "postgresql":
                    for hh in value:
                        where.append(
                            "POSITION('{}' IN systems.key_value_pairs ->> 'hashes')>?".format(
                                hh
                            )
                        )
                        args.append(0)
                else:
                    for hh in value:
                        where.append(
                            "INSTR(systems.key_value_pairs,'{}')>?".format(
                                hh
                            )
                        )
                        args.append(0)
            elif isinstance(key, int):
                if self.type == "postgresql":
                    where.append(
                        "cardinality(array_positions("
                        + "numbers::int[], ?)){}?".format(op)
                    )
                    args += [key, value]
                else:
                    if bad[key]:
                        where.append(
                            "systems.id not in (select id from species "
                            + "where Z=? and n{}?)".format(invop[op])
                        )
                        args += [key, value]
                    else:
                        where.append(
                            "systems.id in (select id from species "
                            + "where Z=? and n{}?)".format(op)
                        )
                        args += [key, value]
            elif self.type == "postgresql":
                jsonop = "->"
                if isinstance(value, basestring):
                    jsonop = "->>"
                elif isinstance(value, bool):
                    jsonop = "->>"
                    value = str(value).lower()
                where.append(
                    "systems.key_value_pairs {} '{}'{}?".format(jsonop, key, op)
                )
                args.append(str(value))
            elif isinstance(value, basestring):
                where.append(
                    "systems.id in (select id from text_key_values "
                    + "where key=? and value{}?)".format(op)
                )
                args += [key, value]
            else:
                where.append(
                    "systems.id in (select id from number_key_values "
                    + "where key=? and value{}?)".format(op)
                )
                args += [key, float(value)]

        if sort:
            if sort_table != "systems":
                tables.append("{} AS sort_table".format(sort_table))
                where.append("systems.id=sort_table.id AND " "sort_table.key=?")
                args.append(sort)
                sort_table = "sort_table"
                sort = "value"

        sql = "SELECT {} FROM\n  ".format(what) + ", ".join(tables)
        if where:
            sql += "\n  WHERE\n  " + " AND\n  ".join(where)
        if sort:
            sql += "\nORDER BY {0}.{1} IS NULL, {0}.{1} {2}".format(
                sort_table, sort, order
            )
        return sql, args

    def _select(
        self,
        keys,
        cmps,
        explain=False,
        verbosity=0,
        limit=None,
        offset=0,
        sort=None,
        include_data=True,
        columns="all",
    ):
        """
        Command to access a row in the database
        Args:
            keys: list of strs
                relevant keys to be included in the where part of the select commands
            cmps: list of tuples (key, op, val)
                a list of tuples representing what the where conditions for the query are
            explain: bool
                Explain query plan.
            verbosity: int
                Possible values: 0, 1 or 2.
            limit: int or None
                Limit selection.
            offset: int
                Offset into selected rows.
            sort: str
                Sort rows after key.  Prepend with minus sign for a decending sort.
            include_data: bool
                Use include_data=False to skip reading data from rows.
            columns: 'all' or list of str
                Specify which columns from the SQL table to include.
                For example, if only the row id and the energy is needed,
                queries can be speeded up by setting columns=['id', 'energy'].
            Yields:
                a row from the database that matches the query
            """
        con = self._connect()
        self._initialize(con)
        values = np.array([None for i in range(len(self.columnnames) - 6)])
        values[len(self.columnnames) - 8] = "{}"
        values[len(self.columnnames) - 7] = "null"
        if "fc_2" in columns and not "natoms_in_sc_2" in columns:
            columns = "all"
        if "fc_3" in columns and not "natoms_in_sc_3" in columns:
            columns = "all"
        if columns == "all":
            columnindex = list(range(len(self.columnnames) - 7))
        else:
            columnindex = [
                c
                for c in range(0, len(self.columnnames) - 7)
                if self.columnnames[c] in columns
            ]
        if include_data:
            columnindex.append(len(self.columnnames) - 7)
        check_sort = [
            "id"
            "energy"
            "username"
            "calculator"
            "ctime"
            "mtime"
            "magmom"
            "pbc"
            "fmax"
            "smax"
            "volume"
            "mass"
            "charge"
            "natoms"
        ]
        if sort:
            if sort[0] == "-":
                order = "DESC"
                sort = sort[1:]
            else:
                order = "ASC"
            if sort in check_sort:
                sort_table = "systems"
            else:
                for dct in self._select(
                    keys + [sort],
                    cmps=[],
                    limit=1,
                    include_data=False,
                    columns=["key_value_pairs"],
                ):
                    if isinstance(dct["key_value_pairs"][sort], basestring):
                        sort_table = "text_key_values"
                    else:
                        sort_table = "number_key_values"
                    break
                else:
                    # No rows.  Just pick a table:
                    sort_table = "number_key_values"

        else:
            order = None
            sort_table = None
        what = ", ".join(
            "systems." + name
            for name in np.array(self.columnnames)[np.array(columnindex)]
        )
        sql, args = self.create_select_statement(
            keys, cmps, sort, order, sort_table, what
        )
        if explain:
            sql = "EXPLAIN QUERY PLAN " + sql
        if limit:
            sql += "\nLIMIT {0}".format(limit)
        if offset:
            sql += "\nOFFSET {0}".format(offset)
        if verbosity == 2:
            print(sql, args)
        cur = con.cursor()
        cur.execute(sql, args)
        if explain:
            for row in cur.fetchall():
                yield {"explain": row}
        else:
            n = 0
            for shortvalues in cur.fetchall():
                values[columnindex] = shortvalues
                yield self._convert_tuple_to_row(tuple(values))
                n += 1

            if sort and sort_table != "systems":
                # Yield rows without sort key last:
                if limit is not None:
                    if n == limit:
                        return
                    limit -= n
                for row in self._select(
                    keys + ["-" + sort],
                    cmps,
                    limit=limit,
                    offset=offset,
                    include_data=include_data,
                    columns=columns,
                ):
                    yield row

    def _initialize(self, con):
        """
        Initializes the database connection/the database
        Args:
            con: Connection object to the database
        """
        if self.initialized:
            return

        self._metadata = {}

        cur = con.execute('SELECT COUNT(*) FROM sqlite_master WHERE name="systems"')

        if cur.fetchone()[0] == 0:
            for statement in init_statements:
                con.execute(statement)
            if self.create_indices:
                for statement in index_statements:
                    con.execute(statement)
            con.commit()
            self.version = VERSION
        else:
            cur = con.execute(
                'SELECT COUNT(*) FROM sqlite_master WHERE name="user_index"'
            )
            if cur.fetchone()[0] == 1:
                # Old version with "user" instead of "username" column
                self.version = 1
            else:
                try:
                    cur = con.execute(
                        'SELECT value FROM information WHERE name="version"'
                    )
                except sqlite3.OperationalError:
                    self.version = 2
                else:
                    self.version = int(cur.fetchone()[0])

                cur = con.execute('SELECT value FROM information WHERE name="metadata"')
                results = cur.fetchall()
                if results:
                    self._metadata = json.loads(results[0][0])

        if self.version > VERSION:
            raise IOError(
                "Can not read new ase.db format "
                "(version {}).  Please update to latest ASE.".format(self.version)
            )
        if self.version < 5 and not self._allow_reading_old_format:
            raise IOError(
                "Please convert to new format. "
                + "Use: python -m ase.db.convert "
                + self.filename
            )
        self.initialized = True


if __name__ == "__main__":
    from hilde.phonon_db.phonon_db import connect

    con = connect(sys.argv[1])
    con._initialize(con._connect())
    print("Version:", con.version)
