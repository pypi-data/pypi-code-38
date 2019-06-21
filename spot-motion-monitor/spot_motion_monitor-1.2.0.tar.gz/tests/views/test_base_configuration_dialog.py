#------------------------------------------------------------------------------
# Copyright (c) 2018-2019 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtWidgets import QDialogButtonBox

from spot_motion_monitor.views import BaseConfigurationDialog

class TestBaseConfigurationDialog:

    def test_inputFromTabsValid(self, qtbot):
        dialog = BaseConfigurationDialog()
        qtbot.addWidget(dialog)
        dialog.show()

        okButton = dialog.buttonBox.button(QDialogButtonBox.Ok)

        dialog.inputFromTabsValid(False)
        assert okButton.isEnabled() is False
        dialog.inputFromTabsValid(True)
        assert okButton.isEnabled() is True
