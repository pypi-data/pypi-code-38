from ftw.upgrade import UpgradeStep


class FixHandlebarsCompression(UpgradeStep):
    """Fix handlebars compression.
    """

    def __call__(self):
        self.install_upgrade_profile()
