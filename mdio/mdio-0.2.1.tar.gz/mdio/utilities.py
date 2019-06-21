import numpy as np
from scipy.spatial.distance import pdist
from pyparsing import Keyword, Word, Combine, Literal, Forward, Optional, nums, alphanums, ZeroOrMore

def process_name(token):
    return 'atom.name.strip()'

def process_index(token):
    return 'atom.index'

def process_mass(token):
    return 'atom.element.mass'

def process_symbol(token):
    return 'atom.element.symbol.strip()'

def process_resSeq(token):
    return 'atom.residue.resSeq'

def process_resid(token):
    return 'atom.residue.resindx'

def process_resname(token):
    return 'atom.residue.name.strip()'

def process_chainid(token):
    return 'atom.chain.chainID.strip()'

def process_all(token):
    return 'True'

def process_water(token):
    return 'atom.residue.name.strip() in ["SOL", "WAT", "HOH"]'

def process_protein(token):
    return 'atom.residue.name.strip() in ["ALA", "ASP", "ASN", "ASH", "CYS", \
                                  "GLY", "GLU", "GLN", "GLH", "HIS", \
                                  "HID", "HIE", "HIP", "LEU", "LYS", \
                                  "LYN", "ARG", "ARN", "MET", "PHE", \
                                  "PRO", "SER", "THR", "TYR", "VAL", \
                                  "ILE", "CYX", "CYH", "TRP"]'

def process_nucleic(token):
    return 'atom.residue.name.strip() in ["ADE", "CYT", "GUA", "THY", \
                                  "A", "C", "G", "T", "DA", "DC", "DG", "DT", \
                                  "DA5", "DC5", "DG5", "DT5", "DA3", "DC3", \
                                  "DG3", "DT3"]'
def torange(tokens):
    return 'in range({}, {})'.format(tokens[0], int(tokens[2]) + 1)

def process_string_expression(tokens):
    return '{} == {}'.format(tokens[0], tokens[1])

def process_short_num_expression(tokens):
    return '{} == {}'.format(tokens[0], tokens[1])

def quote(token):
    return '"{}"'.format(*token)

def create_parser():
    index_key = Keyword('index')
    index_key.setParseAction(process_index)
    name_key = Keyword('name')
    name_key.setParseAction(process_name)
    atom_num_key = index_key
    atom_string_key = name_key

    element_mass_key = Keyword('mass')
    element_mass_key.setParseAction(process_mass)
    element_symbol_key = Keyword('symbol')
    element_symbol_key.setParseAction(process_symbol)
    element_element_key = Keyword('element')
    element_element_key.setParseAction(process_symbol)
    element_num_key = element_mass_key
    element_string_key = element_symbol_key ^ element_element_key

    residue_residue_key = Keyword('residue')
    residue_residue_key.setParseAction(process_resSeq)
    residue_resSeq_key = Keyword('resSeq')
    residue_resSeq_key.setParseAction(process_resSeq)
    residue_resid_key = Keyword('resid')
    residue_resid_key.setParseAction(process_resid)
    residue_resname_key = Keyword('resname')
    residue_resname_key.setParseAction(process_resname)
    residue_string_key = residue_resname_key
    residue_num_key = residue_residue_key ^ residue_resSeq_key ^ residue_resid_key

    chain_chainid_key = Keyword('chainid')
    chain_chainid_key.setParseAction(process_chainid)
    chain_string_key = chain_chainid_key

    string_key = atom_string_key ^ element_string_key ^ residue_string_key ^ chain_string_key
    num_key = atom_num_key ^ element_num_key ^ residue_num_key

    string_value = Word(alphanums)
    string_value.setParseAction(quote)

    integer_value = Word(nums)
    real_value = Combine(integer_value*(None, None) + '.' + integer_value*(None, None))
    num_value = integer_value ^ real_value
    range_value = integer_value + 'to' + integer_value
    range_value.setParseAction(torange)

    string_expression = string_key + string_value
    string_expression.setParseAction(process_string_expression)

    relOp = Literal('==') ^ '>' ^ '>=' ^ '<' ^ '<=' ^ '!='
    full_num_expression = num_key + relOp + num_value
    short_num_expression = num_key + num_value
    short_num_expression.setParseAction(process_short_num_expression)
    num_expression = full_num_expression ^ short_num_expression

    range_expression = num_key + range_value

    all_expression = Keyword('all')
    all_expression.setParseAction(process_all)
    water_expression = Keyword('water')
    water_expression.setParseAction(process_water)
    nucleic_expression = Keyword('nucleic')
    nucleic_expression.setParseAction(process_nucleic)
    protein_expression = Keyword('protein')
    protein_expression.setParseAction(process_protein)

    basic_expression = string_expression ^ num_expression ^ range_expression ^ water_expression ^ protein_expression ^ all_expression ^ nucleic_expression
    expression = Forward()
    bracketed_expression = '(' + expression + ')'
    atom = basic_expression | bracketed_expression | expression
    andor = Keyword('and') ^ Keyword('or')
    expression << Optional('not') + atom + ZeroOrMore(andor + atom)

    return expression.parseString

