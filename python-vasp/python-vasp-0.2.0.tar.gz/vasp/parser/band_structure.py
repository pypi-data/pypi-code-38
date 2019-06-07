import vasp.utils
import vasp.parser.regex
from vasp.parser.kpoint import Kpoint


class BandStructure:
    """
    This parser accepts an outcar file and parses the ``k-points``
    inside, right now it will parse all the ``k-points``, also if
    there are several ionic relaxation iterations.

    .. TODO: In the future, let also the posibility of reading from vasprun.xml

    :param outcar: Filepath of an outcar file
    :type  outcar: str
    """

    def __init__(self, outcar=None):
        #: A list of k-points, see :class:`vasp.parser.kpoint.Kpoint`
        self.kpoints = []
        if outcar is not None:
            with open(outcar) as fd:
                self.lines = fd.readlines()
            self.parse_outcar()

    def parse_outcar(self):
        self.lines = vasp.utils.clean_lines(self.lines)

        spin = None
        kpoint_lines = []
        kpoint_header_matched_before = False
        for line in self.lines:

            # Find spin component
            m = vasp.parser.regex.spin_component_header.match(line)
            if m:
                if kpoint_lines and kpoint_header_matched_before:
                    self.kpoints.append(Kpoint(kpoint_lines, spin=spin))
                spin = int(m.group(1))
                kpoint_header_matched_before = False
                kpoint_lines = []

            # Find start of kpoint
            m = vasp.parser.regex.kpoint_header.match(line)
            if m:
                if kpoint_lines and kpoint_header_matched_before:
                    self.kpoints.append(Kpoint(kpoint_lines, spin=spin))
                kpoint_header_matched_before = True
                kpoint_lines = []

            # Find end of section (-------)
            m = vasp.parser.regex.end_section.match(line)
            if m:
                if kpoint_lines and kpoint_header_matched_before:
                    self.kpoints.append(Kpoint(kpoint_lines, spin=spin))
                kpoint_header_matched_before = False
                kpoint_lines = []

            kpoint_lines.append(line)
