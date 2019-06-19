import csv,re,logging,json
from pinky.smiles import smilin
from pinky.fingerprints import ecfp
from marshmallow import Schema, fields
from cockatoo import metric

logger = logging.getLogger(__name__)
_mol_cache = {}

class Compound(object):
    """
    This class represents a chemcial compound used in a cocktail.

    """
    
    def __init__(self, name, conc, unit, ph=None):
        """
        A compound requires a name, concentration, and a unit. For example:
            sodium chloride, 1.0, M

        :param str name: Name of the compound
        :param float conc: Concentration of the compound
        :param str unit: Unit of the concentration (ex. M, % w/v)
        :param float ph: ph of the compound in solution
            
        """
        self.name = name
        self.conc = conc
        self.unit = unit
        self.ph = ph
        self.molecular_weight = None
        self.density = None
        self.smiles = None

    def mol(self):
        if self.smiles in _mol_cache:
            return _mol_cache[self.smiles]

        mol = None
        if self.smiles is not None:
            try:
                mol = smilin(self.smiles)
                _mol_cache[self.smiles] = mol
            except:
                logger.critical("Invalid smiles format, failed to parse smiles for compound: %s" % self.name)

        return mol

    def fingerprint(self):
        """
        Compute the fingerprint for a compound

        :returns: The fingerprint sparse vector dict
            
        """
        try:
            return getattr(self, '_fp')
        except AttributeError:
            pass

        self._fp = {}
        if self.mol() is not None:
            self._fp = ecfp(self.mol())

        return self._fp

    def molarity(self):
        """
        Convert concentration of compound into molarity 
        
        :returns: The molar concentration or None if missing data

        """
        try:
            return getattr(self, '_molarity')
        except AttributeError:
            pass

        self._molarity = None

        # If missing unit bail
        if self.unit is None: return self._molarity

        if re.search(r'w/v', self.unit) and self.molecular_weight > 0:
            self._molarity = (self.conc * 10) / float(self.molecular_weight)
        elif re.search(r'v/v', self.unit) and self.molecular_weight > 0 and self.density is not None:
            self._molarity =  (self.conc * 0.01) * ((self.density / self.molecular_weight)*1000)
        elif self.unit.lower() == 'm':
            self._molarity = self.conc

        return self._molarity

    def __repr__(self):
        return "[ %s ]" % ", ".join(
            '%r' % i for i in [
                self.name,
                self.conc,
                self.unit,
                self.ph,
                self.smiles,
                self.molecular_weight,
                self.density
            ])


class Cocktail(object):
    """
    This class represents a cocktail.

    A cocktail is made of of one or more compounds.

    """

    def __init__(self, name, ph=None, components=None):
        """
        A cocktail requires a name and optionally a ph and an array of components.

        :param str name: Name of the cocktail
        :param float ph: Overall pH of the the cocktail (default: None)
        :param array components: An array of :class:`cockatoo.Compound` objects (default: [])
            
        """
        self.name = name
        self.ph = ph
        self.components = components if components is not None else []

    def __len__(self):
        """
        :returns: the number of components in the cocktail

        """
        return len(self.components)

    def add_compound(self, compound):
        """
        Add a compound to the cocktail.

        :param compound compound: The compound to add (:class:`cockatoo.Compound`)

        """
        self.components.append(compound)

    def fingerprint(self):
        """
        Compute the fingerprint for a cocktail

        :returns: The fingerprint sparse vector dict
            
        """
        try:
            return getattr(self, '_fp')
        except AttributeError:
            pass

        self._fp = {}
        for cp in self.components:
            if cp.fingerprint() is None: continue
            conc_molarity = cp.molarity()
            if conc_molarity == None: conc_molarity = 1
            for k,v in cp.fingerprint().items():
                self._fp[k] = self._fp.get(k, 0.0) + (float(v) * conc_molarity)
            
        if len(self._fp) == 0:
            self._fp = None

        return self._fp

    def __repr__(self):
        return "[ %s ]" % ", ".join('%r' % i for i in [self.name,len(self),self.ph])

