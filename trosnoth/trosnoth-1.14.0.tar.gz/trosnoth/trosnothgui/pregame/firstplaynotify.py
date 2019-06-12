from trosnoth.gui.common import Location, Area, ScaledPoint, ScaledSize
from trosnoth.gui.notify import NotificationBar


class FirstPlayNotificationBar(NotificationBar):
    '''
    Provides a message for first-time players
    '''
    def __init__(self, app):
        super(FirstPlayNotificationBar, self).__init__(app,
            message =
                'First time playing Trosnoth? Click here to learn the rules.',
            url = 'http://www.trosnoth.org/how-to-play',
            font = app.fonts.default,
            area = Area(
                ScaledPoint(0, 0),
                ScaledSize(1024, 30),
                'topleft'
            ),
            buttonPos = Location(ScaledPoint(1024, 0), 'topright'),
            textPos = Area(
                ScaledPoint(512, 15),
                ScaledSize(1024, 30),
                'centre'
            ),
        )
        self.onClick.addListener(self.hide)
        self.onClose.addListener(app.identitySettings.notFirstTime)
