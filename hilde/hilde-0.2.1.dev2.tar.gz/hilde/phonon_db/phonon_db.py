""" Defines the base class for the phonon database """
import numbers
import operator
import os
import re
import warnings
from pathlib import Path
import numpy as np

# Import ase
from ase.utils import Lock, basestring, PurePath
from ase.db.core import Database, lock, parse_selection, str_represents, now
from ase.calculators.calculator import all_properties, all_changes
from ase.parallel import world, DummyMPI, parallel_function, parallel_generator
from ase.data import atomic_numbers

try:
    from ase.symbols import string2symbols
except ModuleNotFoundError:
    from ase.atoms import string2symbols

# Import Hilde
from hilde.phonon_db.row import PhononRow

# File largely copied from ase.db.core modified to use PhononRows over AtomsRow

default_key_descriptions = {
    "id": ("ID", "Uniqe row ID", ""),
    "age": ("Age", "Time since creation", ""),
    "formula": ("Formula", "Chemical formula", ""),
    "user": ("Username", "", ""),
    "calculator": ("Calculator", "ASE-calculator name", ""),
    "energy": ("Energy", "Total energy", "eV"),
    "fmax": ("Maximum force", "", "eV/Ang"),
    "smax": ("Maximum stress", "", "`\\text{eV/Ang}^3`"),
    "pbc": ("PBC", "Periodic boundary conditions", ""),
    "charge": ("Charge", "", "|e|"),
    "mass": ("Mass", "", "au"),
    "magmom": ("Magnetic moment", "", "au"),
    "unique_id": ("Unique ID", "", ""),
    "volume": ("Volume", "Volume of unit-cell", "`\\text{Ang}^3`"),
}

reserved_keys = set(
    all_properties
    + all_changes
    + list(atomic_numbers)
    + [
        "id",
        "unique_id",
        "ctime",
        "mtime",
        "user",
        "momenta",
        "constraints",
        "natoms",
        "formula",
        "age",
        "calculator",
        "calculator_parameters",
        "key_value_pairs",
        "data",
    ]
)


seconds = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604_800,
    "M": 2_629_800,
    "y": 31_557_600,
}

longwords = {
    "s": "second",
    "m": "minute",
    "h": "hour",
    "d": "day",
    "w": "week",
    "M": "month",
    "y": "year",
}

ops = {
    "<": operator.lt,
    "<=": operator.le,
    "=": operator.eq,
    ">=": operator.ge,
    ">": operator.gt,
    "!=": operator.ne,
}

invop = {"<": ">=", "<=": ">", ">=": "<", ">": "<=", "=": "!=", "!=": "="}

word = re.compile("[_a-zA-Z][_0-9a-zA-Z]*$")

reserved_keys = set(
    all_properties
    + all_changes
    + list(atomic_numbers)
    + [
        "id",
        "unique_id",
        "ctime",
        "mtime",
        "user",
        "momenta",
        "constraints",
        "natoms",
        "formula",
        "age",
        "calculator",
        "calculator_parameters",
        "key_value_pairs",
        "data",
    ]
)

numeric_keys = set(["id", "energy", "magmom", "charge", "natoms", "natoms_in_Sc"])
numeric_keys = set(["id", "energy", "magmom", "charge", "natoms", "natoms_in_Sc"])


def check(key_value_pairs):
    """
    Checks the key value pairs to makes sure they are of the right format
    """
    for key, value in key_value_pairs.items():
        if not word.match(key) or key in reserved_keys:
            raise ValueError("Bad key: {}".format(key))
        try:
            string2symbols(key)
        except ValueError:
            pass
        else:
            warnings.warn(
                "It is best not to use keys ({0}) that are also a "
                'chemical formula.  If you do a "db.select({0!r})",'
                "you will not find rows with your key.  Instead, you wil get "
                "rows containing the atoms in the formula!".format(key)
            )
        if not isinstance(value, (numbers.Real, basestring, np.bool_)):
            print(key, value)
            raise ValueError("Bad value for {!r}: {}".format(key, value))
        if isinstance(value, basestring):
            for t in [int, float]:
                if str_represents(value, t):
                    raise ValueError(
                        "Value "
                        + value
                        + " is put in as string "
                        + "but can be interpreted as "
                        + "{}! Please convert ".format(t.__name__)
                        + "to {} using ".format(t.__name__)
                        + "{}(value) before ".format(t.__name__)
                        + "writing to the database OR change "
                        + "to a different string."
                    )


