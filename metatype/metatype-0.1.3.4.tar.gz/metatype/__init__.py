import os
import yaml
import hashlib

from metatype.defacto import KEYMAP as DEFACTO_KEYMAP
from metatype.mft1 import KEYMAP as MFT1_KEYMAP
from metatype.jsonld import KEYMAP as JSONLD_KEYMAP
from metatype.utils import classproperty, PropertyMeta
from metatype import config

from typology.utils import slug
from metawiki import url2ext

from dateutil.parser import parse as dateparse
from datetime import timezone, datetime


PRIORITY_SEQUENCE = [
    MFT1_KEYMAP,
    JSONLD_KEYMAP,
    DEFACTO_KEYMAP
]

try:
    dumper = yaml.CDumper
    loader = yaml.CLoader
except:
    dumper = yaml.Dumper
    loader = yaml.Loader
    print('''\
Using slower yaml.Dumper/Loader, install CDumper/CLoader to get faster results, by:
 apt install libyaml-dev
 pip --no-cache-dir install --verbose --force-reinstall -I pyyaml''')


class Dict(dict, metaclass=PropertyMeta):
    '''
    Accepts: any dictionary, that optionally has keys specifying:

    '-': item origin
    '*': item schema
    '+': item authorship (identity, keys and permissions)
    '^': item itentionality (fact, possibility, desire)
    '@': (optionally) item metadrive local drive name.

    https://book.mindey.com/metaformat/0002-data-object-format/0002-data-object-format.html

    Returns:
    Dict object, that encodes these attributes to python properties.

    '''
    _DRIVES = []

    @classproperty
    def drives(cls):
        return cls._DRIVES

    @classmethod
    def readin(cls, location, schema=None, limit=None):
        from tqdm import tqdm #noqa

        if os.path.exists(location):
            if os.path.isdir(location):

                n = 0
                for fname in tqdm(os.listdir(location)):
                    record = yaml.load(open(os.path.join(location,fname)).read(), Loader=loader)

                    if schema is not None:
                        import metaform #noqa
                        yield metaform.formatize(
                                metaform.normalize(record, schema))

                    else:
                        yield record

                    if limit is not None:
                        n += 1
                        if n >= limit:
                            break

            elif os.path.isfile(location):
                yield yaml.load(open(location).read(), Loader=loader)


    def set_id(self):
        if not hasattr(self, '_id'):
            self._id = None

        for keymap in PRIORITY_SEQUENCE:
            if keymap.get('_id') in self.keys():
                self._id = self.get(keymap.get('_id'))
                break

    def set_type(self):
        if not hasattr(self, '_type'):
            self._type = None

        for keymap in PRIORITY_SEQUENCE:
            if keymap.get('_type') in self.keys():
                self._type = self.get(keymap.get('_type'))
                break

    def set_auth(self):
        if not hasattr(self, '_auth'):
            self._auth = None

        for keymap in PRIORITY_SEQUENCE:
            if keymap.get('_auth') in self.keys():
                self._auth = self.get(keymap.get('_auth'))
                break

    def set_intent(self):
        if not hasattr(self, '_intent'):
            self._intent = None

        for keymap in PRIORITY_SEQUENCE:
            if keymap.get('_intent') in self.keys():
                self._intent = self.get(keymap.get('_intent'))
                break

    def set_drive(self):
        if not hasattr(self, '_drive'):
            self._drive = None

        for keymap in PRIORITY_SEQUENCE:
            if keymap.get('_drive') in self.keys():
                self._drive = self.get(keymap.get('_drive'))
                break

    def object_modtime(self):
        mtime = None
        possible_fields = ['mtime', 'updated_date', 'modified_date', 'modification_date']
        for field in possible_fields:
            mtime = self.get(field)
            if mtime is not None:
                break

        if mtime is not None:
            modification_time = dateparse(mtime).astimezone(timezone.utc).timestamp()
        else:
            modification_time = datetime.now().timestamp()

        return modification_time

    def initialize(self):
        self.set_id()
        self.set_type()
        self.set_auth()
        self.set_intent()
        self.set_drive()

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)
        self.initialize()

    def get_filedir(self):
        if not hasattr(self, '_drive'):
            self.set_drive()

        if self._drive is not None:

            # parsing '@' field:                                    #sample: PyPI::halfbakery_driver==0.0.1:default.api.Topic
            # TBD: Split to separate methods.
            packman = self._drive.split('::', 1)[0]                 #sample: PyPI  (Conan, NPM, Paket, etc.)
            drivespec = self._drive.split('::', 1)[-1]              #sample: halfbakery_driver==0.0.1:default.api.Topic
            driver_name_version = drivespec.split(':',1)[0]         #sample: halfbakery_driver==0.0.1
            driver_name = driver_name_version.split('==',1)[0]      #sample: halfbakery_driver
            driver_version = driver_name_version.rsplit('==',1)[-1] #sample: 0.0.1
            profile_name_pkg_path = drivespec.rsplit(':',1)[-1]     #sample: default.api.Topic
            profile_name = profile_name_pkg_path.split('.',1)[0]    #sample: default
            pkg_path = profile_name_pkg_path.split('.',1)[-1]       #sample: api.Topic

            if os.name == 'nt':
                drive_name = '{}__{}'.format(driver_name, profile_name)
            else:
                drive_name = '{}:{}'.format(driver_name, profile_name)

            DATA_PATH = os.path.join(config.DATA_DIR, drive_name, type(self).__name__)
        else:
            DATA_PATH = os.path.join(config.DATA_DIR, 'default', type(self).__name__)
            print("Since the _drive or profile is not provided, using default directory {}. The object will be non-resumable.".format(DATA_PATH))

        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)

        return DATA_PATH

    def get_extension(self):
        extension = '.yaml'
        sub_extension = '.'

        if hasattr(self, '_type'):
            if isinstance(self._type, str):
                if self._type.startswith('http'):
                    sub_extension += url2ext(self._type)

        return sub_extension + extension

    def get_urlhash(self, length=6):
        '''
        Get first MD5 hash letters of the url.
        '''
        if not hasattr(self, '_id'):
            self.set_id()

        hsh = hashlib.md5(self._id.encode('utf-8')).hexdigest()
        return hsh[:length]

    def get_filename(self):
        '''
        For convenience purposes:
        1) include the 6-letter hash as prefix.
        2) include slug of url in between.
        3) if possible, include sub_extension indicating wiki concept id, and format id.
        4) include the extension.
        '''

        if not hasattr(self, '_id'):
            self.set_id()

        if self._id is not None:
            hsh = self.get_urlhash() + '.'
            slg = slug(self._id)
            ext = self.get_extension()

            fname = hsh + slg[len(ext)+len(hsh)-config.FILENAME_LENGTH_LIMIT:] + ext

        else:
            raise Exception("Can't determine filename without _id. Assign '-' or 'url' key to data, and try again.")

        return fname

    def get_savepath(self):
        dn = self.get_filedir()
        fn = self.get_filename()
        return os.path.join(dn, fn)

    def local_modtime(self):
        mtime = None
        savepath = self.get_savepath()
        if os.path.exists(savepath):
            return os.path.getmtime(savepath)
        else:
            return None

    def save(self):
        savepath = self.get_savepath()

        with open(savepath, 'w') as f:
            f.write(yaml.dump(dict(self), allow_unicode=True, sort_keys=False, Dumper=dumper))

        os.utime(savepath, (os.path.getatime(savepath), self.object_modtime()))
