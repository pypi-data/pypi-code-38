# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  Copyright (C) 2018
#   Laboratory of Systems Biology, Department of Cybernetics,
#   School of Science, Tallinn University of Technology
#  Authors: Martin Laasmaa and Marko Vendelin
#  This file is part of project: IOCBIO Sparks
#
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QScrollBar, QVBoxLayout, QHBoxLayout, QTabBar
from PyQt5.QtGui import QTransform, QMenu, QAction
# https://groups.google.com/forum/#!topic/pyqtgraph/pTrem1RCKSw
import pyqtgraph as pg
from pyqtgraph.Point import Point
from pyqtgraph.Qt import QtGui, QtCore

from .histogram_plot import Histogram
from .custom_widgets import XYPlot, EmptyContextMenuViewBox
from ..io.export import save_image
from .spark_plot import Action


class DataSelectViewBox(EmptyContextMenuViewBox):
    sigMouseDragDone = QtCore.pyqtSignal([list])

    def mouseDragEvent(self, event, axis=None):
        if event.button() == QtCore.Qt.RightButton:
            event.ignore()
        else:
            pg.ViewBox.mouseDragEvent(self, event, axis)

        event.accept()
        pos = event.pos()

        if event.button() == QtCore.Qt.RightButton and axis is None:
            if event.isFinish():
                self.rbScaleBox.hide()
                self.ax = QtCore.QRectF(Point(event.buttonDownPos(event.button())),
                                        Point(pos))
                self.ax = self.childGroup.mapRectFromParent(self.ax)
                self.sigMouseDragDone.emit(self.get_corner_points())
            else:
                self.updateScaleBox(event.buttonDownPos(), event.pos())

    def get_corner_points(self):
        """returns a list of selected area corner points as [x0, y0, x1, y1]"""
        #return [int(round(self.ax.getCoords()[i])) for i in range(4)]
        return [self.ax.getCoords()[i] for i in range(4)]