def connect(
    name,
    db_type="extract_from_name",
    create_indices=True,
    use_lock_file=True,
    append=True,
    serial=False,
):
    """Create connection to database.
    Modified to link to PhononDatabase types
    name: str
        Filename or address of database.
    db_type: str
        One of 'json', 'db', 'postgresql',
        (JSON, SQLite, PostgreSQL).
        Default is 'extract_from_name', which will guess the type
        from the name.
    use_lock_file: bool
        You can turn this off if you know what you are doing ...
    append: bool
        Use append=False to start a new database.
    """

    name = str(name)

    if db_type == "extract_from_name":
        if name is None:
            db_type = None
        elif not isinstance(name, basestring):
            db_type = "json"
        elif name.startswith("postgresql:/") or name.startswith("postgres:/"):
            db_type = "postgresql"
        else:
            db_type = os.path.splitext(name)[1][1:]
            if db_type == "":
                raise ValueError("No file extension or database type given")

    if db_type is None:
        return Database()

    if not append and world.rank == 0 and os.path.isfile(name):
        os.remove(name)

    if db_type != "postgresql":
        name = os.path.abspath(name)

    if db_type == "json":
        from hilde.phonon_db.phonon_jsondb import PhononJSONDatabase

        return PhononJSONDatabase(name, use_lock_file=use_lock_file, serial=serial)
    if db_type == "db":
        from hilde.phonon_db.phonon_sqlitedb import PhononSQLite3Database

        return PhononSQLite3Database(name, create_indices, use_lock_file, serial=serial)
    if db_type == "postgresql":
        from hilde.phonon_db.phonon_postgresqldb import PhononPostgreSQLDatabase

        return PhononPostgreSQLDatabase(name)
    raise ValueError("Unknown database type: " + type)


