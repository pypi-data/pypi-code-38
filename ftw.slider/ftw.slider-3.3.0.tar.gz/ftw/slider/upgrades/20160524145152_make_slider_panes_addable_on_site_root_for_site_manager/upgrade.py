from ftw.upgrade import UpgradeStep


class MakeSliderPanesAddableOnSiteRootForSiteManager(UpgradeStep):
    """Make slider panes addable on site root for site manager.
    """

    def __call__(self):
        self.install_upgrade_profile()