class Screen(object):
    """
    This class represents a macromolecular crystallization screen.

    A screen is made of of one or more cocktails.

    """

    def __init__(self, name, cocktails=None):
        """
        A screen requires a name and optionally an array of cocktails.

        :param str name: Name of the screen
        :param array cocktails: An array of :class:`cockatoo.Cocktail` objects (default: [])
            
        """
        self.name = name
        self.cocktails = cocktails if cocktails is not None else []

    def __len__(self):
        """
        :returns: the number of components in the cocktail

        """
        return len(self.cocktails)

    def add_cocktail(self, cocktail):
        """
        Add a cocktail to the screen.

        :param cocktail cocktail: The cocktail to add (:class:`cockatoo.Cocktail`)

        """
        self.cocktails.append(cocktail)

    def print_stats(self):
        """
        Print summary stats for the screen.

        """
        cmap = {}
        for cocktail in self.cocktails:
            for c in cocktail.components:
                cmap[c.name] = cmap.get(c.name, 0) + 1

        print("Name: %s" % self.name)
        print("Wells: %s" % len(self))
        print("Distinct Compounds: %s" % len(cmap.keys()))
        for k in sorted(cmap, key=cmap.get, reverse=True):
            print("%s: %s" % (k, cmap[k]))

    def _set_summary_stats(self, path):
        """
        Set summary data for each compound (ex. mw,density,smiles).

        """
        cols = ['molecular_weight', 'density']
        data = {}
        with open(path) as csvfile:
            reader = csv.DictReader(csvfile, delimiter="\t")
            for row in reader:
                data[row['name'].lower()] = row
        
        for ck in self.cocktails:
            for cp in ck.components:
                if cp.name not in data:
                    logger.info("Missing summary data for compound: %s" % cp.name)
                    continue

                row = data[cp.name]
                for key in cols:
                    if key in row and len(row[key]) > 0:
                        setattr(cp, key, float(row[key]))
                    else:
                        setattr(cp, key, None)

                if 'smiles' in row and len(row['smiles']) > 0:
                    cp.smiles = row['smiles']
                    try:
                        mol = smilin(cp.smiles)
                    except:
                        logger.info("Invalid smiles format, failed to parse smiles for compound: %s" % cp.name)
                else:
                    logger.info("Missing smiles data for compound: %s" % cp.name)

    def json(self):
        schema = ScreenSerializer()
        return schema.dumps(self).data

    def __repr__(self):
        return "[ %s ]" % ", ".join([self.name,str(len(self))])


class CompoundSerializer(Schema):
    name = fields.String(default=None)
    conc = fields.Float(default=None)
    unit = fields.String(default=None)
    ph = fields.Float(default=None)
    smiles = fields.String(default=None)
    molecular_weight = fields.Float(default=None)
    density = fields.Float(default=None)

class CocktailSerializer(Schema):
    components = fields.Nested(CompoundSerializer, many=True)
    name = fields.String(default=None)
    ph = fields.Float(default=None)

class ScreenSerializer(Schema):
    cocktails = fields.Nested(CocktailSerializer, many=True)
    name = fields.String(default=None)

def loads(data):
    screen_json = json.loads(data, encoding="utf-8")
    return _parse_json(screen_json)

def load(path):
    with open(path) as f:
        screen_json = json.load(f, encoding="utf-8")
        return _parse_json(screen_json)

def _parse_json(screen_json):
    """
    Parse a screen in JSON format.

    It's assumed the screen was first converted from CSV using the
    'cockatoo-convert' command. If not, ensure all required attributes are
    present in JSON data.

    :param str name: Name of the screen
    :param str path: Path to file

    :returns: The screen (:class:`cockatoo.Screen`)
        
    """
    if 'name' not in screen_json:
        logger.critical('Invalid json, missing screen name')
        return None
    if 'cocktails' not in screen_json:
        logger.critical('Invalid json, no cocktails defined')
        return None

    screen = Screen(screen_json['name'])

    for ck in screen_json['cocktails']:
        cocktail = _parse_cocktail_json(ck)
        if cocktail is None:
            logger.critical('Invalid json for cocktail.. Skipping')
            continue

        screen.add_cocktail(cocktail)
    
    return screen

def parse_cocktail(path):
    """
    Parse a cocktail from JSON file
    """
    with open(path) as f:
        ck = json.load(f, encoding="utf-8")
        return _parse_cocktail_json(ck)


