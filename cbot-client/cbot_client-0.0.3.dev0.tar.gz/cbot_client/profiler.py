from collections import OrderedDict


class ProfileGetter(object):

    def __init__(self, profile_id=None):
        self.profile_id = profile_id or None

    def get_profile_settings_options(self):
        # b-linux_linux_5_libstdcpp_gcc_release_b-64_86.fakeref:shared:true
        if not self.profile_id:
            return None, None

        try:
            settings_str, options_str = self.profile_id.split(".")
            tmp = settings_str.split("_")
            settings = OrderedDict()
            for s in tmp:
                if s in ["linux", "windows", "macos"]:
                    settings["os"] = s[0].upper() + s[1:]
                elif s in ["b-linux", "b-windows", "b-macos"]:
                    settings["os_build"] = s[2].upper() + s[3:]
                elif s in ["86", "64"]:
                    settings["arch"] = {"86": "x86", "64": "x86_64"}.get(s)
                elif s in ["b-86", "b-64"]:
                    settings["arch_build"] = {"b-86": "x86", "b-64": "x86_64"}.get(s)
                elif s in ["gcc", "clang", "vs"]:
                    settings["compiler"] = {"vs": "Visual Studio"}.get(s, s)
                elif s in ["libstdcpp", "libstdcpp11" "libcpp"]:
                    settings["compiler.libcxx"] = {"libstdcpp": "libstdc++",
                                                   "libstdcpp11": "libstdc++11",
                                                   "libcpp": "libcxx"}.get(s)
                elif s in ["release", "debug"]:
                    settings["build_type"] = s[0].upper() + s[1:]
                elif s in ["md", "mt", "mdd", "mtd"]:
                    settings["compiler.runtime"] = {"md": "MD", "mt": "MT", "mtd": "MTd", "mdd": "MDd"}
                elif s in ["39", "40", "50", "60", "70", "49", "5", "6", "7", "8", "9", "91", "90", "100",
                           "14", "15", "16"]:
                    settings["compiler.version"] = {"39": "3.9", "40": "4.0", "50": "5.0", "60": "6.0",
                                                    "70": "7.0", "49": "4.9", "91": "9.1", "90": "9.0",
                                                    "100": "10.0"}.get(s, s)
            options = OrderedDict()
            tmp = options_str.split("_")
            for s in tmp:
                s = s.split(":")
                if len(s) == 2:
                    options[s[0]] = s[1]
                if len(s) == 3:
                    options[s[0] + ":" + s[1]] = s[2]
        except Exception:
            raise Exception("Unknown profileID: {}".format(self.profile_id))

        return self._order_by_key(settings), options

    @staticmethod
    def _order_by_key(settings):
        ordered_keys = sorted(settings.keys())
        ret = OrderedDict()
        for key in ordered_keys:
            ret[key] = settings[key]
        return ret

    def __repr__(self):
        if not self.profile_id:
            return """include(default)\n"""

        settings, options = self.get_profile_settings_options()
        template = """
[settings]
{}

[options]
{}
            """.format("\n".join(["{}={}".format(k, v) for k, v in settings.items()]),
                       "\n".join(["{}={}".format(k, v) for k, v in options.items()]))

        return template


if __name__ == "__main__":
    pr = ProfileGetter("b-linux_linux_5_libstdcpp_gcc_release_b-64_86.fakeref:shared:true")
    print(pr)
