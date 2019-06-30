"""
subclass of QAction to save text, shortcut and tooltip
this information is used for internationalization
"""

from PySide2.QtWidgets import QAction

class QActionWidget(QAction):
    """
    class QAction([parent=None])¶
    QAction(icon, text[, parent=None])
    QAction(text[, parent=None])
    """
    def __init__(self,
                 *args,
                 shortcut=None,
                 tooltip=None,
                 **kwargs
                ):

        super().__init__(*args, **kwargs)

        for p in args:
            if isinstance(p, str):
                self.originaltext = p

        self.shortcut = shortcut
        self.tooltip = tooltip

        if shortcut is not None:
            self.setShortcut(shortcut)
        if tooltip is not None:
            self.setStatusTip(tooltip)

    def setShortcut(self, shortcut, *args, **kwargs):

        if self.shortcut is None:
            self.shortcut = shortcut
        super().setStatusTip(shortcut, *args, **kwargs)

    def setStatusTip(self, tooltip, *args, **kwargs):

        if self.tooltip is None:
            self.tooltip = tooltip
        super().setStatusTip(tooltip, *args, **kwargs)
