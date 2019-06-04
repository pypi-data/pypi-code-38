"""
PDB Objects
Set of classes for object-oriented processing of records from PDB files

(c) 2019  George D. Watson, University of York <https://georgewatson.me>
Available under an MIT license. See the LICENSE file.

Supports the following record types:
    ATOM
    HETATM
    TER
    HELIX
    SHEET
No other record types are currently implemented, but can be implemented upon
request.

Exposes the following classes:
    PDBRecord (should not normally be used directly, except to implement
        another record type)
    Residue
    Atom (for ATOM and HETATM records)
    Helix
    Sheet
    Ter

Exposes the following public functions:
    read_atom
    read_helix
    read_sheet
    read_ter
    read_record
    read_pdb

See class, function, and method docstrings for more information.
"""

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments


class PDBRecord:
    """
    A line from a PDB file
    This class should not normally be used directly;
    instead use one of its subclasses:
        Atom (for ATOM and HETATM records)
        Helix
        Sheet
        Ter
        Residue (for residues, normally components of other records)
    """
    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        """
        Output as a dict
        """
        return str(self.__dict__)


class Residue(PDBRecord):
    """
    A residue, as represented in a PDB file.
    This does not correspond directly to a particular PDB record,
    but is used as a component of many.
    This class has the following attributes:
        str name
        str chain
        int resid
        str insertion
    """
    def __init__(self, name=None, chain=None, resid=None, insertion=None):
        PDBRecord.__init__(self)
        self.name = name
        self.chain = chain
        self.resid = resid
        self.insertion = insertion

    def __eq__(self, other):
        return self.resid == other.resid

    def __gt__(self, other):
        return self.resid > other.resid

    def __lt__(self, other):
        return self.resid < other.resid

    def __contains__(self, atom):
        return atom.residue == self

    def __str__(self):
        return ''.join(['{:>3}'.format(self.name or ""),
                        " ",
                        self.chain or " ",
                        '{:>4}'.format(self.resid or ""),
                        self.insertion or " "])

    def alt_str(self):
        """
        Returns a string with an extra space between chain and resid,
        because the formats used by, e.g., HELIX & SSBOND records require this
        """
        return ''.join(['{:>3}'.format(self.name or ""),
                        " ",
                        self.chain or " ",
                        " ",
                        '{:>4}'.format(self.resid or ""),
                        self.insertion or " "])

    def is_nucleic(self):
        """
        Returns True if the residue is a standard nucleic acid residue
        """
        return any(map(self.name.upper().startswith,
                       ['DA', 'DC', 'DG', 'DT', 'DU']))

    def is_protein(self):
        """
        Returns True if the residue is a standard amino acid
        """
        return any(map(self.name.upper().startswith,
                       ['ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY',
                        'HI', 'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER',
                        'THR', 'TRP', 'TYR', 'VAL']))


class Atom(PDBRecord):
    """
    An ATOM or HETATM from a PDB
    This class has the following attributes:
        str in ['ATOM', 'HETATM'] record_type
        int num
        str name
        str alt_location
        Residue residue
        {'x':float, 'y':float,'z':float} coords
        float occupancy
        float temp_factor
        str segment
        str symbol
        str charge
    Public methods:
        is_element(str element)
        distance({'x':float,'y':float,'z':float} point = {'x':0,'y':0,'z':0}
    """
    def __init__(self, record_type='ATOM', num=None, name=None,
                 alt_location=None, residue=None, coords=None, occupancy=None,
                 temp_factor=None, segment=None, symbol=None, charge=None):
        PDBRecord.__init__(self)
        self.record_type = record_type
        self.num = num
        self.name = name
        self.alt_location = alt_location
        self.residue = residue
        self.coords = coords
        self.occupancy = occupancy
        self.temp_factor = temp_factor
        self.segment = segment
        self.symbol = symbol
        self.charge = charge

    def __eq__(self, other):
        return self.residue == other.residue and self.name == other.name

    def __gt__(self, other):
        return (self.residue > other.residue or
                (self.residue == other.residue and self.num > other.num))

    def __lt__(self, other):
        return (self.residue < other.residue or
                (self.residue == other.residue and self.num < other.num))

    def __str__(self):
        """
        Output in PDB format
        """
        # TODO: Correctly align the symbol within the name column
        return "".join(['{:6}'.format(self.record_type),
                        '{:>5}'.format(self.num or ""),
                        " ",
                        '{:4}'.format(self.name or ""),
                        self.alt_location or " ",
                        (self.residue or Residue()).__str__(),
                        " "*3,
                        '{:8.3f}'.format(self.coords['x'] or 0),
                        '{:8.3f}'.format(self.coords['y'] or 0),
                        '{:8.3f}'.format(self.coords['z'] or 0),
                        '{:6.2f}'.format(self.occupancy or 0),
                        '{:6.2f}'.format(self.temp_factor or 0),
                        " "*6,
                        '{:4}'.format(self.segment or ""),
                        '{:>2}'.format(self.symbol or ""),
                        '{:>2}'.format(self.charge or "")])

    def is_element(self, element):
        """
        Returns True if the atom is (probably) an instance of the element with
        the provided symbol.
        May struggle with unusual elements (like confusing C-alpha and Ca)
        if no explicit symbol is provided.
        """
        return ((self.symbol.upper() == element.upper()) if self.symbol
                else self.name.upper().startswith(element.upper()))

    def distance(self, point=None):
        """
        Returns the distance of an atom from a specified point
        (defaults to the origin)
        """
        if not point:
            point = {'x': 0, 'y': 0, 'z': 0}
        return pow(pow(self.coords['x'] - point['x'], 2) +
                   pow(self.coords['y'] - point['y'], 2) +
                   pow(self.coords['z'] - point['z'], 2), 0.5)


