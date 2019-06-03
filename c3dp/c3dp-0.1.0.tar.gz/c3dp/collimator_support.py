import numpy as np
from instrument.geometry.pml import weave
from instrument.geometry import shapes, operations
from instrument.geometry.pml.Renderer import Renderer as base
import click

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

#import lmfit
import mcvine, mcvine.components
from mcvine import run_script

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
                         min_channel_size=3., detector_dist_fr_sample_center=500., detector_size=500.,
                        clamp_cell_radius=16.02,
                        truss_base_thickness=30., truss_height_factor=10., truss_curvature=1.,
                        trass_final_height_factor=0.77,beam_dist_support=33.,touch_to_halfcircle=0.5,
                        SNAP_acceptance_angle=True, truss_blade_length=10): # small(58 wide x 38 deep x 33 high), medium (160, 65, 65), large(400 wide x 250 deep x 250 high)

        self.inner_radius = clamp_cell_radius  # clamp cell radius (minimum distance from sample center)

        if SNAP_acceptance_angle is True:
            self.horizontal_acceptance_angle = self.span2angle(detector_size, detector_dist_fr_sample_center)  # 53 degree
            self.vertical_acceptance_angle = self.span2angle(detector_size, detector_dist_fr_sample_center)  # 53 degree

            

        else:
            self.horizontal_acceptance_angle = self.span2angle(max_coll_height_detector,
                                                               max_coll_length+self.inner_radius)  # 53 degree

            self.vertical_acceptance_angle = self.span2angle(max_coll_width_detector,
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
        self.truss_blade_length=truss_blade_length


        self.curvature=truss_curvature

        self.outer_radius=(self.max_coll_height_detector/2.)/np.tan(np.deg2rad(self.vertical_acceptance_angle/2.)) #140

        # print ('outer_radius',self.outer_radius)
        #
        # print ('coll_height', self.max_coll_height_detector)

    def coll_height_detector(self):
        return(self.max_coll_height_detector)

    def number_channels(self):
        self.vertical_channel_angle=self.span2angle(self.min_channel_size, self.blade_dist_fr_sample_center)
        number_channels=(self.vertical_acceptance_angle-self.vertical_wall_angle)/\
                        (self.vertical_channel_angle+self.vertical_wall_angle)

        return (number_channels)



    def set_parameters(self, number_channels, channel_length,wall_thickness= None):
        if wall_thickness is None:
            self.wall_thickness= self.min_channel_wall_thickness
        else:
            self.wall_thickness = wall_thickness
        self.number_channels=number_channels
        self.channel_length=channel_length
        self.blade_dist_fr_cell=self.outer_radius-(self.inner_radius+self.channel_length)
        self.blade_dist_fr_sample_center= self.blade_dist_fr_cell+self.inner_radius
      
        self.number_walls = self.number_channels+1
        
        self.vertical_wall_angle =0.0
        # self.vertical_wall_angle=self.span2angle(self.min_channel_wall_thickness, self.inner_radius)
        # self.vertical_acceptance_angle=self.span2angle(self.max_coll_height_detector,self.outer_radius)

        self.vertical_arc_length_detector=self.outer_radius * np.deg2rad(self.vertical_acceptance_angle)

        self.vertical_arc_length_sample=self.inner_radius * np.deg2rad(self.vertical_acceptance_angle)



        self.Vertical_cutoff_distance = (self.number_walls * self.wall_thickness
                                         + self.number_channels * self.min_channel_size) /\
                                        np.deg2rad(self.vertical_acceptance_angle)


        self.vertical_channel_angle=(self.vertical_acceptance_angle-(self.number_walls)*self.vertical_wall_angle)/self.number_channels


        # self.vertical_channel_size=self.inner_radius *np.deg2rad(self.vertical_channel_angle)

        self.vertical_channel_size = self.angle2span(self.blade_dist_fr_sample_center, self.vertical_channel_angle)



        self.vertical_pillar_min_angle = -self.vertical_acceptance_angle / 2. + self.vertical_wall_angle
        self.vertical_pillar_max_angle = self.vertical_acceptance_angle / 2.

        self.vertical_pillar_angle_list = np.arange(
            self.vertical_pillar_min_angle,
            self.vertical_pillar_max_angle + self.vertical_channel_angle / 2.,
            self.vertical_channel_angle)

        # print('vertical cutoff', self.Vertical_cutoff_distance)

        # print ('test angular coverage', np.rad2deg(self.max_coll_height_detector/self.outer_radius))

        # print ('calculated angular coverage', self.vertical_acceptance_angle)
#############################################################################################
        ################################################################
        if self.vertical_channel_size<self.min_channel_size:
            raise Parameter_error(
                ("The number of channels should be less: %s. \n"
                +"Calculated vertical channel size is %s, but the minimum channel size is %s\n") %
                (number_channels, self.vertical_channel_size, self.min_channel_size)
            )
 ########################################################################
        #############################################################


        self.horizontal_wall_angle =0.0
        # self.horizontal_wall_angle = self.span2angle(self.min_channel_wall_thickness, self.inner_radius)
        # self.horizontal_acceptance_angle = self.span2angle(self.max_max_coll_width_detector, self.outer_radius)

        self.horizontal_arc_length_detector = self.outer_radius * np.deg2rad(self.horizontal_acceptance_angle)

        self.horizontal_arc_length_sample = self.inner_radius * np.deg2rad(self.horizontal_acceptance_angle)

        self.horizontal_channel_angle = (self.horizontal_acceptance_angle - (self.number_walls) * self.horizontal_wall_angle) / self.number_channels

        self.horizontal_cutoff_distance = ((self.number_walls * self.wall_thickness)+(self.number_channels*self.min_channel_size))\
                                          /np.deg2rad(self.horizontal_acceptance_angle)



        # self.horizontal_channel_size=self.inner_radius* np.deg2rad(self.horizontal_channel_angle)

        self.horizontal_channel_size = self.angle2span(self.blade_dist_fr_sample_center, self.horizontal_channel_angle)



        self.horizontal_pillar_min_angle = -self.horizontal_acceptance_angle / 2 + self.horizontal_wall_angle
        self.horizontal_pillar_max_angle = self.horizontal_acceptance_angle / 2



        self.horizontal_pillar_angle_list = np.arange(
            self.horizontal_pillar_min_angle,
            self.horizontal_pillar_max_angle + self.horizontal_channel_angle / 2,
            self.horizontal_channel_angle)

        if self.horizontal_channel_size<self.min_channel_size:
            raise ValueError(
                ("The number of walls should be less: %s. \n"
                +"Calculated horizontal channel size is %s, but the minimum channel size is %s\n") %
                (number_channels, self.horizontal_channel_size, self.min_channel_size)
            )

    def angle2span(self,Verticle_distance, angle):
        return(2*Verticle_distance*np.tan(np.deg2rad(angle/2)))

    def span2angle(self,distance, distance_fr_sample, ):
        return(2*(np.rad2deg(np.arctan(distance / (2 * distance_fr_sample)))))

    def size_at_sample_side(self, outsideCurve_length, outsideCurve_radius,insideCurve_radius):
        return ((outsideCurve_length * insideCurve_radius) / outsideCurve_radius)

    def tab_screw(self):
        height=self.max_max_coll_width_detector
        width=3.6*5
        thickness=6.

        source_distance=self.inner_radius+5
        span=self.angle2span(source_distance,self.horizontal_acceptance_angle)

        large_pillar=shapes.block(height='%s *mm' %height, width='%s *mm' %width, thickness='%s *mm' % thickness)
        small_pillar=shapes.block(height='%s *mm' %span, width='%s *mm' %(width+1), thickness='%s *mm' % (thickness+1))

        pillar=operations.subtract(large_pillar, small_pillar)

        length=height-span

        holes_position=span/2 +length/4

        holes=[operations.translate(operations.rotate(shapes.cylinder(radius='%s*mm' %1.6 , height='%s *mm' % (thickness+55)), transversal=1, angle='%s *deg' %90 ), vertical='%s *mm'%a) for a in [holes_position, -holes_position]]

        all_holes=operations.unite(*holes)

        pillar_holes=operations.subtract(large_pillar, all_holes)

        vertical_rot=operations.rotate(pillar_holes, vertical=1, angle='%s *deg' %90)

        beam_rot=operations.rotate(vertical_rot, beam=1, angle='%s *deg' %90)

        move_beam=operations.translate(beam_rot, beam='%s *mm' % -(self.inner_radius+ self.base_thickness/2))

        move_ver=operations.translate(move_beam, vertical='%s *mm' % (-(self.max_coll_height_detector)/2+thickness/2) )

        return (vertical_rot)

    def solid_pyramid(self):
        scale_pyr = 1.1
        pyr_ht = (self.horizontal_arc_length_detector / np.deg2rad(self.horizontal_acceptance_angle)) * scale_pyr

        thickness = (self.max_coll_height_detector + 1 * self.wall_thickness) * scale_pyr,
        height = (self.horizontal_arc_length_detector / np.deg2rad(self.horizontal_acceptance_angle)) * scale_pyr,
        width = (self.max_coll_width_detector + 1 * self.wall_thickness) * scale_pyr

        # pyr_ht = self.outer_radius * np.cos(np.deg2rad(self.horizontal_acceptance_angle/2.)) * scale_pyr
        pyr = shapes.pyramid(
            thickness='%s *mm' % (thickness),
            # height='%s *mm' % (height),
            height='%s *mm' % (height),
            width='%s *mm' % width)
        pyr = operations.rotate(pyr, transversal=1, angle='%s *degree' % (90))
        return (pyr)

    def generate_box_toCut_big_end(self, width=None, height=None):
        if height is None:
            height = self.outer_radius
        else:
            height=height

        # print ('blade height', height)

        if width is None:
            width = self.max_coll_height_detector * 1.2
        else:
            width=width


        thickness = self.outer_radius * 1.2



        box = shapes.block(height='%s *mm' % height, width='%s *mm' % thickness,
                              thickness='%s *mm' % (width))

        box_d = operations.translate(box, vertical='%s *mm' % (-(height) / 2))

        box_beam_vertical = operations.rotate(box_d, transversal=1, angle='%s *degree' % (90))

        return(box_beam_vertical)


    def generate_channels_list(self):

        height = self.outer_radius*1.2

        # print ('blade height', height)
        width = abs(self.angle2span(height, self.horizontal_acceptance_angle))

        arc_width = height * np.deg2rad(self.horizontal_acceptance_angle)

        # print (' arc width', arc_width)
        thickness = self.wall_thickness

        # print ('blade width', width)

        # print ('blade thickness', thickness)

        pillar = shapes.block(height='%s *mm' % height, width='%s *mm' % thickness,
                              thickness='%s *mm' % (arc_width))

        pyl_d = operations.translate(pillar, vertical='%s *mm' % (-(height) / 2))

        pyl_beam_vertical = operations.rotate(pyl_d, transversal=1, angle='%s *degree' % (90))


        pyls_beam_vertical = [operations.rotate(pyl_beam_vertical, vertical="1", angle='%s*deg' % a) for a in
                              self.horizontal_pillar_angle_list]

        pyl_beam_horizontal = operations.rotate(pyl_beam_vertical, beam=1,
                                                angle='%s *degree' % 90)

        pyls_beam_horizontal = [operations.rotate(pyl_beam_horizontal, transversal="1", angle='%s*deg' % a) for a in
                                self.vertical_pillar_angle_list]


        return (pyls_beam_vertical,pyls_beam_horizontal )

    def generate_collimator_channels(self):

        pyls_beam_vertical, pyls_beam_horizontal=self.generate_channels_list()
        channels=operations.unite(operations.unite(*pyls_beam_vertical), *pyls_beam_horizontal)

        return(channels)


    def generate_channels_border(self):

        pyls_beam_vertical, pyls_beam_horizontal = self.generate_channels_list()
        channels_border=operations.unite(operations.unite(operations.unite(pyls_beam_vertical[0], pyls_beam_vertical[-1]),
                                                          pyls_beam_horizontal[0]), pyls_beam_horizontal[-1])

        return channels_border


    def support_design(self):

            main_cylinder_radius = self.inner_radius

            main_cylinder_diameter = main_cylinder_radius * 2.

            height_support = main_cylinder_diameter - 8.

            # print (height_support)

            distance_fr_center_height_main = np.sqrt((main_cylinder_radius) ** 2 - (height_support / 2) ** 2)

            base_width_support = self.truss_base_thickness

            suppert_end_distance_fr_source = self.inner_radius + base_width_support

            thickness_collimator_at_support_end = self.angle2span(suppert_end_distance_fr_source,
                                                                  self.vertical_acceptance_angle)



            pillar = shapes.block(height='%s *mm' % (main_cylinder_diameter+base_width_support+
                                                     self.truss_blade_length),
                                  width='%s *mm' % (thickness_collimator_at_support_end),
                                  thickness='%s *mm' % 1)



            pillar_beam = operations.rotate(pillar, transversal=1, angle="%s *degree" % 90)



            small_pillar_beam_tocut = operations.rotate(shapes.block(height='%s *mm' % (main_cylinder_diameter / 2.),
                                                                     width='%s *mm' % (
                                                                                 thickness_collimator_at_support_end + 5),
                                                                     thickness='%s *mm' % 5), transversal=1,
                                                        angle="%s *degree" % 90)

            pillar_beam = operations.subtract(pillar_beam, operations.translate(small_pillar_beam_tocut,
                                                                                beam='%s*mm' % -(
                                                                                            main_cylinder_radius / 2)))


            angle = 10

            truss_rot_degree=10
            pillar_beam_dia = operations.rotate(pillar_beam, transversal=1, angle='%s *degree' % truss_rot_degree)

            # return (pillar_beam_dia)

            blade1_needed = operations.translate(operations.subtract(operations.rotate(
                shapes.block(height='%s *mm' % (self.max_coll_height_detector * 90.),
                             width='%s *mm' % (thickness_collimator_at_support_end),
                             thickness='%s *mm' % 2), transversal=1, angle="%s *degree" % 90),
                                                                     operations.translate(small_pillar_beam_tocut,
                                                                                          beam='%s*mm' % -(
                                                                                                      main_cylinder_radius / 2))),
                                                 beam='%s *mm' % (distance_fr_center_height_main))



            blade1 = operations.translate(pillar_beam, beam='%s *mm' % (distance_fr_center_height_main))


            blade1_dia = operations.translate(pillar_beam_dia, beam='%s *mm' % (distance_fr_center_height_main))

            vertical_blade = operations.rotate(operations.subtract(operations.rotate(shapes.block(height='%s *mm' % (self.max_coll_height_detector),
                                  width='%s *mm' % (thickness_collimator_at_support_end),
                                  thickness='%s *mm' % 1), transversal=1, angle="%s *degree" % 90),
                                                                   operations.translate(small_pillar_beam_tocut,
                                                                                beam='%s*mm' % -(
                                                                                            main_cylinder_radius / 2))), beam=1, angle='%s *degree' % (90))

            vertical_blade = operations.translate(vertical_blade, beam='%s *mm' % (self.inner_radius))

            vertical_blade = operations.rotate(vertical_blade, transversal=1, angle='%s *degree' % (90))

            vertical_blade = operations.rotate(vertical_blade, vertical=1, angle='%s *degree' % (90))

            vertical_blade = operations.translate(vertical_blade, beam='%s *mm' % (self.inner_radius))
            #
            # return (vertical_blade)



            # return (operations.unite(blade1, blade1_dia))

            pillar_beam2 = operations.translate(pillar_beam, vertical="%s *mm" % -(
                        suppert_end_distance_fr_source * np.sin(np.deg2rad(angle))))

            pillar_beam_dia2 = operations.rotate(pillar_beam2, transversal=1, angle='%s *degree' % truss_rot_degree)

            blade2 = operations.translate(pillar_beam2, beam='%s *mm' % (distance_fr_center_height_main))
            blade2_dia = operations.translate(pillar_beam_dia2, beam='%s *mm' % (distance_fr_center_height_main))

            # return (operations.unite(operations.unite(pillar_beam2, pillar_beam_dia2), pillar_beam))

            pillar_beam3 = operations.translate(pillar_beam2, vertical="%s *mm" % -(
                    suppert_end_distance_fr_source * np.sin(np.deg2rad(angle))))

            pillar_beam_dia3 = operations.rotate(pillar_beam3, transversal=1, angle='%s *degree' % truss_rot_degree)

            blade3 = operations.translate(pillar_beam3, beam='%s *mm' % (distance_fr_center_height_main- self.touch_to_halfcircle))
            blade3_dia = operations.translate(pillar_beam_dia3, beam='%s *mm' % (distance_fr_center_height_main))

            pillar_beam4 = operations.translate(pillar_beam3, vertical="%s *mm" % -(
                    suppert_end_distance_fr_source * np.sin(np.deg2rad(angle))))

            pillar_beam_dia4 = operations.rotate(pillar_beam4, transversal=1, angle='%s *degree' % (truss_rot_degree))

            blade4 = operations.translate(pillar_beam4, beam='%s *mm' % (distance_fr_center_height_main))
            blade4_dia = operations.translate(pillar_beam_dia4, beam='%s *mm' % (distance_fr_center_height_main))



            pillar_beam5 = operations.translate(pillar_beam4, vertical="%s *mm" % -(
                    suppert_end_distance_fr_source * np.sin(np.deg2rad(angle))))

            pillar_beam_dia5 = operations.rotate(pillar_beam5, transversal=1, angle='%s *degree' % (truss_rot_degree))

            blade5 = operations.translate(pillar_beam5, beam='%s *mm' % (distance_fr_center_height_main))
            blade5_dia = operations.translate(pillar_beam_dia5, beam='%s *mm' % (distance_fr_center_height_main))

            pillar_beam6 = operations.translate(pillar_beam5, vertical="%s *mm" % -(
                    suppert_end_distance_fr_source * np.sin(np.deg2rad(angle))))

            pillar_beam_dia6 = operations.rotate(pillar_beam6, transversal=1, angle='%s *degree' % (truss_rot_degree))

            blade6 = operations.translate(pillar_beam6, beam='%s *mm' % (distance_fr_center_height_main))
            blade6_dia = operations.translate(pillar_beam_dia6, beam='%s *mm' % (distance_fr_center_height_main))

            # return (operations.unite(operations.unite(operations.unite(operations.unite(operations.unite(blade1, blade2), blade3), blade4), blade5), blade6))

            pillar_beam7 = operations.translate(pillar_beam6, vertical="%s *mm" % -(
                    suppert_end_distance_fr_source * np.sin(np.deg2rad(angle))))

            pillar_beam_dia7 = operations.rotate(pillar_beam7, transversal=1, angle='%s *degree' % (truss_rot_degree))

            blade7 = operations.translate(pillar_beam7, beam='%s *mm' % (distance_fr_center_height_main))
            blade7_dia = operations.translate(pillar_beam_dia7, beam='%s *mm' % (distance_fr_center_height_main))




            pillar_beam8 = operations.translate(pillar_beam7, vertical="%s *mm" % -(
                    suppert_end_distance_fr_source * np.sin(np.deg2rad(angle))))

            pillar_beam_dia8 = operations.rotate(pillar_beam8, transversal=1, angle='%s *degree' % (truss_rot_degree))

            blade8 = operations.translate(pillar_beam8, beam='%s *mm' % (distance_fr_center_height_main))
            blade8_dia = operations.translate(pillar_beam_dia8, beam='%s *mm' % (distance_fr_center_height_main))

            # return (operations.unite(blade1, blade3))

            pillar_beam9 = operations.translate(pillar_beam8, vertical="%s *mm" % -(
                    suppert_end_distance_fr_source * np.sin(np.deg2rad(angle))))

            pillar_beam_dia9 = operations.rotate(pillar_beam9, transversal=1, angle='%s *degree' % (truss_rot_degree))

            blade9 = operations.translate(pillar_beam9, beam='%s *mm' % (distance_fr_center_height_main))
            blade9_dia = operations.translate(pillar_beam_dia9, beam='%s *mm' % (distance_fr_center_height_main))

            pillar_beam10 = operations.translate(pillar_beam9, vertical="%s *mm" % -(
                    suppert_end_distance_fr_source * np.sin(np.deg2rad(angle))))

            pillar_beam_dia10 = operations.rotate(pillar_beam10, transversal=1, angle='%s *degree' % (truss_rot_degree))

            blade10 = operations.translate(pillar_beam10, beam='%s *mm' % (distance_fr_center_height_main))
            blade10_dia = operations.translate(pillar_beam_dia10, beam='%s *mm' % (distance_fr_center_height_main))

            pillar_beam_last = operations.translate(pillar_beam10, vertical="%s *mm" % -(
                    suppert_end_distance_fr_source * np.sin(np.deg2rad(angle))))

            pillar_beam_dia_last = operations.rotate(blade1, transversal=1, angle='%s *degree' % (90))

            blade_last = operations.translate(pillar_beam_last, beam='%s *mm' % (distance_fr_center_height_main))
            blade_last_dia = operations.translate(pillar_beam_dia_last, beam='%s *mm' % (distance_fr_center_height_main))

            # blade_last_up = operations.rotate(
            #     operations.rotate(pillar_beam_last, transversal=1, angle='%s *degree' % (-180)), vertical=1,
            #     angle='%s *degree' % 180)
            # return(blade_last)

            blades = [vertical_blade, blade1_needed, blade1_dia, blade2, blade2_dia, blade3, blade3_dia, blade4, blade4_dia, blade5,
                      blade5_dia, blade6,]

            # blades = [vertical_blade, blade1_needed, blade1_dia,blade2, blade2_dia, blade3, blade4,
            #           blade4_dia, blade5,
            #           blade5_dia, blade6, blade6_dia, blade7, ]

            all_blades_down=operations.unite(*blades)



            blades_up = operations.rotate(
                operations.rotate(all_blades_down, transversal=1, angle='%s *degree' % (-180)), vertical=1,
                angle='%s *degree' % 180)

            # return (blades_up)


            side_cut_box = shapes.block(height='%s *mm' % 10000,
                             width='%s *mm' % (100),
                             thickness='%s *mm' % (self.inner_radius*2))


            blades_up=operations.subtract(blades_up, side_cut_box)

            # return (operations.unite(blades_up, self.generate_box_toCut_big_end()))

            all_blades=operations.unite(all_blades_down, blades_up)

            # more_blades_up=operations.rotate(
            #     operations.rotate(all_blades, transversal=1, angle='%s *degree' % (-180)), vertical=1,
            #     angle='%s *degree' % 180)

            return (all_blades)

            # return (operations.unoperations.unite(operations.unite(operations.unite(operations.unite(operations.unite(blade1,blade1_dia), blade2), blade2_dia), blade3), blade3_dia))

        # def circle_w_cylindrical_side(self):

    def support(self ):

            main_cylinder_radius = self.inner_radius*self.truss_height_factor

            main_cylinder_diameter = main_cylinder_radius * 2.

            height_support_main = main_cylinder_diameter - self.beam_dist_support

            base_width_support = self.truss_base_thickness



            cyli_radius = main_cylinder_radius * 2

            height_support = height_support_main

            cyli_dia = cyli_radius * 2.



            ################################################ cylinder_radius=self.inner_radius

            cylinder_radius = cyli_dia / 2.
            vertical_cylinder_height = cyli_dia + 100  ## big cylinder height should be greater than the cyli diameter

            suppert_end_distance_fr_source = self.inner_radius + base_width_support

            beam_distance_sphere_move_fr_origin = suppert_end_distance_fr_source

            thickness_collimator_at_support_end = self.angle2span(beam_distance_sphere_move_fr_origin,
                                                                  self.vertical_acceptance_angle)

            height_factor=1.
            height = thickness_collimator_at_support_end*height_factor

            cylinder = shapes.cylinder(radius='%s *mm' % (cylinder_radius),
                                       height='%s *mm' % (height * 2 + 10))

            cylinder_transversal = operations.rotate(cylinder, beam=1,
                                                     angle='%s *degree' % 90)

            vertical_cylinder = shapes.cylinder(radius='%s *mm' % (cylinder_radius),
                                                height='%s *mm' % (vertical_cylinder_height))

            distance_fr_center_height_main = np.sqrt((main_cylinder_radius) ** 2 - (height_support / 2) ** 2)

            angular_cut = self.span2angle(height_support, distance_fr_center_height_main) / 2.

            distance_fr_center_height = cylinder_radius * np.cos(np.deg2rad(angular_cut))

            vertical_cylinder_move_dist = abs(cylinder_radius - distance_fr_center_height)

            distance_fr_center_height = np.sqrt((cylinder_radius) ** 2 - (height_support / 2) ** 2)

            vertical_cylinder_move_dist = abs(cylinder_radius - distance_fr_center_height_main)

            unwanted_part_of_smallcircle0 = operations.subtract(cylinder_transversal,
                                                                operations.translate(vertical_cylinder,
                                                                                     beam='%s *mm' % -vertical_cylinder_move_dist))

            moving_dist_cylinder = 20

            # unwanted_part_of_smallcircle0= operations.translate(unwanted_part_of_smallcircle0, beam='%s *mm' %-moving_dist_cylinder)

            unwanted_part_of_bigcircle2 = operations.translate(unwanted_part_of_smallcircle0, beam='%s *mm' % (1))

            cylinder_radius = self.inner_radius

            cylinder_transversal_1_0 = operations.rotate(shapes.cylinder(radius='%s *mm' % (cylinder_radius),
                                                                         height='%s *mm' % ((height * 2))), beam=1,
                                                         angle='%s *degree' % 90)

            # return(operations.unite(cylinder_transversal_1_0, operations.translate(vertical_cylinder, beam='%s *mm' % -vertical_cylinder_move_dist)))
            mod_cylinder_transversal = operations.subtract(cylinder_transversal_1_0, unwanted_part_of_smallcircle0)

            # return (operations.subtract(cylinder_transversal,operations.subtract(cylinder_transversal,operations.translate(vertical_cylinder, beam='%s *mm' % -vertical_cylinder_move_dist))))
            # return (operations.unite(cylinder_transversal_1_0,unwanted_part_of_smallcircle0 ))
            # return(mod_cylinder_transversal)
            # return (vertical_cylinder)
            # return (operations.subtract(vertical_cylinder, cylinder_transversal))

            ########################################################################################################################################
            #########################################################################################################################################

            solid_shape = mod_cylinder_transversal

            cylinder_transversal = mod_cylinder_transversal  ## small inside cylinder

            cylinder_2 = shapes.cylinder(radius='%s *mm' % (cylinder_radius + 1),  ###big cylinder (outside cylinder)
                                         height='%s *mm' % (height * 2))

            cylinder_transversal_2_0 = operations.rotate(cylinder_2, beam=1,
                                                         angle='%s *degree' % 90)

            cylinder_transversal_2 = operations.subtract(cylinder_transversal_2_0, unwanted_part_of_bigcircle2)

            width_factor=2.

            big_block = shapes.block(height='%s *mm' % cyli_dia, width='%s *mm' % (suppert_end_distance_fr_source * width_factor),
                                     thickness='%s *mm' % (height))

            big_block_rotate = operations.rotate(big_block, vertical=1,
                                                 angle='%s *degree' % 90)

            big_block_2 = shapes.block(height='%s *mm' % (cyli_dia - 1),
                                       width='%s *mm' % ((suppert_end_distance_fr_source * width_factor) - 2),
                                       thickness='%s *mm' % (height + 1))  #### small blog

            big_block_rotate_2 = operations.rotate(big_block_2, vertical=1,
                                                   angle='%s *degree' % 90)

            parts = operations.subtract(big_block_rotate, cylinder_transversal)

            # return(operations.unite(big_block_rotate, cylinder_transversal))

            # return(big_block_rotate)

            parts_2 = operations.subtract(big_block_rotate_2, cylinder_transversal_2)

            parts_frame = operations.subtract(parts, parts_2)

            # parts_frame=operations.unite(parts_frame, solid_shape)

            # return (parts_frame)
            # return (operations.subtract(parts_frame,parts_2))

            # return operations.unite(cylinder_transversal_1_0,unwanted_part_of_smallcircle0)
            # return(operations.unite(cylinder_transversal, cylinder_transversal_2))

            blades_in_frames = operations.subtract(self.support_design(), cylinder_transversal)

            parts_frame_blades_pre = operations.unite(parts_frame, blades_in_frames)

            parts_frame_blades_pre=parts_frame

            # return (parts_frame_blades_pre)
            #############################################################CHANGES#####################################################
            #########################################################################################################################

            # solid=operations.subtract(vertical_cylinder, unwanted_part_of_bigcircle2)
            #
            # parts_frame_blades_pre = operations.unite(parts_frame_blades_pre, solid)

            side_cut_box = operations.translate(operations.rotate(
                shapes.block(height='%s *mm' % cyli_dia, width='%s *mm' % (suppert_end_distance_fr_source * width_factor),
                             thickness='%s *mm' % (height * 2)), vertical=1,
                angle='%s *degree' % 90), beam='%s *mm' % -(suppert_end_distance_fr_source))

            up_cut_box = operations.translate(operations.rotate(
                shapes.block(height='%s *mm' % cyli_dia, width='%s *mm' % ((suppert_end_distance_fr_source * width_factor) + 1),
                             thickness='%s *mm' % (height * 2)), vertical=1,
                angle='%s *degree' % 90), vertical='%s *mm' % (cyli_dia/2. )) ########################

            down_cut_box = operations.translate(operations.rotate(
                shapes.block(height='%s *mm' % cyli_dia, width='%s *mm' % ((suppert_end_distance_fr_source * width_factor) + 1),
                             thickness='%s *mm' % (height * 2)), vertical=1,
                angle='%s *degree' % 90), vertical='%s *mm' % (-(cyli_dia - 2)))

            parts_frame_blades = operations.subtract(
                operations.subtract(operations.subtract(parts_frame_blades_pre, side_cut_box), up_cut_box),
                down_cut_box)


            parts_frame_blades=operations.unite(parts_frame_blades, blades_in_frames)


            parts_frame_blades = operations.subtract(operations.subtract(parts_frame_blades, side_cut_box), down_cut_box)

            # return (parts_frame_blades)

            thickness_parts = ((suppert_end_distance_fr_source * width_factor) - (self.inner_radius)) / 2

            parts_move_beam = operations.translate(parts_frame_blades, beam='%s *mm' % (
                        -(self.inner_radius) * 2 - base_width_support + 1))
            angle = self.vertical_acceptance_angle # 15
            # parts_move_up = operations.translate(parts_move_beam, vertical='%s *mm' % (
            #             self.inner_radius + (
            #                 self.curvature * self.inner_radius * np.tan(np.deg2rad(angle/2.)))))

            parts_move_up = operations.translate(parts_move_beam, vertical='%s *mm' % (self.inner_radius +
                    (self.curvature * (self.inner_radius*2.+base_width_support) * np.tan(np.deg2rad(angle / 2.)))))

            # return (parts_move_up)
            # return(parts_frame)
            return (operations.intersect(parts_move_up,self.generate_box_toCut_big_end(width=self.max_coll_height_detector*self.trass_final_height_factor,
                                                                                       height=(self.inner_radius*2.+base_width_support+100.))))
            # return (self.support_design())
            # return (parts_frame_blades)
            # return (operations.unite(big_block_rotate, cylinder_transversal))
            # return (operations.subtract(big_block_rotate, cylinder_transversal))

    def gen_one_col(self, collimator_Nosupport=True):
        pyr = self.solid_pyramid()

        big_cylinder = shapes.cylinder(radius='%s *mm' % (self.outer_radius),
                                       height='%s *mm' % (self.max_coll_height_detector * 10))

        big_box=self.generate_box_toCut_big_end()

        outside_sphere = shapes.sphere(radius='%s *mm' % self.outer_radius)


        channels=self.generate_collimator_channels()
        channels_border=self.generate_channels_border()

        conical_colli = operations.intersect(channels, pyr)

        conical_channels_border=operations.intersect(channels_border, pyr)


        cutoff_cylinder = shapes.cylinder(radius='%s *mm' % (self.inner_radius),
                                          height='%s *mm' % (self.max_coll_height_detector * 90.))

        blade_cutoff_cylinder = shapes.cylinder(radius='%s *mm' % (self.blade_dist_fr_sample_center),
                                          height='%s *mm' % (self.max_coll_height_detector * 10))

        # return (operations.subtract(conical_channels_border, cutoff_cylinder))

        open_collimator=operations.intersect(operations.subtract(conical_channels_border, cutoff_cylinder), big_box)



        collimator_with_blades = operations.intersect(operations.subtract(conical_colli, blade_cutoff_cylinder), big_box)


        collimator=operations.unite(open_collimator, collimator_with_blades)



        scale_pyr = 1.1
        pyr_ht = (self.horizontal_arc_length_detector / np.deg2rad(self.horizontal_acceptance_angle)) * scale_pyr

        thickness = (self.max_coll_height_detector + 1 * self.wall_thickness) * scale_pyr
        height = (self.horizontal_arc_length_detector / np.deg2rad(self.horizontal_acceptance_angle)) * scale_pyr
        width = (self.max_coll_width_detector + 1 * self.wall_thickness) * scale_pyr

        # pyr_ht = self.outer_radius * np.cos(np.deg2rad(self.horizontal_acceptance_angle/2.)) * scale_pyr
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


        support_top=operations.intersect(operations.subtract(self.support(), pyr_lateral), pyr_depth)



        # support_top =operations.subtract(self.support(), pyr_lateral)

        support_bottom=operations.rotate(operations.rotate(support_top, transversal=1, angle='%s *degree' %(-180)), vertical=1, angle='%s *degree' %180)


        supports=operations.subtract(operations.unite(support_top, support_bottom), cutoff_cylinder)

        if collimator_Nosupport is True:
            return(collimator)
        else:
            return(operations.unite(collimator,supports))
        # return (collimator)
        # return(self.support())
        # return (operations.unite(self.solid_pyramid(), support))

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


