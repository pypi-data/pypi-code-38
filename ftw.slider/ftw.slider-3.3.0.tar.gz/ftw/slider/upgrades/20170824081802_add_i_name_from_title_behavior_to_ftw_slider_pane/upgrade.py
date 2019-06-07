from ftw.upgrade import UpgradeStep


class AddINameFromTitleBehaviorToFtwSliderPane(UpgradeStep):
    """Add "INameFromTitle" behavior to "ftw.slider.Pane".
    """

    def __call__(self):
        self.install_upgrade_profile()
