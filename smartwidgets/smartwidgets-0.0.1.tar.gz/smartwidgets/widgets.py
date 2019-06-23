from matplotlib.widgets import RectangleSelector, EllipseSelector, PolygonSelector, LassoSelector, Button, RadioButtons, AxesWidget
from matplotlib.patches import Ellipse
import matplotlib.pyplot as plt
import numpy as np


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
    # first deal with width (from axes)
    # add new lines to the labels but don't return the original labels in functions
    # then deal with height to make sure that the circles look good
    def __init__(self, ax, labels, active=0, activecolor='blue', radius=10, orientation='vertical'):
        AxesWidget.__init__(self, ax)
        self.activecolor = activecolor
        self.value_selected = None

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_navigate(False)
        dy = 1. / (len(labels) + 1)
        ys = np.linspace(1 - dy, dy, len(labels))
        cnt = 0
        axcolor = ax.get_facecolor()

        self.labels = []
        self.circles = []
        for y, label in zip(ys, labels):
            t = ax.text(0.25, y, label, transform=ax.transAxes,
                        horizontalalignment='left',
                        verticalalignment='center')

            if cnt == active:
                self.value_selected = label
                facecolor = activecolor
            else:
                facecolor = axcolor

            p = Ellipse(xy=(0.15, y), width=radius/ax.get_window_extent().width,
                        height=radius/ax.get_window_extent().height, edgecolor='black',
                        facecolor=facecolor, transform=ax.transAxes)
            p.radius = (p.width + p.height)/2

            self.labels.append(t)
            self.circles.append(p)
            ax.add_patch(p)
            cnt += 1

        def _resized(event):
            for p in self.circles:
                p.width = radius/ax.get_window_extent().width
                p.height = radius/ax.get_window_extent().height
                p.radius = (p.width + p.height)/2

        self.connect_event('button_press_event', self._clicked)
        self.connect_event('resize_event', _resized)
        self.cnt = 0
        self.observers = {}
