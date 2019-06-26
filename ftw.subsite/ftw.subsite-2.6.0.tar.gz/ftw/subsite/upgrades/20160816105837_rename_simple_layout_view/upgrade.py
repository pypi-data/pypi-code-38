from ftw.upgrade import UpgradeStep


class RenameSimpleLayoutView(UpgradeStep):
    """Rename simple layout view.
    """

    def __call__(self):
        self.install_upgrade_profile()
