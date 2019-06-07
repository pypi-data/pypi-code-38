import vasp.parser.poscar
from vasp.parser.regex import parse_vector


class Chgcar:

    def __init__(self, chgcar_path):
        self.poscar = vasp.parser.poscar.Poscar(chgcar_path)
        self.lines = self.poscar.lines
        self.grid = []
        self.values = []
        self.nvalues = None

        self.parse()

    def parse(self):
        self.grid = parse_vector(self.lines.pop(0), 3, int)
        self.nvalues = self.grid[0] * self.grid[1] * self.grid[2]
        values = []

        for line in self.lines:
            try:
                grid = parse_vector(line, 3, int)
            except ValueError:
                values.extend(parse_vector(line, None, float))
            else:
                # if we found again a grid, it means that it is spin polarized
                assert(self.grid == grid)
                self.values.append(values)
                values = []

        self.values.append(values)