def parse_csv(name, path):
    """
    Parse a screen in CSV format.

    :param str name: Name of the screen
    :param str path: Path to file

    :returns: The screen (:class:`cockatoo.Screen`)
        
    """
    screen = Screen(name)

    with open(path) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Skip comments
            if re.search(r'^#', row[0]): continue
            cocktail = _parse_cocktail_csv(row)
            if cocktail is not None:
                screen.add_cocktail(cocktail)

    return screen


def _parse_float(val):
    try:
        val = float(val)
    except:
        val = None

    return val


def _parse_cocktail_json(ck):
    """
    Private function to parse cocktail data from JSON object

    See test screens for example of JSON format.

    :param dict ck: JSON object

    :returns: The cocktail (:class:`cockatoo.Cocktail`)

    """

    if 'name' not in ck:
        logger.critical('Invalid json, missing cocktail name.')
        return None
    if 'components' not in ck:
        logger.critical('Invalid json, no components defined')
        return None

    cocktail = Cocktail(ck['name'])
    for key in cocktail.__dict__.keys():
        if key == 'components' or key.startswith('_'): continue
        if key not in ck:
            logger.debug('Invalid json, missing cocktail attribute %s: ' % key)
            continue
        setattr(cocktail, key, ck[key])

    for cp in ck['components']:
        is_valid = True
        for key in ('conc', 'molecular_weight', 'name', 'smiles', 'unit'):
            if key not in cp:
                logger.critical('Invalid json, cocktail %s has compound missing required value %s: ' % (cocktail.name, key))
                is_valid = False

        if not is_valid:
            return None

        compound = Compound(cp['name'].encode('utf-8'), cp['conc'], cp['unit'])
        for key in compound.__dict__.keys():
            if key.startswith('_'): continue
            if key not in cp:
                continue
            setattr(compound, key, cp[key])

        # handle special case for tacsimate
        if re.search(r'tacsimate', compound.name, re.IGNORECASE):
            if not re.search(r'v\/v', compound.unit, re.IGNORECASE):
                logger.warning('Malformed line, tacsimate should be % v/v: {}'.format(compound))
                return None
            for c in _create_tacsimate(compound):
                cocktail.add_compound(c)
        else:
            cocktail.add_compound(compound)
                
    return cocktail

def _parse_cocktail_csv(row):
    """
    Private function to parse cocktail data from CSV row.

    The format for columns is assumed to be:

    name,overall_ph,[conc,unit,name,ph]*
    
     *repeated 1 or more times for each compound

    It's common to put the buffer as the first compound which will be used as
    the overall ph.

    See test screens for example of CSV format.

    :param str name: Name of the screen
    :param str path: Path to file

    :returns: The cocktail (:class:`cockatoo.Cocktail`)
        
    """
    cocktail = Cocktail(
        row[0].strip(),
        _parse_float(re.sub(r'(?i)ph\s*','', row[1].strip()))
    )

    if len(cocktail.name) <= 0:
        logger.warning('Malformed line, missing cocktail name: %s' % (row))
        return None

    ph_vals = []
    compounds = row[2:]
    if not len(compounds) % 4 == 0:
        logger.warning('Malformed line: %s' % (row))

    index = 0
    while index < len(compounds):
        compound = Compound(
            compounds[index+2].strip(),
            _parse_float(compounds[index].strip()),
            compounds[index+1].strip(),
            _parse_float(re.sub(r'(?i)ph\s*','', compounds[index+3].strip()))
        )

        if len(compound.name) > 0:
            compound.name = compound.name.lower()
        else:
            logger.warning('Malformed line, missing compound name: %s' % (row))
            return None

        if compound.conc is None:
            logger.warning('Malformed line, missing concentration value: %s' % (row))
            return None

        if compound.ph is not None:
            ph_vals.append(compound.ph)

        matches = re.search(r'^((?:peg|polyethylene\sglycol)[^\d]+)(\d+)', compound.name)

        # handle special case for tacsimate
        if re.search(r'tacsimate', compound.name, re.IGNORECASE):
            if not re.search(r'v\/v', compound.unit, re.IGNORECASE):
                logger.warning('Malformed line, tacsimate should be % v/v: {}'.format(row))
                return None
            for c in _create_tacsimate(compound):
                cocktail.add_compound(c)
        else:
            cocktail.add_compound(compound)

        index += 4

    ph = list(set(ph_vals))
    if cocktail.ph is not None:
        pass
    elif len(ph) == 1:
        cocktail.ph = ph[0]
    elif len(ph) > 1:
        logger.info("Multiple pH values found using the buffer (first one in list): %s" % cocktail)
        cocktail.ph = ph_vals[0]

    return cocktail

