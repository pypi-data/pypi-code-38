"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from functools import partial
import os, sys
from typing import Tuple

import numpy
from PyQt5 import QtCore, QtGui, QtWidgets
from skimage.measure import points_in_poly

from pyjamas.dragdropmainwindow import DragDropMainWindow
from pyjamas.rimage.rimclassifier.batchclassifier import BatchClassifier
import pyjamas.rimage.rimcore as rimcore
from pyjamas.rimage.rimutils import rimutils
from pyjamas.rutils import RUtils


class PyJAMAS(QtCore.QObject):
    '''
    PyJAMAS is Just A More Awesome Siesta.

    Uses calendar versioning (https://calver.org).
    Format: YYYY.M.minor

    YYYY - Full year - 2006, 2016, 2106
    M - Short month - 6, 16, 106
    minor - minor version number, starts at 0 for a given YYYY.M combination.


    PyJAMAS() creates a PyJAMAS user interface.

    PROPERTIES -----------------------
    (Created with the following code:
    thekeys = list(self.__dict__.keys())
    thetypes = [str(type(x)) for x in self.__dict__.values()]
    [(x, thetypes[ind]) for ind, x in enumerate(thekeys)]
    )


     todo:
     - Follow track fiducials example to run in a thread with segmentation and classification options.
     - Should crop into new window launch a new thread?
     - Batch measure movies (polygon_analysis_script_wh).
     - Remove shapely dependency by using skimage.measure.points_in_poly??? Problem are the exterior, centroid and area functions of the shapely.polygon class
     - Random forests, Neural networks, K-means clustering (https://www.kdnuggets.com/2019/05/guide-k-means-clustering-algorithm.html)
     - Move polylines with cursor.
     - Open and closed trajectories.
     - Create one class per callback function, and use a common name ('cb'?) for the callback function in each case?
     - Standardize features for classifiers (see Chapter 2 in Raschka). Uses sklearn's StandardScaler.
     - PIV-based image registration.
     - Add PIV to track_fiducials to improve the results (as an option).
     - Improve watershed: are we sure that the images that we feed into the watershed functions are identical in SIESTA and PyJAMAS? For instance, do the Gaussian smoothing functions result in indentical images when identical parameters are used?
     - Add option to quantify trajectory profile.
     - Merge rcbnextframe, rcbprevframe and rcbtimeslider.
     - Scrollable status bar: https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
     - Adjust contrast (currently linear stretch between 0 and max: see pjscore.displayData, add options for custom min/max values, based on displaying the histogram and the resulting image within the dialog).
     - Save display (converts to 8b).
     - Export movie.
     - Add ROI options to find_seeds, expand_seeds, propagate_seeds, etc.
     - cbFindSeeds allows selection of thresholding method, and displays all possible outcomes for one image using skimage.filters import try_all_threshold
     - Menus disappear when opening a matplotlib figure - can be solved my minimizing and remaximizing the main window.
     - Undo button: store n copies of pyjamas in a fifo cue. n is determined by an option. __copy__ and __deepcopy__ methods are already "drafted".
     - Parallelize non_max_suppression in rimclassifier.
     - Many of the options in the Image dialog get rid of all annotations (e.g. invert, which probably should not). At least issue a warning the first time.
     - Instead of using timepoints dialog, use rutils.parse_range_list.
     - Move dragdropmainwindow to dialogs module (?).
     - Bug: keyboard (mouse?) does not work on original pyjamas after crop into new window.
     - Bug: some times scrollbar not properly repositioned after zoom/window resize (when image is big or small?).
       BUT IT WORKS BEAUTIFULLY IF YOU ADD A FIDUCIAL IN THE IMAGE BEFORE RESIZING.
     - Add image/path parameter to the constructor of PyJAMAS (to avoid loading logo). Use in rcbcrop for crop into new pyjamas.
     - Conway's game of life for initial image (start with Pyjamas pattern). Add a "divertimento" that binarizes the image and
     uses it as the initial configuration for Conway's. Need "binarize" option.
     - Move everything in rimcore to rimutils (as class methods). Get rid of rimcore. Alternatively, implement
     rimutils methods as instance methods in rimcore.
     - centerSeeds is SLOW!!! Can it be optimized? Check Cython's pure python mode - https://cython.readthedocs.io/en/latest/src/tutorial/pure.html
     - MEDUSA: http://scikit-image.org/docs/dev/auto_examples/edges/plot_active_contours.html
     - Distance-transform based watershed.
     - Filter output section in rimutils.flow.
     - Add option for floating point fps (e.g. 0.5). Currently only integers are acceptable.
     - Add options to do MIP and concatenation of files in folders, so that you can get rid of ImageJ.
     - Add option to change brightness and contrast (a la Fiji).
     - Consider splitting rcallbacks module into submodules (one per menu?).
     - Add option to add a polygon with the alpha shape of the fiducials (ask for the value of alpha)
     - See scipy.spatial.ConvexHull and modify RUtils.concave_hull to return the points in order.
     - In expand seeds, compare images pixel by pixel with Matlab. Are the results in PyJAMAS as good as SIESTA's?
     - Consider storing all callback classes into a single class, such that one can use a = PyJAMAS(), a.callbacks.load_time_series(filename)
     (rather than the current a.load_time_series_object.load_time_series(filename)).
     - Consider merging rcbimage (flip, rotate, etc.) and rcbsaveimage.
     - Circular import: right now PyJAMAS imports rcallbacks inside a method because if imported at the beginning,
     rcallbacks also imports PyJAMAS at the beginning and that leads to an issue: the from rcallbacks import * at the beginning
     of pyjamas jumps to rcallbacks.py, and the import pyjamas at the beginning of rcallbacks jumps back to pyjamas. When
     the execution realizes the circular loop, it continues a reaches calls to rcallbacks that have not been defined because ...
     Is this solved in Python 3.7 con future import? Try to search for importing an undefined package and circular imports in stackoverflow.
     - (Same as above?) Cyclic import between pyjamas and rcallback ends up up a module 'pyjamas' has no attribute 'PyJAMAS'. So I
       delayed the import of rcallbacks until the setupUI method in this class.
     - Fix the problem with skimage io.imread loading 4-page images in rcbloadtimeseries (documented there).
     - Single fiducial seed propagation crashes.
     - add gradient option to flow calculations.
     - Write rimcore.makeGraph in cython (how to debug?).
     - Sparse matrices in cython (see https://www.evernote.com/shard/s448/nl/82435167/75e1d48a-fde9-4f5b-8b4c-7eebd3a2e7c9/)
     - Deep learning-based image segmentation
     - Raise exceptions instead of returning nones
     - Profile with quantifiedcode.
     - Add a "BATCH" menu to process multiple images
     - Quantify laser cutting (local_all_these_movies_time).
     - Quantify and plot polygon data (polygon_analysis_script_wh?).
     - LiveTrajectories.
     - LiveA* (calling mex code?).
     - QuPID
     - Zoom out -> when you load an image, zoom it out if it is too big to fit in the screen.
     - Docstring document of properties, methods and classes. Use sphinx: http://www.sphinx-doc.org/en/stable/tutorial.html
     - Copy & paste polylines.
     - Is there any reason that we are drawing QGraphicsItems and storing QPoint and QPolygonF? Would it make any sense
        to store the QGraphicsItems in fiducials or polylines?
     - Deep learning-based image super-resolution (or other approaches, see Eugene Myers', but also others').
     - Find a better initial image.
     - Include default, initial image in a data file.
     - Rescale intensity (for display, currently just linear stretch, but within skimage.exposure, there are multiple
     options for this. Also, in QtGui.QImage (see displayData) Format_Alpha8 gives you images a la Tony Harris, with inverted signal.
     - Enhance with Laplacian (see Fig. 3.40 in Gonzalez&Woods, 2nd ed).

     NOT SO IMPORTANT
     - Segment only in ROI (see call to watershed in rimcore, it has a mask parameter for this).
     - Go to time point.
     - Move to time point 1, 2, 3, 4, ...
     - Jump 10, 20, 30, 40, etc, time points.
     - Color images & split channels: how important is this? That is barely used in SIESTA.
     - Encode initial image, rather than distributing it as an image.


     DONE (in chronological order):
     - Load initial image.
     - Compare pillow.Image and scikit-image (which is a lot better documented). ENDED UP MOVING TO SCIKIT, BECAUSE
       OF THE BETTER DOC, BUT ALSO BECAUSE SO FAR WE ONLY USE LOAD METHODS, AND THOSE USE THE SAME LIBTIFF USED IN
       PILLOW. PLUS SCIKIT HAS A LOT MORE ALGORITHMIC DEVELOPMENT BEHIND.
     - Display coordinates and pixel value as mouse moves on image.
     - Zoom.
     - Polylines.
     - Delete all annotations in a time point/in the movie.
     - Cannot delete imported fiducials (but not problem with polylines).
     - drawPolyline/addPolyline and removePolyline need restructuring so that addPolyline does not depend on drawPolyline,
     but can be used to add a polyline to PyJAMAS in any time point (and thus called from loadannotations, importannotations,
     etc.
     - Show that PyJAMAS is faster than SIESTA handling images with LOTS of annotations.
     - Break event filter into smaller function calls. It's gonna become a monster function otherwise. Maybe even
     take it outside and create an eventListener class that does all the event handling.
     - Deleting a rectangle has some weird bug when deleting a rectangle overlapped by another one. From that
        point on, if you try to delete the last rectangle drawn, you will not see the rectangle disappear until
        the mouse is pressed again.
     - LiveWire.
     - Refactor rimcore to use row, col, not x, y (N4, N8, ND).
     - Profile with CProfile/
     - Recover focus after import SIESTA annotations.
     - requirements.txt (pipreqs .). Now one can install with pip install -r requirements.txt
     - Save annotations as xml files (similar to labelImg, to train TensorFlow. Or do csv directly, since xml
        annotations are converted into csv with python xml_to_csv.py
     - Still, some images will not open properly????? The pixel values are correct, but the order in whcih they are
        displayed is not. See, for instance, Clipboard_2.tif in the training folder. SOLVED BY ADDING AN ADDITIONAL PARAMETER
        IN THE QIMAGE CONSTRUCTOR USED IN DISPLAY_DATA.
     - When drawing polygons and rectangles, limit coordinates to within the image (or clip them at the end). Righjt now
        it is possible to draw beyond the image limits if the window is bigger than the image.
     - Measure polygons (skimage.measure). Need to check coordinate range and exit if polygon outside the image.
     - Brush size.
     - Native Menu Bar.
     - Save time series.
     - Crop image
     - Crop into a new window.
     - Move polylines.
     - Optic flow
     - Seed propagation
     - Scrollbar to move across time points.
     - Hide annotations.
     - Display fiducial ids.
     - Watershed (with Gaussian filtering BEFORE!!!)
     - Import/Export SIESTA annotations
     - Apply centerSeeds only to central, not peripheral seeds.
     - Remove magic numbers from rcbsegment.
     - Use concave hull of seeds to decide which ones are at the edges (instead of convex hull).
     - Gradient-based watershed -> this does not work very well (double edges?)
     - Add options to flip, rotate.
     - Export tracked polygons.
     - Argument parser for MIP.
     - Add progress information to project and concatenate.
     - Batch classifier hard_negative_mining? Necessary to wrap rimclassifier function? NO, as fit in rimclassifier
       already calls hard_negative_mining.
     - Time points in non-max suppression.
     - Move progress dialog to rutils (?) and add progress info, for instance in batch classifier. ENDED UP MOVING
     PROGRESS INFORMATION TO STATUS BAR.
     - Maximum suppression dial.
     - Classifier (a different GUI?).
     - Change flow field interpolation to linear, as done in rflow.m. The bivariate spline performs significantly worse ...
     - Make sure that optic flow does not push points too close to the image boundaries or outside (or at least has a
     flag that prevents that).
     - Open files dragged onto the window (both images and annotations).
     - Make sure that the default working folder (self.cwd) is being used every time a file dialog is open.
     - Add about option that displays the LICENSE file.
     - Test other watershed functions (e.g. opencv). CURRENT ONE IS BAD!!!
     - When displaying fiducial ids, a newly added fiducial should also get its id displayed.
     - Delete all seeds outside/inside polygon -> test skimage,measure.points_in_poly function to test polygon inclusion.
     - Use a different navigation toolbar (or no navigation toolbar) in matplotlibdialog.
     - Add zoom option to preview dialog in find seeds
     - Font size in preview window in findseedsdialog becomes smaller after the first live value change.
     - Invert image.
     - Segment objects localized by classifier: 1. Segmenting cardioblasts - for each detection, take the image, adaptive threshold, distance transform, identify one seed (close to the centre, discard image edges), identify a second seed (in the pixel with the lowest pixel value in the image - is this necessary?), and expand using the watershed on the gradient of the original image (or the inverted original image). Get rid of contours overlapping more than 10% with a pre-existing one when you are done (or as you go).
     - Find seeds - add polygon centroids as fiducials.
     - Track fiducials.
     - Autoplay movie (+ fps option)
     - Kymographs
     - Display polyline ids.
     - Track fiducials should extend to polylines.
     - Logistic regression.
     - Image registration.
     - Launch thread to do fiducial tracking, signal propagation, and display progress in the progress bar.
     - Add option to go to slice 0/end using RCBTimeSlicer.cbGoto.
     - Progress in statusbar is not visible!!! Is this because the dialogs are modal? Need multithreading!! See cbPlay, play_movie and progress_fn in rcbimage, and pjsthreads.
     - Fix error with export annotations to SIESTA format.
     - Copy&paste polylines.
      '''

    # Logo path.
    logo_filename = 'pyjamas.tif'
    logo_folder = os.path.split(__file__)[0]
    logo_path = os.path.join(logo_folder, logo_filename)

    # Annotation modes. @todo: convert into enum and use auto() to generate constants (?).
    no_annotations: int = 0
    fiducials: int = 1
    rectangles: int = 2
    polylines: int = 3
    livewire: int = 4
    move_polyline: int = 5
    export_fiducial_polyline: int = 6
    delete_fiducials_outside_polyline: int = 7
    delete_fiducials_inside_polyline: int = 8
    copy_polyline: int = 9

    # Data file extension.
    data_extension: str = '.pjs'
    matlab_extension: str = '.mat'
    image_extensions: Tuple[str] = ('.tif', '.tiff', '.jpg')

    # Plotting constants.
    fiducial_color = QtCore.Qt.red
    polyline_color = QtCore.Qt.green
    fiducial_radius: int = 6
    fiducial_brush_style: QtGui.QBrush = QtGui.QBrush()  # No fill for fiducials (open circles).
    polyline_brush_style: QtGui.QBrush = QtGui.QBrush()
    fiducial_font: QtGui.QFont = QtGui.QFont('Arial', 8)

    zoom_factors: tuple = (1., 2., 4., 8., .125, .25, .5)

    livewire_margin: int = 5

    def __init__(self):
        self.setupUI()  # Build the GUI.
        self.initData()  # Initialize object variables.

    def setupUI(self):
        self.app = QtWidgets.QApplication(sys.argv)

        import pyjamas.pjseventfilter as pjseventfilter
        import pyjamas.rcallbacks as rcallbacks

        QtCore.QObject.__init__(self)
        self.MainWindow = DragDropMainWindow()

        self.MainWindow.dropped.connect(self.file_dropped)

        self.MainWindow.setObjectName('PyJAMAS')
        self.MainWindow.resize(1183, 761)
        self.MainWindow.setWindowTitle('PyJAMAS')

        self.gScene = QtWidgets.QGraphicsScene(self.MainWindow)
        self.gScene.setSceneRect(0, 0, 1183, 761)
        self.gScene.setObjectName('gScene')

        self.gView = QtWidgets.QGraphicsView(self.gScene)
        self.gView.setObjectName('gView')
        self.gView.setMouseTracking(
            True)  # This here is necessary so that MouseMove events are triggered when no mouse buttons are pressed.
        self.filter = pjseventfilter.PJSEventFilter(self)
        self.gView.viewport().installEventFilter(self.filter)
        self.MainWindow.setCentralWidget(self.gView)

        self.timeSlider = QtWidgets.QSlider(self.MainWindow)
        self.timeSlider.setGeometry(QtCore.QRect(0, 0, 1183, 22))
        self.timeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.timeSlider.setObjectName("timeSlider")
        self._cbTimeSlider = rcallbacks.rcbtimeslider.RCBTimeSlider(self)
        self.timeSlider.valueChanged.connect(self._cbTimeSlider.cbTimeSlider)

        self.menubar = QtWidgets.QMenuBar(self.MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1183, 22))
        self.menubar.setObjectName('menubar')
        self.menuIO = QtWidgets.QMenu(self.menubar)
        self.menuIO.setObjectName('menuIO')
        self.menuOptions = QtWidgets.QMenu(self.menubar)
        self.menuOptions.setObjectName('menuOptions')
        self.menuImage = QtWidgets.QMenu(self.menubar)
        self.menuImage.setObjectName('menuImage')
        self.menuClassifiers = QtWidgets.QMenu(self.menuImage)
        self.menuClassifiers.setObjectName('menuClassifiers')
        self.menuAnnotations = QtWidgets.QMenu(self.menubar)
        self.menuAnnotations.setObjectName('menuAnnotations')
        self.menuMeasurements = QtWidgets.QMenu(self.menubar)
        self.menuMeasurements.setObjectName('menuMeasurements')
        self.menuBatch = QtWidgets.QMenu(self.menubar)
        self.menuBatch.setObjectName('menuBatch')
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName('menuHelp')
        self.MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(self.MainWindow)
        self.statusbar.setObjectName('statusbar')
        self.MainWindow.setStatusBar(self.statusbar)

        self.threadpool = QtCore.QThreadPool()
        #print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        # IO MENU ----------------------------------------------------------------------
        # Load image action
        self._cbLoadTS = rcallbacks.rcbloadtimeseries.RCBLoadTimeSeries(self)
        self.addMenuItem(self.menuIO, 'Load grayscale image ...', QtCore.Qt.Key_T,
                         self._cbLoadTS.cbLoadTimeSeries)

        # Save time-lapse.
        self._cbSaveTS = rcallbacks.rcbsavetimeseries.RCBSaveTimeSeries(self)
        self.addMenuItem(self.menuIO, 'Save grayscale image ...', QtCore.Qt.Key_S,
                         self._cbSaveTS.cbSaveTimeSeries)

        # Save time-lapse, but only ROI inside the polygon.
        self._cbSaveSubim = rcallbacks.rcbsaveimage.RCBSaveImage(self)
        self.addMenuItem(self.menuIO, 'Save grayscale image in polygon ...', QtCore.Qt.Key_U,
                         partial(self._cbSaveSubim.cbSaveImage, filename=''))

        self.menuIO.addSeparator()

        # Load annotations.
        self._cbLoadAnn = rcallbacks.rcbloadannotations.RCBLoadAnnotations(self)
        self.addMenuItem(self.menuIO, 'Load annotations ...', QtCore.Qt.SHIFT + QtCore.Qt.Key_L,
                         self._cbLoadAnn.cbLoadAnnotations)

        # Save annotations.
        self._cbSaveAnn = rcallbacks.rcbsaveannotations.RCBSaveAnnotations(self)
        self.addMenuItem(self.menuIO, 'Save annotations ...', QtCore.Qt.Key_A,
                         self._cbSaveAnn.cbSaveAnnotations)

        self._cbExportPolylineAnn = rcallbacks.rcbexportpolylineannotations.RCBExportPolylineAnnotations(self)
        self.addMenuItem(self.menuIO, 'Export individual fiducial-polyline annotations ...', None,
                         self._cbExportPolylineAnn.cbExportPolylineAnnotations)

        self.menuIO.addSeparator()

        self._cbLoadClassifier = rcallbacks.rcbloadclassifier.RCBLoadClassifier(self)
        self.addMenuItem(self.menuIO, 'Load classifier ...', None,
                         self._cbLoadClassifier.cbLoadClassifier)

        self._cbSaveClassifier = rcallbacks.rcbsaveclassifier.RCBSaveClassifier(self)
        self.addMenuItem(self.menuIO, 'Save current classifier ...', None,
                         self._cbSaveClassifier.cbSaveClassifier)

        self.menuIO.addSeparator()

        # Save XML roi (for TensorFlow training).
        self._cbSaveAnnXML = rcallbacks.rcbsaveannotationsXML.RCBSaveAnnotationsXML(self)
        self.addMenuItem(self.menuIO, 'Save XML ROI ...', QtCore.Qt.Key_X,
                         self._cbSaveAnnXML.cbSaveAnnotationsXML)

        self.menuIO.addSeparator()

        # Import SIESTA annotations.
        self._cbImportSIESTAAnn = rcallbacks.rcbimportsiestaannotations.RCBImportSIESTAAnnotations(self)
        self.addMenuItem(self.menuIO, 'Import SIESTA annotations ...', None,
                         self._cbImportSIESTAAnn.cbImportSIESTAAnnotations)

        # Export SIESTA annotations.
        self._cbExportSIESTAAnn = rcallbacks.rcbexportsiestaannotations.RCBExportSIESTAAnnotations(self)
        self.addMenuItem(self.menuIO, 'Export SIESTA annotations ...', None,
                         self._cbExportSIESTAAnn.cbExportSIESTAAnnotations)

        self.menuIO.addSeparator()

        # Save display.
        self._cbSaveDisplay = rcallbacks.rcbsavedisplay.RCBSaveDisplay(self)
        self.addMenuItem(self.menuIO, 'Save display ...', None, self._cbSaveDisplay.cbSaveDisplay)

        self.menuIO.addSeparator()

        self._cbQuit = rcallbacks.rcbquit.RCBQuit(self)
        self.addMenuItem(self.menuIO, 'See ya\'!!', QtCore.Qt.ALT + QtCore.Qt.Key_Q, self._cbQuit.cbQuit)
        self.menubar.addMenu(self.menuIO)

        # OPTIONS MENU ----------------------------------------------------------------------
        # Set brush size.
        self._cbBrushSize = rcallbacks.rcbsetbrushsize.RCBSetBrushSize(self)
        self.addMenuItem(self.menuOptions, 'Set brush size ...', QtCore.Qt.Key_B,
                         self._cbBrushSize.cbSetBrushSize)

        self._cbFiducalIDs = rcallbacks.rcbdisplayfiducialids.RCBDisplayFiducialIDs(self)
        self.addMenuItem(self.menuOptions, 'Display fiducial and polyline ids', QtCore.Qt.Key_I,
                         self._cbFiducalIDs.cbDisplayFiducialIDs)

        self._cbFramesPerSec = rcallbacks.rcbframespersec.RCBFramesPerSec(self)
        self.addMenuItem(self.menuOptions, 'Set frames per sec ...', None,
                         self._cbFramesPerSec.cbFramesPerSec)

        self._cbCWD = rcallbacks.rcbsetcwd.RCBSetCWD(self)
        self.addMenuItem(self.menuOptions, 'Set working folder ...', None, self._cbCWD.cbSetCWD)

        self.menubar.addMenu(self.menuOptions)

        # IMAGE MENU ----------------------------------------------------------------------
        # Rotate image CW.
        self._cbImage = rcallbacks.rcbimage.RCBImage(self)
        self.addMenuItem(self.menuImage, 'Play sequence', QtCore.Qt.Key_Backslash, self._cbImage.cbPlay)

        self.menuImage.addSeparator()

        self.addMenuItem(self.menuImage, 'Rotate 90 degree clockwise', QtCore.Qt.SHIFT + QtCore.Qt.Key_Right,
                         partial(self._cbImage.cbRotateImage,
                                 direction=rcallbacks.rcbimage.RCBImage.CW))

        # Rotate image CCW.
        self.addMenuItem(self.menuImage, 'Rotate 90 degree counter-clockwise', QtCore.Qt.SHIFT + QtCore.Qt.Key_Left,
                         partial(self._cbImage.cbRotateImage,
                                 direction=rcallbacks.rcbimage.RCBImage.CCW))

        # Flip left-right.
        self.addMenuItem(self.menuImage, 'Flip left-right', QtCore.Qt.AltModifier + QtCore.Qt.Key_Right,
                         partial(self._cbImage.cbFlipImage,
                                 direction=rcallbacks.rcbimage.RCBImage.LEFT_RIGHT))

        # Flip top-bottom.
        self.addMenuItem(self.menuImage, 'Flip up-down', QtCore.Qt.AltModifier + QtCore.Qt.Key_Up,
                         partial(self._cbImage.cbFlipImage,
                                 direction=rcallbacks.rcbimage.RCBImage.UP_DOWN))

        self.menuImage.addSeparator()

        # Invert image.
        self.addMenuItem(self.menuImage, 'Invert image', None, self._cbImage.cbInvertImage)

        # Maximum intensity projection.
        self.addMenuItem(self.menuImage, 'Maximum intensity projection', None, self._cbImage.cbMIPImage)

        self.menuImage.addSeparator()

        self.addMenuItem(self.menuImage, 'Register image', QtCore.Qt.SHIFT + QtCore.Qt.Key_R, self._cbImage.cbRegisterImage)

        self.menuImage.addSeparator()
        # Zoom action.
        self._cbZoom = rcallbacks.rcbzoom.RCBZoom(self)
        self.addMenuItem(self.menuImage, 'Zoom', QtCore.Qt.Key_Z, self._cbZoom.cbZoom)

        # Crop action.
        self._cbCrop = rcallbacks.rcbcrop.RCBCrop(self)
        self.addMenuItem(self.menuImage, 'Crop', QtCore.Qt.SHIFT + QtCore.Qt.Key_P, self._cbCrop.cbCrop)

        # Crop action.
        self._cbCropNewW = rcallbacks.rcbcrop.RCBCrop(self)
        # Here I use partial to pass parameters to the cbCrop function.
        self.addMenuItem(self.menuImage, 'Crop into a new window', None, partial(self._cbCropNewW.cbCrop,
                                                                                 new_window=True))

        self._cbKymograph = rcallbacks.rcbkymograph.RCBKymograph(self)
        self.addMenuItem(self.menuImage, 'Kymograph', None, self._cbKymograph.cbKymograph)

        self.menuImage.addSeparator()

        # Find seeds.
        self._cbSegmentation = rcallbacks.rcbsegment.RCBSegment(self)
        self.addMenuItem(self.menuImage, 'Find seeds ...', QtCore.Qt.SHIFT + QtCore.Qt.Key_S,
                         self._cbSegmentation.cbFindSeeds)

        # Add fiducials in the centre of polylines.
        self.addMenuItem(self.menuImage, 'Add seeds in polyline centroids ...', QtCore.Qt.SHIFT + QtCore.Qt.Key_C,
                         self._cbSegmentation.cbCentroidSeeds)

        # Propagate seeds.
        self.addMenuItem(self.menuImage, 'Propagate seeds ...', QtCore.Qt.SHIFT + QtCore.Qt.Key_E,
                         self._cbSegmentation.cbPropagateSeeds)

        # Expand seeds.
        self.addMenuItem(self.menuImage, 'Expand seeds ...', QtCore.Qt.SHIFT + QtCore.Qt.Key_X,
                         self._cbSegmentation.cbExpandSeeds)

        # Expand and propagate seeds.
        self.addMenuItem(self.menuImage, 'Expand and propagate seeds ...', QtCore.Qt.SHIFT + QtCore.Qt.Key_Z,
                         self._cbSegmentation.cbExpandNPropagateSeeds)

        # Classifiers.
        self.menuImage.addMenu(self.menuClassifiers)
        # -- Display Classifier: YellowBrick?
        self._cbCreateLR = rcallbacks.rcbcreateLR.RCBCreateLR(self)
        self.addMenuItem(self.menuClassifiers, 'Create and train logistic regression model ...', None,
                         self._cbCreateLR.cbCreateLR)
        self._cbCreateSVM = rcallbacks.rcbcreateSVM.RCBCreateSVM(self)
        self.addMenuItem(self.menuClassifiers, 'Create and train support vector machine ...', None,
                         self._cbCreateSVM.cbCreateSVM)
        # -- Decision Trees

        self.menuClassifiers.addSeparator()

        self._cbApplyClassifier = rcallbacks.rcbapplyclassifier.RCBApplyClassifier(self)
        self.addMenuItem(self.menuClassifiers, 'Apply classifier ...', None, self._cbApplyClassifier.cbApplyClassifier)

        self.menuClassifiers.addSeparator()

        self._cbNonMaxSuppression = rcallbacks.rcbnonmax.RCBNonMax(self)
        self.addMenuItem(self.menuClassifiers, 'Non-maximum suppression ...', None,
                         self._cbNonMaxSuppression.cbNonMaxSuppression)

        self.addMenuItem(self.menuClassifiers, 'Segment detected objects ...', None, self._cbSegmentation.cbSegmentDetectedObjects)

        self.menuImage.addSeparator()

        # Next image action
        self._cbNextFrame = rcallbacks.rcbnextframe.RCBNextFrame(self)
        self.addMenuItem(self.menuImage, 'Next frame', QtCore.Qt.Key_Period, self._cbNextFrame.cbNextFrame)

        # Previous image action
        self._cbPrevFrame = rcallbacks.rcbprevframe.RCBPrevFrame(self)
        self.addMenuItem(self.menuImage, 'Previous frame', QtCore.Qt.Key_Comma, self._cbPrevFrame.cbPrevFrame)

        # Beginning and end actions
        self.addMenuItem(self.menuImage, 'Go to beginning', QtCore.Qt.Key_1, partial(self._cbTimeSlider.cbGoTo, slice_index=0))
        self.addMenuItem(self.menuImage, 'Go to end', QtCore.Qt.Key_0, partial(self._cbTimeSlider.cbGoTo, slice_index=-1))

        self.menubar.addMenu(self.menuImage)

        # ANNOTATIONS MENU ----------------------------------------------------------------------
        # No annotations.
        self._cbNoAnn = rcallbacks.rcbnoann.RCBNoAnn(self)
        self.addMenuItem(self.menuAnnotations, 'No annotations', QtCore.Qt.Key_N, self._cbNoAnn.cbNoAnn)

        self._cbHideAnn = rcallbacks.rcbhideann.RCBHideAnn(self)
        self.addMenuItem(self.menuAnnotations, 'Hide/display annotations', QtCore.Qt.Key_H, self._cbHideAnn.cbHideAnn)

        # Fiducials
        self._cbFidu = rcallbacks.rcbfiducials.RCBFiducials(self)
        self.addMenuItem(self.menuAnnotations, 'Fiducials', QtCore.Qt.Key_F, self._cbFidu.cbFiducials)

        # Rectangles
        self._cbRect = rcallbacks.rcbrectangles.RCBRectangles(self)
        self.addMenuItem(self.menuAnnotations, 'Rectangles', QtCore.Qt.Key_R, self._cbRect.cbRectangles)

        # Polylines
        self._cbPoly = rcallbacks.rcbpolylines.RCBPolylines(self)
        self.addMenuItem(self.menuAnnotations, 'Polylines', QtCore.Qt.Key_Y, self._cbPoly.cbPolylines)

        # Livewire
        self._cbLW = rcallbacks.rcblivewire.RCBLiveWire(self)
        self.addMenuItem(self.menuAnnotations, 'LiveWire', QtCore.Qt.Key_W, self._cbLW.cbLiveWire)

        self.menuAnnotations.addSeparator()

        # Copy and paste polyline
        self._cbCopyPastePoly = rcallbacks.rcbcopypastepolyline.RCBCopyPastePolyline(self)
        self.addMenuItem(self.menuAnnotations, 'Copy polyline', QtCore.Qt.Key_C, self._cbCopyPastePoly.cbCopyPolyline)

        self.addMenuItem(self.menuAnnotations, 'Paste polyline', QtCore.Qt.Key_V, self._cbCopyPastePoly.cbPastePolyline)

        # Move polyline.
        self._cbMovePoly = rcallbacks.rcbmovepolyline.RCBMovePolyline(self)
        self.addMenuItem(self.menuAnnotations, 'Move polyline', QtCore.Qt.Key_M, self._cbMovePoly.cbMovePolyline)

        self.menuAnnotations.addSeparator()

        self._cbTrackFidu = rcallbacks.rcbtrackfiducials.RCBTrackFiducials(self)
        self.addMenuItem(self.menuAnnotations, 'Track fiducials ...', QtCore.Qt.SHIFT + QtCore.Qt.Key_T,
                         self._cbTrackFidu.cbTrackFiducials)

        self.menuAnnotations.addSeparator()

        # Delete annotations on the current image.
        self._cbDeleteCurrentAnn = rcallbacks.rcbdeletecurrentann.RCBDeleteCurrentAnn(self)
        self.addMenuItem(self.menuAnnotations, 'Delete all annotations on current frame', QtCore.Qt.Key_Minus,
                         self._cbDeleteCurrentAnn.cbDeleteCurrentAnn)

        # Delete ALL annotations.
        self._cbDeleteAllAnn = rcallbacks.rcbdeleteallann.RCBDeleteAllAnn(self)
        self.addMenuItem(self.menuAnnotations, 'Delete all annotations in the sequence', QtCore.Qt.Key_Underscore,
                         self._cbDeleteAllAnn.cbDeleteAllAnn)

        # Delete fiducials OUTSIDE polyline.
        self._cbDeleteFiducialsOutsidePoly = rcallbacks.rcbdeletefiducialsinoutpoly.RCBDeleteFiducialsPoly(self)
        self.addMenuItem(self.menuAnnotations, 'Delete fiducials outside polyline',
                         QtCore.Qt.SHIFT + QtCore.Qt.Key_O,
                         self._cbDeleteFiducialsOutsidePoly.cbDeleteFiducialsOutsidePoly)

        self.menubar.addMenu(self.menuAnnotations)

        # Delete fiducials INSIDE polyline.
        self._cbDeleteFiducialsInsidePoly = rcallbacks.rcbdeletefiducialsinoutpoly.RCBDeleteFiducialsPoly(self)
        self.addMenuItem(self.menuAnnotations, 'Delete fiducials inside polyline',
                         QtCore.Qt.SHIFT + QtCore.Qt.Key_I,
                         self._cbDeleteFiducialsInsidePoly.cbDeleteFiducialsInsidePoly)

        self.menubar.addMenu(self.menuAnnotations)

        # MEASUREMENTS MENU --------------------------------------------------------------------
        self._cbMeasurePoly = rcallbacks.rcbmeasurepoly.RCBMeasurePoly(self)
        self.addMenuItem(self.menuMeasurements, 'Measure polylines ...', None, self._cbMeasurePoly.cbMeasurePoly)

        self.menubar.addMenu(self.menuMeasurements)

        # BATCH MENU ---------------------------------------------------------------------------
        # Project and concatenate.
        self._cbBatchProjectConcatenate = rcallbacks.rcbbatchprojectconcatenate.RCBBatchProjectConcat(self)
        self.addMenuItem(self.menuBatch, "Project and concatenate ...", None,
                         self._cbBatchProjectConcatenate.cbBatchProjectConcat)

        self.menubar.addMenu(self.menuBatch)

        # HELP MENU ---------------------------------------------------------------------------
        # Project and concatenate.
        self._cbAbout = rcallbacks.rcbabout.RCBAbout(self)
        self.addMenuItem(self.menuHelp, "About", None,
                         self._cbAbout.cbAbout)

        self.menubar.addMenu(self.menuHelp)

        self.menubar.setNativeMenuBar(True)
        self.retranslateUi(self.MainWindow)

    def initData(self):
        self._imageItem = None  # pixmap containing the image currently being displayed.
        self.zoom_index = 0  # index into PyJAMAS.zoom_factors to establish the zoom level.
        self.brush_size: int = 3  # brush size to paint polylines
        self.show_annotations: bool = True  # display or not annotations.
        self.display_fiducial_ids: bool = False  # display an identifier next to each fiducial
        self.fps: int = 7  # frames per second used to play the current sequence or when exporting as a movie.
        self.annotation_mode = PyJAMAS.no_annotations
        self.batch_classifier: BatchClassifier = None

        self._cbLoadTS.cbLoadTimeSeries(PyJAMAS.logo_path)
        self.cwd = os.getcwd()

        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

        self.gView.show()
        self.MainWindow.show()

        self._poly_ = []  # Stores polyline coordinates while they are being drawn. Dunder (__a__) is reserved for special methods (e.g. __len__()).
        self._copied_poly_ = None  # Stores copied polyline to be pasted.
        self._agraphicsitem_ = None  # Stores a graphicsitem transiently (e.g. a rectangle as it is being dragged).

        return True

    def prepare_image(self):
        if len(self.slices.shape) == 2:
            self.slices = numpy.expand_dims(self.slices, axis=0)

        self.curslice: int = 0
        self.imagedata: numpy.ndarray = self.slices[self.curslice]
        self.n_frames: int = self.slices.shape[0]
        self.height: int = self.slices.shape[1]  # number of rows.
        self.width:int = self.slices.shape[2]  # number of columns.

    def initImage(self):
        self.prepare_image()

        self.fiducials = [[] for i in range(self.n_frames)]
        self.polylines = [[] for i in range(self.n_frames)]

        # Make sure to continue to store the classifier in memory.
        if self.batch_classifier is not None:
            self.batch_classifier = BatchClassifier(self.n_frames, self.batch_classifier.image_classifier)
        else:
            self.batch_classifier = BatchClassifier(self.n_frames)

        self.displayData()

        # Resizing the window.
        self.gScene.setSceneRect(0, 0, self.width, self.height)
        self.MainWindow.resize(self.width * self.zoom_factors[self.zoom_index],
                               self.height * self.zoom_factors[self.zoom_index] + 60)
        self.timeSlider.setGeometry(QtCore.QRect(0, self.height + 18, self.MainWindow.width(), 22))
        self.timeSlider.setMinimum(1)
        self.timeSlider.setMaximum(self.n_frames)
        self.timeSlider.setValue(1)

    def retranslateUi(self, PyJAMAS):
        _translate = QtCore.QCoreApplication.translate
        self.menuIO.setTitle(_translate('PyJAMAS', 'IO'))
        self.menuOptions.setTitle(_translate('PyJAMAS', 'Options'))
        self.menuImage.setTitle(_translate('PyJAMAS', 'Image'))
        self.menuClassifiers.setTitle(_translate('PyJAMAS', 'Classifiers'))
        self.menuAnnotations.setTitle(_translate('PyJAMAS', 'Annotations'))
        self.menuMeasurements.setTitle(_translate('PyJAMAS', 'Measurements'))
        self.menuBatch.setTitle(_translate('PyJAMAS', 'Batch'))
        self.menuHelp.setTitle(_translate('PyJAMAS', 'Help'))
        self.menuHelp.setTitle(_translate('PyJAMAS', 'Help'))

        return True

    def addMenuItem(self, themenu, theitemname, theshortcut, thecallbackfunction):
        newAction = QtWidgets.QAction(self.MainWindow)
        newAction.setEnabled(True)
        newAction.setText(theitemname)
        newAction.setIconText(theitemname)
        newAction.setToolTip(theitemname)
        newAction.setObjectName('action' + theitemname)
        newAction.triggered.connect(thecallbackfunction)

        if theshortcut != None:
            newAction.setShortcut(theshortcut)

            # There are other possible values for the ShortcutContext in Qt.ShortcutContext. This is key for shortcuts to work when setNativeMenuBar(True) is used.
            newAction.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
            newShortcut = QtWidgets.QShortcut(QtGui.QKeySequence(theshortcut),
                                              self.MainWindow)
            newShortcut.activated.connect(thecallbackfunction)

        themenu.addAction(newAction)

        return True

    def displayData(self):
        # Delete annotations from the screen.
        self.eraseAnnotations()

        # Stretch the dynamic range of the image and then convert to 8 bits.
        # There is an autocontrast function in pillow, but it only works on 8 bit grayscale or color data.
        # And converting to 8 bit and then doing the stretch leads to information loss and pixelated images.
        # img_16bit_to_8bit = RImage(self.imagedata).stretch()
        # img_16bit_to_8bit = numpy.array(img_16bit_to_8bit, dtype=numpy.uint8)

        # themin = numpy.min(self.imagedata)
        # themax = numpy.max(self.imagedata)

        # Now we stretch the image for display. I tested skimage.exposure.rescale_intensity and my own stretch method
        # (implemented  following the code in dipimage). stretch took 419 us, vs 484 us for rescale_intensity.
        # img_16bit_to_8bit = exposure.rescale_intensity(self.imagedata, in_range=(themin, themax), out_range=(0, 255))

        img_16bit_to_8bit = rimutils.stretch(self.imagedata)
        img_16bit_to_8bit = numpy.array(img_16bit_to_8bit, dtype=numpy.uint8)

        # Display image. The fourth parameter in the QImage constructor is 1*self.width for grayscale images,
        # and 3*self.width for color images.
        qImg = QtGui.QImage(bytes(img_16bit_to_8bit), self.width, self.height, self.width,
                            QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap.fromImage(qImg)

        if self._imageItem != None:
            self.gScene.removeItem(self._imageItem)

        self._imageItem = QtWidgets.QGraphicsPixmapItem(pixmap)
        self.gScene.addItem(self._imageItem)

        if self.show_annotations:
            self.paintAnnotations()

        self.statusbar.showMessage(str(self.curslice + 1) + '/' + str(self.n_frames))

        return True

    # Perhaps create a class RAnnotations, and a PyJAMAS object has an RAnnotations property, that contains fields fiducials, polylines, etc. Does it contain the GraphicsScene as well? Yes, it is the argument to the constructor.
    # Add and remove methods take on an additional argument, the current slice. Constants are taken from class properties (PyJAMAS.fiducial_color, etc.).
    def addFiducial(self, x, y, z, paint=True):
        """

        :param x:
        :param y:
        :param z:
        :param paint: when set to False, the screen will not be repainted. This helps when adding fiducials on a different thread (which is not allowed to modify the GUI - see https://doc.qt.io/qt-5/thread-basics.html#gui-thread-and-worker-thread)
        :return:
        """
        self.fiducials[z].append([x, y])
        # print('Fiducials on frame ' + str(self.curslice) + ': ' + self.fiducials[self.curslice].__str__())

        # Add ellipse at (0,0). Then move it to the right position. This is important so that scenePos() returns the proper coordinates for the item.
        # If you add here directly in the (x, y) coordinates, scenePos() returns [0, 0].
        if paint and z == self.curslice:
            theItem = self.gScene.addEllipse(0, 0, PyJAMAS.fiducial_radius, PyJAMAS.fiducial_radius,
                                             PyJAMAS.fiducial_color,
                                             PyJAMAS.fiducial_brush_style)
            theItem.setPos(x - PyJAMAS.fiducial_radius / 2, y - PyJAMAS.fiducial_radius / 2)

            # If fiducial ids are on display, repaint them.
            if self.display_fiducial_ids:
                self.repaint()

        return True

    def findGraphicItem(self, x, y, class_type,
                        radius=fiducial_radius):  # Substitute in removeFiducial, removePolygon and movepolyline.
        theItems = self.gScene.items(
            QtCore.QRectF(x - radius / 4, y - radius / 4, radius / 2, radius / 2))

        # Because there are layers, if a rectangle was drawn on the ellipse, the rectangle will come first. So we look for the ellipse.
        for theClickedItem in theItems:
            if type(theClickedItem) == class_type:
                return (theClickedItem)

        return None

    def find_clicked_polyline(self, x: int, y: int) -> int:
        self._agraphicsitem_ = self.findGraphicItem(x, y, QtWidgets.QGraphicsPolygonItem)

        if type(self._agraphicsitem_) == QtWidgets.QGraphicsPolygonItem:
            theClickedPolygon = self._agraphicsitem_.polygon()

            try:
                index = self.polylines[self.curslice].index(theClickedPolygon)
            except LookupError:
                return -1
            else:
                self._poly_ = self.polylines[self.curslice][index]
                return index
        else:
            return -1

    def removeFiducial(self, x, y, z):
        # Grab items within a small square around the click point.
        """theItems = self.gScene.items(
            QtCore.QRectF(x - PyJAMAS.fiducial_radius / 4, y - PyJAMAS.fiducial_radius / 4, PyJAMAS.fiducial_radius / 2,
                          PyJAMAS.fiducial_radius / 2))

        # Because there are layers, if a rectangle was drawn on the ellipse, the rectangle will come first. So we look for the ellipse.
        for theClickedItem in theItems:
            if type(theClickedItem) == QtWidgets.QGraphicsEllipseItem:
                break
        """

        theClickedItem = self.findGraphicItem(x, y, QtWidgets.QGraphicsEllipseItem)

        # If you found an ellipse:
        if type(theClickedItem) == QtWidgets.QGraphicsEllipseItem:
            # Get coordinates. Find item in fiducial list. If you can find it, delete it there and delete the item from the scene.
            pos = theClickedItem.scenePos()
            deleteCoords = [int(pos.x() + PyJAMAS.fiducial_radius / 2), int(pos.y() + PyJAMAS.fiducial_radius / 2)]

            if deleteCoords in self.fiducials[z]:
                self.fiducials[z].remove(deleteCoords)
                self.gScene.removeItem(theClickedItem)
                # print('Fiducials on frame ' + str(self.curslice) + ': ' + self.fiducials[self.curslice].__str__())

                # If fiducial ids are on display, repaint them.
                if self.display_fiducial_ids:
                    self.repaint()

        return True

    def removeFiducialsPolyline(self, polyline: QtGui.QPolygonF = None, inside_flag: bool = True):
        # Go through the list of fiducials.
        polyline_list = RUtils.qpolygonf2ndarray(polyline)

        inside_poly_flags: numpy.ndarray = points_in_poly(self.fiducials[self.curslice], polyline_list)

        # To avoid deleting fiducials from the list we are checking.
        fiducial_list = self.fiducials[self.curslice].copy()

        for thefiducial, is_inside in zip(fiducial_list, inside_poly_flags):
            if (is_inside and inside_flag) or ((not is_inside) and (not inside_flag)):
                self.removeFiducial(thefiducial[0], thefiducial[1], self.curslice)

        return True

    def drawRectangle(self, x0, y0, x1, y1):
        # print([x0,y0].__str__() + " " + [x1, y1].__str__())
        if x0 > x1:
            dummy = x1
            x1 = x0
            x0 = dummy

        if y0 > y1:
            dummy = y1
            y1 = y0
            y0 = dummy

        # print([x0,y0].__str__() + " " + [x1, y1].__str__())
        pen = QtGui.QPen()
        pen.setWidth(self.brush_size)
        pen.setColor(PyJAMAS.polyline_color)

        # thepolyline = QtGui.QPolygonF()

        theItem = self.gScene.addRect(x0, y0, x1 - x0, y1 - y0, pen, PyJAMAS.polyline_brush_style)

        return theItem  # , thepolyline

    def drawPath(self, coordinates):
        thepolyline = QtGui.QPolygonF()

        for i, thepoint in enumerate(coordinates):
            thepolyline.append(QtCore.QPointF(thepoint[0], thepoint[1]))

        thepath = QtGui.QPainterPath()
        thepath.addPolygon(thepolyline)

        pen = QtGui.QPen()
        pen.setWidth(self.brush_size)
        pen.setColor(PyJAMAS.polyline_color)

        theItem = self.gScene.addPath(thepath, pen, PyJAMAS.polyline_brush_style)

        return theItem, thepolyline

    def drawPolyline(self, aQPolygonF):
        pen = QtGui.QPen()
        pen.setWidth(self.brush_size)
        pen.setColor(PyJAMAS.polyline_color)

        theItem = self.gScene.addPolygon(aQPolygonF, pen, PyJAMAS.polyline_brush_style)

        return theItem

    def addPolyline(self, coordinates: list, z: int, paint: bool = True) -> bool:
        thepolyline = QtGui.QPolygonF()

        for thepoint in coordinates:
            thepolyline.append(QtCore.QPointF(thepoint[0], thepoint[1]))

        self.polylines[z].append(thepolyline)

        # Draw the polyline if it is being added to the right time point.
        if paint and z == self.curslice:
            self.drawPolyline(thepolyline)

            # If ids are on display, repaint them.
            if self.display_fiducial_ids:
                self.repaint()

        return True

    def replacePolyline(self, index: int, coordinates: list, z: int, paint: bool = True) -> bool:
        thepolyline = QtGui.QPolygonF()

        for thepoint in coordinates:
            thepolyline.append(QtCore.QPointF(thepoint[0], thepoint[1]))

        self.polylines[z][index] = thepolyline

        # Draw the polyline if it is being added to the right time point.
        if paint and z == self.curslice:
            self.drawPolyline(thepolyline)

            # If ids are on display, repaint them.
            if self.display_fiducial_ids:
                self.repaint()

        return True

    def removePolyline(self, x, y, z):
        # Grab items within a small square around the click point.
        """theItems = self.gScene.items(
            QtCore.QRectF(x - PyJAMAS.fiducial_radius / 4, y - PyJAMAS.fiducial_radius / 4, PyJAMAS.fiducial_radius / 2,
                          PyJAMAS.fiducial_radius / 2))

        # Because there are layers, if something was drawn on the polygon, that other thing will come first. So we look for the first polygon.
        for theClickedItem in theItems:
            if type(theClickedItem) == QtWidgets.QGraphicsPolygonItem:
                break
        """

        theClickedItem = self.findGraphicItem(x, y, QtWidgets.QGraphicsPolygonItem)

        # print("(" + theClickedItem.scenePos().x().__str__() + ", " + theClickedItem.scenePos().y().__str__() + ") " + theClickedItem.type().__str__())
        # If you clicked on a polyline (not only the edge, but anywhere inside as well):
        if type(theClickedItem) == QtWidgets.QGraphicsPolygonItem:
            theClickedPolygon = theClickedItem.polygon()

            try:
                index = self.polylines[z].index(theClickedPolygon)
            except LookupError:
                return False
            else:
                self.polylines[z].pop(index)
                self.gScene.removeItem(theClickedItem)

                # If ids are on display, repaint them.
                if self.display_fiducial_ids:
                    self.repaint()

                return True
        else:
            return False

    def eraseAnnotations(self):
        allItems = self.gScene.items()

        for i in allItems:
            if type(i) in [QtWidgets.QGraphicsEllipseItem, QtWidgets.QGraphicsPolygonItem, QtWidgets.QGraphicsTextItem]:
                self.gScene.removeItem(i)

        return True

    def paintAnnotations(self):
        pen = QtGui.QPen()
        pen.setWidth(self.brush_size)
        pen.setColor(PyJAMAS.polyline_color)

        for i, thepoly in enumerate(self.polylines[self.curslice]):
            if thepoly == [] or list(thepoly) == []:
                continue

            self.gScene.addPolygon(thepoly, pen, PyJAMAS.polyline_brush_style)

            if self.display_fiducial_ids:
                polygon = RUtils.qpolygonf2polygon(thepoly)
                theItem = self.gScene.addText(str(i + 1), PyJAMAS.fiducial_font)
                theItem.setPos(polygon.centroid.x, polygon.centroid.y)
                theItem.setDefaultTextColor(self.polyline_color)

        # Paint fiducials after polylines so that polylines are in the foreground.
        for i, thefiducial in enumerate(self.fiducials[self.curslice]):
            # Add ellipse at (0,0). Then move it to the right position. This is important so that scenePos() returns the proper coordinates for the item.
            # If you add here directly in the (x, y) coordinates, scenePos() returns [0, 0].
            theItem = self.gScene.addEllipse(0, 0, self.fiducial_radius, self.fiducial_radius, self.fiducial_color,
                                             self.fiducial_brush_style)

            x = thefiducial[0]
            y = thefiducial[1]
            theItem.setPos(x - PyJAMAS.fiducial_radius / 2, y - PyJAMAS.fiducial_radius / 2)

            if self.display_fiducial_ids:
                theItem = self.gScene.addText(str(i + 1), PyJAMAS.fiducial_font)
                theItem.setPos(x - PyJAMAS.fiducial_radius / 2, y - PyJAMAS.fiducial_radius / 2)
                theItem.setDefaultTextColor(self.fiducial_color)

        # Make sure focus goes back to the main window.
        self.MainWindow.activateWindow()

        return True

    def repaint(self):
        self.eraseAnnotations()
        self.paintAnnotations()

        return True

    def file_dropped(self, l: list) -> bool:
        for file_name in l:
            if os.path.exists(file_name):
                file_name_str = str(file_name).lower()
                _, extension = os.path.splitext(file_name_str)

                if extension in rimcore.rimage.image_extensions:
                    self._cbLoadTS.cbLoadTimeSeries(file_name_str)
                elif extension == PyJAMAS.data_extension:
                    self._cbLoadAnn.cbLoadAnnotations(file_name_str)
                elif extension == PyJAMAS.matlab_extension:
                    self._cbImportSIESTAAnn.cbImportSIESTAAnnotations(file_name_str)

            else:
                return False

        return True

    def __copy__(self):
        newone = type(self)()
        newone.__dict__.update(self.__dict__)
        return newone

    def __deepcopy__(self, memodict={}):
        newone = type(self)()
        memodict[id(self)] = newone

        # Deep copy methods with a __deepcopy__ magic method.
        # Otherwise, copy by reference.
        for k, v in self.__dict__.items():
            if getattr(v, "__deepcopy__", None):
                setattr(newone, k, v.__deepcopy__(memodict))
            else:
                setattr(newone, k, v)

        return newone


def main():
    #app = QtWidgets.QApplication(sys.argv)

    aPyJAMA: PyJAMAS = PyJAMAS()
    sys.exit(aPyJAMA.app.exec_())


if __name__ == '__main__':
    main()
