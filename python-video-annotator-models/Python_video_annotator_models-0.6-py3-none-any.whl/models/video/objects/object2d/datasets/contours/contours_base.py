import cv2, math, os, numpy as np
from pythonvideoannotator_models.models.video.objects.object2d.utils.interpolation import interpolate_positions
from pythonvideoannotator_models.models.video.objects.object2d.datasets.dataset import Dataset

from pythonvideoannotator_models.utils.tools import points_angle, min_dist_angles,lin_dist, rotate_image
  

class ContoursBase(Dataset):

    COLORS = [
        (240, 163, 255), (0, 117, 220), (153, 63, 0), (76, 0, 92),
        (25, 25, 25), (0, 92, 49), (43, 206, 72), (255, 204, 153),
        (128, 128, 128), (148, 255, 181), (143, 124, 0), (157, 204, 0),
        (194, 0, 136), (0, 51, 128), (255, 164, 5), (255, 168, 187),
        (66, 102, 0), (255, 0, 16), (94, 241, 242), (0, 153, 143),
        (116, 10, 255), (153, 0, 0), (255, 255, 0), (255, 80, 5)
    ]

    count_contours = 0

    def __init__(self, object2d):
        super(ContoursBase, self).__init__(object2d)
        
        self.object2d   = object2d
        self.name       = 'contours({0})'.format(len(object2d)) if len(object2d)>0 else 'contours'
        self._contours  = []
        self._angles    = []

        self._color = self.COLORS[ContoursBase.count_contours]

        ContoursBase.count_contours += 1
        if ContoursBase.count_contours>=len(self.COLORS):
            ContoursBase.count_contours = 0


        
    ######################################################################
    ### CLASS FUNCTIONS ##################################################
    ######################################################################

    def __len__(self):              return len(self._contours)
    def __getitem__(self, index):   return self._contours[index] if index<len(self) else None
    def __str__(self):              return self.name

    
    ######################################################################
    ### DATA ACCESS FUNCTIONS ############################################
    ######################################################################

    def flip(self, index):
        """
        flip the orientation of the contour
        """
        head, tail  = self.get_extreme_points(index)
        centroid    = self.get_position(index)

        if tail is not None and centroid is not None:
            self.set_angle(index, points_angle(centroid, tail) )

    def get_position(self, index):
        cnt = self.get_contour(index)
        if cnt is None: return None

        M = cv2.moments(cnt)
        if M["m00"]==0:
            return None
        else:
            return int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])

    def get_velocity(self, index):
        p1 = self.get_position(index)
        p2 = self.get_position(index-1)
        if p1 is None or p2 is None: return None
        return p2[0]-p1[0], p2[1]-p1[1]

    def get_velocity_with_direction(self, index):
        vel = self.get_absolute_velocity(index)
        if vel is None: return None

        vel_angle = self.get_velocity_angle(index)
        obj_angle = self.get_angle(index)

        if min_dist_angles(vel_angle, obj_angle)>(np.pi/2):
            return -vel 
        else:
            return vel



    def get_absolute_velocity(self, index):
        v = self.get_velocity(index)
        return math.sqrt(v[1]**2+v[0]**2) if v is not None else None

    def get_velocity_angle(self, index):
        vel = self.get_velocity(index)
        p0  = self.get_position(index)
        if vel is not None and p0 is not None:
            p1 = p0[0]-vel[0], p0[1]-vel[1]
            return points_angle(p0, p1)
        else:
            return None
        
    def get_acceleration(self, index):
        v1 = self.get_velocity(index)
        v2 = self.get_velocity(index-1)
        if v1 is None or v2 is None: return None
        return v2[0]-v1[0], v2[1]-v1[1]

    def get_bounding_box(self, index):
        cnt = self.get_contour(index)
        if cnt is None: return None
        return cv2.boundingRect(cnt)
        
    def get_fit_ellipse(self, index):
        cnt = self.get_contour(index)
        if cnt is None or len(cnt)<5: return None
        return cv2.fitEllipse(cnt)
        
    def get_convex_hull(self, index):
        cnt = self.get_contour(index)
        if cnt is None: return None
        pass

    def __lin_dist(self, p1, p2): return np.linalg.norm( (p1[0]-p2[0], p1[1]-p2[1]) )

    def get_extreme_points(self, index):
        centroid = self.get_position(index)
        contour  = self.get_contour(index)

        if centroid is not None and contour is not None:
            dists = list(map( lambda p: self.__lin_dist( p[0], centroid ), contour ))
            ndx = dists.index(max(dists))           
            head = tuple(contour[ndx][0])
            
            dists = list(map( lambda p: self.__lin_dist( p[0], contour[ndx][0] ), contour ))
            ndx = dists.index(max(dists))
            tail = tuple(contour[ndx][0])

            angle = self.get_angle(index)
            if angle is not None:
                angle1 = points_angle(centroid, head)
                angle2 = points_angle(centroid, tail)

                diff1 = min_dist_angles(angle, angle1)
                diff2 = min_dist_angles(angle, angle2)
                if diff1>diff2:
                    return tail, head           
            
            return head, tail
        else:
            return None, None

    def draw_path(self, frame, start=None, end=None):

        if start is None:
            start=0
        if end is None:
            end=len(self._contours)

        points = []
        for index in range(start, end):
            points.append(self.get_position(index))

        cnt = np.int32([p for p in points if p is not None])

        cv2.polylines(frame, [cnt], False, self.color, 1, lineType=cv2.LINE_AA)

    def get_angle_diff_to_zero(self, index):
        angle = self.get_angle(index)
        return None if angle is None else min_dist_angles(angle, 0)

    def get_angle(self, index):
        if index<0 or index>=len(self._angles): return None
        return self._angles[index] if self._angles[index] is not None else None

    def get_angular_velocity(self, index):
        a1 = self.get_angle(index)
        a2 = self.get_angle(index+1)
        return min_dist_angles(a1, a2) if (a1 is not None and a2 is not None) else None

    def get_contour(self, index):

        if index<0 or index>=len(self._contours): return None
        return self._contours[index] if self._contours[index] is not None else None

    def get_minimumenclosingtriangle(self, index):
        cnt = self.get_contour(index)
        if cnt is None: return None
        res, (p1, p2, p3) = cv2.minEnclosingTriangle(cnt)
        if not res: return None
        return p1, p2, p3

    def get_minimumenclosingtriangle_angle(self, index):
        triangle = self.get_minimumenclosingtriangle(index)
        if triangle is None: return None

        p1, p2, p3 = triangle
        p1, p2, p3 = tuple(p1.flatten()), tuple(p2.flatten()), tuple(p3.flatten()) 
        
        center = (p1[0]+p2[0]+p3[0])/3, (p1[1]+p2[1]+p3[1])/3
        points = sorted([
            (lin_dist(p1, p2)+lin_dist(p1, p3),p1),
            (lin_dist(p1, p2)+lin_dist(p2, p3),p2),
            (lin_dist(p3, p2)+lin_dist(p1, p3),p3),
        ], reverse=True)
        farthest_pt = points[0][1]
        
        return points_angle(center, farthest_pt)
        

    def get_minimumenclosingcircle(self, index):
        cnt = self.get_contour(index)
        if cnt is None: return None
        return cv2.minEnclosingCircle(cnt)

    def get_rotatedrectangle(self, index):
        contour = self.get_contour(index)
        if contour is None: return None
        return cv2.minAreaRect(contour)

    def get_moments(self, index):
        contour = self.get_contour(index)
        if contour is None: return None
        return cv2.moments(contour)

    def get_moment(self, index, key):
        m = self.get_moments(index)
        return None if m is None else m[key]

    def get_humoments(self, index):
        moments = self.get_moments(index)
        if moments is None: return None
        return cv2.HuMoments(moments)

    def get_humoment(self, index, key):
        m = self.get_humoments(index)
        return None if m is None else m[key]

    def set_contour(self, index, contour, angle=None):

        
        # add contours in case they do not exists
        if index >= len(self._contours):
            for i in range(len(self._contours), index + 1): 
                self._contours.append(None)

        if index >= len(self._angles):
            for i in range(len(self._angles), index + 1): 
                self._angles.append(None)

        self._contours[index] = contour

        # No angle was provided to save, we will try to calculate one
        if angle is None:
            p1, p2 = self.get_extreme_points(index)
            centroid = self.get_position(index)
            if centroid is not None:
                angle1  = points_angle(centroid,p1)
                angle2  = points_angle(centroid,p2)

                # Search for the last angle
                last_angle = None
                for i in range(index-1, -1, -1):
                    tmp_angle = self._angles[i]
                    if tmp_angle is not None: 
                        last_angle = tmp_angle
                        break

                # try to match the current angle with the last angle.
                # angles cannot switch values drastically
                if last_angle is not None:
                    diff1 = min_dist_angles(last_angle, angle1)
                    diff2 = min_dist_angles(last_angle, angle2)
                
                    self._angles[index] = angle2 if diff1>diff2 else angle1
                else:
                    #print math.degrees(angle)
                    self._angles[index] = angle1
            else:
                self._angles[index] = angle
        else:
            self._angles[index] = angle
         
    def set_data_from_blob(self,index, blob):
        if blob is None:
            self.set_contour(index, None)
        else:
            self.set_contour(index, blob._contour)


    def set_angle(self, index, angle):
        if index >= len(self._angles):
            for i in range(len(self._angles), index + 1): 
                self._angles.append(None)

        self._angles[index] = angle
    
    
    def calc_walked_distance(self, window_size=0):
        """
        Calculate the walked distance and the total walked distance and the walked distance in a window of frames
        """
        walked_distance         = []
        walked_distance_window  = []
        for i in range(len(self)):
            vel = self.get_absolute_velocity(i)
            if vel is None: vel = 0
            walked_distance.append(
                vel + (walked_distance[i-1] if i>0 else 0)
            )
            walked_distance_window.append(
                walked_distance[i] - (walked_distance[i-window_size] if i>window_size else 0)
            )
        return walked_distance, walked_distance_window
    

    def calc_walked_distance_with_direction(self, window_size=0):
        """
        Calculate the walked distance and the total walked distance and the walked distance in a window of frames
        """
        walked_distance         = []
        walked_distance_window  = []

        for i in range(len(self)):
            vel = self.get_velocity_with_direction(i)
            if vel is None: vel = 0

            walked_distance.append( vel + (walked_distance[i-1] if i>0 else 0) )
            walked_distance_window.append( walked_distance[i] - (walked_distance[i-window_size] if i>window_size else 0) )
           
        return walked_distance, walked_distance_window
    

    def __cut_image(self, frame, x, y, xx, yy):
        x, y, xx, yy = round(x), round(y), round(xx), round(yy)
        x, y, xx, yy = int(x),   int(y),   int(xx),   int(yy)

        
        if len(frame.shape)==3:
            img = np.zeros( (yy-y, xx-x, frame.shape[2]), dtype=frame.dtype)
        else:
            img = np.zeros( (yy-y, xx-x), dtype=frame.dtype)

        _x  = x if x>=0 else 0
        _y  = y if y>=0 else 0
        _xx = xx if xx<=frame.shape[1] else frame.shape[1]
        _yy = yy if yy<=frame.shape[0] else frame.shape[0]
        frame_crop = frame[_y:_yy, _x:_xx]

        
        x1, y1   = _x-x, _y-y
        xx1, yy1 = _xx+x1, _yy+y1
        
        if xx>frame.shape[1]: xx1 = x1+frame_crop.shape[1]
        if yy>frame.shape[0]: yy1 = y1+frame_crop.shape[0]
        #print(x1, y1, xx1, yy1, "|", _x, _y, _xx, _yy, "|",x, y, xx, yy)
        """
        if xx1>img.shape[1]: xx1 = int(img.shape[1])
        if yy1>img.shape[0]: yy1 = int(img.shape[0])

        if (xx1-x1)>(_xx-_x):
            x1, xx1 = (xx1-x1)/2-(_xx-_x)/2, (xx1-x1)/2+(_xx-_x)/2
        if (yy1-y1)>(_yy-_y): 
            y1, yy1 = (yy1-y1)/2-(_yy-_y)/2, (yy1-y1)/2+(_yy-_y)/2
        """
        img[y1:yy1, x1:xx1] = frame_crop
        

        return img

    def get_image(self, index, frame=None, 
        mask=False, 
        circular_mask=False, 
        ellipse_mask=False,
        rect_mask=False,
        angle=False, 
        margin=0, 
        size=None,
        stretch=False,
        image_center=None 
    ):
        bounding_box = self.get_bounding_box(index)
        if bounding_box is None: return False, None


        if type(frame) is not np.ndarray:
            # if the frame is None, get the frame from the video
            cap = self.object2d.video.video_capture
            cap.set(cv2.CAP_PROP_POS_FRAMES, index-1)
            res, frame = cap.read()
            if not res: return False, None #exit in the case the frame was not read.

        #frame[image_center[1]-4:image_center[1]+4, image_center[0]-4:image_center[0]+4] = 255

        ################################################################################################
        # MASK THE IMAGE 
        if mask:
            maskimg = np.zeros_like(frame)
            cnt     = self.get_contour(index)
            if cnt is not None: 
                cv2.fillPoly( maskimg, np.array([cnt]), (255,255,255) )
                if not isinstance(mask, bool) and isinstance(mask, int):
                    if (mask % 2)!=1: 
                        mask += 1
                    kernel  = np.ones((mask,mask),np.uint8)
                    maskimg = cv2.dilate(maskimg,kernel)
            frame = cv2.bitwise_and(frame, maskimg)
        
        if circular_mask:
            maskimg = np.zeros_like(frame)
            center  = self.get_position(index)
            cv2.circle(maskimg, center, circular_mask, (255,255,255), -1)
            frame = cv2.bitwise_and(frame, maskimg)

        if ellipse_mask:
            maskimg = np.zeros_like(frame)
            (x,y),(MA,ma),a = self.get_fit_ellipse(index)
            cv2.ellipse(maskimg,
                (int(round(x)),int(round(y)) ),( int(round(MA)), int(round(ma)) ) ,int(round(a)),0,360,(255,255,255), -1)
            frame = cv2.bitwise_and(frame, maskimg)

        if rect_mask:
            maskimg = np.zeros_like(frame)
            rect = self.get_rotatedrectangle(index)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.fillPoly( maskimg, np.array([box]), (255,255,255) )
            frame = cv2.bitwise_and(frame, maskimg)
        ################################################################################################
        
        bigger_side  = max(bounding_box[2], bounding_box[3])
        x, y, w, h   = bounding_box
        """if image_center is not None:
            x, y, xx, yy = image_center[0]-w/2, image_center[1]-h/2, image_center[0]+w/2, image_center[1]+h/2
        else:
        """
        x, y, xx, yy = x, y, x+w, y+h
        x, y, xx, yy = x-margin, y-margin, xx+margin, yy+margin

        cut_center = (x+xx)/2, (y+yy)/2

        if angle:
            safe_margin  = bigger_side/2
            x, y, xx, yy = x-safe_margin, y-safe_margin, xx+safe_margin, yy+safe_margin
            
            #print('cut', index, frame.shape, x, y, xx, yy)
            cut = self.__cut_image(frame, x, y, xx, yy)

          
            if angle=='up':     angle = self.get_angle(index)
            if angle=='down':   angle = self.get_angle(index)+np.pi
            rotdeg = math.degrees( angle )


            if image_center is not None:
                #o = cut.copy()
                x_shift, y_shift = int(round(cut_center[0]-image_center[0])), int(round(cut_center[1]-image_center[1]))
                M   = np.float32([[1,0,x_shift],[0,1,y_shift]])
                cut = cv2.warpAffine(cut,M,(cut.shape[1],cut.shape[0]))

                #cut[cut.shape[0]/2-4:cut.shape[0]/2+4, cut.shape[1]/2-4:cut.shape[1]/2+4,0] = 255
                #cut[cut.shape[0]/2-4:cut.shape[0]/2+4, cut.shape[1]/2-4:cut.shape[1]/2+4,1:] = 0

                #cv2.imwrite('test/{0}.png'.format(index), cut )
            
            #cv2.imwrite('test/{0}.png'.format(index), cut )

            img2save = rotate_image( cut, rotdeg+90)
            #img2save[:,:,1] = rotate_image( o,   rotdeg+90)[:,:,1]
            #img2save[:,:,0] = 0


            _, sizes, _ = self.get_rotatedrectangle(index)
            center_x, center_y = img2save.shape[1]/2, img2save.shape[0]/2
            (width, height) = min(sizes), max(sizes)

            
            result = self.__cut_image(img2save, 
                center_x-width/2-margin, center_y-height/2-margin,
                center_x+width/2+margin, center_y+height/2+margin
            )
        else:
            result = self.__cut_image(frame, x,y,xx,yy)

        if size is not None:
            if stretch:
                result = cv2.resize(result, size)
            else:
                h, w = result.shape[:2]
                if w>size[0] or h>size[1]:
                    if h>w:
                        ratio = float(size[1])/float(h)
                        new_w, new_h = int((w*ratio)), int((h*ratio))
                        result = cv2.resize(result, (new_w, new_h) )
                    else:
                        ratio = float(size[0])/float(w)
                        new_w, new_h = int((w*ratio)), int((h*ratio))
                        result = cv2.resize(result, (new_w, new_h) )

                if len(result.shape)>2:
                    final = np.zeros( (size[0], size[1], result.shape[2]), dtype=result.dtype)
                else:
                    final = np.zeros( (size[0], size[1]), dtype=result.dtype)

                hh, ww       =  final.shape[:2]
                h, w         =  result.shape[:2]
                x, y, xx, yy =  (ww/2)-(w/2), (hh/2)-(h/2), \
                                (ww/2)+(w/2), (hh/2)+(h/2)
                x, y, xx, yy = int(x), int(y), int(xx), int(yy)

                final[y:yy, x:xx] = result
                result = final


        return True, result


    ######################################################################
    ### PROPERTIES #######################################################
    ######################################################################

    @property
    def data(self):
        return self._contours

    @property
    def angles(self):
        return self._angles

    @property
    def color(self):
        if self._color is None:
            self._color = (255, 0, 0)
        return self._color


    @color.setter
    def color(self, value):
        self._color = value
