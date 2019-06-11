import cv2, math, os, numpy as np
from pythonvideoannotator_models.models.video.objects.object2d.utils.interpolation import interpolate_positions
from pythonvideoannotator_models.models.video.objects.object2d.datasets.dataset import Dataset



class PathBase(Dataset):

    COLORS = [
        (240, 163, 255), (0, 117, 220), (153, 63, 0), (76, 0, 92),
        (25, 25, 25), (0, 92, 49), (43, 206, 72), (255, 204, 153),
        (128, 128, 128), (148, 255, 181), (143, 124, 0), (157, 204, 0),
        (194, 0, 136), (0, 51, 128), (255, 164, 5), (255, 168, 187),
        (66, 102, 0), (255, 0, 16), (94, 241, 242), (0, 153, 143),
        (116, 10, 255), (153, 0, 0), (255, 255, 0), (255, 80, 5)
    ]

    count_paths = 0

    def __init__(self, object2d):
        super(PathBase, self).__init__(object2d)

        self.name       = 'path({0})'.format(len(object2d))  if len(object2d)>0 else 'path'

        self._apply_referencial = False
        self._referencial       = None # point to be use as reference point to the path
        self._points            = []   # path of the object
        self._modified          = []   # store all the frames where there were manual modifications.
        self._identity_switched   = []   # store all the identification switches

        self._tmp_points= [] #store a temporary path to pre-visualize de interpolation
        self._sel_pts   = [] #store the selected points


        self._color = self.COLORS[PathBase.count_paths]

        PathBase.count_paths += 1
        if PathBase.count_paths>=len(self.COLORS):
            PathBase.count_paths = 0

        self._show_object_name = True # Flag to show or hide the object name
        self._show_name = True # Flag to show or hide the name

    ######################################################################
    ### CLASS FUNCTIONS ##################################################
    ######################################################################

    def __len__(self):                   return len(self._points)
    def __getitem__(self, index):

        if isinstance(index, slice):
            # Get the start, stop, and step from the slice
            return [self.get_position(i) for i in range(index.start, index.stop) ]
        else:
            return self.get_position(index)


    def __setitem__(self, index, value):
        if value is None:
            self.set_position(index, None, None)
        else:
            self.set_position(index, value[0], value[1])
    def __str__(self):                   return self.name

    ######################################################################
    ### DATA MODIFICATION AND ACCESS #####################################
    ######################################################################

    def clone_path(self):
        path                   = self.object2d.create_path()
        path.name              = self.name + ' (copy {0})'.format(len(self.object2d))
        path._points           = list(self._points)
        path.referencial       = self.referencial if self.referencial else None
        path.apply_referencial = self.apply_referencial
        return path

    def calculate_tmp_interpolation(self): 
        #store a temporary path to visualize the interpolation 
        begin       = self._sel_pts[0]
        end         = self._sel_pts[-1]
        positions   = [[i, self.get_position(i)] for i in range(begin, end+1) if self.get_position(i) is not None]

        if len(positions)>=2:
            positions   = interpolate_positions(positions, begin, end, interpolation_mode=self.interpolation_mode)
            self._tmp_points= [pos for frame, pos in positions]
            return True
        else:
            return False

    def delete_range(self, begin, end):
        for index in range(begin+1, end):
            if index <= len(self) and self[index] != None: self[index] = None
            self._tmp_points= []

    def interpolate_range(self, begin, end, interpolation_mode=None):
        positions = [[i, self.get_position(i)] for i in range(begin, end+1) if self.get_position(i) is not None]
        if len(positions)>=2:
            positions = interpolate_positions(positions, begin, end, interpolation_mode)
            for frame, pos in positions: self.set_position(frame, pos[0], pos[1])
            self._tmp_points= []

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

    def was_modified(self, index):
        if len(self._modified)<=index:
            return False
        else:
            return self._modified[index]

    def was_identity_switched(self, index):
        if len(self._identity_switched)<=index:
            return False
        else:
            return self._identity_switched[index]

    def get_position(self, index, use_referencial=True):
        if index<0 or index>=len(self): return None

        #In case the referencial is active
        if use_referencial and self.apply_referencial and self.referencial:
            if self._points[index]:
                p = self._points[index]
                r = self.referencial
                return p[0]-r[0], p[1]-r[1]
            else:
                return None
        else:
            return self._points[index]

    def set_position(self, index, x, y):
        # add positions in case they do not exists
        if index >= len(self):
            self._points += [None]*(index+1-len(self))

        if index >= len(self._modified):
            self._modified += [False] * (index+1-len(self._modified))

        if x is None or y is None: 
            self._points[index] = None
        else:
            # create a new moment in case it does not exists
            self._points[index] = x,y

        self._modified[index] = True


    def set_data_from_blob(self, index, blob):
        if blob is None: 
            self.set_position(index, None, None)
        else:
            x, y = blob.centroid
            self.set_position(index, x, y)

    def collide_with_position(self, index, x, y, radius=20):
        p1 = self.get_position(index)
        if p1 is None: return False
        return math.sqrt((p1[0] - x)**2 + (p1[1] - y)**2) < radius
    
    def switch_identity(self,
            positions,
            begin=0,
            end=None
        ):
        """
        Switch identity with other path.

        :param list((float,float)) positions: Path to switch identity with.
        :param int begin: Start frame. By default it starts in the frame 0.
        :param int end: Last frame. By default if no frame is defined it replaces the entire path.
        """
        if end >= len(self): self._points += [None] * (len(self) - end + 1)
        if end >= len(self._identity_switched):
            self._identity_switched += [False] * (len(self._identity_switched) - end + 1)

        if end is None: end = len(self)

        self._points[begin:end+1]            = positions[begin:end+1]
        self._identity_switched[begin:end+1] = [True]*(end-begin+1)
    
    ######################################################################
    ### VIDEO EVENTS #####################################################
    ######################################################################

    def draw_circle(self, frame, frame_index):
        position = self.get_position(frame_index)
        if position != None:
            pos = int(round(position[0], 0)), int(round(position[1], 0))
            cv2.circle(frame, pos, 20, (255, 255, 255), 4, lineType=cv2.LINE_AA)  # pylint: disable=no-member
            cv2.circle(frame, pos, 20, (50, 50, 255), 1, lineType=cv2.LINE_AA)  # pylint: disable=no-member

            cv2.putText(frame, str(frame_index), pos, cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness=2, lineType=cv2.LINE_AA)  # pylint: disable=no-member
            cv2.putText(frame, str(frame_index), pos, cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), thickness=1, lineType=cv2.LINE_AA)  # pylint: disable=no-member

    def draw_position(self, frame, frame_index):
        pos = self.get_position(frame_index)
        if pos is None: return

        pos = int(round(pos[0],0)), int(round(pos[1],0))
        cv2.circle(frame, pos, 8, (255,255,255), -1, lineType=cv2.LINE_AA)
        cv2.circle(frame, pos, 6, self.color,     -1, lineType=cv2.LINE_AA)

    def draw_objname(self, frame, frame_index):
        """
        Draw the name of the object
        :param numpy.array frame: Frame image
        :param int frame_index: Index of the frame to be draw
        """
        pos = self.get_position(frame_index)
        if pos is None: return

        pos = int(round(pos[0], 0)), int(round(pos[1], 0))
        cv2.putText(frame, self.object2d.name, (pos[0], pos[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(frame, self.object2d.name, (pos[0], pos[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)

    def draw_name(self, frame, frame_index):
        """
        Draw the name of the object
        :param numpy.array frame: Frame image
        :param int frame_index: Index of the frame to be draw
        """
        pos = self.get_position(frame_index)
        if pos is None: return

        pos = int(round(pos[0], 0)), int(round(pos[1], 0))
        cv2.putText(frame, self.name, (pos[0], pos[1] + 25), cv2.FONT_HERSHEY_SIMPLEX, .7, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(frame, self.name, (pos[0], pos[1] + 25), cv2.FONT_HERSHEY_SIMPLEX, .7, (0, 90, 0), 2, cv2.LINE_AA)

    def draw_path(self,frame, start=None, end=None):
        # Draw the selected path #store a temporary path for interpolation visualization
        points = self._points
        if end:   points = points[:end]
        if start: points = points[start:]
        cnt = np.int32([p for p in points if p is not None])
        cv2.polylines(frame, [cnt], False, self.color, 1, lineType=cv2.LINE_AA)

    def draw(self, frame, frame_index):
        self.draw_position(frame, frame_index)

        if self.referencial:
            cv2.circle(frame, self.referencial, 8, (0,255,0), -1, lineType=cv2.LINE_AA)
            cv2.circle(frame, self.referencial, 6, (100,0,100), -1, lineType=cv2.LINE_AA)

        # Draw the selected blobs
        for item in self._sel_pts: #store a temporary path for interpolation visualization
            self.draw_circle(frame, item)

        # Draw a temporary path
        if len(self._tmp_points) >= 2:
            cnt = np.int32(self._tmp_points)
            cv2.polylines(frame, [cnt], False, (255, 0, 0), 1, lineType=cv2.LINE_AA)

        if 1 <= len(self._sel_pts) >= 2: #store a temporary path for interpolation visualization
            start = self._sel_pts[0] #store a temporary path for interpolation visualization
            end = frame_index if len(self._sel_pts)==1 else self._sel_pts[-1]
            self.draw_path(frame, start, end)



        if self.show_object_name:
            self.draw_objname(frame, frame_index)

        if self.show_name:
            self.draw_name(frame, frame_index)


    ######################################################################
    ### PROPERTIES #######################################################
    ######################################################################

    @property
    def show_object_name(self):
        return self._show_object_name
    @show_object_name.setter
    def show_object_name(self, value):
        self._show_object_name = value

    @property
    def color(self):
        if self._color is None:
            self._color = (255, 0, 0)
        return self._color

    @color.setter
    def color(self, value):
        self._color = value

    @property
    def show_name(self):
        return self._show_name

    @show_name.setter
    def show_name(self, value):
        self._show_name = value

    @property
    def interpolation_mode(self): return None

    @property
    def referencial(self): return self._referencial
    @referencial.setter
    def referencial(self, value): self._referencial = value

    @property
    def apply_referencial(self):  return self._apply_referencial
    @apply_referencial.setter
    def apply_referencial(self, value): self._apply_referencial = value

    @property
    def data(self):
        return self._points

    @data.setter
    def data(self, value):
        self._points = value

    @property
    def selected_frames(self):
        return self._sel_pts