from zope.interface import Interface


SLIDER_VIEW = 'slider_view'


class IContainer(Interface):
    """Marker interface for the slider container.
    """


class IPane(Interface):
    """Marker interface for the slider pane.
    """
