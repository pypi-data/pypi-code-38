import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse
from matplotlib.widgets import (AxesWidget, Button, EllipseSelector,
                                LassoSelector, PolygonSelector, RadioButtons,
                                RectangleSelector)


def lower_upper_and_ctrl_plus(key):
    return key.lower(), key.upper(), 'ctrl+' + key.lower(), 'ctrl+' + key.upper()

class RotatingRectangleSelector(RectangleSelector):
    """A modification of the matplotlib.widgets.RectangleSelector object
    that allows for rotating the shape in axes using the rotation_keys."""
    def __init__(self, ax, onselect, drawtype='box',
                 minspanx=None, minspany=None, useblit=False,
                 lineprops=None, rectprops=None, spancoords='data',
                 button=None, maxdist=10, marker_props=None,
                 interactive=True, state_modifier_keys=None,
                 rotation_keys=None, rotation_step=3):
        """*rotation_keys* are a list of keys that rotate the shape. These work 
        alongside the state_modifier_keys (i.e. pressing key, KEY, ctrl+key, and 
        ctrl+KEY will all perform the action assigned to key).
        
        The default rotation_keys are:
        dict(counterclockwise='e', clockwise='r', reset='t')

        *rotation_step* is the number of degrees to rotate the shape whenever a rotation_key is pressed.
        """
        super().__init__(ax, onselect, drawtype=drawtype,
                         minspanx=minspanx, minspany=minspany, useblit=useblit,
                         lineprops=lineprops, rectprops=rectprops, spancoords=spancoords,
                         button=button, maxdist=maxdist, marker_props=marker_props,
                         interactive=interactive, state_modifier_keys=state_modifier_keys)
        
        self.rotation_keys = rotation_keys or ['e', 'r', 't']
        self.rotation_step = rotation_step

    def _press(self, event):
        super()._press(event)
        if self.active_handle is None or not self.interactive:
            # reset angle before drawing new one
            self.to_draw.angle = 0
            self.update()

    def _on_key_press(self, event):
        self.connect_event('key_press_event', self.rotate)

    def rotate(self, event):
        """Rotate the shape when a rotation key is pressed."""
        # rotate CCW
        if event.key in lower_upper_and_ctrl_plus(self.rotation_keys[0]):
            self.to_draw.angle -= self.rotation_step
            self.update()

        # rotate CW
        if event.key in lower_upper_and_ctrl_plus(self.rotation_keys[1]):
            self.to_draw.angle += self.rotation_step
            self.update()
        
        # reset angle
        if event.key in lower_upper_and_ctrl_plus(self.rotation_keys[2]):
            self.to_draw.angle = 0
            self.update()


class RotatingEllipseSelector(EllipseSelector, RotatingRectangleSelector): 
    """A modification of the matplotlib.widgets.EllipseSelector object
    that allows for rotating the shape in axes using the rotation_keys."""
    pass


class SmartRadioButtons(RadioButtons):
    """A modification of the matplotlib.widgets.RadioButtons object
    that resizes the circles whenever the figure is resize and allows for 
    horizontal or vertical buttons."""
    def __init__(self, ax, labels, active=0, activecolor='blue', size=10, orientation='vertical'):
        # same as super __init__
        AxesWidget.__init__(self, ax)
        self.activecolor = activecolor
        self.value_selected = None

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_navigate(False)

        def dynamic_width():
            return size/ax.get_window_extent().width

        def dynamic_height():
            return size/ax.get_window_extent().height

        # allow for orientation
        # change to accept nrows, ncols in future
        if orientation in ['h', 'horizontal']:
            dx = 1. / (len(labels) + 1)
            ellipse_xs = np.linspace(dynamic_width() + dx/len(labels), 1 - dx, len(labels))
            ys = np.ones(ellipse_xs.shape) * 0.5
            text_xs = ellipse_xs + 0.025
        elif orientation in ['v', 'vertical']:
            dy = 1. / (len(labels) + 1)
            ys = np.linspace(1 - dy, dy, len(labels))
            ellipse_xs = np.ones(ys.shape) * 0.15
            text_xs = ellipse_xs + 0.1
        else:
            raise ValueError('orientation must be one of ("v", "vertical", "h", "horizontal")')

        axcolor = ax.get_facecolor()

        self.circles = []
        self.labels = []

        for i, ex, tx, y in zip(range(len(text_xs)), ellipse_xs, text_xs, ys):
            if i == active:
                facecolor = activecolor
            else:
                facecolor = axcolor
            
            t = ax.text(tx, y, labels[i], transform=ax.transAxes,
                        horizontalalignment='left',
                        verticalalignment='center')

            e = Ellipse(xy=(ex, y), width=dynamic_width(),
                        height=dynamic_height(), edgecolor='black',
                        facecolor=facecolor, transform=ax.transAxes)
            
            # need to add this for later functions to work
            e.radius = (e.width + e.height)/2

            self.circles.append(e)
            self.labels.append(t)
            ax.add_patch(e)

        def resized(event):
            for e in self.circles:
                e.width = dynamic_width()
                e.height = dynamic_height()
                e.radius = (e.width + e.height)/2

        self.connect_event('button_press_event', self._clicked)
        self.connect_event('resize_event', resized)

        self.cnt = 0
        self.observers = {}