class PhononDatabase(Database):
    """Base class for all databases."""

    def __init__(
        self, filename=None, create_indices=True, use_lock_file=False, serial=False
    ):
        """Database object.
        Args:
            filename: str
                Filename of the database
            create_indices: bool

            serial: bool
                Let someone else handle parallelization.  Default behavior is
                to interact with the database on the master only and then
                distribute results to all slaves.
        """
        if isinstance(filename, basestring):
            filename = os.path.expanduser(filename)
        self.filename = filename
        self.create_indices = create_indices
        if use_lock_file and isinstance(filename, basestring):
            self.lock = Lock(filename + ".lock", world=DummyMPI())
        else:
            self.lock = None
        self.serial = serial
        self._metadata = None  # decription of columns and other stuff

    def _write(self, row, key_value_pairs, data, id=None):
        check(key_value_pairs)
        return 1

    def get_phonon(self, selection=None, get_id=False, **kwarg):
        """
        Gets a phonopy object from a database row
        Args:
            selection: selection criteria for the database query
            kwargs   : additional selection criteria not stored in selection
        Returns:
            the phonopy object of the row
        """
        row = self.get(selection, **kwarg)
        if get_id:
            return row.id, row.to_phonon()
        return row.to_phonon()

    def get_phonon3(self, selection=None, get_id=False, **kwarg):
        """
        Gets a phonopy object from a database row
        Args:
            selection: selection criteria for the database query
            kwargs   : additional selection criteria not stored in selection
        Returns:
            the phonopy object of the row
        """
        row = self.get(selection, **kwarg)
        if get_id:
            return row.id, row.to_phonon3()
        return row.to_phonon3()

    @parallel_function
    @lock
    def update(
        self,
        id,
        dct=None,
        phonon3=None,
        phonon=None,
        store_second_order=False,
        delete_keys=None,
        data=None,
        **add_key_value_pairs,
    ):
        """Update and/or delete key-value pairs of row(s).

        id: int
            ID of row to update.
        dct: dict
            Optionally update the row with a dict.
        phonon3: Phono3py object
            Optionally update the Phononpy data (positions, cell, ...).
        phonon: Phonopy object
            Optionally update the Phononpy data (positions, cell, ...).
        data: dict
            Data dict to be added to the existing data.
        delete_keys: list of str
            Keys to remove.

        Use keyword arguments to add new key-value pairs.

        Returns number of key-value pairs added and removed.
        """
        if delete_keys is None:
            delete_keys = []
        if not isinstance(id, numbers.Integral):
            if isinstance(id, list):
                err = (
                    "First argument must be an int and not a list.\n"
                    "Do something like this instead:\n\n"
                    "with db:\n"
                    "    for id in ids:\n"
                    "        db.update(id, ...)"
                )
                raise ValueError(err)
            raise TypeError("id must be an int")

        check(add_key_value_pairs)

        oldrow = self._get_row(id)
        if phonon3:
            row = PhononRow(phonon3=phonon3, store_second_order=store_second_order)
        elif phonon:
            row = PhononRow(phonon=phonon)
        elif dct:
            row = PhononRow(dct)

        # Copy over data, kvp, ctime, user and id
        row._data = oldrow._data
        kvp = oldrow.key_value_pairs
        row.__dict__.update(kvp)
        row._keys = list(kvp)
        row.ctime = oldrow.ctime
        row.user = oldrow.user
        row.id = id
        if "forces_2" not in row and "forces_2" in oldrow:
            row.forces_2 = oldrow.forces_2
        if "forces_3" not in row and "forces_3" in oldrow:
            row.forces_3 = oldrow.forces_3
        kvp = row.key_value_pairs

        n = len(kvp)
        for key in delete_keys:
            kvp.pop(key, None)
        n -= len(kvp)
        m = -len(kvp)
        kvp.update(add_key_value_pairs)
        hashes = []
        if "hashes" in kvp:
            temp_hashes = kvp.pop("hashes").split("_")
            for th in temp_hashes:
                if th not in hashes:
                    hashes.append(th)
        for key, val in kvp.items():
            if "hash" in key and val not in hashes:
                hashes.append(val)
        kvp["hashes"] = "_".join(hashes)
        m += len(kvp)

        moredata = data
        data = row.get("data", {})
        if moredata:
            data.update(moredata)
        if not data:
            data = None

        # Update the row with values in old row not in row
        for key, val in oldrow.__dict__.items():
            if key not in row:
                row[key] = val

        self._write(row, kvp, data, row.id)

        return m, n

    def write(
        self,
        dct=None,
        phonon3=None,
        phonon=None,
        key_value_pairs=None,
        data=None,
        id=None,
        **kwargs,
    ):
        """Write atoms to database with key-value pairs.

        atoms: Atoms object
            Write atomic numbers, positions, unit cell and boundary
            conditions.  If a calculator is attached, write also already
            calculated properties such as the energy and forces.
        key_value_pairs: dict
            Dictionary of key-value pairs.  Values must be strings or numbers.
        data: dict
            Extra stuff (not for searching).
        id: int
            Overwrite existing row.

        Key-value pairs can also be set using keyword arguments::

            connection.write(atoms, name='ABC', frequency=42.0)

        Returns integer id of the new row.
        """
        if data is None:
            data = {}
        if key_value_pairs is None:
            key_value_pairs = {}
        if phonon3:
            row = PhononRow(phonon3=phonon3, phonon=phonon)
        elif phonon:
            row = PhononRow(phonon=phonon)
        elif dct:
            row = PhononRow(dct=dct)
        row.user = os.getenv("USER")
        row.ctime = now()
        kvp = dict(key_value_pairs)  # modify a copy
        kvp.update(kwargs)
        hashes = []
        if "hashes" in kvp:
            temp_hashes = kvp.pop("hashes").split("_")
            for th in temp_hashes:
                if th not in hashes:
                    hashes.append(th)
        for key, val in kvp.items():
            if "hash" in key and val not in hashes:
                hashes.append(val)
        kvp["hashes"] = "_".join(hashes)
        id = self._write(row, kvp, data, id)
        return id

    @parallel_generator
    def select(
        self,
        selection=None,
        filter=None,
        explain=False,
        verbosity=1,
        limit=None,
        offset=0,
        sort=None,
        include_data=True,
        columns="all",
        **kwargs,
    ):
        """Select rows.

        Return PhononRow iterator with results.  Selection is done
        using key-value pairs and the special keys:

            formula, age, user, calculator, natoms, energy, magmom
            and/or charge.

        selection: int, str or list
            Can be:

            * an integer id
            * a string like 'key=value', where '=' can also be one of
              '<=', '<', '>', '>=' or '!='.
            * a string like 'key'
            * comma separated strings like 'key1<value1,key2=value2,key'
            * list of strings or tuples: [('charge', '=', 1)].
        filter: function
            A function that takes as input a row and returns True or False.
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
        """
        if sort:
            if sort == "age":
                sort = "-ctime"
            elif sort == "-age":
                sort = "ctime"
            elif sort.lstrip("-") == "user":
                sort += "name"
        keys, cmps = parse_selection(selection, **kwargs)
        for row in self._select(
            keys,
            cmps,
            explain=explain,
            verbosity=verbosity,
            limit=limit,
            offset=offset,
            sort=sort,
            include_data=include_data,
            columns=columns,
        ):
            if filter is None or filter(row):
                yield row
