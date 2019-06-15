import os
import subprocess


class Commander:
    def __init__(self, config):
        self.verbose = config.get("verbose")

    def ln(self, target, link_name):
        self.mkdir(os.path.dirname(link_name))

        cmd = "ln {} {} {}".format(self.ln_flags(), target, link_name)
        subprocess.call(cmd.split())

    def mkdir(self, dirpath):
        cmd = "mkdir {} {}".format(self.mkdir_flags(), dirpath)
        subprocess.call(cmd.split())

    # private

    def ln_flags(self):
        flags = ["-s", "-f", "-n", self.verbose_flag()]
        return " ".join(flags)

    def mkdir_flags(self):
        flags = ["-p", self.verbose_flag()]
        return " ".join(flags)

    def verbose_flag(self):
        return "-v" if self.verbose else ""
