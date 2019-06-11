import pyforms, math, cv2, numpy as np
from confapp import conf
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlDir
from pyforms.controls import ControlNumber
from pyforms.controls import ControlList
from pyforms.controls import ControlCombo
from pyforms.controls import ControlSlider
from pyforms.controls import ControlImage
from pyforms.controls import ControlButton
from pyforms.controls import ControlCheckBox
from pyforms.controls import ControlCheckBoxList
from pyforms.controls import ControlEmptyWidget
from pyforms.controls import ControlProgress

from mcvapi.blobs.order_by_position import combinations

from pythonvideoannotator_models_gui.dialogs import DatasetsDialog
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.contours import Contours
from pythonvideoannotator_models.utils.tools import points_angle, min_dist_angles, lin_dist

from pythonvideoannotator_models.utils.tools import savitzky_golay

from sklearn import svm, metrics
from sklearn.model_selection import GridSearchCV
from sklearn.decomposition import PCA
from sklearn.svm import SVC



class FindOrientationWindow(BaseWidget):

    def __init__(self, parent=None):
        super(FindOrientationWindow, self).__init__('Estimate countour orientation', parent_win=parent)
        self.mainwindow = parent

        self.set_margin(5)
        
        self.setMinimumHeight(300)
        self.setMinimumWidth(300)

        self._panel         = ControlEmptyWidget('Videos')
        self._progress      = ControlProgress('Progress')
        self._apply         = ControlButton('Apply', checkable=True)
        self._debug         = ControlCheckBox('Create all the intermediate values')

        self._min_steps     = ControlSlider('Minimum steps', default=20,  minimum=1, maximum=1000)
        self._min_dist      = ControlSlider('Minimum distance', default=30,  minimum=1, maximum=1000)

        self._panel.value = self.contours_dialog = DatasetsDialog(self)
        self.contours_dialog.datasets_filter = lambda x: isinstance(x, Contours)

        
        self._formset = [         
            '_panel',
            ('_min_steps','_min_dist'),
            '_debug',
            '_apply',
            '_progress'
        ]

        self._apply.value           = self.__apply_event
        self._apply.icon            = conf.ANNOTATOR_ICON_PATH

        self._progress.hide()

    def init_form(self):
        super(FindOrientationWindow, self). init_form()
        
    ###########################################################################
    ### EVENTS ################################################################
    ###########################################################################



    ###########################################################################
    ### PROPERTIES ############################################################
    ###########################################################################
    
    
    
    def __apply_event(self):
        IMAGE_SIZE = 150

        if self._apply.checked and self._apply.label == 'Apply':
            self._panel.enabled         = False
            self._apply.label           = 'Cancel'
            self._min_dist.enabled      = False
            self._min_steps.enabled     = False

            total_2_analyse  = 0
            for video, (begin, end), datasets in self.contours_dialog.selected_data:
                capture          = video.video_capture
                total_2_analyse += (end-begin)#*len(datasets)*1

            self._progress.min = 0
            self._progress.max = total_2_analyse
            self._progress.show()

            debug_mode = self._debug.value

            count = 0
            for video, (begin, end), datasets in self.contours_dialog.selected_data:
                if len(datasets)==0: continue
                begin, end = int(begin), int(end)
                
                back_frames  = []
                front_frames = []
                for dataset in datasets:

                    for i in range(begin, end):
                        self._progress.value = count; count+=1
                        
                        ok, img   = dataset.get_image(i, mask=True, angle='up', size=(IMAGE_SIZE,IMAGE_SIZE) )
                       
                        if ok:
                            cv2.normalize(img,   img,   0, 255, cv2.NORM_MINMAX)

                            v1 = img[:int(img.shape[0]/2)].sum() / np.count_nonzero(img[:int(img.shape[0]/2)])
                            v2 = img[int(img.shape[0]/2):].sum() / np.count_nonzero(img[int(img.shape[0]/2):])

                            if v1<v2: 
                                dataset.flip(i)   

            """
                    window      = 30
                    min_walked  = 50
                    savitzky_golay_window_size = (window+1 if (window % 2 )==0 else window)

                    if debug_mode:
                        # create the values for debug ##########################################
                        v1 = dataset.object2d.create_value()
                        v1.name = 'Est. orient. - step1 - smoothed walked distance (prev {0} frames)'.format(window)
                        v2 = dataset.object2d.create_value()
                        v2.name = 'Est. orient. - step1 - smoothed walked distance with direction (prev {0} frames)'.format(window)    

                        vflipped = dataset.object2d.create_value()
                        vflipped.name = 'Est. orient. - step1 - flipped images'
                        ########################################################################

                    
                    _, walked_distance     = dataset.calc_walked_distance(window)
                    _, dir_walked_distance = dataset.calc_walked_distance_with_direction(window)
                    walked_distance        = savitzky_golay(np.array(walked_distance), window_size=savitzky_golay_window_size)
                    dir_walked_distance    = savitzky_golay(np.array(dir_walked_distance), window_size=savitzky_golay_window_size)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
                    for i in range(begin, end):
                        self._progress.value = count; count+=1
                        if i>=len(walked_distance): continue

                        vflipped.set_value(i, 0)

                        ### Debug ##############################################################
                        if debug_mode: 
                            v1.set_value(i, walked_distance[i])
                            v2.set_value(i, dir_walked_distance[i])
                        ########################################################################

                        if walked_distance[i]>min_walked and dir_walked_distance[i]<-min_walked:
                            dataset.flip(i)

                            if debug_mode: vflipped.set_value(i, 1) 


                    if debug_mode:
                        # create the values for debug ##########################################
                        v1 = dataset.object2d.create_value()
                        v1.name = 'Est. orient. - step2 - smoothed walked distance (prev {0} frames)'.format(window)
                        v2 = dataset.object2d.create_value()
                        v2.name = 'Est. orient. - step2 - smoothed walked distance with direction (prev {0} frames)'.format(window)    

                        vtrainning = dataset.object2d.create_value()
                        vtrainning.name = 'Est. orient. - step2 - good images for trainning'
                        ########################################################################

                    _, walked_distance     = dataset.calc_walked_distance(window)
                    _, dir_walked_distance = dataset.calc_walked_distance_with_direction(window)
                    
                    trainning_frames = []

                    IMAGE_SIZE         = 150
                    MAX_TRAINNING_SET  = 400

                    model = cv2.ml.ANN_MLP_create()
                    layer_sizes = np.int32([IMAGE_SIZE**2, IMAGE_SIZE, IMAGE_SIZE, 2])

                    model.setLayerSizes(layer_sizes)
                    model.setTrainMethod(cv2.ml.ANN_MLP_BACKPROP)
                    model.setBackpropMomentumScale(0.0)
                    model.setBackpropWeightScale(0.001)
                    model.setTermCriteria((cv2.TERM_CRITERIA_COUNT, 20, 0.01))
                    model.setActivationFunction(cv2.ml.ANN_MLP_SIGMOID_SYM, 2, 1)

                    train   = []
                    answers = []
                    for i in range(begin, end):
                        self._progress.value = count; count+=1
                        if i>=len(walked_distance): continue

                        trainning_frames.append(False)
                        if debug_mode: vtrainning.set_value(i, 0)

                        ### Debug ##############################################################
                        if debug_mode: 
                            #v1.set_value(i, walked_distance[i])
                            #v2.set_value(i, dir_walked_distance[i])
                            pass
                        ########################################################################
                        triangle_angle = dataset.get_minimumenclosingtriangle_angle(i)
                        if triangle_angle is None: continue

                        dataset_angle  = dataset.get_angle(i)
                        if dataset_angle is None:  continue

                        if  walked_distance[i]>min_walked and dir_walked_distance[i]>min_walked and \
                            min_dist_angles(dataset_angle, triangle_angle)<(np.pi/2):
                            trainning_frames[i] = True

                            if MAX_TRAINNING_SET is None or len(train)<MAX_TRAINNING_SET:

                                ok1, img_up   = dataset.get_image(i, mask=True, angle='up', size=(IMAGE_SIZE,IMAGE_SIZE) )
                                ok2, img_down = dataset.get_image(i, mask=True, angle='down', size=(IMAGE_SIZE,IMAGE_SIZE) )
                                print(ok1)
                                if ok1 and ok2:
                                    cv2.normalize(img_up, img_up, 0, 255, cv2.NORM_MINMAX)
                                    cv2.normalize(img_down, img_down, 0, 255, cv2.NORM_MINMAX)

                                    train.append(img_up[:,:,0].flatten())
                                    train.append(img_down[:,:,0].flatten())
                                    answers.append([1,0])
                                    answers.append([0,1])

                                    v1.set_value(i, 
                                        img_up[:int(img_up.shape[0]/2)].sum() / np.count_nonzero(img_up[:int(img_up.shape[0]/2)])
                                    )
                                    v2.set_value(i, 
                                        img_up[int(img_up.shape[0]/2):].sum() / np.count_nonzero(img_up[int(img_up.shape[0]/2):])
                                    )

                                    cv2.imwrite('/home/manuel/Desktop/test/{0}.png'.format(i), img_up)
                                    if debug_mode: vtrainning.set_value(i, 1)    
                                

                    print("1")    
                    train   = np.float32(train)
                    answers = np.float32(answers)
                    model.train(train, cv2.ml.ROW_SAMPLE, answers)


                    if debug_mode:
                        # create the values for debug ##########################################
                        v1 = dataset.object2d.create_value()
                        v1.name = 'Est. orient. - step3 - prediction front'
                        v2 = dataset.object2d.create_value()
                        v2.name = 'Est. orient. - step3 - prediction back'
                        v3 = dataset.object2d.create_value()
                        v3.name = 'Est. orient. - step3 - binary prediction'

                    print("2") 
                    
                    for i in range(begin, end):
                        self._progress.value = count; count+=1
                        if i>=len(trainning_frames): continue
                        
                        if debug_mode: v1.set_value(i,0)

                        if not trainning_frames[i]:

                            ok, img = dataset.get_image(i, mask=True, angle='up', size=(IMAGE_SIZE,IMAGE_SIZE) )
                            
                            if ok:
                                cv2.normalize(img, img)
                                
                                _ret, resp = model.predict(np.float32([img[:,:,0].flatten()]))
                                if resp.argmax()==1: dataset.flip(i) 

                                if debug_mode: 
                                    v1.set_value(i,resp[0][0])
                                    v2.set_value(i,resp[0][1]) 
                                    v3.set_value(i,resp.argmax()) 
            """
                       
            
        

                        

                        

                

            self._min_dist.enabled      = True
            self._min_steps.enabled     = True
            self._panel.enabled         = True
            self._apply.label           = 'Apply'
            self._apply.checked         = False
            self._progress.hide()



if __name__ == '__main__': 
    pyforms.start_app(FindOrientationWindow)
