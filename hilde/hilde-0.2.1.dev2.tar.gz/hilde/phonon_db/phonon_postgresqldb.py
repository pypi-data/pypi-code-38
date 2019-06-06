"""
This file is a copy of ase's postgresql class, it is copied so the function
overrides from PhononSQLite3Database persist
"""
import json

import numpy as np
from psycopg2 import connect
from psycopg2.extras import execute_values

import ase.io.jsonio
from ase.db.postgresql import jsonb_indices
from ase.db.postgresql import remove_nan_and_inf
from ase.db.postgresql import insert_nan_and_inf
from ase.db.postgresql import Connection
from ase.db.postgresql import Cursor

from hilde.phonon_db.phonon_sqlitedb import init_statements
from hilde.phonon_db.phonon_sqlitedb import index_statements
from hilde.phonon_db.phonon_sqlitedb import VERSION
from hilde.phonon_db.phonon_sqlitedb import PhononSQLite3Database


class PhononPostgreSQLDatabase(PhononSQLite3Database):
    """
    The copy of the ASE PostgreSQLDatabase to override PhononSQLite3Database
    functions
    """

    type = "postgresql"
    default = "DEFAULT"

    def encode(self, obj):
        return ase.io.jsonio.encode(remove_nan_and_inf(obj))

    def decode(self, obj):
        return insert_nan_and_inf(ase.io.jsonio.numpyfy(obj))

    def blob(self, array):
        """Convert array to blob/buffer object."""

        if array is None:
            return None
        if array.size == 0:
            array = np.zeros(0)
        if array.dtype == np.int64:
            array = array.astype(np.int32)
        return array.tolist()

    def deblob(self, buf, dtype=float, shape=None):
        """Convert blob/buffer object to ndarray of correct dtype and shape.

        (without creating an extra view)."""
        if buf is None:
            return None
        return np.array(buf, dtype=dtype)

    def _connect(self):
        return Connection(connect(self.filename))

    def _initialize(self, con):
        if self.initialized:
            return

        self._metadata = {}

        cur = con.cursor()
        cur.execute("show search_path;")
        schema = cur.fetchone()[0].split(", ")
        if schema[0] == '"$user"':
            schema = schema[1]
        else:
            schema = schema[0]

        cur.execute(
            """
        SELECT EXISTS(select * from information_schema.tables where
        table_name='information' and table_schema='{}');
        """.format(
                schema
            )
        )

        if not cur.fetchone()[0]:  # information schema doesn't exist.
            # Initialize database:
            sql = ";\n".join(init_statements)
            sql = schema_update(sql)
            cur.execute(sql)
            if self.create_indices:
                cur.execute(";\n".join(index_statements))
                cur.execute(";\n".join(jsonb_indices))
            con.commit()
            self.version = VERSION
        else:
            cur.execute("select * from information;")
            for name, value in cur.fetchall():
                if name == "version":
                    self.version = int(value)
                elif name == "metadata":
                    self._metadata = json.loads(value)

        assert 5 < self.version <= VERSION

        self.initialized = True

    def get_last_id(self, cur):
        cur.execute("SELECT last_value FROM systems_id_seq")
        id = cur.fetchone()[0]
        return int(id)


def schema_update(sql):
    for a, b in [
        ("REAL", "DOUBLE PRECISION"),
        ("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY"),
    ]:
        sql = sql.replace(a, b)

    arrays_1D = [
        "numbers",
        "initial_magmoms",
        "initial_charges",
        "masses",
        "tags",
        "momenta",
        "stress",
        "dipole",
        "magmoms",
        "charges",
        "tp_T",
        "tp_A",
        "tp_S",
        "tp_Cv",
    ]

    arrays_2D = ["positions", "cell", "forces", "tp_kappa"]

    arrays_3D = ["force_2", "force_3"]

    txt2jsonb = [
        "calculator_parameters",
        "key_value_pairs",
        "data",
        "qpoints",
        "phonon_bs_fp",
        "phonon_dos_fp",
        "displacement_dataset_2",
        "displacement_dataset_3",
    ]

    for column in arrays_1D:
        if column in ["numbers", "tags"]:
            dtype = "INTEGER"
        else:
            dtype = "DOUBLE PRECISION"
        sql = sql.replace("{} BLOB,".format(column), "{} {}[],".format(column, dtype))
    for column in arrays_2D:
        sql = sql.replace(
            "{} BLOB,".format(column), "{} DOUBLE PRECISION[][],".format(column)
        )

    for column in arrays_3D:
        sql = sql.replace(
            "{} BLOB,".format(column), "{} DOUBLE PRECISION[][][],".format(column)
        )

    for column in txt2jsonb:
        sql = sql.replace("{} TEXT,".format(column), "{} JSONB,".format(column))

    return sql
