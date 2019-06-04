from ftw.upgrade import UpgradeStep


class FixJavascriptLoadingOrder(UpgradeStep):
    """Fix javascript loading order.
    """

    def __call__(self):
        self.install_upgrade_profile()
