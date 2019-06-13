"""
subclass of QMenu to save title
used in internationalization
"""

from PySide2.QtWidgets import QMenu

class QMenuWidget(QMenu):
    """Override QMenu __init__ to save title"""

    def __init__(self, title=None):
        super().__init__(title)

        self.originaltitle = title
