import nanome
from nanome._internal._structure import _Complex, _Molecule, _Chain, _Residue, _Atom, _Bond
from nanome.util import Logs

class Results(object):
    def __init__(self):
        self.saved_atoms = []
        self.saved_bonds = []

    class SavedAtom(object):
        def __init(self):
            self.serial = 0
            self.atom = None
            self.residue = None
            self.residue_serial = 0
            self.model_number = 0

    class SavedBond(object):
        def __init(self):
            self.serial_atom1 = 0
            self.serial_atom2 = 0
            self.bond = None
            self.serial = 0


def to_file(path, complex):
    lines = []
    molecule_number = 1
    full_result = Results()
    for molecule in complex._molecules:
        current_result = Results()
        serial_by_atom_serial = {}  #<long, int>
        atom_serial = 1
        bond_serial = 1
        residue_serial = 1

        chains = molecule._chains
        for chain in chains:
            for residue in chain._residues:
                for atom in residue._atoms:
                    serial_by_atom_serial[atom._serial] = atom_serial
                    saved_atom = Results.SavedAtom()
                    saved_atom.serial = atom_serial
                    saved_atom.atom = atom
                    saved_atom.residue = residue
                    saved_atom.model_number = molecule_number
                    current_result.saved_atoms.append(saved_atom)
                    full_result.saved_atoms.append(saved_atom)
                    atom_serial += 1
                residue_serial += 1
        for chain in chains:
            for residue in chain._residues:
                for bond in residue._bonds:
                    if bond._atom1._serial in serial_by_atom_serial and bond._atom2._serial in serial_by_atom_serial:
                        saved_bond = Results.SavedBond()
                        saved_bond.serial_atom1 = serial_by_atom_serial[bond._atom1._serial]
                        saved_bond.serial_atom2 = serial_by_atom_serial[bond._atom2._serial]
                        saved_bond.bond = bond
                        saved_bond.serial = bond_serial
                        current_result.saved_bonds.append(saved_bond)
                        full_result.saved_bonds.append(saved_bond)
                        bond_serial += 1
        add_molecule(lines, molecule)
        add_atoms(lines, current_result.saved_atoms)
        add_bonds(lines, current_result.saved_bonds)
        molecule_number += 1
    file_text = '\n'.join(lines)
    f = open(path, "w")
    f.write(file_text)
    f.close()
    return full_result


def add_molecule(lines, molecule):
    lines.append("@<TRIPOS>MOLECULE")
    lines.append(molecule._name)
    lines.append(" " + str(len(molecule.atoms)) + " " + str(len(molecule.bonds)) + " 0 0 0")
    lines.append("SMALL")
    lines.append("GASTEIGER")
    lines.append("")


def add_atoms(lines, saved_atoms):
    lines.append("@<TRIPOS>ATOM")
    for saved_atom in saved_atoms:
        atom = saved_atom.atom
        new_line = "      "
        new_line += str(saved_atom.serial)
        new_line += "  "
        new_line += atom._name
        new_line += "         "
        new_line += float_to_string(atom._position.x, 4)
        new_line += "    "
        new_line += float_to_string(atom._position.y, 4)
        new_line += "    "
        new_line += float_to_string(atom._position.z, 4)
        new_line += " "
        new_line += atom._name
        new_line += "     "
        new_line += atom.residue_serial
        new_line += "  "
        new_line += atom.residue._name
        lines.append(new_line)


def add_bonds(lines, saved_bonds):
    lines.append("@<TRIPOS>BOND")
    for saved_bond in saved_bonds:
        bond = saved_bond.bond
        new_line = "     "
        new_line += str(saved_bond.serial)
        new_line += "   "
        new_line += str(saved_bond.serial_atom1)
        new_line += "   "
        new_line += str(saved_bond.serial_atom2)
        new_line += "    "
        if bond._kind == _Bond.Kind.CovalentDouble:
            new_line += "2"
        elif bond._kind == _Bond.Kind.CovalentTriple:
            new_line += "3"
        else:
            new_line += "1"
        lines.append(new_line)


def float_to_string(value, digits):
    int_comp = int(value)
    string_val = str(round(value, digits))
    float_digits = len(string_val) - len(str(int_comp)) - 1
    if (int_comp == 0 and value < 0):
        float_digits -= 1
    for i in range(digits - float_digits):
        string_val += '0'
    return string_val