class OverViewPlot(QWidget):
    # sigRoisListModified = pyqtSignal(list)

    sigRoiAdd = pyqtSignal(list)
    sigRoiRemove = pyqtSignal(str)
    sigRoiChanged = pyqtSignal(str, list)

    sigActiveRoi = pyqtSignal(str)
    sigZoomXChanged = pyqtSignal(float, float)

    pens = {'active roi': {'color': 'fe642e', 'width': 2},
            'inactive roi': {'color': '8856a7', 'width': 2},
            }

    def __init__(self, image):
        """
        image : io.image.Image object
        """
        QWidget.__init__(self)

        self.image = image
        raw_shape = self.image.raw.shape
        self.dx = image.dx
        self.dt = image.dt
        self.current_image_displayed = 'Experiment'
        self.last_image_save_path = self.image.get_image_filepath
        self.read_only = False
        self.stages = None

        image_transformer = QTransform()
        image_transformer.scale(self.dt, self.dx)

        self.view_t0 = 0
        self.view_t1 = raw_shape[0] * self.dt
        self.view_t_min = 0
        self.view_t_max = raw_shape[0] * self.dt

        self.view_x0 = 0
        self.view_x1 = raw_shape[1] * self.dx
        self.view_x_min = 0
        self.view_x_max = raw_shape[1] * self.dx

        self.image_levels = [0, 255]

        gw = pg.GraphicsLayoutWidget()
        gw.ci.layout.setContentsMargins(0, 0, 0, 0)
        vb = DataSelectViewBox()
        self.plot_item = gw.addPlot(viewBox=vb)
        self.plot_item.setRange(xRange=[self.view_t0,self.view_t1],
                                yRange=[self.view_x_min,self.view_x_max],
                                padding=0)
        self.image_item = pg.ImageItem(autoDownsample=True)
        self.image_item.setTransform(image_transformer)
        self.plot_item.addItem(self.image_item)
        self.set_image(self.image.raw)

        # https://stackoverflow.com/questions/31775468/show-string-values-on-x-axis-in-pyqtgraph
        self.plot_item.setLabel('left', 'x', units='m')
        self.plot_item.setLabel('bottom', 't', units='s')

        # TODO where we hold analysis region
        self.analysis_region = pg.LinearRegionItem((0,0), movable=False)
        self.analysis_region.setBrush(pg.mkBrush(None))
        self.analysis_region.setZValue(10)
        self.plot_item.addItem(self.analysis_region)

        self.scroll_time = QScrollBar(Qt.Horizontal)
        self.scroll_time.setRange(self.view_t0, self.view_t0)
        self.scroll_time.setTracking(True)

        self.active_roi_id = None
        self.rois_map = {}
        self.show_roi_labels = True

        image_switch_tabs = QTabBar()
        image_switch_tabs.setShape(QTabBar.RoundedEast)
        image_switch_tabs.setUsesScrollButtons(True)
        self.image_switch_tabs_list = ['Experiment', 'Corrected Mean', 'Corrected Mean MedBlu', 'Filtered', 'F0']
        image_switch_tabs_list_short = ['Experiment', 'Corrected', 'MedBlu', 'Filtered', 'F0']
        for tab in image_switch_tabs_list_short:
            image_switch_tabs.addTab(tab)

        # { Event bindings
        vb.sigMouseDragDone.connect(self.roi_new_requested)
        vb.sigYRangeChanged.connect(self.plot_item_space_changed)
        vb.sigXRangeChanged.connect(self.plot_item_time_changed)
        self.scroll_time.valueChanged.connect(self.scroll_time_changed)
        image_switch_tabs.currentChanged.connect(self.image_tab_changed)

        # { Creating layout
        mainlayout = QHBoxLayout()
        layout = QVBoxLayout()
        layout.addWidget(gw)
        layout.addWidget(self.scroll_time)
        mainlayout.addLayout(layout)
        mainlayout.addWidget(image_switch_tabs)
        self.setLayout(mainlayout)
        # }

        # { Creating new context menu
        view_all = QAction('View All', self)
        view_all.triggered.connect(lambda x: self.update_view(self.view_t_min, self.view_t_max, self.view_x_min, self.view_x_max))
        view_analysis_range = QAction('View analysis region', self)
        view_analysis_range.triggered.connect(self._view_analysis_range)

        vb.menu.addAction(view_all)
        vb.menu.addAction(view_analysis_range)

        self.save_image_action = None
        self.context_menu = vb.menu
        self.update_context_menu()
        #}

    def _view_analysis_range(self):
        t0, t1 = self.analysis_region.getRegion()
        self.update_view(t0, t1, self.view_x_min, self.view_x_max)

    def save_image(self, stage_id=False):
        #if self.current_image_displayed == 'Experiment' and stage_id is not None:
        if stage_id is not False:
            t0 = self.stages[stage_id]['start']
            t1 = self.stages[stage_id]['end']
            [t0, t1], _ = self.image.get_array_indices([[t0, t1], [0, 0]])
            im = self.image.get_slice('Raw', [[t0, t1], [0,self.image.raw.shape[1]]])
            self.last_image_save_path = save_image(im,
                                                   self.current_image_displayed+'_'+self.stages[stage_id]['name'],
                                                   self.last_image_save_path,
                                                   parent=self)

        else:
            self.last_image_save_path = save_image(self.image_item.image,
                                                   self.current_image_displayed,
                                                   self.last_image_save_path,
                                                   parent=self)

    def image_tab_changed(self, index):
        self.update_image(self.image_switch_tabs_list[index])

    def set_rois(self, rois, sorted_roi_list):
        # delete absent rois
        keys = list(self.rois_map.keys())
        for k in keys:
            if k not in rois:
                self.plot_item.removeItem(self.rois_map[k].label)
                self.plot_item.removeItem(self.rois_map[k])
                del self.rois_map[k]

        # load missing rois
        for k, r in rois.items():
            if k not in self.rois_map:
                x0, y0, x1, y1 = r['data coordinates']
                self.roi_add(coords = [x0*self.dt,
                                       y0*self.dx,
                                       x1*self.dt,
                                       y1*self.dx],
                             roi_id = k)

        if self.show_roi_labels:
            self.update_roi_labels(sorted_roi_list)

    def plot_item_space_changed(self, value):
        _, [x0, x1] = value.viewRange()
        self.view_x0 = max(self.view_x_min, x0)
        self.view_x1 = min(self.view_x_max, x1)
        self.plot_item.setYRange(self.view_x0, self.view_x1, padding=0)

    def plot_item_time_changed(self, value):
        [t0, t1], _ = value.viewRange()
        self.update_view(t0, t1)

    def scroll_time_changed(self, t0):
        if self.view_t0 != t0 or self.scroll_time.value() != t0:
            w = self.view_t1 - self.view_t0
            t1_n = t0 + w

            if t1_n > self.view_t_max:
                t1_n = self.view_t_max
                t0 = t1_n - w

            self.scroll_time.setValue(t0)
            self.scroll_time.setPageStep(w)
            self.scroll_time.setMaximum(self.view_t_max - w)
            self.update_view(t0, t1_n)

    def update_view(self, t0, t1, x0=None, x1=None):
        if self.view_t0 != t0 or self.view_t1 != t1:
            self.view_t0 = max(self.view_t_min, t0)
            self.view_t1 = min(self.view_t_max, t1)
            self.plot_item.setXRange(self.view_t0, self.view_t1, padding=0)
            self.scroll_time_changed(self.view_t0)
            self.sigZoomXChanged.emit(t0, t1)
        if x0 is not None and x1 is not None:
            if self.view_x0 != x0 or self.view_x1 != x1:
                self.view_x0 = max(self.view_x_min, x0)
                self.view_x1 = min(self.view_x_max, x1)
                self.plot_item.setYRange(self.view_x0, self.view_x1, padding=0)

    def shift_plot_item_time(self, key):
        [t0, t1], _ = self.plot_item.viewRange()

        if key == Qt.Key_PageDown or key == Qt.Key_Right:
            w = t1-t0
            if key == Qt.Key_PageDown:
                shift = 0.95*w
            else:
                shift = 0.1*w
            t0_n = t0 + shift
            t1_n = t0_n + w
            if t1_n > self.view_t_max:
                t1_n = self.view_t_max
                t0_n = t1_n - w
            self.update_view(t0_n, t1_n)

        if key == Qt.Key_PageUp or key == Qt.Key_Left:
            w = t1-t0
            if key == Qt.Key_PageUp:
                shift = 0.95*w
            else:
                shift = 0.1*w
            t0_n = t0 - shift
            t1_n = t0_n + w
            if t0_n < self.view_t_min:
                t0_n = self.view_t_min
                t1_n = t0_n + w
            self.update_view(t0_n, t1_n)

        if key == Qt.Key_Home:
            self.update_view(self.view_t_min, self.view_t_min + t1 - t0)

        if key == Qt.Key_End:
            self.update_view(self.view_t_max - t1 + t0, self.view_t_max)

        if key == Qt.Key_Plus:
            w = int(0.25*(t1 - t0))
            self.update_view(t0 + w, t1 - w)

        if key == Qt.Key_Minus:
            w = int(0.5*(t1 - t0))
            self.update_view(max(t0 - w, self.view_t_min),
                             min(t1 + w, self.view_t_max))
        if key == Qt.Key_0:
            self.update_view(self.view_t_min, self.view_t_max)

    def roi_new_requested(self, coords):
        if self.read_only: return
        x0, y0, x1, y1 = coords

        if x0 < self.view_t_min:
            x0 = self.view_t_min
        if y0 < self.view_x_min:
            y0 = self.view_x_min
        if x1 > self.view_t_max:
            x1 = self.view_t_max
        if y1 > self.view_x_max:
            y1 = self.view_x_max

        [x0, x1], [y0, y1] = self.image.get_array_indices([[x0, x1],[y0, y1]])
        self.sigRoiAdd.emit([x0, y0, x1, y1])

    def update_roi_labels(self, sorted_roi_list):
        for i, k in enumerate(sorted_roi_list):
            self.rois_map[k].label.setText(str(i+1))

    def update_roi_label_location(self, roi):
        label = roi.label
        x, y = roi.pos()
        label.setPos(x, y+roi.size()[1])

    def set_roi_labels_visible(self, b=True):
        if not self.show_roi_labels and b:
            for _, roi in self.rois_map.items():
                self.plot_item.addItem(roi.label)

        if self.show_roi_labels and not b:
            for _, roi in self.rois_map.items():
                self.plot_item.removeItem(roi.label)

        self.show_roi_labels = b

    def roi_add(self, roi_id, coords):
        x0, y0, x1, y1 = coords

        if x0 < self.view_t_min:
            x0 = self.view_t_min
        if y0 < self.view_x_min:
            y0 = self.view_x_min
        if x1 > self.view_t_max:
            x1 = self.view_t_max
        if y1 > self.view_x_max:
            y1 = self.view_x_max
        coords = x0, y0, x1, y1

        roi = pg.RectROI([x0, y0], [x1-x0, y1-y0],
                         pen=self.pens['inactive roi'],
                         removable=True)

        # { creating labels for rois
        label = pg.TextItem(anchor=(0,0), color='#000000', fill='#ffffff')
        roi.label = label
        self.update_roi_label_location(roi)
        # }
        roi.roi_id = roi_id
        self.plot_item.addItem(roi) # adding roi to the plot
        if self.show_roi_labels:
            self.plot_item.addItem(roi.label) # adding roi label to the plot

        self.rois_map[roi.roi_id] = roi

        # { Event bindings
        roi.sigRemoveRequested.connect(self.roi_remove)
        roi.sigRegionChangeFinished.connect(self.roi_changed)
        roi.sigHoverEvent.connect(self.roi_hover)
        # }

    def roi_remove(self, roi):
        def removekey(d, key):
            r = dict(d)
            del r[key]
            return r
        self.plot_item.removeItem(roi.label)
        self.plot_item.removeItem(roi)
        self.rois_map = removekey(self.rois_map, roi.roi_id)
        self.sigRoiRemove.emit(roi.roi_id)

    def roi_changed(self, roi):
        if self.read_only:
            roi.sigRegionChangeFinished.disconnect(self.roi_changed)
            roi.setState(roi.preMoveState)
            roi.sigRegionChangeFinished.connect(self.roi_changed)
            return
        x0, y0, x1, y1 = self.get_roi_coordinates(roi)
        [x0, x1], [y0, y1] = self.image.get_array_indices([[x0, x1],[y0, y1]])
        self.sigRoiChanged.emit(roi.roi_id, [x0, y0, x1, y1])
        self.set_roi_color(roi.roi_id)
        self.update_roi_label_location(roi)

    def roi_hover(self, roi):
        self.sigActiveRoi.emit(roi.roi_id)
        if self.active_roi_id != roi.roi_id:
            self.set_roi_color(roi.roi_id)

    def _get_roi_corners(self, roi):
        pos0 = roi.pos()
        pos1 = pos0 + roi.size()
        # returns: (t0, t1, x0, x1)
        return pos0.x(), pos1.x(), pos0.y(), pos1.y()

    def _is_roi_in_view(self, roi):
        t0, t1, x0, x1 = self._get_roi_corners(roi)
        if t0 < self.view_t0 or t1 > self.view_t1 or x0 < self.view_x0 or x1 > self.view_x1:
            return False
        return True

    def set_active_roi(self, roi_id):
        if self.active_roi_id != roi_id and roi_id in self.rois_map:
            self.set_roi_color(roi_id)

            roi = self.rois_map[roi_id]
            if not self._is_roi_in_view(roi):
                t0, t1, x0, x1 = self._get_roi_corners(roi)
                trng = 0.5*(self.view_t1 - self.view_t0)
                xrng = 0.5*(self.view_x1 - self.view_x0)
                ct = t0 + 0.5*(t1 - t0)
                cx = x0 + 0.5*(x1 - x0)

                nt0 = ct - trng
                nt1 = ct + trng
                nx0 = cx - xrng
                nx1 = cx + xrng

                if nt0 < self.view_t_min:
                    nt0 = self.view_t_min
                    nt1 = nt0 + 2*trng

                if nt1 > self.view_t_max:
                    nt1 = self.view_t_max
                    nt0 = nt1 - 2*trng

                if nx0 < self.view_x_min:
                    nx0 = self.view_x_min
                    nx1 = nx0 + 2*xrng

                if nx1 > self.view_x_max:
                    nx1 = self.view_x_max
                    nx0 = nx1 - 2*xrng

                self.update_view(nt0, nt1, nx0, nx1)

    def set_roi_color(self, roi_id):
        if self.active_roi_id is None:
            self.active_roi_id = roi_id
            self.rois_map[self.active_roi_id].setPen(self.pens['active roi'])
        else:
            if self.active_roi_id == roi_id:
                self.rois_map[self.active_roi_id].setPen(self.pens['active roi'])
            else:
                if self.active_roi_id in self.rois_map:
                    self.rois_map[self.active_roi_id].setPen(self.pens['inactive roi'])
                self.active_roi_id = roi_id
                if self.active_roi_id in self.rois_map:
                    self.rois_map[self.active_roi_id].setPen(self.pens['active roi'])

    def get_roi_coordinates(self, roi):
        pos = roi.pos()
        size = roi.size()
        x0 = pos.x()
        y0 = pos.y()
        return [x0, y0, x0+size.x(), y0+size.y()]

    def update_analysis_region(self, rng):
        self.analysis_region.setRegion(rng)

    def set_levels(self, mn, mx):
        """ Sets intensity levels of the image """
        self.image_levels = [mn, mx]
        self.image_item.setLevels([mn, mx])

    def update_current_image(self, name):
        if name == self.current_image_displayed:
            self.update_image(name)
        if name == 'ALL' and self.current_image_displayed != 'Experiment':
            self.set_image(None)

    def update_image(self, name):
        self.current_image_displayed = name
        if name == 'Experiment':
            self.set_image(self.image.raw)
        else:
            self.set_image(self.image.get_slice(name), *self.image.processed_offset)
        self.update_context_menu()

    def set_image(self, image, ht=0, hx=0):
        if image is None:
            self.image_item.image = image
            self.plot_item.update()
        else:
            tr = QTransform()
            tr.scale(self.image.dt, self.image.dx)
            tr.translate(ht, hx)
            self.image_item.setTransform(tr)
            self.image_item.setImage(image)
            if self.current_image_displayed != 'Filtered':
                self.set_levels(*self.image_levels)

    def set_lut(self, cmap_dict):
        """ Set lookup table for the image """
        self.image_item.setLookupTable(cmap_dict['lut'])
        self.update_pens(cmap_dict['active roi'], cmap_dict['inactive roi'])

    def update_pens(self, active, inactive):
        """ Updates ROI colors accordingly to the selected colormap"""
        self.pens['active roi']['color'] = active
        self.pens['inactive roi']['color'] = inactive
        for roi_id in self.rois_map.keys():
            self.set_roi_color(roi_id)

    def update_stages(self, stages, sorted_stage_list):
        self.stages = stages
        self.update_context_menu()

    def update_context_menu(self):

        if self.save_image_action is not None:
            self.save_image_action.disconnect()
            self.context_menu.removeAction(self.save_image_action)

        self.save_image_action = QAction('Save image', self)

        if self.current_image_displayed == 'Experiment':
            menu = QMenu('', self)
            action = QAction('Entire image', self)
            action.triggered.connect(self.save_image)
            menu.addAction(action)
            menu.addSeparator()

            if self.stages is not None:
                for name, k in sorted([[d['name'], k] for k, d in self.stages.items()]):
                    action = Action(name, self, k)
                    # action = Action(self.stages[k]['name'], self, k)
                    action.sigTriggered.connect(self.save_image)
                    menu.addAction(action)
            self.save_image_action.setMenu(menu)

        else:
            self.save_image_action.triggered.connect(self.save_image)

        self.context_menu.addAction(self.save_image_action)

    def set_read_only(self, state):
        self.read_only = state

        for _, roi in self.rois_map.items():
            roi.removable = not self.read_only
            #roi.translatable = not self.read_only
            #roi.handles[0]['item'].hide()
