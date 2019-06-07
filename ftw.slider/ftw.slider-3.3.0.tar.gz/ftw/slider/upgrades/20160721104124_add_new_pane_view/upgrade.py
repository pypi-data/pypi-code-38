from ftw.upgrade import UpgradeStep


class AddNewPaneView(UpgradeStep):
    """Add new pane view.
    """

    def __call__(self):
        self.install_upgrade_profile()