# XXX: Tacsimate is mixture. consider adding support for mixtures. For now we hardcode (yuck)
_TACSIMATE = [
    {'conc': 1.8305, 'name': 'malonic acid', 'smiles': 'C(C(=O)O)C(=O)O', 'unit': 'M', 'ph': 7.0, 'molecular_weight': 104.06146, 'density': None},
    {'conc': 0.25, 'name': 'ammonium citrate tribasic', 'smiles': 'C(C(=O)O)C(CC(=O)O)(C(=O)O)O.N.N.N', 'unit': 'M', 'ph': 7.0, 'molecular_weight': 243.21508, 'density': None},
    {'conc': 0.12, 'name': 'succinic acid', 'smiles': 'C(CC(=O)O)C(=O)O', 'unit': 'M', 'ph': 7.0, 'molecular_weight': 118.088, 'density': None},
    {'conc': 0.3, 'name': 'dl-malic acid', 'smiles': 'O=C(O)CC(O)C(=O)O', 'unit': 'M', 'ph': 7.0, 'molecular_weight': 134.0874, 'density': None},
    {'conc': 0.4, 'name': 'sodium acetate trihydrate', 'smiles': '[Na+].[O-]C(=O)C.O.O.O', 'unit': 'M', 'ph': 7.0, 'molecular_weight': 136.0796, 'density': None},
    {'conc': 0.5, 'name': 'sodium formate', 'smiles': '[Na+].[O-]C=O', 'unit': 'M', 'ph': 7.0, 'molecular_weight': 68.0072, 'density': None},
    {'conc': 0.16, 'name': 'ammonium tartrate dibasic', 'smiles': 'O=C(O)[C@H](O)[C@@H](O)C(=O)O.N.N', 'unit': 'M', 'ph': 7.0, 'molecular_weight': 184.1479, 'density': None}
]

def _create_tacsimate(cp):
    """
    Private function handle Tacsimate (actually a mixture). See:
    http://hamptonresearch.com/documents/product/hr000175_what_is_tacsimate_new.pdf

    """
    mixture = []
    for n in _TACSIMATE:
        mixture.append(Compound(
            n['name'],
            n['conc'] * (cp.conc * 0.01), # assume % v/v
            'M',
            cp.ph
        ))

        cp.smiles = n['smiles']
        cp.molecular_weight = n['molecular_weight']
        cp.density = n['density']

    return mixture

def distance(screen1, screen2, weights):
    """
    Compute the distance between two screens (from Newman et al. 2010).

    :param screen screen1: First screen
    :param screen screen2: Second screen
    :param array weights: weights

    :returns: The distance score between 0 and 1
        
    """
    sum1 = 0.0
    for c1 in screen1.cocktails:
        mini = 100000000
        for c2 in screen2.cocktails:
            distance = metric.distance(c1, c2, weights)
            if mini > distance:
                mini = distance
        sum1 += mini

    sum2 = 0.0
    for c1 in screen2.cocktails:
        mini = 100000000
        for c2 in screen1.cocktails:
            distance = metric.distance(c1, c2, weights)
            if mini > distance:
                mini = distance
        sum2 += mini

    score = ( (sum1/float(len(screen1))) + (sum2/float(len(screen2))) )/2.0
    return score

def internal_similarity(s, weights):
    """
    Compute the internal diversity within a screen (from Newman et al. 2010).

    :param screen s: The screen
    :param array weights: weights

    :returns: The diversity score between 0 and 1
        
    """
    sum_avg = 0
    for c1 in s.cocktails:
        isum = 0
        n = 0
        for c2 in s.cocktails:
            isum += metric.distance(c1, c2, weights)
            n += 1

        sum_avg += isum / n

    return sum_avg / len(s)
