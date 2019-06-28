from box import Box
import configobj

from .utils import convert_jsonfile_to_ini, convert_yamlfile_to_ini


class Config(configobj.ConfigObj):

    def __init__(self, fp, *args, **kwargs):
        self.fbuffer = None
        self._any_filetype_to_ini(fp)
        if self.fbuffer is None:
            configobj.ConfigObj(fp, file_error=True, raise_errors=True)
        super(Config, self).__init__(self.fbuffer, *args, **kwargs)

    def _try_ini_file(self, fp):
        try:
            fbuffer = fp
            configobj.ConfigObj(fbuffer, file_error=True)
        except Exception:
            fbuffer = None
        return fbuffer

    def _try_json_file(self, fp):
        try:
            fbuffer = convert_jsonfile_to_ini(fp)
            configobj.ConfigObj(fbuffer)
            fbuffer.seek(0)
        except Exception:
            fbuffer = None
        return fbuffer

    def _try_yaml_file(self, fp):
        try:
            fbuffer = convert_yamlfile_to_ini(fp)
            configobj.ConfigObj(fbuffer)
            fbuffer.seek(0)
        except Exception:
            fbuffer = None
        return fbuffer

    def _available_methods(self):
        possible_methods = [
            self._try_ini_file,
            self._try_json_file,
            self._try_yaml_file,
        ]
        for method in possible_methods:
            if self.fbuffer is None:
                yield method

    def _any_filetype_to_ini(self, fp):
        for method in self._available_methods():
            self.fbuffer = method(fp)

    @property
    def dot(self):
        return Box(self.main)

    def _get_section(self, scope, section):
        sect = scope
        for step in section.split("."):
            sect = getattr(sect, step)
        return sect

    def _get_sections(self, sections):
        res = self.dot

        if isinstance(sections, str):
            res = self._get_section(res, sections)

        elif isinstance(sections, list):
            res_sections = Box()
            for section in sections:
                res_sections.update(self._get_section(res, section))
            res = res_sections

        return res
