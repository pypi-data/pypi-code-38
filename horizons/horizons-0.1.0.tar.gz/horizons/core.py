from dataclasses import dataclass
from horizons.parse_table import parse_table
import logging
import re
from telnetlib import Telnet


logger = logging.getLogger(__name__)


class HorizonsException(Exception):
    pass


@dataclass
class VectorsResult:
    """Class for storing the result of a vectors query."""
    epoch_jd_tdb: float
    calendar_date_tdb: str
    pos_km: (float, float, float)
    vel_kmps: (float, float, float)


@dataclass
class BodyResult:
    """Class for storing the result of a body query."""
    id: str
    name: str
    designation: str
    other: str


class Horizons:
    TIMEOUT = 4  # seconds
    PLANET_IDS = [f'{i}99' for i in range(1, 10)]

    def __init__(self, url='horizons.jpl.nasa.gov', port=6775):
        # connect
        self.tn = Telnet(url, port)
        self._expect('Horizons> ')
        logger.info('connected to HORIZONS')

        # disable scrolling
        self._write('PAGE')
        self._expect('Output PAGING toggled OFF.')
        self._expect('Horizons> ')

        # cache major bodies
        self._major_bodies = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._write('X')
        self.tn.close()
        return True

    def _write(self, command):
        self.tn.write(command.encode('utf-8'))
        self.tn.write(b'\r\n')

    def _expect(self, *expected):
        """Read until a string shows up in the output or a timeout occurs."""
        expected = list(map(re.escape, expected))
        return self._expect_regex(*expected)

    def _expect_regex(self, *expected):
        """Read until a pattern shows up in the output or a timeout occurs."""
        bytes_expected = list(map(str.encode, expected))
        r = self.tn.expect(bytes_expected, Horizons.TIMEOUT)
        output = r[2].decode('utf-8')
        if r[1] is None:
            logging.error(f'expected one of: {expected}')
            logging.error(f'actual:   \"{output}\"')
            raise HorizonsException(f'Unexpected output: {output}')
        logger.debug(f'output: {output}')
        return (r[0], r[1], output)

    def search_major_bodies(self, query: str):
        """Search the major bodies list. The result will be a subset of `Horizons.get_major_bodies()`.
        
        :query str: a search query, e.g. "Saturn" or "699"

        :returns a BodyResult list with all the matching major bodies
        """
        self._write(query)
        expect_result = self._expect('Select ... [F]tp, [M]ail, [R]edisplay, ?, <cr>: ')

        # clear space for next query
        self._write('')
        self._expect('Horizons> ')

        # split query output into lines
        output = expect_result[2]
        lines = output.split('\r\n')

        # trim the output to just the table
        last_line_index = next(i for (i, line) in enumerate(lines) if line.isspace())
        lines = lines[4:last_line_index]

        # parse the output as a table
        logger.debug('parsing lines as table')
        table = parse_table(lines)
        logger.debug('mapping table to BodyResult list')
        return list(map(
            lambda item: BodyResult(
                item['ID#'],
                item['Name'],
                item['Designation'],
                item['IAU/aliases/other'],
            ),
            table
        ))

    def get_major_bodies(self):
        """Get a list of all available major bodies.

        :return a BodyResult list
        """
        if not self._major_bodies:
            self._major_bodies = self.search_major_bodies('MB')
        return self._major_bodies

    def get_planets(self):
        """Get a list of all planets and also Pluto.

        :return a BodyResult list made up of all planets and Pluto.
        """
        return [b for b in self.get_major_bodies() if b.id in Horizons.PLANET_IDS]

    def get_moons(self, planet_id=None):
        """Get a list of all moons.

        :param planet_id: the ID of a planet to get moons for. Defaults to None, which will get all moons.

        :return a BodyResult list made up of all moons of the specified planet.
        """
        if planet_id and planet_id not in Horizons.PLANET_IDS:
            raise HorizonsException(f'{planet_id} is not a planet ID')

        moons = []
        for b in self.get_major_bodies():
            # Moon IDs have the same first digit as the planet they orbit and are three digits long.
            # For example, Earth's ID is 399. The Moon's ID is 301.
            # There are also special cases to avoid: negative IDs or Lagrange points.
            if all([
                len(b.id) == 3,
                b.id not in Horizons.PLANET_IDS,
                b.id[0] != '-',
                (not planet_id or planet_id[0] == b.id[0]),
                'Lagrangian' not in b.other,
            ]):
                moons.append(b)

        return moons

    def get_vectors(self, body_id: str, center='sun', ref='eclip', epoch_jd_tdb=2458642.5):
        """Get position and velocity vectors for a body.

        :param body_id: the body ID as used in Horizons.BodyResult
        :param center: the ID of a center body (defaults to sun)
        :param ref: the reference frame (can be eclip, frame, or body; defaults to eclip)
        :param date_jdtdb: the epoch to find vectors for (defaults to 2458642.5 i.e. June 9, 2019)

        :returns a VectorResult
        """
        # We're only interested in the vectors at the provided date, but the API insists we gather points over an
        # interval. We'll get two sets of vectors at the end but only return the first one (the start date).
        start_date = f'JD{epoch_jd_tdb}'
        end_date = f'JD{epoch_jd_tdb + 1}'

        # the center is assumed to be an Earth station code unless prefixed with an '@' sign
        center = f'@{center}'

        logging.info(f'getting vectors for {body_id} (center: {center}, ref: {ref}, epoch: {epoch_jd_tdb})')

        self._write(body_id)
        self._expect('Select ... [E]phemeris, [F]tp, [M]ail, [R]edisplay, ?, <cr>: ')
        self._write('E')
        self._expect('Observe, Elements, Vectors  [o,e,v,?] : ')
        self._write('V')
        expect_result = self._expect(
            'Coordinate center [ <id>,coord,geo  ] : ',
            'Use previous center  [ cr=(y), n, ? ] : '
        )
        if expect_result[0] == 1:
            # if the "previous center" option came up, reply No and prepare to be asked which center
            self._write('N')
            self._expect('Coordinate center [ <id>,coord,geo  ] : ')
        self._write(center)
        self._expect('Reference plane [eclip, frame, body ] : ')
        self._write(ref)
        self._expect_regex(r'Starting TDB \[.*\] : ')
        self._write(start_date)
        self._expect_regex(r'Ending   TDB \[.*\] : ')
        self._write(end_date)
        self._expect('Output interval [ex: 10m, 1h, 1d, ? ] : ')
        self._write('1d')
        self._expect('Accept default output [ cr=(y), n, ?] : ')
        self._write('N')
        self._expect('Output reference frame [J2000, B1950] : ')
        self._write('J2000')
        self._expect('Corrections [ 1=NONE, 2=LT, 3=LT+S ]  : ')
        self._write('LT')
        self._expect('Output units [1=KM-S, 2=AU-D, 3=KM-D] : ')
        self._write('KM-S')
        self._expect('Spreadsheet CSV format    [ YES, NO ] : ')
        self._write('YES')
        self._expect('Output delta-T (TDB-UT)   [ YES, NO ] : ')
        self._write('NO')
        self._expect('Select output table type  [ 1-6, ?  ] : ')
        self._write('2')
        expect_result = self._expect('>>> Select... [A]gain, [N]ew-case, [F]tp, [M]ail, [R]edisplay, ? : ')
        output = expect_result[2]
        self._write('N')
        self._expect('Horizons> ')

        # find the lines between $$SOE and $$EOE
        lines = output.split('\r\n')
        after_soe = False
        rows = []
        for line in lines:
            if line.startswith("$$EOE"):
                break
            elif line.startswith("$$SOE"):
                after_soe = True
            elif after_soe:
                rows.append(line)

        # the rows are JDTDB, Calendar Date (TDB), X, Y, Z, VX, VY, VZ
        results = []
        for row in rows:
            items = row.split(',')
            result = VectorsResult(
                float(items[0]),
                items[1].strip(),
                (
                    float(items[2]),
                    float(items[3]),
                    float(items[4]),
                ),
                (
                    float(items[5]),
                    float(items[6]),
                    float(items[7]),
                ),
            )
            results.append(result)

        return results[0]