class Helix(PDBRecord):
    """
    A HELIX record from a PDB file
    This class has the following attributes:
        str=='HELIX' record_type
        int helix_num
        str helix_id
        Residue initial
        Residue terminal
        int helix_type
        str comment
        int length
    """
    def __init__(self, helix_num=None, helix_id=None, initial=None,
                 terminal=None, helix_type=1, comment=None, length=None):
        PDBRecord.__init__(self)
        self.record_type = 'HELIX'
        self.helix_num = helix_num
        self.helix_id = helix_id
        self.initial = initial
        self.terminal = terminal
        self.helix_type = helix_type
        self.comment = comment
        self.length = length

    def __eq__(self, other):
        return self.helix_num == other.helix_num

    def __gt__(self, other):
        return self.helix_num > other.helix_num

    def __lt__(self, other):
        return self.helix_num < other.helix_num

    def __str__(self):
        return "".join(['{:6}'.format(self.record_type),
                        " ",
                        '{:>3}'.format(self.helix_num or ""),
                        " ",
                        '{:3}'.format(self.helix_id or ""),
                        " ",
                        (self.initial or Residue()).alt_str(),
                        " ",
                        (self.terminal or Residue()).alt_str(),
                        '{:>2}'.format(self.helix_type),
                        '{:30}'.format(self.comment or ""),
                        " ",
                        '{:>5}'.format(self.length or "")])


class Sheet(PDBRecord):
    """
    A SHEET record from a PDB file
    This class has the following attributes:
        str=='SHEET' record_type
        int strand_num
        str sheet_id
        int num_strands
        Residue initial
        Residue terminal
        str sense
        {'current':Atom,'previous':Atom} hbond
    """
    def __init__(self, strand_num=None, sheet_id=None, num_strands=None,
                 initial=None, terminal=None, sense=None, hbond=None):
        PDBRecord.__init__(self)
        self.record_type = 'SHEET'
        self.strand_num = strand_num
        self.sheet_id = sheet_id
        self.num_strands = num_strands
        self.initial = initial
        self.terminal = terminal
        self.sense = sense
        self.hbond = hbond

    def __eq__(self, other):
        return (self.strand_num == other.strand_num and
                self.sheet_id == other.sheet_id)

    def __gt__(self, other):
        return (self.sheet_id > other.sheet_id or
                (self.sheet_id == other.sheet_id and
                 self.strand_num > other.strand_num))

    def __lt__(self, other):
        return (self.sheet_id < other.sheet_id or
                (self.sheet_id == other.sheet_id and
                 self.strand_num < other.strand_num))

    def __str__(self):
        """
        Output in PDB format
        """
        return "".join(['{:6}'.format(self.record_type),
                        " ",
                        '{:>3}'.format(self.strand_num or ""),
                        " ",
                        '{:>3}'.format(self.sheet_id or ""),
                        '{:>2}'.format(self.num_strands or ""),
                        " ",
                        (self.initial or Residue()).__str__(),
                        " ",
                        (self.terminal or Residue()).__str__(),
                        '{:>2}'.format(self.sense or ""),
                        " ",
                        '{:4}'.format(self.hbond['current'].name or ""),
                        (self.hbond['current'].residue or Residue()).__str__(),
                        " ",
                        '{:4}'.format(self.hbond['previous'].name or ""),
                        (self.hbond['previous'].residue or
                         Residue()).__str__()])


