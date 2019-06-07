from collections import namedtuple
import vasp.utils
import vasp.parser.regex

Band = namedtuple('Band', ['number', 'energy', 'occupation', 'spin'])


class Kpoint:
    """
    Parse a kpoint text in a list of lines, e.g.:
    The spin has to be optional since we do not know in advance from
    the k-point chunk if it's spin 1 or 2, in vasp parlance.

    ::

         k-point     1 :       0.5000    0.5000    0.5000
          band No.  band energies     occupation
              1      -4.1306      2.00000
              2      -1.4815      2.00000
              3       4.2930      2.00000
              4       4.2930      2.00000
              5       7.0479      0.00000
              6       8.8314      0.00000
              7       8.8314      0.00000
              8      13.2218      0.00000

    :param lines: Lines containing an outcar kpoint chunk
    :type  lines: list
    :param spin: Wether it is spin polarized or no, (``ISPIN=1,2``)
    :type  spin: parameter_type
    """
    def __init__(self, lines, spin=None):
        self.lines = lines
        self.value = [] #: The value of the k-point
        self.spin = spin #: Original `ISPIN`
        self.index = None #: K-point index
        self.bands = [] #: A list of bands
        self.parse()
        assert(len(self.value) == 3)
        assert(len(self.bands) > 0)

    def parse(self):
        self.lines = vasp.utils.clean_lines(self.lines)

        kpoint_header = self.lines[0]
        m = vasp.parser.regex.kpoint_header.match(kpoint_header)
        if not m:
            raise SyntaxError(
                'The header of the kpoint is not what is expected\n'
                'header = "{0}"'.format(kpoint_header)
            )
        else:
            self.index = int(m.group(1))
            self.value = [float(m.group(i)) for i in range(2, 5)]

        band_header = self.lines[1]
        m = vasp.parser.regex.band_header.match(band_header)
        if not m:
            raise SyntaxError(
                'The header of the bands is not what is expected\n'
                'header = "{0}"'.format(band_header)
            )

        # process bands
        for i in range(2, len(self.lines)):
            m = vasp.parser.regex.band.match(self.lines[i])
            if not m:
                raise SyntaxError(
                    'Error parsing band, check it!\n'
                    'band = "{0}"'.format(self.lines[i])
                )

            self.bands.append(
                Band(
                    number=int(m.group(1)),
                    energy=float(m.group(2)),
                    occupation=float(m.group(3)),
                    spin=self.spin,
                )
            )
