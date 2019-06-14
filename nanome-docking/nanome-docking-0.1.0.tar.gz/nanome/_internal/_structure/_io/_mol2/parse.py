from nanome.util import Logs
from .content import Content

def parse_lines(lines):
    try:
        return _parse_lines(lines)
    except:
        Logs.error("Could not read pdb")
        raise

class LineReader():
    def __init__(self, lines):
        self.__lines = [line.rstrip() for line in lines]
        self.__line_counter = 0
        self.__total_lines = len(self.__lines)

    def next_line(self):
        self.__line_counter += 1
        if self.__line_counter >= self.__total_lines:
            return None
        return self.__lines[self.__line_counter]

    def current_line_number(self):
        return self.__line_counter

    def back(self):
        self.__line_counter -= 1

def _parse_lines(lines):
    content = Content()
    line_reader = LineReader(lines)
    line = line_reader.next_line()
    while (line != None):
        try:
            if line == "@<TRIPOS>MOLECULE":
                record_molecule(content, line_reader)
            elif line == "@<TRIPOS>ATOM":
                record_atoms(content, line_reader)
            elif line == "@<TRIPOS>BOND":
                record_bonds(content, line_reader)
        except:
            Logs.error("LINE: " + line_reader.current_line_number())
            Logs.error("PDB Parsing error")
            raise
        line = line_reader.next_line()
    return content

def record_molecule(content, line_reader):
    molecule = Content.Molecule()
    name = line_reader.next_line()
    if not name or name.startswith("@<TRIPOS>"):
        raise Exception("Invalid molecule: name missing")
    molecule.name = name
    numbers = line_reader.next_line()
    if not numbers or numbers.startswith("@<TRIPOS>"):
        raise Exception("Invalid molecule: numbers missing")
    numbers_arr = numbers.split(' ')
    molecule.num_atoms = int(numbers_arr[0])
    try:
        molecule.num_bonds = int(numbers_arr[1])
        molecule.num_subst = int(numbers_arr[2])
        molecule.num_feat = int(numbers_arr[3])
        molecule.num_sets = int(numbers_arr[4])
    except:
        pass
    type = line_reader.next_line()
    if not type or type.startswith("@<TRIPOS>"):
        raise Exception("Invalid molecule: type missing")
    molecule.mol_type = type
    charge = line_reader.next_line()
    if not charge or charge.startswith("@<TRIPOS>"):
        raise Exception("Invalid molecule: charge missing")
    molecule.charge_type = charge
    while line_reader.next_line():
        continue
    content.molecules.append(molecule)

def record_atoms(content, line_reader):
    molecule = content.molecules[-1]
    line = line_reader.next_line()
    while line and not line.startswith("@<TRIPOS>"):
        arr = line.split()
        atom = record_atom(arr)
        molecule.atoms.append(atom)
        line = line_reader.next_line()
    if line.startswith("@<TRIPOS>"):
        line_reader.back()

def record_atom(line_arr):
    atom = Content.Atom()
    atom.serial = int(line_arr[0])
    atom.name = line_arr[1]
    atom.x = float(line_arr[2])
    atom.y = float(line_arr[3])
    atom.z = float(line_arr[4])
    atom.type = line_arr[5]
    try:
        atom.subst_id = int(line_arr[6])
        atom.subst_name = line_arr[7]
        atom.charge = float(line_arr[8])
        atom.status_bits = line_arr[9]
    except:
        pass
    return atom

def record_bonds(content, line_reader):
    molecule = content.molecules[-1]
    line = line_reader.next_line()
    while line and not line.startswith("@<TRIPOS>"):
        arr = line.split()
        bond = record_bond(arr)
        molecule.bonds.append(bond)
        line = line_reader.next_line()
    if line.startswith("@<TRIPOS>"):
        line_reader.back()

def record_bond(line_arr):
    bond = Content.Bond()
    bond.serial = int(line_arr[0])
    bond.serial_atom1 = int(line_arr[1])
    bond.serial_atom2 = int(line_arr[2])
    bond.type = line_arr[3]
    try:
        bond.status_bits = line_arr[4]
    except:
        pass
    return bond
