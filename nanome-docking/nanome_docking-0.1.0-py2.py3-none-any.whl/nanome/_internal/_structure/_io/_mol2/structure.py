from nanome._internal._structure import _Complex, _Molecule, _Chain, _Residue, _Bond, _Atom

def structure(content):
    complex = _Complex._create()
    for molecule in content.molecules:
        complex._molecules.append(structure_molecule(molecule))
    return complex


def structure_molecule(model):
    molecule = _Molecule._create()
    molecule._name = model.name

    chain = _Chain._create()
    chain._name = "M"
    molecule._chains.append(chain)
    residues = {}
    atoms_by_serial = {}

    for model_atom in model.atoms:
        residue_serial = model_atom.subst_id
        try:
            residue = residues[residue_serial]
        except KeyError:
            residue = _Residue._create()
            residue._name = model_atom.subst_name
            if residue._name == "":
                residue._name = "MOL" + residue_serial
        atom = _Atom._create()
        atom._serial = model_atom.serial
        atom._name = model_atom.name
        atom._symbol = atom._name
        atom._position.x = model_atom.x
        atom._position.y = model_atom.y
        atom._position.z = model_atom.z
        atoms_by_serial[atom._serial] = atom
        residue._atoms.append(atom)

    for model_bond in model.bonds:
        if model_bond.serial_atom1 in atoms_by_serial and model_bond.serial_atom2 in atoms_by_serial:
            bond = _Bond._create()
            bond._atom1 = atoms_by_serial[model_bond.serial_atom1]
            bond._atom2 = atoms_by_serial[model_bond.serial_atom2]
            if model_bond.type == "1":
                bond._kind = bond.Kind.CovalentSingle
            elif model_bond.type == "2":
                bond._kind = bond.Kind.CovalentDouble
            elif model_bond.type == "3":
                bond._kind = bond.Kind.CovalentTriple
            else:
                bond._kind = bond.Kind.CovalentSingle
            residue._bonds.append(bond)
    return molecule
