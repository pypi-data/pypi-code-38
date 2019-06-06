import os

import numpy as np

from ase.db.core import ops, now
from ase.db.jsondb import JSONDatabase
from ase.utils import basestring

from hilde.phonon_db.phonon_db import PhononDatabase
from hilde.phonon_db.row import PhononRow


class PhononJSONDatabase(PhononDatabase, JSONDatabase, object):
    """
    A modified ASE JSONDatabase to include phonopy objects, For missing functions see ase.db.jsondb
    """

    def _write(self, row, key_value_pairs, data, id):
        """
        Writes a phonopy object to the database
        Args:
            row: PhononRow object
                PhononRow object to be added to the database
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
        bigdct = {}
        ids = []
        nextid = 1
        if isinstance(self.filename, basestring) and os.path.isfile(self.filename):
            try:
                bigdct, ids, nextid = self._read_json()
            except (SyntaxError, ValueError):
                pass
        dct = {}
        for key in row.__dict__:
            if key[0] == "_" or key in row._keys or key == "id":
                continue
            dct[key] = row[key]
        dct["mtime"] = now()
        if key_value_pairs:
            dct["key_value_pairs"] = key_value_pairs
        if data:
            dct["data"] = data
        constraints = row.get("constraints")
        if constraints:
            dct["constraints"] = constraints
        if id is None:
            id = nextid
            ids.append(id)
            nextid += 1
        else:
            assert id in bigdct
        bigdct[id] = dct
        self._write_json(bigdct, ids, nextid)
        return id

    def _get_row(self, id):
        bigdct, ids, nextid = self._read_json()
        if id is None:
            assert len(ids) == 1
            id = ids[0]
        dct = bigdct[id]
        dct["id"] = id
        return PhononRow(dct)

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
        if explain:
            yield {"explain": (0, 0, 0, "scan table")}
            return
        if sort:
            if sort[0] == "-":
                reverse = True
                sort = sort[1:]
            else:
                reverse = False

            def f(row):
                return row.get(sort, missing)

            rows = []
            missing = []
            for row in self._select(keys, cmps):
                key = row.get(sort)
                if key is None:
                    missing.append((0, row))
                else:
                    rows.append((key, row))

            rows.sort(reverse=reverse, key=lambda x: x[0])
            rows += missing

            if limit:
                rows = rows[offset : offset + limit]
            for key, row in rows:
                yield row
            return
        try:
            bigdct, ids, nextid = self._read_json()
        except IOError:
            return
        if not limit:
            limit = -offset - 1
        cmps = [(key, ops[op], val) for key, op, val in cmps]
        n = 0
        for id in ids:
            if n - offset == limit:
                return
            dct = bigdct[id]
            if not include_data:
                dct.pop("data", None)
            row = PhononRow(dct)
            row.id = id
            for key in keys:
                if key not in row:
                    break
            else:
                temp = None
                for key, op, val in cmps:
                    if key == "tp_T":
                        assert op is ops["="]
                        temp = val
                for key, op, val in cmps:
                    if key == "sc_matrix_2":
                        if not isinstance(val, list):
                            val = list(val.flatten())
                    if key == "sc_matrix_3":
                        if not isinstance(val, list):
                            val = list(val.flatten())
                    if key == "tp_T":
                        continue
                    elif isinstance(key, int):
                        value = np.equal(row.numbers, key).sum()
                    elif key in ["tp_A", "tp_S", "tpCv"]:
                        value = row.get(key)[np.where(row.get("tp_T") == temp)[0]]
                    elif key in ["hashes", "hash"]:
                        hashes = []
                        for k, v in row.key_value_pairs.items():
                            if "hash" in k:
                                hashes.append(v)
                        value = val in hashes
                        val = True
                        op = ops["="]
                    else:
                        value = row.get(key)
                        if key == "pbc":
                            assert op in [ops["="], ops["!="]]
                            value = "".join("FT"[x] for x in value)
                    if value is None or not op(value, val):
                        break
                else:
                    if n >= offset:
                        yield row
                    n += 1
