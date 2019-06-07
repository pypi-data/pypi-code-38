from ftw.upgrade import UpgradeStep


class SetShowTitleOnExistingSliderPanes(UpgradeStep):
    """Set "show_title" on existing slider panes.
    """

    def __call__(self):
        self.install_upgrade_profile()
        slider_panes = self.objects({'portal_type': 'ftw.slider.Pane'},
                                    message='Set "show_title" of existing slider panes.')
        for slider_pane in slider_panes:
            if slider_pane.text:
                slider_pane.show_title = True
