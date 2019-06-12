from ftw.upgrade import UpgradeStep


class DefineScaleForContactSummaryImage(UpgradeStep):
    """Define scale for contact summary image.
    """

    def __call__(self):
        self.install_upgrade_profile()
