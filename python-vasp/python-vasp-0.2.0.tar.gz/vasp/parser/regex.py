"""
Collections of regular expressions to be shared by different module
"""
import re


band = re.compile(r'^(\d+) ([^ ]+) ([^ ]+)$')
band_header = re.compile(r"^band No. band energies occupation$")
kpoint_header = re.compile(r"^k-point (\d+) : ([^ ]+) ([^ ]+) ([^ ]+)$")
spin_component_header = re.compile(r"^spin component ([12])$")

# This is for the outcar, every section seems to end by a long series of '-'
end_section = re.compile(r'-' * 30)

real_number = re.compile(r'(\+?-?\d+\.?\d*[Ee]?\+?-?\d*)')

# For poscar recognition
atom_header = re.compile(r' *([a-zA-Z]+) *')


def parse_vector(line, length, dtype, delimiter=r"\s+"):
    assert(isinstance(line, str))
    m = re.split(delimiter, line.strip())
    length = length or len(m)
    return [dtype(m[i]) for i in range(length)]
