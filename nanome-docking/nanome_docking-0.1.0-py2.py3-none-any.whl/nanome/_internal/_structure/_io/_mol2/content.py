class Content(object):
    def __init__(self):
        self.name = ""
        self.molecules = []

    class Atom(object):
        def __init__(self):
            self.serial = 0
            self.name = "C"
            self.x = 0
            self.y = 0
            self.z = 0
            self.type = "C"
            self.subst_id = 0
            self.subst_name = ""
            self.charge = 0
            self.status_bits = ""

    class Bond(object):
        def __init__(self):
            self.serial = 0
            self.serial_atom1 = 0
            self.serial_atom2 = 0
            self.type = ""
            self.status_bits = ""

    class Molecule(object):
        def __init__(self):
            self.name = ""
            self.num_atoms = 0
            self.num_bonds = 0
            self.num_subst = 0
            self.num_feat = 0
            self.num_sets = 0
            self.mol_type = ""
            self.charge_type = ""
            self.status_bits = ""
            self.comments = ""
            self.atoms = []
            self.bonds = []
