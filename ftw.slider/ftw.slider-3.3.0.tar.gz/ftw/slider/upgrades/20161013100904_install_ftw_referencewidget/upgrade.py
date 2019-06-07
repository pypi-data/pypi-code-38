from ftw.upgrade import UpgradeStep


class InstallFtwReferencewidget(UpgradeStep):
    """Install ftw.referencewidget.
    """

    def __call__(self):

        self.setup_install_profile('profile-ftw.referencewidget:default')
        self.install_upgrade_profile()
