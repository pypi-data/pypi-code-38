import numpy as np
from instrument.geometry.pml import weave
from instrument.geometry import shapes, operations
from instrument.geometry.pml.Renderer import Renderer as base
from support_only_for_collimator import  Collimator_support


class File_inc_Renderer(base):
    def _renderDocument(self, body):
        self.onGeometry(body)
        return
    def header(self):
        return []
    def footer(self):
        return []
    def end(self):
        return



def write_file(fl_name,geom,scad_flag):
    with open (fl_name,'wt') as file_h:
        if scad_flag:
            weave(geom,file_h,print_docs = False)
        else:
            weave(geom,file_h,print_docs = False,renderer=File_inc_Renderer(), author='')

class Parameter_error (Exception):
    pass

class Collimator_geom(object):


    def set_constraints(self, max_coll_height_detector=250., max_coll_width_detector=250.,
                        max_coll_length=380.,
                        min_channel_wall_thickness=1.,
                         min_channel_size=3., detector_dist_fr_sample_center=500., detector_size=500., collimator_front_end_from_center=16.02,
                        truss_base_thickness=30., truss_height_factor=10., truss_curvature=1.,
                        trass_final_height_factor=0.77,beam_dist_support=33.,touch_to_halfcircle=0.5,
                        SNAP_acceptance_angle=False,
                        initial_collimator_horizontal_channel_angle=0.0,
                        initial_collimator_vertical_channel_angle =0.0,
                        vertical_odd_blades=False, vertical_even_blades=False,
                        horizontal_odd_blades=False, horizontal_even_blades=False,
                        top_border_odds=False, top_border_evens=False,
                        bottom_border_odds= False, bottom_border_evens=False,
                        left_border_odds= False, left_border_evens= False,
                        right_border_odds = False, right_border_evens= False,
                        collimator_parts=False): # small(58 wide x 38 deep x 33 high), medium (160, 65, 65), large(400 wide x 250 deep x 250 high)


        self.inner_radius = collimator_front_end_from_center  # clamp cell radius (minimum distance from sample center)

        self.vertical_odd_blades=vertical_odd_blades
        self. vertical_even_blades=vertical_even_blades
        self.horizontal_odd_blades = horizontal_odd_blades
        self.horizontal_even_blades = horizontal_even_blades
        self.top_border_odds = top_border_odds
        self.top_border_evens = top_border_evens
        self.bottom_border_odds = bottom_border_odds
        self.bottom_border_evens = bottom_border_evens
        self.left_border_odds = left_border_odds
        self.left_border_evens = left_border_evens
        self.right_border_odds = right_border_odds
        self.right_border_evens = right_border_evens

        self.initial_collimator_horizontal_channel_angle = initial_collimator_horizontal_channel_angle # has to be in radians

        self.initial_collimator_vertical_channel_angle = initial_collimator_vertical_channel_angle



        self.collimator_parts=collimator_parts


        if SNAP_acceptance_angle is True:
            self.horizontal_acceptance_angle = self.span2angle(detector_size, detector_dist_fr_sample_center)  # 53 degree
            self.vertical_acceptance_angle = self.span2angle(detector_size, detector_dist_fr_sample_center)  # 53 degree

        else:
            self.horizontal_acceptance_angle = self.span2angle(max_coll_width_detector,
                                                               max_coll_length+self.inner_radius)  # 53 degree

            self.vertical_acceptance_angle = self.span2angle(max_coll_height_detector,
                                                               max_coll_length+self.inner_radius)



        self.max_coll_height_detector=max_coll_height_detector

        self.max_coll_width_detector=max_coll_width_detector


        self.min_channel_wall_thickness=min_channel_wall_thickness
        self.max_length_channels=max_coll_length-self.inner_radius
        self.min_channel_size=min_channel_size
        self.truss_base_thickness=truss_base_thickness
        self.truss_height_factor=truss_height_factor
        self.trass_final_height_factor=trass_final_height_factor
        self.beam_dist_support=beam_dist_support
        self.touch_to_halfcircle=touch_to_halfcircle

        self.curvature=truss_curvature

        self.vertical_outer_radius=(self.max_coll_height_detector/2.)/np.tan(np.deg2rad(self.vertical_acceptance_angle/2.)) #140


        self.horizontal_outer_radius = (self.max_coll_width_detector / 2.) / np.tan(
        np.deg2rad(self.horizontal_acceptance_angle / 2.))  # 140



    def set_parameters(self, vertical_number_channels,horizontal_number_channels, channel_length,wall_thickness= None):
        if wall_thickness is None:
            self.wall_thickness= self.min_channel_wall_thickness
        else:
            self.wall_thickness = wall_thickness
        self.vertical_number_channels=vertical_number_channels
        self.horizontal_number_channels = horizontal_number_channels
        self.channel_length=channel_length
        self.vertical_blade_dist_fr_cell=self.vertical_outer_radius-(self.inner_radius+self.channel_length)
        self.vertical_blade_dist_fr_sample_center= self.vertical_blade_dist_fr_cell+self.inner_radius

        self.horizontal_blade_dist_fr_cell = self.horizontal_outer_radius - (self.inner_radius + self.channel_length)
        self.horizontal_blade_dist_fr_sample_center = self.horizontal_blade_dist_fr_cell + self.inner_radius
      
        self.vertical_number_walls = self.vertical_number_channels+1
        
        self.vertical_wall_angle =0.0
        # self.vertical_wall_angle=self.span2angle(self.min_channel_wall_thickness, self.inner_radius)
        # self.vertical_acceptance_angle=self.span2angle(self.max_coll_height_detector,self.vertical_outer_radius)

        self.vertical_arc_length_detector=self.vertical_outer_radius * np.deg2rad(self.vertical_acceptance_angle)

        self.vertical_arc_length_sample=self.inner_radius * np.deg2rad(self.vertical_acceptance_angle)



        self.Vertical_cutoff_distance = (self.vertical_number_walls * self.wall_thickness
                                         + self.vertical_number_channels * self.min_channel_size) /\
                                        np.deg2rad(self.vertical_acceptance_angle)


        self.vertical_channel_angle=(self.vertical_acceptance_angle-(self.vertical_number_walls)*self.vertical_wall_angle)/self.vertical_number_channels

        if self.initial_collimator_vertical_channel_angle>0.0:
            self.vertical_channel_angle = self.initial_collimator_vertical_channel_angle+self.min_channel_wall_thickness+\
                                          (self.initial_collimator_vertical_channel_angle*0.5)

        # self.vertical_channel_size=self.inner_radius *np.deg2rad(self.vertical_channel_angle)

        self.vertical_channel_size = self.angle2span(self.vertical_blade_dist_fr_sample_center, self.vertical_channel_angle)



        self.vertical_pillar_min_angle = -self.vertical_acceptance_angle / 2. + self.vertical_wall_angle
        self.vertical_pillar_max_angle = self.vertical_acceptance_angle / 2.

        self.vertical_pillar_angle_list = np.arange(
            self.vertical_pillar_min_angle,
            self.vertical_pillar_max_angle + self.vertical_channel_angle / 2.,
            self.vertical_channel_angle)

        # print (self.vertical_channel_angle)
