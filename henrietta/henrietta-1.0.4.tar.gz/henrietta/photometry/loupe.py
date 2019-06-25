import illumination as il
from ..imports import *
from .apertures import *
from ..imaging import io
from tqdm import tqdm

from IPython.display import display

# is there a way to force %matplotlib notebook?
#from IPython import get_ipython
#get_ipython().run_line_magic('matplotlib', 'widget')

from astropy.table import vstack
import ipywidgets as widgets

from lightkurve import LightCurve

class Loupe(il.IllustrationBase):
    '''
    An interactive Illustration, that allows us to do
    aperture photometry on particular locations in an image.
    '''
    illustrationtype = 'Loupe'

    def create_frame(self, *args, **framekw):
        '''
        (part of __init__)
        Create the illustration frame.
        '''
        plt.ioff()

        # don't let this illustration talk
        self._pithy = True


        # figure out the geometry, for the figure
        aspectratio = self.image.shape[1]/float(self.image.shape[0])
        width = 5.5
        height = width/aspectratio
        #if aspectratio >=1:
        #    width = size*aspectratio
        #    height = size
        #else:
        #    width = size
        #    height = size/float(aspectratio)

        # create the basic illustration layout (this creates a self.grid)
        il.IllustrationBase.__init__(self, 1, 1,
                                  figkw=dict(figsize=(width, height), dpi=100),
                                  hspace=0.02, wspace=0.02,
                                  left=0.05, right=0.95,
                                  bottom=0.1, top=0.9)
        self._pithy = True

        # create an imshowFrame to display the image (and hide its text output)
        self.frames['imshow'] = il.imshowFrame(data=self.images, illustration=self, **framekw)
        self.frames['imshow']._pithy=True

        # create an ax for this frame
        self.frames['imshow'].ax = plt.subplot(self.grid[0, 0])


        # draw this illustration
        self.plot()

    def change_image(self, i, quick=False):

        # update the current image data
        self.image = self.images[i]

        # update the displayed image
        time = self.images.time[i]
        if not quick:
            self.update(time)
            plt.draw()

    def create_widgets(self, aperture_radius=5, subtract_background = False, background_radii=[15, 25], maxaperture=100, maxbackground=200, **kwargs):
        '''
        Create the control widgets for interactions.
        (part of __init__)

        Parameters
        ----------
        aperture_radius : int
            The default radius for the photometric aperture
            (can be changed interactively)

        subtract_background : bool
            Should we attempt to do background subtraction?
            (can be changed interactively)

        background_radii : list of two ints
            The default radii for background subtraction
            (can be changed interactively)

        maxaperture : int
            The maximum aperture radius to allow interactively.

        maxbackground : int
            The maximum background radius to allow interactively.
        '''

        ####################################
        # create the aperture radius control
        ####################################

        # a label for setting the aperture
        aperture_radius_label = widgets.Label('Photometric Aperture')

        # a slider to pick the radius of the aperture
        '''
        aperture_radius_slider = widgets.FloatSlider(
                                    value=aperture_radius,
                                    min=0,
                                    max=maxaperture,
                                    step=1,
                                    description='Radius',
                                    orientation='horizontal',
                                    continuous_update=False,
                                    readout=False,
                                    layout={'width':'100%'})
        '''
        aperture_radius_text = widgets.FloatText(
                                    value=aperture_radius,
                                    description='Radius',
                                    layout={'width':'80%'})

        #widgets.jslink([aperture_radius_slider, 'value'],
        #               [aperture_radius_text, 'value'])

        # make the combined aperture widget
        self._widget_aperture = widgets.VBox([aperture_radius_label,
                                              #aperture_radius_slider,
                                              aperture_radius_text])

        ###########################################
        # create the background subtraction control
        ###########################################

        # a checkbox to decide if we should subtract the background
        background_checkbox = widgets.Checkbox(
                                        value=False,
                                        description='Subtract Background?',
                                        disabled=False)

        # a label for the background subtraction
        background_label = widgets.Label('Background Subtraction',
                                         disabled=True)

        # create text boxes for the inner and outer radii
        background_inner_text = widgets.BoundedFloatText(
                                    value=background_radii[0],
                                    description='Inner Radius',
                                    layout={'width':'80%'})

        background_outer_text = widgets.BoundedFloatText(
                                    value=background_radii[1],
                                    description='Outer Radius',
                                    layout={'width':'80%'})

        widgets.jslink((aperture_radius_text, 'value'),
                       (background_inner_text, 'min'))

        widgets.jslink((background_inner_text, 'value'),
                       (background_outer_text, 'min'))

        # a range slider to pick the inner + outer radii of the annulus
        background_slider = widgets.IntRangeSlider(
                                value=background_radii,
                                min=0,
                                max=maxbackground,
                                step=1,
                                description='Radii',
                                disabled=True,
                                continuous_update=False,
                                orientation='horizontal',
                                readout=True,
                                layout={'width':'100%'})

        # only turn on the background slider if we need it
        def update_background_slider(checkbox):
            '''
            What do we do to the background slider
            when the background checkbox is updated?
            '''
            do_background = checkbox['new'] == False
            background_inner_text.disabled = do_background
            background_outer_text.disabled = do_background

        background_checkbox.observe(update_background_slider, names='value')

        # don't let the background inner radius go inside the aperture radius
        #widgets.jslink((aperture_radius_slider, 'value'),
        #               (background_slider, 'min'))

        # create the combined background widget
        self._widget_background = widgets.VBox([background_label,
                                               background_checkbox,
                                               background_inner_text,
                                               background_outer_text])


        #########################################
        # create some output widgest for displays
        #########################################

        # create a place to share instructions
        self._widget_instruction = widgets.Output(layout={'border': '1px solid black',
                                                        'margin': '1% 0% 1% 0%',
                                                        'max_height':'30px',
                                                        'background_color':'red',
                                                        })

        # create an output to share results
        self._widget_results = widgets.Output(layout={'border': '1px solid black',
                                                    'margin': '1% 0% 1% 0%',
                                                    'max_height':'200px',
                                                    'min_height':'30px'})

        #####################################
        # create time slider to change images
        #####################################

        # a slider to pick the radius of the aperture
        image_slider = widgets.IntSlider(
                                    value=0,
                                    min=0,
                                    max=len(self.images)-1,
                                    step=1,
                                    description='#',
                                    orientation='vertical',
                                    continuous_update=False,
                                    readout=True,
                                    layout=dict(height='100%'))

        # create a container to store the time slider in
        self._widget_imageslider = widgets.VBox([image_slider],
                             layout=dict(margin='0% 0% 0% 0%'))


        # set up the interaction loop for the photometry
        self._interaction_photometry = widgets.interactive(self.photometry,
                                         aperture_radius=aperture_radius_text,
                                         background_inner=background_inner_text,
                                         background_outer=background_outer_text,
                                         subtract_background=background_checkbox,
                                         image_number=image_slider)


        # create a shared widget for the controls
        self._widget_controls = widgets.VBox([self._widget_aperture, self._widget_background])

    def __init__(self, images, aperture_radius=5, subtract_background = False, background_radii=[15, 25], **framekw):
        '''
        Parameters
        ----------

        image : 2D array, str
            An image or a path to a filename containing an image.

        **framekw passed to CameraFrame
        '''

        ####################################
        # set the defaults
        ####################################

        self.aperture_radius = aperture_radius
        self.subtract_background = subtract_background
        self.background_radii = background_radii


        ####################################
        # load sequence of images
        ####################################

        # load an image if given a filename
        if type(images) == str:
            images = io.read_image(images)

        self.images = il.make_image_sequence(images)

        #  define the first image, initially
        self.image = self.images[0]


        # create the widgets
        self.create_widgets(aperture_radius=aperture_radius,
                            subtract_background=subtract_background,
                            background_radii=background_radii)

        with self._widget_instruction:
            print("Please [a]dd or [z]ap an aperture at the cursor location.")


        # populate the illustration with data
        self.create_frame()


        self._widget_image = widgets.VBox([self.figure.canvas],
                             layout=dict(width='62%', margin='0% 2% 0% 0%'))

        self._widget_left = widgets.VBox([
                                          self._widget_controls,
                                          self._widget_results],
                            layout=dict(width='30%', margin='0% 0% 0% 2%'))


        self._widget_interaction = widgets.HBox([self._widget_left,
                                            self._widget_imageslider,
                                            self._widget_image])


        self._widget_layout = widgets.VBox([self._widget_instruction,
                                            self._widget_interaction])



        display(self._widget_layout)

        # set it up so we can add or subtract an aperture by clicking on the image
        self.figure.canvas.mpl_connect('key_press_event', self.do_something_with_keyboard)


        # start with no apertures defined
        self.apertures = []
        self.napertures = 0

    def do_something_with_keyboard(self, event):
        '''
        If the user clicks on the imshow, do something with that click.

        Parameters
        ----------
        event : matplotlib.backend_bases.LocationEvent
        '''

        # store the last event that was clicked
        self.lastevent = event

        # define the available options
        self.options = {'z':self.remove_aperture,
                        'a':self.add_aperture}

        # do the requested action
        key_pressed = event.key.lower()
        action = self.options.get(key_pressed, None)
        if action is not None:
            action(event.xdata, event.ydata)

            # update the plot and the photometry
            plt.draw()
            self._interaction_photometry.update()

    def add_aperture(self, x, y):
        '''
        Add an aperture at a particular (x, y) location.
        '''
        #with self.out:
        #    print('adding aperture at {}'.format((x,y)))
        position = np.array([x,y])
        name = '{}'.format(self.napertures)

        new = InteractiveAperture(name=name,
                                  pos=position,
                                  loupe=self,
                                  aperture_radius=self.aperture_radius,
                                  subtract_background=self.subtract_background,
                                  background_radii=self.background_radii,
                                  )

        # plot this aperture on the image
        new.plot(ax=self.frames['imshow'].ax)

        # store this new aperture in a list
        self.apertures.append(new)
        self.napertures += 1

    def remove_aperture(self, x, y):
        '''
        Remove the closest aperture to the given (x,y) location.

        Parameters
        ----------
        x, y : float
            The location where we want to remove an aperture.
        '''

        positions = [a.positions[0] for a in self.apertures]
        xexisting, yexisting = np.array(positions).T
        distance = (xexisting - x)**2 + (yexisting - y)**2
        closest = np.argmin(distance)

        toremove = self.apertures.pop(closest)
        toremove.erase()


    def photometry(self, aperture_radius=5,
                         subtract_background = False,
                         background_inner=15,
                         background_outer=25,
                         image_number=0,
                         quick=False):

        '''
        Create apertures around specified list of stars

        Parameters:
        -----------

        aperture_radius : float
            The radius of a circular aperture in pixel size
        r_in : float
            The inner radius of background aperture in pixel size
            (Ignore if back_photo=False)
        r_out : float
            The outer radius of background aperture in pixel size
            (Ignore if back_photo=False)

        Returns
        -------
        photometry of each star : array
        average background pixel value around each star : array (If back_photo=True)
        plots image with the aperture and centroids located for each star
        '''


        background_radii=[background_inner, background_outer]
        # point at this current figure
        if not quick:
            plt.figure(self.figure.number)

        # set the image to image
        self.change_image(image_number, quick=quick)

        # if we have no apertures, do nothing
        if len(self.apertures) == 0:
            return None

        # pull out the plotting ax and the image
        ax = self.frames['imshow'].ax
        image = self.image

        self.aperture_radius = aperture_radius
        self.subtract_background = subtract_background
        self.background_radii = background_radii

        for i, a in enumerate(self.apertures):
            a.update()

        #if back_photo == True:
        #    back_table = photutils.aperture_photometry(image,back_aperture)
        #    area = np.pi*(r_out**2-r_in**2)
        #    a = np.ones((np.shape(image)[0],np.shape(image)[1]))
        #    area = photutils.aperture_photometry(a,back_aperture)
        #    back_values = back_table['aperture_sum'].data/area['aperture_sum'].data
        #    return flux_values,back_values*np.pi*aperture_radius**2
        #else:

        self.measurements = vstack([a.table for a in self.apertures])

        if not quick:
            self._widget_results.clear_output()
            with self._widget_results:
                print('r={:.0f}px (area={:.1f}px)'.format(self.aperture_radius, self.apertures[0].area()))
                print(self.measurements)
            plt.draw()

        return self.measurements

    def make_lightcurves(self):

        # create an empty list of photometry tables and times
        tables = []
        times = []

        # loop over all the images
        for i in tqdm(range(len(self.images))):
            table = self.photometry(image_number=i, quick=True)
            table.add_index('#')
            tables.append(table)
            times.append(self.images.time[i].jd)

        lightcurves = {}
        for k in tables[0]['#']:
            lightcurves[k] = LightCurve( flux=[t.loc[k]['flux'] for t in tables])

        self.lightcurves = lightcurves
        return lightcurves
