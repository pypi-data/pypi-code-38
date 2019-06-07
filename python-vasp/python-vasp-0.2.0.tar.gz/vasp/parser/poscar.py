import vasp.utils
from vasp.parser.regex import parse_vector, atom_header


class Poscar:
    """
    This poscar parser *only* parses the poscar, it does not apply
    any transformation or conversion from cartesian into direct or
    otherwise.

    :param poscar_path: Path to a poscar file
    :type  poscar_path: str
    """

    def __init__(self, poscar_path):
        self.modeline = None #: Wether cartesian or direct
        self.basis = [] #: Basis elements
        self.name = "" #: Name of the system
        self.constant = None #: Multiplicative constant
        self.symbols = [] #: Atomic labels
        self.symbols_number = [] #: Atomic numbers
        self.natoms = None #: Number of atoms
        self.coordinates = [] #: Coordinates

        with open(poscar_path) as fd:
            self.lines = fd.readlines()
        self.parse()

    def parse(self):

        self.lines = vasp.utils.clean_lines(self.lines)
        self.name = self.lines.pop(0)
        self.constant = float(self.lines.pop(0))
        self.basis.append(parse_vector(self.lines.pop(0), 3, float))
        self.basis.append(parse_vector(self.lines.pop(0), 3, float))
        self.basis.append(parse_vector(self.lines.pop(0), 3, float))

        self.symbols = atom_header.findall(self.lines.pop(0))
        if not self.symbols:
            raise SyntaxError(
                "There is no description of the atoms in the poscar\n"
                "Please write explicitly the atoms appearing in the poscar"
            )

        self.symbols_number = parse_vector(
            self.lines.pop(0), len(self.symbols), int
        )
        self.natoms = sum(self.symbols_number)

        self.modeline = self.lines.pop(0)

        for i in range(self.natoms):
            self.coordinates.append(parse_vector(self.lines.pop(0), 3, float))
