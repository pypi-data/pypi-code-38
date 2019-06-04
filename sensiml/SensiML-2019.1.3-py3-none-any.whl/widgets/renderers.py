from sensiml.render import BaseRenderer


class WidgetAttributeRenderer(BaseRenderer):

    def __init__(self, widget, render_attribute):
        self.widget = widget
        self.render_attribute = render_attribute

    def render(self, value):
        msg = value
        msg = '<b>' + msg + "</b>"
        msg = '<font size = "+0" >' + msg + "</font>"
        msg = '<p align="right";>' + msg + "</p>"
        setattr(self.widget, self.render_attribute, msg)
