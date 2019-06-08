import os
import toml

DEFAULT_CONFIG = {'sget': {'editor': ''}}


class Config():
    def __init__(self):
        self._snippet_file_name = 'snippets.toml'
        self._root_dir = os.path.expanduser('~/.sget')
        self._file = os.path.join(self._root_dir, 'config.toml')
        self._snippet_file = os.path.join(self._root_dir,
                                          self._snippet_file_name)
        self._make_root_dir()
        try:
            self._cfg = self._parse_cfg()
        except IOError:
            self._cfg = self._create_cfg()

    def _make_root_dir(self):
        if not os.path.exists(self.root_dir):
            os.mkdir(self.root_dir)

    def _parse_cfg(self):
        with open(self.file, 'r') as open_file:
            cfg = toml.loads(open_file.read())
            if 'sget' not in cfg:
                msg = 'Error parsing config file, missing section \'sget\'.'
                raise ValueError(msg)
            return cfg

    def _create_cfg(self):
        with open(self.file, 'w') as open_file:
            open_file.write(toml.dumps(DEFAULT_CONFIG))
        return DEFAULT_CONFIG

    def _get(self, key):
        return self._cfg['sget'].get(key, None)

    @property
    def snippet_file(self):
        return self._snippet_file

    @property
    def root_dir(self):
        return self._root_dir

    @property
    def file(self):
        return self._file

    @property
    def editor(self):
        return self._get('editor')



CONFIG = Config()
