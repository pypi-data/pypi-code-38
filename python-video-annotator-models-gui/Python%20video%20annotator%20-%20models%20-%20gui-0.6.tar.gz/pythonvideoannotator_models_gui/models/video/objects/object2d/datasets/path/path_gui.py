import math, cv2, numpy as np, AnyQt


from confapp import conf
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlButton
from pyforms.controls import ControlCombo
from pyforms.controls import ControlLabel
from pyforms.controls import ControlText
from pyforms.controls import ControlCheckBox
from pythonvideoannotator.utils import tools

from pythonvideoannotator_models.models.video.objects.object2d.datasets.path import Path
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.dataset_gui import DatasetGUI

if conf.PYFORMS_MODE=='GUI':
    from AnyQt import QtCore
    from AnyQt.QtWidgets import QMessageBox, QColorDialog
    from AnyQt.QtGui import QColor
    


class PathGUI(DatasetGUI, Path, BaseWidget):

    def __init__(self, object2d=None):
        DatasetGUI.__init__(self)
        Path.__init__(self, object2d)
        BaseWidget.__init__(self, '2D Object', parent_win=object2d)

        self.create_tree_nodes()
        
        self._mark_pto_btn        = ControlButton('&Mark point',   checkable=True, icon=conf.ANNOTATOR_ICON_MARKPLACE )
        self._sel_pto_btn         = ControlButton('&Select point', default=self.__sel_pto_btn_event, icon=conf.ANNOTATOR_ICON_SELECTPOINT)
        self._del_path_btn        = ControlButton('Delete path',   default=self.__del_path_btn_event, icon=conf.ANNOTATOR_ICON_DELETEPATH, visible=False)
        self._del_point_btn       = ControlButton('Delete point',  default=self.__del_point_btn_event, icon=conf.ANNOTATOR_ICON_SELECTPOINT, visible=False)
        self._use_referencial     = ControlCheckBox('Apply')
        self._referencial_pt      = ControlText('Referencial',     changed_event=self.__referencial_pt_changed_event)

        self._interpolation_title = ControlLabel('Interpolation',  default='INTERPOLATION', visible=False)
        self._interpolation_mode  = ControlCombo('Mode',           changed_event=self.__interpolation_mode_changed_event, visible=False)
        self._interpolate_btn     = ControlButton('Apply',         default=self.__interpolate_btn_event, icon=conf.ANNOTATOR_ICON_INTERPOLATE, visible=False)
        self._remove_btn          = ControlButton('Remove dataset',default=self.__remove_path_dataset, icon=conf.ANNOTATOR_ICON_REMOVE)

        self._pickcolor   = ControlButton('Pick a color', default=self.__pick_a_color_event)

        self._show_object_name = ControlCheckBox('Show object name', default=False)
        self._show_name = ControlCheckBox('Show name', default=False)

        self._formset = [ 
            '_name',
            ('_show_name', '_show_object_name'),
            ('_referencial_pt', '_use_referencial'),
            '_remove_btn',            
            ' ',
            '_pickcolor',
            ' ',
            ('_mark_pto_btn', '_sel_pto_btn'),
            '_del_path_btn',
            '_del_point_btn',
            '_interpolation_title',
            ('_interpolation_mode', '_interpolate_btn'),
            ' '
        ]

        #### set controls ##############################################
        self._interpolation_mode.add_item("Auto", -1)
        self._interpolation_mode.add_item("Linear", 'slinear')
        self._interpolation_mode.add_item("Quadratic", 'quadratic')
        self._interpolation_mode.add_item("Cubic", 'cubic')

    ######################################################################
    ### FUNCTIONS ########################################################
    ######################################################################

    def get_velocity(self, index):
        p1 = self.get_position(index)
        p2 = self.get_position(index-1)
        if p1 is None or p2 is None: return None
        return p2[0]-p1[0], p2[1]-p1[1]

    def get_acceleration(self, index):
        v1 = self.get_velocity(index)
        v2 = self.get_velocity(index-1)
        if v1 is None or v2 is None: return None
        return v2[0]-v1[0], v2[1]-v1[1]

    def get_position_x_value(self, index):
        v = self.get_position(index)
        return v[0] if v is not None else None

    def get_position_y_value(self, index):
        v = self.get_position(index)
        return v[1] if v is not None else None

    def get_velocity_x_value(self, index):
        v = self.get_velocity(index)
        return v[0] if v is not None else None

    def get_velocity_y_value(self, index):
        v = self.get_velocity(index)
        return v[1] if v is not None else None

    def get_velocity_absolute_value(self, index):
        v = self.get_velocity(index)
        return math.sqrt(v[1]**2+v[0]**2) if v is not None else None

    def get_acceleration_x_value(self, index):
        v = self.get_acceleration(index)
        return v[0] if v is not None else None

    def get_acceleration_y_value(self, index):
        v = self.get_acceleration(index)
        return v[1] if v is not None else None

    def get_acceleration_absolute_value(self, index):
        v = self.get_acceleration(index)
        return math.sqrt(v[1]**2+v[0]**2) if v is not None else None
        

    ######################################################################
    ### AUX FUNCTIONS ####################################################
    ######################################################################

    def create_popupmenu_actions(self):
        self.tree.add_popup_menu_option(
            label='Duplicate', 
            function_action=self.clone_path, 
            item=self.treenode, icon=conf.ANNOTATOR_ICON_DUPLICATE
        )

        self.tree.add_popup_menu_option(
            label='Remove', 
            function_action=self.__remove_path_dataset, 
            item=self.treenode, icon=conf.ANNOTATOR_ICON_DELETE
        )
        
    def create_tree_nodes(self):
        self.treenode = self.tree.create_child(self.name, icon=conf.ANNOTATOR_ICON_PATH, parent=self.parent_treenode )
        self.treenode.win = self
        self.create_popupmenu_actions()

        self.create_group_node('position',      icon=conf.ANNOTATOR_ICON_POSITION)
        self.create_data_node('position > x',   icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('position > y',   icon=conf.ANNOTATOR_ICON_Y)

        self.create_group_node('velocity',          icon=conf.ANNOTATOR_ICON_VELOCITY)
        self.create_data_node('velocity > x',       icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('velocity > y',       icon=conf.ANNOTATOR_ICON_Y)
        self.create_data_node('velocity > absolute', icon=conf.ANNOTATOR_ICON_INFO)

        self.create_group_node('acceleration',          icon=conf.ANNOTATOR_ICON_ACCELERATION)
        self.create_data_node('acceleration > x',       icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('acceleration > y',       icon=conf.ANNOTATOR_ICON_Y)
        self.create_data_node('acceleration > absolute', icon=conf.ANNOTATOR_ICON_INFO)




    ######################################################################
    ### GUI EVENTS #######################################################
    ######################################################################

    def __del_point_btn_event(self):
        video_index = self.mainwindow._player.video_index-1
        if video_index<0:return

        self.set_position(video_index, None, None)
        try:
            self._sel_pts.remove(video_index)
            self._interpolate_btn.hide()
            self._interpolation_mode.hide()
            self._interpolation_title.hide()
            self._del_path_btn.hide()
            self._tmp_points = []
        except ValueError:
            self.calculate_tmp_interpolation()
        
        self.mainwindow._player.refresh()

        if self.visible:
            if len(self._sel_pts)==2:
                self._del_path_btn.show()
            else:
                self._del_path_btn.hide()

    def __sel_pto_btn_event(self):
        video_index = self.mainwindow._player.video_index-1
        if video_index<0:return 
        
        position = self[video_index]
        if position is None: return

        if video_index in self._sel_pts:
            self._sel_pts.remove(video_index)
        else:
            self._sel_pts.append(video_index)
            self._sel_pts = sorted(self._sel_pts)

        if self.visible:
            #store a temporary path for interpolation visualization
            if len(self._sel_pts) >= 2:
                #########################################################
                #In case 2 frames are selected, draw the temporary path##
                #########################################################
                if self.calculate_tmp_interpolation():
                    self._interpolate_btn.show()
                    self._interpolation_mode.show()
                    self._interpolation_title.show()

                    if len(self._sel_pts)==2:
                        self._del_path_btn.show()
                    else:
                        self._del_path_btn.hide()
                #########################################################
            else:
                self._interpolate_btn.hide()
                self._interpolation_mode.hide()
                self._interpolation_title.hide()
                self._del_path_btn.hide()
                self._tmp_points = []

        self.mainwindow._player.refresh()


    def __remove_path_dataset(self):
        item = self.tree.selected_item
        if item is not None: self.object2d -= item.win


    def __referencial_pt_changed_event(self):
        try:
            self._referencial = eval(self._referencial_pt.value)
        except:
            self._referencial = None

    def __pick_a_color_event(self):
        color = QColor(self.color[2], self.color[1], self.color[0])
        color = QColorDialog.getColor(color, parent = self, title = 'Pick a color for the path')
        self.color = color.blue(), color.green(), color.red()
        self.mainwindow._player.refresh()

    ####################################################################

    def __interpolate_btn_event(self): 
        #store a temporary path for interpolation visualization
        if len(self._sel_pts) >= 2:
            mode = None if self._interpolation_mode.value=='Auto' else self._interpolation_mode.value        #store a temporary path for interpolation visualization
            self.interpolate_range( self._sel_pts[0], self._sel_pts[-1], interpolation_mode=mode)
            self.mainwindow._player.refresh()
        else:
            QMessageBox.about(self, "Error", "You need to select 2 frames.")

    def __interpolation_mode_changed_event(self): 
        #store a temporary path for interpolation visualization
        if len(self._sel_pts) >= 2:
            if self.calculate_tmp_interpolation():
                self.mainwindow._player.refresh()

    def __del_path_btn_event(self): #store a temporary path for interpolation visualization
        if len(self._sel_pts) == 2:
            reply = QMessageBox.question(self, 'Confirmation',
                                               "Are you sure you want to delete this path?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes: #store a temporary path for interpolation visualization
                start, end = self._sel_pts[0], self._sel_pts[1]
                self.delete_range(start, end)
                self.calculate_tmp_interpolation()
                self.mainwindow._player.refresh()
        else:
            QMessageBox.about(self, "Error", "You need to select 2 frames.")

    def __lin_dist(self, p1, p2): return np.linalg.norm( (p1[0]-p2[0], p1[1]-p2[1]) )

    ######################################################################
    ### VIDEO EVENTS #####################################################
    ######################################################################


    def on_click(self, event, x, y):
        if event.button== 1:
            frame_index = self.mainwindow._player.video_index-1

            if self._mark_pto_btn.checked:
                frame_index = frame_index if frame_index>=0 else 0
                self.set_position(frame_index, x, y)
                self._mark_pto_btn.checked = False
            else:
                position = self.get_position(frame_index)
                if position is not None and self.__lin_dist(position, (x,y))<10:

                    modifier = int(event.event.modifiers())

                    # If the control button is pressed will add the blob to the previous selections
                    if modifier == QtCore.Qt.ControlModifier:
                        if frame_index not in self._sel_pts: #store a temporary path for interpolation visualization
                            self._sel_pts.append(frame_index)
                            
                        else:
                            # Remove the blob in case it was selected before #store a temporary path for interpolation visualization
                            self._sel_pts.remove(frame_index)
                    else:
                        # The control key was not pressed so will select only one #store a temporary path for interpolation visualization
                        self._sel_pts =[frame_index]
                else: #store a temporary path for interpolation visualization
                    self._sel_pts =[]  # No object selected: remove previous selections #store a temporary path for interpolation visualization
                self._sel_pts = sorted(self._sel_pts)

            if self.visible:
                #store a temporary path for interpolation visualization
                if len(self._sel_pts) >= 2:
                    #########################################################
                    #In case 2 frames are selected, draw the temporary path##
                    #########################################################
                    res = self.calculate_tmp_interpolation()
                    if self.visible & res:
                        self._interpolate_btn.show()
                        self._interpolation_mode.show()
                        self._interpolation_title.show()
                        self._del_path_btn.show()
                        #self._sel_pto_btn.hide()
                    #########################################################
                else:
                    if self.visible:
                        self._interpolate_btn.hide()
                        self._interpolation_mode.hide()
                        self._interpolation_title.hide()
                        self._del_path_btn.hide()
                    self._tmp_points = []

            
            self.mainwindow._player.refresh()

    
        
    def draw(self, frame, frame_index):

        if not self.mainwindow.player.is_playing and self.visible:

            if self[frame_index] is None:
                self._del_point_btn.hide()
            else:
                self._del_point_btn.show()

        Path.draw(self, frame, frame_index)

    ######################################################################
    ### PROPERTIES #######################################################
    ######################################################################

    @property
    def mainwindow(self):    return self._object2d.mainwindow
    @property 
    def tree(self):          return self._object2d.tree
    @property 
    def video_capture(self): return self._object2d.video_capture

    @property 
    def parent_treenode(self):  return self._object2d.treenode

    @property
    def interpolation_mode(self): return None if self._interpolation_mode.value==-1 else self._interpolation_mode.value

    @property
    def mark_point_button(self):
        return self._mark_pto_btn

    @property
    def referencial(self): 
        return Path.referencial.fget(self)

    @referencial.setter
    def referencial(self, value):
        self._referencial_pt.value = str(value)[1:-1] if value else ''

    @property
    def apply_referencial(self):  
        return self._use_referencial.value

    @apply_referencial.setter
    def apply_referencial(self, value): 
        self._use_referencial.value = value

    @property
    def show_object_name(self):
        return self._show_object_name.value

    @show_object_name.setter
    def show_object_name(self, value):
        self._show_object_name.value = value

    @property
    def show_name(self):
        return self._show_name.value

    @show_name.setter
    def show_name(self, value):
        self._show_name.value = value