class Ter(PDBRecord):
    """
    A TER record from a PDB file
    This class has the following attributes:
        str=='TER' record_type
        int num
        Residue residue
    """
    def __init__(self, num=None, residue=None):
        PDBRecord.__init__(self)
        self.record_type = 'TER'
        self.num = num
        self.residue = residue

    def __eq__(self, other):
        return self.residue == other.residue

    def __gt__(self, other):
        return self.residue > other.residue

    def __lt__(self, other):
        return self.residue < other.residue

    def __str__(self):
        return "".join(['{:6}'.format(self.record_type),
                        '{:>5}'.format(self.num),
                        (self.residue or Residue()).__str__()])


def read_atom(line):
    """
    Reads an ATOM or HETATM from a PDB file into an Atom object
    """
    return Atom(record_type=line[:6].strip(),
                num=int(line[6:11]),
                name=line[12:16].strip(),
                alt_location=line[16:17].strip(),
                residue=Residue(name=line[17:21].strip(),
                                chain=line[21:22].strip(),
                                resid=int(line[22:26]),
                                insertion=line[26:27].strip()),
                coords={'x': float(line[30:38]),
                        'y': float(line[38:46]),
                        'z': float(line[46:54])},
                occupancy=float(line[54:60]),
                temp_factor=float(line[60:66]),
                segment=line[72:76].strip(),
                symbol=line[76:78].strip(),
                charge=line[78:80].strip())


def read_helix(line):
    """
    Reads a HELIX record from a PDB file into a Helix object
    """
    return Helix(helix_num=int(line[7:10]),
                 helix_id=line[11:14].strip(),
                 initial=Residue(name=line[15:19].strip(),
                                 chain=line[19:20].strip(),
                                 resid=int(line[21:25]),
                                 insertion=line[25:26].strip()),
                 terminal=Residue(name=line[27:31].strip(),
                                  chain=line[31:32].strip(),
                                  resid=int(line[33:37]),
                                  insertion=line[37:38].strip()),
                 helix_type=int(line[38:40]),
                 comment=line[40:70].strip(),
                 length=int(line[71:76]))


def read_sheet(line):
    """
    Reads a SHEET record from a PDB file into a Sheet object
    """
    return Sheet(strand_num=int(line[7:10]),
                 sheet_id=line[11:14].strip(),
                 num_strands=int(line[14:16]),
                 initial=Residue(name=line[17:21].strip(),
                                 chain=line[21:22].strip(),
                                 resid=int(line[22:26]),
                                 insertion=line[26:27].strip()),
                 terminal=Residue(name=line[28:32].strip(),
                                  chain=line[32:33].strip(),
                                  resid=int(line[33:37]),
                                  insertion=line[38:39].strip()),
                 sense=int(line[38:40]),
                 hbond={'current':
                        Atom(name=line[41:45].strip(),
                             residue=Residue(
                                 name=line[45:49].strip(),
                                 chain=line[49:50].strip(),
                                 resid=int(line[50:54]),
                                 insertion=line[54:55].strip())),
                        'previous':
                        Atom(name=line[56:60].strip(),
                             residue=Residue(
                                 name=line[60:64].strip(),
                                 chain=line[64:65].strip(),
                                 resid=int(line[65:69]),
                                 insertion=line[69:70].strip()))})


def read_ter(line):
    """
    Reads a TER record from a PDB file into a Ter object
    """
    return Ter(num=int(line[5:11]),
               residue=Residue(name=line[17:21].strip(),
                               chain=line[21:22].strip(),
                               resid=int(line[22:26]),
                               insertion=line[26:27].strip()))


def read_record(line):
    """
    Converts a line in PDB format to an appropriate PDBRecord object
    """
    if any(map(line.upper().startswith, ['ATOM', 'HETATM'])):
        return read_atom(line)

    if line.upper().startswith('TER'):
        return read_ter(line)

    if line.upper().startswith('HELIX'):
        return read_helix(line)

    if line.upper().startswith('SHEET'):
        return read_sheet(line)

    return None


def read_pdb(filename, types=None):
    """
    Reads a PDB file into a list of appropriate PDBRecord objects.
    Arguments:
        str filename
        opt [str in ['ATOM','HETATM','TER','HELIX','SHEET']] types
    """
    types = ['ATOM', 'HETATM', 'TER', 'HELIX', 'SHEET'] or types
    with open(filename, 'r') as pdb:
        records = filter(None, [read_record(line) for line in pdb])
    return [r for r in records if r.record_type in types]