#############################################################################################
        ################################################################
        if self.vertical_channel_size<self.min_channel_size:
            raise Parameter_error(
                ("The number of channels should be less: %s. \n"
                +"Calculated vertical channel size is %s, but the minimum channel size is %s\n") %
                (vertical_number_channels, self.vertical_channel_size, self.min_channel_size)
            )
 ########################################################################
        #############################################################


        self.horizontal_wall_angle =0.0


        self.horizontal_arc_length_detector = self.horizontal_outer_radius * np.deg2rad(self.horizontal_acceptance_angle)

        self.horizontal_arc_length_sample = self.inner_radius * np.deg2rad(self.horizontal_acceptance_angle)

        self.horizontal_number_walls = self.horizontal_number_channels + 1

        self.horizontal_channel_angle = (self.horizontal_acceptance_angle - (self.horizontal_number_walls) * self.horizontal_wall_angle)\
                                        / self.horizontal_number_channels


        if self.initial_collimator_horizontal_channel_angle>0.0:
            self.horizontal_channel_angle = self.initial_collimator_horizontal_channel_angle+self.min_channel_wall_thickness+\
                                            (self.initial_collimator_horizontal_channel_angle*0.5)

        self.horizontal_cutoff_distance = ((self.horizontal_number_walls * self.wall_thickness)+(self.horizontal_number_channels*self.min_channel_size))\
                                          /np.deg2rad(self.horizontal_acceptance_angle)



        # self.horizontal_channel_size=self.inner_radius* np.deg2rad(self.horizontal_channel_angle)

        self.horizontal_channel_size = self.angle2span(self.horizontal_blade_dist_fr_sample_center, self.horizontal_channel_angle)



        self.horizontal_pillar_min_angle = -self.horizontal_acceptance_angle / 2 + self.horizontal_wall_angle
        self.horizontal_pillar_max_angle = self.horizontal_acceptance_angle / 2



        self.horizontal_pillar_angle_list = np.arange(
            self.horizontal_pillar_min_angle,
            self.horizontal_pillar_max_angle + self.horizontal_channel_angle / 2,
            self.horizontal_channel_angle)

        if self.horizontal_channel_size<self.min_channel_size:
            raise Parameter_error(
                ("The number of channels should be less: %s. \n"
                +"Calculated horizontal channel size is %s, but the minimum channel size is %s\n") %
                (horizontal_number_channels, self.horizontal_channel_size, self.min_channel_size)
            )


    def Vertical_number_channels(self, channel_length):
        vertical_blade_dist_fr_cell = self.vertical_outer_radius - (self.inner_radius + channel_length)
        vertical_blade_dist_fr_sample_center = vertical_blade_dist_fr_cell + self.inner_radius
        vertical_wall_angle = 0.0
        vertical_channel_angle=self.span2angle(self.min_channel_size, vertical_blade_dist_fr_sample_center)
        if self.initial_collimator_vertical_channel_angle>0.0:
            self.vertical_channel_angle = self.initial_collimator_vertical_channel_angle+self.min_channel_wall_thickness+\
                                          (self.initial_collimator_vertical_channel_angle*0.5)
        vertical_number_channels=(self.vertical_acceptance_angle-vertical_wall_angle)/\
                        (vertical_channel_angle+vertical_wall_angle)

        return (vertical_number_channels)


    def Horizontal_number_channels(self,channel_length):

        horizontal_blade_dist_fr_cell = self.horizontal_outer_radius - (self.inner_radius + channel_length)
        horizontal_blade_dist_fr_sample_center = horizontal_blade_dist_fr_cell + self.inner_radius
        horizontal_channel_angle=self.span2angle(self.min_channel_size, horizontal_blade_dist_fr_sample_center)
        if self.initial_collimator_horizontal_channel_angle>0.0:
            self.horizontal_channel_angle = self.initial_collimator_horizontal_channel_angle + self.min_channel_wall_thickness+\
                                            (self.initial_collimator_horizontal_channel_angle*0.5)
        horizontal_wall_angle=0.0
        horizontal_number_channels=(self.horizontal_acceptance_angle-horizontal_wall_angle)/\
                        (horizontal_channel_angle+horizontal_wall_angle)

        return (horizontal_number_channels)

    def angle2span(self,Verticle_distance, angle):
        return(2*Verticle_distance*np.tan(np.deg2rad(angle/2)))

    def span2angle(self,distance, distance_fr_sample, ):
        return(2*(np.rad2deg(np.arctan(distance / (2 * distance_fr_sample)))))

    def size_at_sample_side(self, outsideCurve_length, outsideCurve_radius,insideCurve_radius):
        return ((outsideCurve_length * insideCurve_radius) / outsideCurve_radius)



    def solid_pyramid(self):
        scale_pyr = 1.1
        pyr_ht = (self.horizontal_arc_length_detector / np.deg2rad(self.horizontal_acceptance_angle)) * scale_pyr

        thickness = (self.max_coll_height_detector + 1 * self.wall_thickness) * scale_pyr,
        height = (self.horizontal_arc_length_detector / np.deg2rad(self.horizontal_acceptance_angle)) * scale_pyr,
        width = (self.max_coll_width_detector + 1 * self.wall_thickness) * scale_pyr

        # pyr_ht = self.vertical_outer_radius * np.cos(np.deg2rad(self.horizontal_acceptance_angle/2.)) * scale_pyr
        pyr = shapes.pyramid(
            thickness='%s *mm' % (thickness),
            # height='%s *mm' % (height),
            height='%s *mm' % (height),
            width='%s *mm' % width)
        pyr = operations.rotate(pyr, transversal=1, angle='%s *degree' % (90))
        return (pyr)


    def generate_box_toIntersect_big_end(self, width=None, height=None):
        if height is None:
            height = self.vertical_outer_radius
        else:
            height=height


        if width is None:
            width = self.max_coll_height_detector * 1.2 #height of the collimator

        else:
            width=width


        thickness = self.vertical_outer_radius * 1.2 #width of the collimator



        box = shapes.block(height='%s *mm' % height, width='%s *mm' % thickness,
                              thickness='%s *mm' % (width))

        box_d = operations.translate(box, vertical='%s *mm' % (-(height) / 2))

        box_beam_vertical = operations.rotate(box_d, transversal=1, angle='%s *degree' % (90))

        return(box_beam_vertical)



    def generate_horizontal_blade_PLUS_border_list(self):


        height = self.horizontal_outer_radius * 1.2

        arc_width = height * np.deg2rad(self.horizontal_acceptance_angle)

        thickness = self.wall_thickness

        pillar = shapes.block(height='%s *mm' % height, width='%s *mm' % thickness,
                              thickness='%s *mm' % (arc_width))

        pyl_d = operations.translate(pillar, vertical='%s *mm' % (-(height) / 2))

        one_vertical_blade = operations.rotate(pyl_d, transversal=1, angle='%s *degree' % (90))


        one_horizontal_blade = operations.rotate(one_vertical_blade, beam=1,
                                                 angle='%s *degree' % 90)

        horizontal_blades = [operations.rotate(one_horizontal_blade, transversal="1", angle='%s*deg' % a) for a in
                             self.vertical_pillar_angle_list]

        return (horizontal_blades)

    def generate_vertical_blade_PLUS_border_list(self):


        height = self.horizontal_outer_radius * 1.2

        arc_width = height * np.deg2rad(self.vertical_acceptance_angle)

        thickness = self.wall_thickness

        pillar = shapes.block(height='%s *mm' % height, width='%s *mm' % thickness,
                              thickness='%s *mm' % (arc_width))

        pyl_d = operations.translate(pillar, vertical='%s *mm' % (-(height) / 2))

        one_vertical_blade = operations.rotate(pyl_d, transversal=1, angle='%s *degree' % (90))

        vertical_blades = [operations.rotate(one_vertical_blade, vertical="1", angle='%s*deg' % a) for a in
                              self.horizontal_pillar_angle_list]

        return (vertical_blades )

    def generate_blade_PLUS_border_list(self):

        r"""
          Generate the list for vertical and horizontal blades".

         Return
         ----------
         two separate list of vertical blades (largest dimension in vertical direction)
         and horizontal blades(largest dimension in horizontal direction)

          """
        vertical_blades = self.generate_vertical_blade_PLUS_border_list()

        horizontal_blades = self.generate_horizontal_blade_PLUS_border_list()

        return (vertical_blades,horizontal_blades )

    def generate_blade_list(self):

        r"""
          Generate the list for vertical and horizontal blades".

         Return
         ----------
         two separate list of vertical blades (largest dimension in vertical direction)
         and horizontal blades(largest dimension in horizontal direction)

          """
        vertical_blades = self.generate_vertical_blade_PLUS_border_list()[1:-1]

        horizontal_blades = self.generate_horizontal_blade_PLUS_border_list()[1:-1]

        return (vertical_blades, horizontal_blades)


    def generate_oneside_discrete_vertical_channel_left_borders(self):

        r"""
                Generate the list of the vertical channels left borders". (left or right??., please check with figures)

               Return
               ----------
                list of vertical channel left borders (largest dimension in vertical direction)


                """

        if self.max_coll_height_detector>self.max_coll_width_detector:
            height = self.horizontal_outer_radius * 1.2

        else:
            height = self.vertical_outer_radius*1.2

        arc_width = height * np.deg2rad(self.vertical_channel_angle)
        thickness = self.wall_thickness

        pyr = shapes.pyramid(
            thickness='%s *mm' % (thickness),
            height='%s *mm' % (height),
            width='%s *mm' % (arc_width))

        pyr = operations.rotate(pyr, transversal=1, angle='%s *degree' % (90))


        pyl_beam_vertical = operations.rotate(pyr, beam=1, angle='%s *degree' % (90))


        horizontal_pillar_extreme_angle_list= self.horizontal_pillar_min_angle#   [self.horizontal_pillar_min_angle, self.horizontal_pillar_max_angle]


        one_channel_border = operations.rotate(pyl_beam_vertical, vertical="1", angle='%s*deg' % horizontal_pillar_extreme_angle_list)

        all_channel_borders = [operations.rotate(one_channel_border, transversal="1", angle='%s*deg' % a) for a in
                                self.vertical_pillar_angle_list]


        return (all_channel_borders)
        # return (operations.unite(*all_channel_borders))


    def generate_oneside_discrete_vertical_channel_right_borders(self):

        r"""
                Generate the list of the vertical channels right borders".

               Return
               ----------
                list of vertical channel right borders (largest dimension in vertical direction)


                """

        if self.max_coll_height_detector>self.max_coll_width_detector:
            height = self.horizontal_outer_radius * 1.2

        else:
            height = self.vertical_outer_radius*1.2

        arc_width = height * np.deg2rad(self.vertical_channel_angle)
        thickness = self.wall_thickness

        pyr = shapes.pyramid(
            thickness='%s *mm' % (thickness),
            height='%s *mm' % (height),
            width='%s *mm' % (arc_width))

        pyr = operations.rotate(pyr, transversal=1, angle='%s *degree' % (90))


        pyl_beam_vertical = operations.rotate(pyr, beam=1, angle='%s *degree' % (90))


        horizontal_pillar_extreme_angle_list = self.horizontal_pillar_max_angle


        one_channel_border = operations.rotate(pyl_beam_vertical, vertical="1", angle='%s*deg' % horizontal_pillar_extreme_angle_list)

        all_channel_borders = [operations.rotate(one_channel_border, transversal="1", angle='%s*deg' % a) for a in
                                self.vertical_pillar_angle_list]


        return (all_channel_borders)


    def generate_oneside_discrete_horizontal_channel_top_borders(self):

        r"""
                Generate the list of the horizontal channels top borders".

               Return
               ----------
                list of horizontal channel top borders (largest dimension in horizontal direction)


                """

        if self.max_coll_height_detector>self.max_coll_width_detector:
            height = self.horizontal_outer_radius * 1.2

        else:
            height = self.vertical_outer_radius*1.2

        arc_width = height * np.deg2rad(self.horizontal_channel_angle)
        thickness = self.wall_thickness

        pyr = shapes.pyramid(
            thickness='%s *mm' % (thickness),
            height='%s *mm' % (height),
            width='%s *mm' % (arc_width))

        pyr = operations.rotate(pyr, transversal=1, angle='%s *degree' % (90))


        vertical_blade_extreme_angle_list= self.vertical_pillar_min_angle#   [self.horizontal_pillar_min_angle, self.horizontal_pillar_max_angle]


        one_channel_border = operations.rotate(pyr, transversal="1", angle='%s*deg' % vertical_blade_extreme_angle_list)

        all_channel_borders = [operations.rotate(one_channel_border, vertical="1", angle='%s*deg' % a) for a in
                                self.horizontal_pillar_angle_list]


        return (all_channel_borders)

    def generate_oneside_discrete_horizontal_channel_bottom_borders(self):

        r"""
                Generate the list of the horizontal channels bottom borders".

               Return
               ----------
                list of horizontal channel bottom borders (largest dimension in horizontal direction)


                """

        if self.max_coll_height_detector>self.max_coll_width_detector:
            height = self.horizontal_outer_radius * 1.2

        else:
            height = self.vertical_outer_radius*1.2

        arc_width = height * np.deg2rad(self.horizontal_channel_angle)
        thickness = self.wall_thickness

        pyr = shapes.pyramid(
            thickness='%s *mm' % (thickness),
            height='%s *mm' % (height),
            width='%s *mm' % (arc_width))

        pyr = operations.rotate(pyr, transversal=1, angle='%s *degree' % (90))



        vertical_blade_extreme_angle_list = self.vertical_pillar_max_angle



        one_channel_border = operations.rotate(pyr, transversal="1", angle='%s*deg' % vertical_blade_extreme_angle_list)

        all_channel_borders = [operations.rotate(one_channel_border, vertical="1", angle='%s*deg' % a) for a in
                                self.horizontal_pillar_angle_list]


        return (all_channel_borders)



    def vertically_oddsOReven_blades(self):

        vertical_blades, pyls_beam_horizontal = self.generate_blade_list()

        # shiftangle = self.horizontal_pillar_angle_list - self.horizontal_channel_angle * 0.5

        vertical_odd_blades = operations.unite(*vertical_blades[1::2])

        vertical_even_blades = operations.unite(*vertical_blades[::2])

        # channels_shift = [operations.rotate(vertical_odd_blades, vertical="1", angle='%s*deg' % a)
        #               # "vertical" create the pyramid in horizontal direc
        #               for a in shiftangle]
        # #
        # channels_notshift = [operations.rotate(vertical_even_blades, vertical="1", angle='%s*deg' % a)
        #               # "vertical" create the pyramid in horizontal direc
        #               for a in self.horizontal_pillar_angle_list]

        return(vertical_odd_blades,  vertical_even_blades)

    def horizontally_oddsOReven_blades(self):

        pyls_beam_vertical, horizontal_blades = self.generate_blade_list()


        horizontal_odd_blades = operations.unite(*horizontal_blades[1::2])

        horizontal_even_blades = operations.unite(*horizontal_blades[::2])


        return (horizontal_odd_blades, horizontal_even_blades)




    def generate_collimator_channels(self):
        
        vertical_blades_list,horizontal_blades_list=self.generate_blade_list()


        horizontal_odd_blades, horizontal_even_blades = self.horizontally_oddsOReven_blades()
        
        vertical_odd_blades, vertical_even_blades = self.vertically_oddsOReven_blades()

        vertical_blades = operations.unite(*vertical_blades_list)
        horizontal_blades = operations.unite(*horizontal_blades_list)

        if self.vertical_odd_blades:

            vertical_blades = vertical_odd_blades
            
        if self.vertical_even_blades:
            
            vertical_blades = vertical_even_blades

        if self.horizontal_odd_blades:
            horizontal_blades = horizontal_odd_blades

        if self.horizontal_even_blades:
            horizontal_blades = horizontal_even_blades

        channels = operations.unite(vertical_blades, horizontal_blades)

        return (channels)



    def generate_channels_border(self):

        vertical_blades, horizontal_blades = self.generate_blade_PLUS_border_list()

        top_border = horizontal_blades[0]

        bottom_border = horizontal_blades[-1]

        left_border = vertical_blades[0]

        right_border = vertical_blades[-1]


        if self.top_border_odds:
            top_border_list= self.generate_oneside_discrete_horizontal_channel_top_borders()[1::2]
            top_border=operations.unite(*top_border_list)

        if self.top_border_evens:
            top_border_list = self.generate_oneside_discrete_horizontal_channel_top_borders()[0::2]
            top_border = operations.unite(*top_border_list)

        if self.bottom_border_odds:
            bottom_border_list = self.generate_oneside_discrete_horizontal_channel_bottom_borders()[1::2]
            bottom_border = operations.unite(*bottom_border_list)

        if self.bottom_border_evens:
            bottom_border_list = self.generate_oneside_discrete_horizontal_channel_bottom_borders()[0::2]
            bottom_border = operations.unite(*bottom_border_list)

        if self.left_border_odds:
            left_border_list = self.generate_oneside_discrete_vertical_channel_left_borders()[1::2]
            left_border = operations.unite(*left_border_list)

        if self.left_border_evens:
            left_border_list = self.generate_oneside_discrete_vertical_channel_left_borders()[0::2]
            left_border = operations.unite(*left_border_list)

        if self.right_border_odds:
            right_border_list = self.generate_oneside_discrete_vertical_channel_right_borders()[1::2]
            right_border = operations.unite(*right_border_list)

        if self.right_border_evens:
            right_border_list = self.generate_oneside_discrete_vertical_channel_right_borders()[0::2]
            right_border = operations.unite(*right_border_list)



        channel_border= operations.unite(operations.unite(operations.unite(top_border,bottom_border),
                         left_border), right_border)


        return channel_border




    def gen_one_col(self, collimator_Nosupport=True):
        pyr = self.solid_pyramid()

        big_cylinder = shapes.cylinder(radius='%s *mm' % (self.vertical_outer_radius),
                                       height='%s *mm' % (self.max_coll_height_detector * 10))

        big_box=self.generate_box_toIntersect_big_end()

        outside_sphere = shapes.sphere(radius='%s *mm' % self.vertical_outer_radius)


        channels=self.generate_collimator_channels()
        channels_border=self.generate_channels_border()

        conical_colli = operations.intersect(channels, pyr)

        conical_channels_border=operations.intersect(channels_border, pyr)


        cutoff_cylinder = shapes.cylinder(radius='%s *mm' % (self.inner_radius),
                                          height='%s *mm' % (self.max_coll_height_detector * 90.))

        blade_cutoff_cylinder = shapes.cylinder(radius='%s *mm' % (self.vertical_blade_dist_fr_sample_center),
                                          height='%s *mm' % (self.max_coll_height_detector * 10))



        cutoff_box = shapes.block(width='%s *mm' % (self.inner_radius*2), thickness='%s *mm' % (self.inner_radius*2),
                                          height='%s *mm' % (self.max_coll_height_detector * 90.))

        blade_cutoff_box = shapes.block(width='%s *mm' % (self.vertical_blade_dist_fr_sample_center*2),
                                        thickness='%s *mm' % (self.vertical_blade_dist_fr_sample_center*2),
                                                height='%s *mm' % (self.max_coll_height_detector * 10))


        # return (operations.subtract(conical_channels_border, cutoff_cylinder))

        if self.collimator_parts is True:
            open_collimator = operations.intersect(operations.subtract(conical_channels_border, cutoff_box),
                                                   big_box)

            collimator_with_blades = operations.intersect(operations.subtract(conical_colli, blade_cutoff_box),
                                                          big_box)

        else:
            open_collimator=operations.intersect(operations.subtract(conical_channels_border, cutoff_cylinder), big_box)



            collimator_with_blades = operations.intersect(operations.subtract(conical_colli, blade_cutoff_cylinder), big_box)


        collimator=operations.unite(open_collimator, collimator_with_blades)



        scale_pyr = 1.1
        pyr_ht = (self.horizontal_arc_length_detector / np.deg2rad(self.horizontal_acceptance_angle)) * scale_pyr

        thickness = (self.max_coll_height_detector + 1 * self.wall_thickness) * scale_pyr
        height = (self.horizontal_arc_length_detector / np.deg2rad(self.horizontal_acceptance_angle)) * scale_pyr
        width = (self.max_coll_width_detector + 1 * self.wall_thickness) * scale_pyr

        # pyr_ht = self.vertical_outer_radius * np.cos(np.deg2rad(self.horizontal_acceptance_angle/2.)) * scale_pyr
        pyr_lateral = shapes.pyramid(
            thickness='%s *mm' % (thickness),
            # height='%s *mm' % (height),
            height='%s *mm' % (height),
            width='%s *mm' % (width+900.))
        pyr_lateral = operations.rotate(pyr_lateral, transversal=1, angle='%s *degree' % (90))

        pyr_depth = shapes.pyramid(
            thickness='%s *mm' % (thickness+6900),
            # height='%s *mm' % (height),
            height='%s *mm' % (height),
            width='%s *mm' % (width ))
        pyr_depth = operations.rotate(pyr_depth, transversal=1, angle='%s *degree' % (90))

        collimator_support = Collimator_support()
        collimator_support.set_constraints(
            truss_base_thickness=30., trass_final_height_factor=0.45,
            touch_to_halfcircle=6, SNAP_acceptance_angle=False)

        supports = collimator_support.support()


        support_top=operations.intersect(operations.subtract(supports, pyr_lateral), pyr_depth)



        # support_top =operations.subtract(self.support(), pyr_lateral)

        support_bottom=operations.rotate(operations.rotate(support_top, transversal=1, angle='%s *degree' %(-180)), vertical=1, angle='%s *degree' %180)


        supports=operations.subtract(operations.unite(support_top, support_bottom), cutoff_cylinder)

        if collimator_Nosupport is True:
            return(collimator)
        else:
            return(operations.unite(collimator,supports))


    def gen_collimators(self, detector_angles=[-45, -135], multiple_collimator=True,collimator_Nosupport=True):

        if multiple_collimator is True:
            rotated_coll = [operations.rotate(self.gen_one_col(collimator_Nosupport), beam="1", angle='%s*deg' % (a)) for a in
                            detector_angles]
            all_coll = operations.unite(*rotated_coll)
        else:
            rotated_coll = operations.rotate(self.gen_one_col(collimator_Nosupport), vertical="1",
                                             angle='%s*deg' % (180 + detector_angles[0]))  # transversal ,90

            all_coll = rotated_coll

        return (all_coll)

    def gen_collimators_xml(self, detector_angles=[-45, -135],collimator_Nosupport=True, multiple_collimator=True, scad_flag=False,
                            coll_file="coll_geometry.xml"):
        write_file(coll_file, self.gen_collimators(detector_angles, multiple_collimator,collimator_Nosupport), scad_flag)


