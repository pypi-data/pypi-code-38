# coding:utf-8

from tweb.license import License
import config


class Passport(License):
    systems = dict()

    def __init__(self, system='all'):
        temp_profiles = dict()
        temp_display = dict()
        if system == 'all':
            for cfg in self.systems.values():
                self._init_profile(cfg, temp_profiles, temp_display)
        else:
            cfg = self.systems.get(system)
            self._init_profile(cfg, temp_profiles, temp_display)

        super(Passport, self).__init__(temp_profiles, temp_display,
                                       authority=config.PLATFORM, secret=config.TornadoSettings['cookie_secret'])

    @staticmethod
    def _init_profile(cfg, out_profiles, out_display):
        if cfg is None:
            return

        for k, v in cfg['profiles'].items():
            if k in out_profiles:
                continue
            out_profiles[k] = v

        for k, v in cfg['display'].items():
            if k not in out_display:
                out_display[k] = dict()
            out_display[k].update(v)

    @staticmethod
    def add_system_profile(system_name, profile, display):
        if system_name in Passport.systems:
            return

        Passport.systems[system_name] = {
            'profiles': profile,
            'display': display
        }
