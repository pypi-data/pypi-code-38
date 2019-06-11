import math, cv2, numpy as np
from confapp import conf
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlButton
from pyforms.controls import ControlCombo
from pyforms.controls import ControlLabel
from pyforms.controls import ControlText

from pyforms.controls import ControlCheckBoxList
from pythonvideoannotator.utils import tools
from pythonvideoannotator_models_gui.models.video.objects.object2d.utils import points as pts_utils
from pythonvideoannotator_models.models.video.objects.object2d.datasets.contours import Contours

from pythonvideoannotator_models.utils.tools import points_angle, min_dist_angles, lin_dist

from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.dataset_gui import DatasetGUI

if conf.PYFORMS_MODE=='GUI':
    from AnyQt.QtWidgets import QInputDialog, QColorDialog
    from AnyQt.QtGui import QColor

class ContoursGUI(DatasetGUI, Contours, BaseWidget):

    def __init__(self, object2d=None):
        DatasetGUI.__init__(self)
        Contours.__init__(self, object2d)
        BaseWidget.__init__(self, '2D Object', parent_win=object2d)

        self._sel_pts=[]

        self._remove_btn        = ControlButton('Remove')
        self._layers            = ControlCheckBoxList('Layers')
        self._sel_pto_btn       = ControlButton('Select point')     
        self._switchangle_btn   = ControlButton('Switch orientation')
        self._pickcolor   = ControlButton('Pick a color', default=self.__pick_a_color_event)

        self._formset = [ 
            '_name',
            '_remove_btn',
            '_sel_pto_btn',
            '_switchangle_btn',          
            ' ',
            '_pickcolor',
            ' ',
            '_layers'
        ]

        self._switchangle_btn.hide()


        #### set controls ##############################################
        self._remove_btn.icon       = conf.ANNOTATOR_ICON_REMOVE    
        self._sel_pto_btn.icon      = conf.ANNOTATOR_ICON_SELECTPOINT
        self._switchangle_btn.icon  = conf.ANNOTATOR_ICON_REMOVE

        #### set events #################################################
        self._remove_btn.value      = self.remove_dataset
        self._sel_pto_btn.value     = self.__sel_pto_btn_event
        self._switchangle_btn.value = self.__switchangle_btn_event


        self.create_tree_nodes()

        self._layers.value = [
            ('contours', True),
            ('angle', True),
            ('velocity vector', True),
            ('bounding rect', False),
            ('fit ellipse', False),
            ('extreme points', False),
            ('convex hull', False),
            ('rotated rectangle', False),
            ('minimum enclosing circle', False),
            ('minimum enclosing triangle', False)
        ]

    ######################################################################
    ### EVENTS ###########################################################
    ######################################################################
    def __sel_pto_btn_event(self):
        video_index = self.mainwindow._player.video_index-1

        if video_index<0 and self.get_position(video_index) is not None:return 

        self._sel_pts.append(video_index)
        self._sel_pts =sorted(self._sel_pts)
        #store a temporary path for interpolation visualization
        if len(self._sel_pts) == 2: 
            self._switchangle_btn.show()
        elif len(self._sel_pts) > 2:
            self._sel_pts = self._sel_pts[-1:]
            self._switchangle_btn.hide()
        else:
            self._switchangle_btn.hide()

        self.mainwindow._player.refresh()


    def __switchangle_btn_event(self):
        if len(self._sel_pts) == 2:
            for i in range(self._sel_pts[0], self._sel_pts[1]+1):
                head, tail = self.get_extreme_points(i)
                centroid   = self.get_position(i)
                self._angles[i] = points_angle(centroid, tail)

            self.mainwindow._player.refresh()

    def __calc_walked_distance(self):
        v1 = self.object2d.create_value()
        v1.name = "Total walked distance"
        v1._values, _ = self.calc_walked_distance()

    def __calc_walked_distance_window(self):
        winsize,ok = QInputDialog.getInt(self,"Calculate the walked distance","Enter the window size", 30)
        if ok:
            v2 = self.object2d.create_value()
            v2.name = "Walked distance in the previous {0} frames".format(winsize)
            _, v2._values = self.calc_walked_distance(winsize)

    def __calc_walked_distance_with_direction(self):
        v1 = self.object2d.create_value()
        v1.name = "Total walked distance with direction"
        v1._values, _ = self.calc_walked_distance_with_direction()

    def __calc_walked_distance_window_with_direction(self):
        winsize,ok = QInputDialog.getInt(self,"Calculate the walked distance with direction","Enter the window size", 30)
        if ok:
            v2 = self.object2d.create_value()
            v2.name = "Walked distance with direction in the previous {0} frames".format(winsize)
            _, v2._values = self.calc_walked_distance_with_direction(winsize)

    
    def __pick_a_color_event(self):
        color = QColor(self.color[2], self.color[1], self.color[0])
        color = QColorDialog.getColor(color, parent = self, title = 'Pick a color for the path')
        self.color = color.blue(), color.green(), color.red()
        self.mainwindow._player.refresh()

    ######################################################################
    ### FUNCTIONS ########################################################
    ######################################################################
    def create_popupmenu_actions(self):
        self.tree.add_popup_menu_option(
            label='Remove', 
            function_action=self.remove_dataset, 
            item=self.treenode, icon=conf.ANNOTATOR_ICON_DELETE
        )

        self.tree.add_popup_menu_option('-',item=self.treenode)

        self.tree.add_popup_menu_option(
            label='Total walked distance', 
            function_action=self.__calc_walked_distance, 
            item=self.treenode, icon=conf.ANNOTATOR_ICON_POSITION
        )
        self.tree.add_popup_menu_option(
            label='Walked distance in a window', 
            function_action=self.__calc_walked_distance_window, 
            item=self.treenode, icon=conf.ANNOTATOR_ICON_POSITION
        )

        self.tree.add_popup_menu_option(
            label='Total distance with direction', 
            function_action=self.__calc_walked_distance_with_direction, 
            item=self.treenode, icon=conf.ANNOTATOR_ICON_POSITION
        )
        self.tree.add_popup_menu_option(
            label='Walked distance in a window with direction', 
            function_action=self.__calc_walked_distance_window_with_direction, 
            item=self.treenode, icon=conf.ANNOTATOR_ICON_POSITION
        )

    def create_tree_nodes(self):
        self.treenode = self.tree.create_child(self.name, icon=conf.ANNOTATOR_ICON_CONTOUR, parent=self.parent_treenode )
        self.treenode.win = self
        self.create_popupmenu_actions()

        
        self.create_tracking_tree_nodes()



    ######################################################################
    ### FUNCTIONS ########################################################
    ######################################################################

    def get_angle_angle_value(self, index):
        return self.get_angle(index)

    def get_angle_angularvelocity_value(self, index):
        return self.get_angular_velocity(index)

    def get_angle_difftozero_value(self, index):
        return self.get_angle_diff_to_zero(index)


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
        return self.get_absolute_velocity(index)

    def get_velocity_withdirection_value(self, index):
        return self.get_velocity_with_direction(index)

    def get_velocity_angle_value(self, index):
        return self.get_velocity_angle(index)


    def get_acceleration_x_value(self, index):
        v = self.get_acceleration(index)
        return v[0] if v is not None else None

    def get_acceleration_y_value(self, index):
        v = self.get_acceleration(index)
        return v[1] if v is not None else None

    def get_acceleration_absolute_value(self, index):
        v = self.get_acceleration(index)
        return math.sqrt(v[1]**2+v[0]**2) if v is not None else None








    ################# BOUNDING RECT ###################################################
        
    def create_tracking_boundingrect_tree_nodes(self):
        self.create_group_node('bounding rect', icon=conf.ANNOTATOR_ICON_AREA)
        self.create_data_node('bounding rect > left x', icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('bounding rect > left y', icon=conf.ANNOTATOR_ICON_Y)
        self.create_data_node('bounding rect > width',  icon=conf.ANNOTATOR_ICON_WIDTH)
        self.create_data_node('bounding rect > height', icon=conf.ANNOTATOR_ICON_HEIGHT)
        self.create_data_node('bounding rect > aspect ratio', icon=conf.ANNOTATOR_ICON_ASPECT_RATIO)
        self.create_data_node('bounding rect > area',   icon=conf.ANNOTATOR_ICON_AREA)
        self.create_data_node('bounding rect > perimeter',   icon=conf.ANNOTATOR_ICON_AREA)
        self.create_data_node('bounding rect > equivalent diameter',   icon=conf.ANNOTATOR_ICON_AREA)
        self.create_data_node('bounding rect > extend', icon=conf.ANNOTATOR_ICON_INFO)

    def get_boundingrect_leftx_value(self, index):
        v = self.get_bounding_box(index)
        return v[0] if v is not None else None

    def get_boundingrect_lefty_value(self, index):
        v = self.get_bounding_box(index)
        return v[1] if v is not None else None

    def get_boundingrect_width_value(self, index):
        v = self.get_bounding_box(index)
        return v[2] if v is not None else None

    def get_boundingrect_height_value(self, index):
        v = self.get_bounding_box(index)
        return v[3] if v is not None else None

    def get_boundingrect_aspectratio_value(self, index):
        cnt = self.get_contour(index)
        if cnt is None: return None
        x,y,w,h = cv2.boundingRect(cnt)
        return float(w)/float(h)

    def get_boundingrect_area_value(self, index):
        v = self.get_bounding_box(index)
        return v[0]*v[1] if v is not None else None

    def get_boundingrect_perimeter_value(self, index):
        cnt = self.get_contour(index)
        if cnt is None: return None
        area = cv2.contourArea(cnt)
        x,y,w,h = cv2.boundingRect(cnt)
        return 2*w+2*h
        
    def get_boundingrect_equivalentdiameter_value(self, index):
        area = self.get_boundingrect_area_value(index)
        if area is None: return None
        return np.sqrt(4*area/np.pi)

    def get_boundingrect_extend_value(self, index):
        cnt = self.get_contour(index)
        if cnt is None: return None
        area = cv2.contourArea(cnt)
        x,y,w,h = cv2.boundingRect(cnt)
        rect_area = w*h
        return float(area)/float(rect_area)

    ################# BOUNDING RECT ###################################################









    ################# minimum enclosing triangle ###################################################
        
    def create_tracking_minenclosingtriangle_tree_nodes(self):
        self.create_group_node('minimum enclosing triangle', icon=conf.ANNOTATOR_ICON_AREA)
        
        self.create_group_node('minimum enclosing triangle > p1', icon=conf.ANNOTATOR_ICON_POINT)
        self.create_data_node('minimum enclosing triangle > p1 > x', icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('minimum enclosing triangle > p1 > y', icon=conf.ANNOTATOR_ICON_Y)

        self.create_group_node('minimum enclosing triangle > p2', icon=conf.ANNOTATOR_ICON_POINT)
        self.create_data_node('minimum enclosing triangle > p2 > x', icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('minimum enclosing triangle > p2 > y', icon=conf.ANNOTATOR_ICON_Y)

        self.create_group_node('minimum enclosing triangle > p3', icon=conf.ANNOTATOR_ICON_POINT)
        self.create_data_node('minimum enclosing triangle > p3 > x', icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('minimum enclosing triangle > p3 > y', icon=conf.ANNOTATOR_ICON_Y)

        self.create_data_node('minimum enclosing triangle > perimeter',   icon=conf.ANNOTATOR_ICON_AREA)
        self.create_data_node('minimum enclosing triangle > angle',   icon=conf.ANNOTATOR_ICON_AREA)

    


    def get_minimumenclosingtriangle_p1_x_value(self, index):
        triangle = self.get_minimumenclosingtriangle(index)
        if triangle is None: return None
        return triangle[0][0][0]

    def get_minimumenclosingtriangle_p1_y_value(self, index):
        triangle = self.get_minimumenclosingtriangle(index)
        if triangle is None: return None
        return triangle[0][0][1]

    def get_minimumenclosingtriangle_p2_x_value(self, index):
        triangle = self.get_minimumenclosingtriangle(index)
        if triangle is None: return None
        return triangle[0][1][0]

    def get_minimumenclosingtriangle_p2_y_value(self, index):
        triangle = self.get_minimumenclosingtriangle(index)
        if triangle is None: return None
        return triangle[0][1][1]

    def get_minimumenclosingtriangle_p3_x_value(self, index):
        triangle = self.get_minimumenclosingtriangle(index)
        if triangle is None: return None
        return triangle[0][2][0]

    def get_minimumenclosingtriangle_p3_y_value(self, index):
        triangle = self.get_minimumenclosingtriangle(index)
        if triangle is None: return None
        return triangle[0][2][1]

    def get_minimumenclosingtriangle_perimeter_value(self, index):
        triangle = self.get_minimumenclosingtriangle(index)
        if triangle is None: return None
        p1, p2, p3 = triangle
        return pts_utils.lin_dist(p1[0], p2[0]) + pts_utils.lin_dist(p2[0], p3[0]) + pts_utils.lin_dist(p3[0], p1[0])


    def get_minimumenclosingtriangle_angle_value(self, index):
        return self.get_minimumenclosingtriangle_angle(index)
    ################# minimum enclosing triangle ###################################################




















    def create_tracking_minenclosingcircle_tree_nodes(self):
        self.create_group_node('minimum enclosing circle',      icon=conf.ANNOTATOR_ICON_CIRCLE)
        self.create_data_node('minimum enclosing circle > x',   icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('minimum enclosing circle > y',   icon=conf.ANNOTATOR_ICON_Y)
        self.create_data_node('minimum enclosing circle > radius', icon=conf.ANNOTATOR_ICON_WIDTH)



    


    def get_minimumenclosingcircle_x_value(self, index):
        circle = self.get_minimumenclosingcircle(index)
        if circle is None: return None
        center, radius = circle
        return center[0]

    def get_minimumenclosingcircle_y_value(self, index):
        circle = self.get_minimumenclosingcircle(index)
        if circle is None: return None
        center, radius = circle
        return center[1]

    def get_minimumenclosingcircle_radius_value(self, index):
        circle = self.get_minimumenclosingcircle(index)
        if circle is None: return None
        center, radius = circle
        return radius
















    ################# EXTREME POINTS ####################################################
        
    def create_tracking_extremepoints_tree_nodes(self):
        self.create_group_node('extreme points',            icon=conf.ANNOTATOR_ICON_POINT)
        
        self.create_group_node('extreme points > p1',   icon=conf.ANNOTATOR_ICON_POINT)
        self.create_data_node('extreme points > p1 > x',    icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('extreme points > p1 > y',    icon=conf.ANNOTATOR_ICON_Y)
        
        self.create_group_node('extreme points > p2',   icon=conf.ANNOTATOR_ICON_POINT)
        self.create_data_node('extreme points > p2 > x',    icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('extreme points > p2 > y',    icon=conf.ANNOTATOR_ICON_Y)
        
        self.create_data_node('extreme points > angle',     icon=conf.ANNOTATOR_ICON_ANGLE)
        
    def get_extremepoints_p1_x_value(self, index):
        v = self.get_extreme_points(index)
        return v[0][0] if v is not None else None

    def get_extremepoints_p1_y_value(self, index):
        v = self.get_extreme_points(index)
        return v[0][1] if v is not None else None

    def get_extremepoints_p2_x_value(self, index):
        v = self.get_extreme_points(index)
        return v[1][0] if v is not None else None

    def get_extremepoints_p2_y_value(self, index):
        v = self.get_extreme_points(index)
        return v[1][1] if v is not None else None

    def get_extremepoints_angle_value(self, index):
        v = self.get_extreme_points(index)
        return math.degrees(pts_utils.points_angle(v[0], v[1])) if v is not None else None

    ################# FIT ELLISPSE ####################################################











    ################# FIT ELLIPSE ####################################################
        
    def create_tracking_fitellipse_tree_nodes(self):
        self.create_group_node('fit ellipse',                icon=conf.ANNOTATOR_ICON_ELLIPSE)
        self.create_data_node('fit ellipse > center x',          icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('fit ellipse > center y',          icon=conf.ANNOTATOR_ICON_Y)
        self.create_data_node('fit ellipse > major axis size', icon=conf.ANNOTATOR_ICON_HEIGHT)
        self.create_data_node('fit ellipse > minor axis size', icon=conf.ANNOTATOR_ICON_WIDTH)
        self.create_data_node('fit ellipse > angle',             icon=conf.ANNOTATOR_ICON_ANGLE)

        
        
    def get_fitellipse_centerx_value(self, index):
        v = self.get_fit_ellipse(index)
        return v[0][0] if v is not None else None

    def get_fitellipse_centery_value(self, index):
        v = self.get_fit_ellipse(index)
        return v[0][1] if v is not None else None

    def get_fitellipse_majoraxissize_value(self, index):
        v = self.get_fit_ellipse(index)
        return v[1][1] if v is not None else None

    def get_fitellipse_minoraxissize_value(self, index):
        v = self.get_fit_ellipse(index)
        return v[1][0] if v is not None else None

    def get_fitellipse_angle_value(self, index):
        v = self.get_fit_ellipse(index)
        return v[2] if v is not None else None


    ################# FIT ELLIPSE ####################################################






    ################# CONVEX HULL ####################################################
        
    def create_tracking_convexhull_tree_nodes(self):
        self.create_group_node('convex hull',         icon=conf.ANNOTATOR_ICON_HULL)
        self.create_data_node('convex hull > area', icon=conf.ANNOTATOR_ICON_AREA)
        self.create_data_node('convex hull > perimeter', icon=conf.ANNOTATOR_ICON_AREA)
        self.create_data_node('convex hull > equivalent diameter', icon=conf.ANNOTATOR_ICON_CIRCLE)
        self.create_data_node('convex hull > solidity', icon=conf.ANNOTATOR_ICON_BLACK_CIRCLE)

    def get_convexhull_area_value(self, index):
        cnt = self.get_contour(index)
        if cnt is None: return None
        hull = cv2.convexHull(cnt)
        return cv2.contourArea(hull)

    def get_convexhull_perimeter_value(self, index):
        cnt = self.get_contour(index)
        if cnt is None: return None
        hull = cv2.convexHull(cnt)
        return cv2.arcLength(hull, True)

    def get_convexhull_equivalentdiameter_value(self, index):
        cnt = self.get_contour(index)
        if cnt is None: return None
        hull = cv2.convexHull(cnt)
        area = cv2.contourArea(hull)
        return np.sqrt(4*area/np.pi)
        
    def get_convexhull_solidity_value(self, index):
        cnt = self.get_contour(index)
        if cnt is None: return None
        area = cv2.contourArea(cnt)
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        return float(area)/float(hull_area)

    ################# CONVEX HULL ####################################################




    ################# ROTATED RECTANGLE ####################################################

    def create_tracking_rotatedrectangle_tree_nodes(self):
        self.create_group_node('rotated rectangle',             icon=conf.ANNOTATOR_ICON_AREA)
        self.create_data_node('rotated rectangle > center x',   icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('rotated rectangle > center y',   icon=conf.ANNOTATOR_ICON_Y)
        self.create_data_node('rotated rectangle > width',      icon=conf.ANNOTATOR_ICON_HEIGHT)
        self.create_data_node('rotated rectangle > height',     icon=conf.ANNOTATOR_ICON_WIDTH)
        self.create_data_node('rotated rectangle > angle',      icon=conf.ANNOTATOR_ICON_ANGLE)

    

    def get_rotatedrectangle_centerx_value(self, index):
        v = self.get_rotatedrectangle(index)
        return v[0][0] if v is not None else None

    def get_rotatedrectangle_centery_value(self, index):
        v = self.get_rotatedrectangle(index)
        return v[0][1] if v is not None else None

    def get_rotatedrectangle_width_value(self, index):
        v = self.get_rotatedrectangle(index)
        return v[1][0] if v is not None else None

    def get_rotatedrectangle_height_value(self, index):
        v = self.get_rotatedrectangle(index)
        return v[1][1] if v is not None else None

    def get_rotatedrectangle_angle_value(self, index):
        v = self.get_rotatedrectangle(index)
        return v[2] if v is not None else None

    

    ################# ROTATED RECTANGLE ####################################################






    ################# MOMENTS ####################################################

    def create_tracking_moments_tree_nodes(self):
        self.create_group_node('moments',           icon=conf.ANNOTATOR_ICON_HULL)
        self.create_data_node('moments > m00',  icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > m10',  icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > m01',  icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > m20',  icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > m11',  icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > m02',  icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > m30',  icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > m21',  icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > m12',  icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > m03',  icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > mu20',     icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > mu11',     icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > mu02',     icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > mu30',     icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > mu21',     icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > mu12',     icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > mu03',     icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > nu20',     icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > nu11',     icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > nu02',     icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > nu30',     icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > nu21',     icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > nu12',     icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('moments > nu03',     icon=conf.ANNOTATOR_ICON_X)

    ################# MOMENTS ####################################################

    

    def get_moments_m00_value(self, index): return self.get_moment(index, 'm00')
    def get_moments_m10_value(self, index): return self.get_moment(index, 'm10')
    def get_moments_m01_value(self, index): return self.get_moment(index, 'm01')
    def get_moments_m20_value(self, index): return self.get_moment(index, 'm20')
    def get_moments_m11_value(self, index): return self.get_moment(index, 'm11')
    def get_moments_m02_value(self, index): return self.get_moment(index, 'm02')
    def get_moments_m30_value(self, index): return self.get_moment(index, 'm30')
    def get_moments_m21_value(self, index): return self.get_moment(index, 'm21')
    def get_moments_m12_value(self, index): return self.get_moment(index, 'm12')
    def get_moments_m03_value(self, index): return self.get_moment(index, 'm03')
    def get_moments_mu20_value(self, index): return self.get_moment(index, 'mu20')
    def get_moments_mu11_value(self, index): return self.get_moment(index, 'mu11')
    def get_moments_mu02_value(self, index): return self.get_moment(index, 'mu02')
    def get_moments_mu30_value(self, index): return self.get_moment(index, 'mu30')
    def get_moments_mu21_value(self, index): return self.get_moment(index, 'mu21')
    def get_moments_mu12_value(self, index): return self.get_moment(index, 'mu12')
    def get_moments_mu03_value(self, index): return self.get_moment(index, 'mu03')
    def get_moments_nu20_value(self, index): return self.get_moment(index, 'nu20')
    def get_moments_nu11_value(self, index): return self.get_moment(index, 'nu11')  
    def get_moments_nu30_value(self, index): return self.get_moment(index, 'nu02')
    def get_moments_nu02_value(self, index): return self.get_moment(index, 'nu30')
    def get_moments_nu21_value(self, index): return self.get_moment(index, 'nu21')
    def get_moments_nu12_value(self, index): return self.get_moment(index, 'nu12')
    def get_moments_nu03_value(self, index): return self.get_moment(index, 'nu03')



    ################# HU MOMENTS ####################################################

    def create_tracking_humoments_tree_nodes(self):
        self.create_group_node('hu moments',        icon=conf.ANNOTATOR_ICON_HULL)
        self.create_data_node('hu moments > hu0',   icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('hu moments > hu1',   icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('hu moments > hu2',   icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('hu moments > hu3',   icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('hu moments > hu4',   icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('hu moments > hu5',   icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('hu moments > hu6',   icon=conf.ANNOTATOR_ICON_X)


    

    def get_humoments_hu0_value(self, index): return self.get_humoment(index, 0)
    def get_humoments_hu1_value(self, index): return self.get_humoment(index, 1)
    def get_humoments_hu2_value(self, index): return self.get_humoment(index, 2)
    def get_humoments_hu3_value(self, index): return self.get_humoment(index, 3)
    def get_humoments_hu4_value(self, index): return self.get_humoment(index, 4)
    def get_humoments_hu5_value(self, index): return self.get_humoment(index, 5)
    def get_humoments_hu6_value(self, index): return self.get_humoment(index, 6)
    


    ################# HU MOMENTS ####################################################










    def create_tracking_tree_nodes(self):
        ################# CONTOUR #########################################################
        self.create_data_node('area',  icon=conf.ANNOTATOR_ICON_AREA)
        self.create_data_node('perimeter', icon=conf.ANNOTATOR_ICON_AREA)
        
        self.create_data_node('equivalent diameter', icon=conf.ANNOTATOR_ICON_CIRCLE)

        self.create_group_node('angle',                     icon=conf.ANNOTATOR_ICON_ANGLE)
        self.create_data_node('angle > angle',              icon=conf.ANNOTATOR_ICON_POSITION)
        self.create_data_node('angle > angular velocity',   icon=conf.ANNOTATOR_ICON_VELOCITY)
        self.create_data_node('angle > diff to zero',       icon=conf.ANNOTATOR_ICON_VELOCITY)


        self.create_group_node('position', icon=conf.ANNOTATOR_ICON_POSITION)
        self.create_data_node('position > x',   icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('position > y',   icon=conf.ANNOTATOR_ICON_Y)

        self.create_group_node('velocity',          icon=conf.ANNOTATOR_ICON_VELOCITY)
        self.create_data_node('velocity > x',       icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('velocity > y',       icon=conf.ANNOTATOR_ICON_Y)
        self.create_data_node('velocity > absolute', icon=conf.ANNOTATOR_ICON_INFO)
        self.create_data_node('velocity > with direction', icon=conf.ANNOTATOR_ICON_INFO)
        self.create_data_node('velocity > angle',   icon=conf.ANNOTATOR_ICON_INFO)


        self.create_group_node('acceleration',          icon=conf.ANNOTATOR_ICON_ACCELERATION)
        self.create_data_node('acceleration > x',       icon=conf.ANNOTATOR_ICON_X)
        self.create_data_node('acceleration > y',       icon=conf.ANNOTATOR_ICON_Y)
        self.create_data_node('acceleration > absolute', icon=conf.ANNOTATOR_ICON_INFO)

        self.create_tracking_boundingrect_tree_nodes()      
        self.create_tracking_fitellipse_tree_nodes()
        self.create_tracking_extremepoints_tree_nodes()
        self.create_tracking_convexhull_tree_nodes()
        self.create_tracking_rotatedrectangle_tree_nodes()
        self.create_tracking_minenclosingcircle_tree_nodes()
        self.create_tracking_minenclosingtriangle_tree_nodes()
        self.create_tracking_moments_tree_nodes()
        self.create_tracking_humoments_tree_nodes()
                
    ######################################################################
    ### FUNCTIONS ########################################################
    ######################################################################

    def __draw_point(self, frame, p, color=(100,0,100)):
        cv2.circle(frame, p, 5, (255,255,255), -1)
        cv2.circle(frame, p, 3, color, -1)

    def draw_contour(self, frame, frame_index):
        cnt = self.get_contour(frame_index)
        if cnt is not None: cv2.polylines(frame, np.array( [cnt] ), True, self.color, 2)

    def draw_angle(self, frame, frame_index):
        angle = self.get_angle(frame_index)
        p1 = self.get_position(frame_index)
        if angle is None or p1 is None: return None

        p2 = int(round(p1[0]+40*math.cos(angle))), int(round(p1[1]+40*math.sin(angle)))
        cv2.line(frame, p1, p2, (255,100,0), 2)
    
    def draw_boundingrect(self, frame, frame_index):
        rect = self.get_bounding_box(frame_index)
        if rect is None: return None
        x,y,w,h = rect
        cv2.rectangle(frame,(x,y),(x+w,y+h), self.color,2)

    def draw_fitellipse(self, frame, frame_index):
        ellipse = self.get_fit_ellipse(frame_index)
        if ellipse is None: return None
        (x,y),(MA,ma),angle = ellipse
        cv2.ellipse(frame,(int(round(x)),int(round(y)) ),( int(round(MA)), int(round(ma)) ) ,int(round(angle)),0,360,(0,0,255), 1)

    def draw_extremepoints(self, frame, frame_index):
        head, tail = self.get_extreme_points(frame_index)
        if head is not None: self.__draw_point(frame, head, color=(100,0,100) )
        if tail is not None: self.__draw_point(frame, tail, color=(100,100,0) )

    def draw_convexhull(self, frame, frame_index):
        cnt = self.get_contour(frame_index)
        if cnt is None: return None
        hull = cv2.convexHull(cnt)
        cv2.polylines(frame, np.array( [hull] ), True, self.color, 1)

    def draw_rotatedrectangle(self, frame, frame_index):
        
        rect = self.get_rotatedrectangle(frame_index)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(frame,[box],0, self.color,1)

    def draw_minimumenclosingcircle(self, frame, frame_index):
        circle = self.get_minimumenclosingcircle(frame_index)
        if circle is not None:
            center, radius = circle
            center = int(round(center[0])), int(round(center[1]))
            cv2.circle(frame, center, int(round(radius)), self.color)


    def draw_minenclosingtriangle(self, frame, frame_index):
        triangle = self.get_minimumenclosingtriangle(frame_index)
        if triangle is not None:
            p1, p2, p3 = triangle
            p1, p2, p3 = tuple(p1[0]),tuple(p2[0]),tuple(p3[0])
            cv2.line(frame, p1, p2, 255)
            cv2.line(frame, p2, p3, 255)
            cv2.line(frame, p3, p1, 255)

    def draw_velocity_vector(self, frame, frame_index):
        vel = self.get_velocity(frame_index)
        p0  = self.get_position(frame_index)
        if vel is not None and p0 is not None:
            p1 = p0[0]-vel[0], p0[1]-vel[1]
            cv2.line(frame, p0, p1, (255,255,0))



    def draw(self, frame, frame_index):

        for i in self._sel_pts: #store a temporary path for interpolation visualization
            p = self.get_position(i)
            cv2.circle(frame, p, 20, (255, 255, 255), 4, lineType=cv2.LINE_AA)  # pylint: disable=no-member
            cv2.circle(frame, p, 20, (50, 50, 255), 1, lineType=cv2.LINE_AA)  # pylint: disable=no-member


        layers = self._layers.value
        if 'contours' in layers:                    self.draw_contour(frame, frame_index)
        if 'angle' in layers:                       self.draw_angle(frame, frame_index)
        if 'velocity vector' in layers:             self.draw_velocity_vector(frame, frame_index)
        if 'bounding rect' in layers:               self.draw_boundingrect(frame, frame_index)
        if 'fit ellipse' in layers:                 self.draw_fitellipse(frame, frame_index)
        if 'extreme points' in layers:              self.draw_extremepoints(frame, frame_index)
        if 'convex hull' in layers:                 self.draw_convexhull(frame, frame_index)
        if 'rotated rectangle' in layers:           self.draw_rotatedrectangle(frame, frame_index)
        if 'minimum enclosing circle' in layers:    self.draw_minimumenclosingcircle(frame, frame_index)
        if 'minimum enclosing triangle' in layers:  self.draw_minenclosingtriangle(frame, frame_index)
        
    ################# CONTOUR #########################################################

    
    def get_angle_value(self, index):
        return self.get_angle(index)

    def get_area_value(self, index):
        cnt = self.get_contour(index)
        if cnt is None: return None
        return cv2.contourArea(cnt)

    def get_perimeter_value(self, index):
        cnt = self.get_contour(index)
        if cnt is None: return None
        return cv2.arcLength(cnt, True)

    def get_equivalentdiameter_value(self, index):
        cnt = self.get_contour(index)
        if cnt is None: return None
        area = cv2.contourArea(cnt)
        return np.sqrt(4*area/np.pi)


    

    @property
    def mainwindow(self):    return self.object2d.mainwindow
    @property 
    def tree(self): return self.object2d.tree
    @property 
    def video_capture(self): return self._object2d.video_capture

    @property 
    def parent_treenode(self):  return self.object2d.treenode
