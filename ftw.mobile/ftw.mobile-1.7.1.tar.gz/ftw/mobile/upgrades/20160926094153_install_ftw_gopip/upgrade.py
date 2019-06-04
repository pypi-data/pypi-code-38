from ftw.upgrade import UpgradeStep


class InstallFtwGopip(UpgradeStep):
    """Install ftw.gopip (reindexes getObjPositionInParent!)
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.setup_install_profile('profile-ftw.gopip:default')
