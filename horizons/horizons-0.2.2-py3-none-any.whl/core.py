from horizons.parse_table import parse_table
import logging
import re
import requests
from typing import NamedTuple, Tuple


logger = logging.getLogger(__name__)


class HorizonsException(Exception):
    pass


class VectorsResult(NamedTuple):
    """Class for storing the result of a vectors query."""
    epoch_jd_tdb: float
    calendar_date_tdb: str
    pos_km: Tuple[float, float, float]
    vel_kmps: Tuple[float, float, float]


class BodyResult(NamedTuple):
    """Class for storing the result of a body query."""
    id: str
    name: str
    designation: str
    other: str


class PhysicalProperty(NamedTuple):
    value: float
    uncertainty: float
    unit: str


class Horizons:
    PLANET_IDS = [f'{i}99' for i in range(1, 10)]
    SUN_ID = '10'

    def __init__(self, url='https://ssd.jpl.nasa.gov/horizons_batch.cgi'):
        self._session = requests.Session()
        self._url = url

        # cache major bodies and physical properties
        self._major_bodies = None
        self._physical_props = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._session.close()
        return True

    def _get(self, **options):
        params = {'batch': '1'}

        # make each key upper case and wrap the values in quotes
        for key, option in options.items():
            params[key.upper()] = f'\'{option.upper()}\''

        r = self._session.get(self._url, params=params)
        r.raise_for_status()
        logger.debug(f'output: {r.text}')
        return r.text

    def search_major_bodies(self, query: str):
        """Search the major bodies list. The result will be a subset of `Horizons.get_major_bodies()`.
        
        :query str: a search query, e.g. "Saturn" or "699"

        :returns a BodyResult list with all the matching major bodies
        """
        logger.debug(f'searching major bodies with query \'{query}\'')
        output = self._get(command=query)
        lines = output.split('\n')

        if not lines[1].startswith(' Multiple major-bodies match string'):
            raise HorizonsException('search gave unexpected result')

        # trim the output to just the table
        last_line_index = next(i for (i, line) in enumerate(lines) if line.isspace())
        lines = lines[3:last_line_index]

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

    def get_sun(self):
        return next(b for b in self.get_major_bodies() if b.id == Horizons.SUN_ID)

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

        :returns a VectorResult, or None if no vectors are available at the requested epoch
        """
        logger.info(f'getting vectors for {body_id} (center: {center}, ref: {ref}, epoch: {epoch_jd_tdb})')
        output = self._get(
            command=body_id,
            make_ephem='yes',
            table_type='vectors',
            center=f'@{center}',
            ref_plane=ref,
            tlist=str(epoch_jd_tdb),
            ref_system='j2000',
            out_units='km-s',
            vec_table='2',
            vec_corr='lt',
            csv_format='yes',
        )

        # find the lines between $$SOE and $$EOE
        lines = output.split('\n')
        after_soe = False
        rows = []
        for line in lines:
            if line.startswith("$$EOE"):
                break
            elif line.startswith("$$SOE"):
                after_soe = True
            elif after_soe:
                rows.append(line)

        # If $$SOE and $$EOE aren't found, there are no ephemerics for this body at this time
        # This is true for at least Daphnis
        if not rows:
            logger.warning(f'No ephemeris for {body_id}')
            return None

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

    def get_raw_physical_properties(self, body_id: str):
        """Get the physical properties of a major body.
        The format of physical properties returned by HORIZONS is inconsistent. This parsing is done on a best-effort
        basis.

        :param body_id: the ID of the body as returned by Horizons.get_major_bodies

        :returns a dictionary from property name to value. The available properties, their names, and the format of
            the value are inconsistent between bodies. Some values are dictionaries.
        """
        if body_id in self._physical_props:
            return self._physical_props[body_id]

        logger.info(f'getting phyiscal properties for {body_id}')

        output = self._get(
            command=body_id,
            make_ephem='no',
        )

        lines = output.split('\n')
        properties = _parse_physical_properties(lines)

        self._physical_props[body_id] = properties
        return properties

    def _get_physical_property(self, body_id: str, key: str):
        props = self.get_raw_physical_properties(body_id)
        props = _clean_properties(props)
        if key not in props:
            return None
        prop = props[key]
        return PhysicalProperty(
            prop['value'],
            prop['uncertainty'],
            prop['unit'],
        )

    def get_radius(self, body_id: str):
        """Get the radius of a major body

        :param body_id: the ID of the body as returned by Horizons.get_major_bodies

        :returns a dictionary with value, uncertainty, and unit, or None if no radius is found
        """
        return self._get_physical_property(body_id, 'radius')

    def get_mass(self, body_id: str):
        """Get the mass of a major body

        :param body_id: the ID of the body as returned by Horizons.get_major_bodies

        :returns a dictionary with value, uncertainty, and unit, or None is no mass is found
        """
        return self._get_physical_property(body_id, 'mass')


def _parse_physical_properties(lines):
    properties = {}
    building_prop = False
    building_prop_indent = None
    building_prop_key = None
    for line in lines:
        m = re.search(r"^\s\s(\S.+?)[\=|:](.+?)\s*([A-Z].+)[\=|:](.+)?$", line)
        if not m:
            continue

        properties[m.group(1).strip()] = m.group(2).strip()

        if not m.group(4):
            building_prop = True
            building_prop_indent = m.start(3)
            building_prop_key = m.group(3).strip()
            properties[building_prop_key] = {}
        elif building_prop and m.start(3) == building_prop_indent + 2:
            properties[building_prop_key][m.group(3).strip()] = m.group(4).strip()
        else:
            building_prop = False
            properties[m.group(3).strip()] = m.group(4).strip()

    return properties


def _parse_number(number: str):
    m = re.search(r"^~?([\d+|\.]\.?\d*)\s*(\+\-)?\s*(\d*\.?\d*)?(.+)?$", number)
    if not m:
        return None
    return {
        'value': float(m.group(1)),
        'uncertainty': float(m.group(3)) if m.group(3) else None,
        'unit': m.group(4) if m.group(4) else None,
    }


def _clean_properties(props):
    clean_props = {}
    for key, val in props.items():
        mass_match = re.search(r"^mass.*10\^(\d+).*kg.*$", key, re.IGNORECASE)
        if mass_match:
            exp = int(mass_match.group(1))
            number = _parse_number(val)
            if not number:
                logger.warning(f'failed to parse mass property: \"{val}\"')
            else:
                number['unit'] = 'kg'
                number['value'] *= 10**exp
                if number['uncertainty']:
                    number['uncertainty'] *= 10**exp

                clean_props['mass'] = number
            continue

        radius_match = re.search(r"^(vol\. )?(mean )?radius.*km.*$", key, re.IGNORECASE)
        if radius_match:
            number = _parse_number(val)
            if not number:
                logger.warning(f'failed to parse radius property: \"{val}\"')
            else:
                number['unit'] = 'km'
                clean_props['radius'] = number
            continue

    return clean_props