def parse_selection(selection):
    parser = create_parser()
    return ' '.join(parser(selection))

def la2v(lengths, angles):
    alpha = angles[0] * np.pi / 180
    beta = angles[1] * np.pi / 180
    gamma = angles[2] * np.pi / 180

    a = np.array([lengths[0], 0.0, 0.0])
    b = np.array([lengths[1]*np.cos(gamma), lengths[1]*np.sin(gamma), 0.0])
    cx = lengths[2]*np.cos(beta)
    cy = lengths[2]*(np.cos(alpha) - np.cos(beta)*np.cos(gamma)) / np.sin(gamma)
    cz = np.sqrt(lengths[2]*lengths[2] - cx*cx - cy*cy)
    c = np.array([cx,cy,cz])

    v = np.array((a,b,c))
    # Make sure that all vector components that are _almost_ 0 are set exactly
    # to 0
    tol = 1e-6
    v[np.logical_and(v>-tol, v<tol)] = 0.0

    return v

def v2la(vectors):
    a = vectors[0]
    b = vectors[1]
    c = vectors[2]

    a_length = np.sqrt(np.sum(a*a))
    b_length = np.sqrt(np.sum(b*b))
    c_length = np.sqrt(np.sum(c*c))

    if min(a_length, b_length, c_length) == 0:
        a_length = 0.0
        b_length = 0.0
        c_length = 0.0
        alpha = 90.0
        beta = 90.0
        gamma = 90.0
    else:
        alpha = np.arccos(np.dot(b, c) / (b_length * c_length))
        beta = np.arccos(np.dot(c, a) / (c_length * a_length))
        gamma = np.arccos(np.dot(a, b) / (a_length * b_length))

        alpha = alpha * 180.0 / np.pi
        beta = beta * 180.0 / np.pi
        gamma = gamma * 180.0 / np.pi

    return [a_length, b_length, c_length], [alpha, beta, gamma]

class Imager(object):
    def __init__(self, unitcell_vectors):
        self.unitcell_vectors = unitcell_vectors
        if unitcell_vectors is not None:
            self.A = self.unitcell_vectors.T
            self.B = np.linalg.inv(self.A)

    def pack(self, xyz, centre_atom_indices=None):
        """
        Pack a set of coordinates into the periodic cell
        """
        if self.unitcell_vectors is None:
            return self
        if centre_atom_indices is not None:
            box_centre = np.matmul(self.A, [0.5, 0.5, 0.5])
            dv = box_centre - xyz[centre_atom_indices].mean(axis=0)
        else:
            dv = 0.0
        r = xyz + dv
        f = np.matmul(self.B, r.T)
        g = f - np.floor(f)
        t = np.matmul(self.A, g)
        xyz_packed = t.T - dv
        return xyz_packed

    def image(self, vector):
        """
        Return an imaged vector
        """
        if not vector.shape == (3,):
            raise ValueError('Error: 3-element vector required.')
        dv = np.matmul(self.A, [0.5, 0.5, 0.5])
        r = vector + dv
        f = np.matmul(self.B, r.T)
        g = f - np.floor(f)
        t = np.matmul(self.A, g)
        v_packed = t.T - dv
        return v_packed

    def pdist(self, xyz):
        """
        pdist function with imaging.
        """
        result = None
        ucv = self.unitcell_vectors
        for i in [-0.5, 0.5]:
            for j in [-0.5, 0.5]:
                for k in [-0.5, 0.5]:
                    shift = ucv[0] * i + ucv[1] * j + ucv[2] * k
                    xyzt = self.pack(xyz + shift)
                    if result is None:
                        result = pdist(xyzt)
                    else:
                        result = np.stack((result, pdist(xyzt))).min(axis=0)
        return result

def selection_to_indices(selection, topology):
    if selection is None:
        return None

    if isinstance(selection, str):
        if topology is not None:
            indices = topology.select(selection)
        else:
            raise TypeError('Error - selection strings require a topology.')
    else:
        try:
            indices = list(selection)
        except:
            raise TypeError('Error - selection must be a string or list.')
    return indices
