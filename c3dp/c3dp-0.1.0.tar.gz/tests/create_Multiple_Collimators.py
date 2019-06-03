import os, sys
from instrument.geometry.pml import weave
from instrument.geometry import  operations

thisdir = os.path.abspath(os.path.dirname(__file__))
libpath = os.path.join(thisdir, '../c3dp')
if not libpath in sys.path:
    sys.path.insert(0, libpath)

path = os.path.expanduser('/home/fi0/dev/scadgen/SCADGen/')
sys.path.append(path)
import SCADGen.Parser

# from collimator_fun_ori_constant_thickness_2_support_mod_3 import Collimator_geom
from create_collimator_geometry import Collimator_geom

from clampcell_geo import Clampcell



clampcell=Clampcell(total_height=True)
outer_body=clampcell.outer_body()
inner_sleeve=clampcell.inner_sleeve()
sample=clampcell.sample()

sample_assemblyCad=operations.unite(operations.unite(outer_body, sample), inner_sleeve)

# detector_angles=[-45,-135]

###########################################################
#############################################################333
###################################0, 0.01, 1#######################3

scad_flag = True  ########CHANGE CAD FLAG HERE

if scad_flag is True:
    samplepath = os.path.join(thisdir, '../figures')
else:
    samplepath = os.path.join(thisdir, '../sample')


for coll_length in [380.]: #100, 230,380


    channel_length=380. #32, 17

    min_channel_wall_thickness=1.

    coll = Collimator_geom()
    coll.set_constraints(max_coll_height_detector=230., max_coll_width_detector=230.,
                        min_channel_wall_thickness=min_channel_wall_thickness,
                        max_coll_length=coll_length, min_channel_size=3.,
                         truss_base_thickness=30., trass_final_height_factor=0.66,touch_to_halfcircle=6 ,SNAP_acceptance_angle=False)


    coll.set_parameters(number_channels=3.,channel_length =channel_length)

    filename = 'coll_geometry_{coll_length}_{coll_height}_{coll_width}_{channel_length}_{wall_thickness}.xml'.\
        format(coll_length=coll_length, coll_height=coll.max_coll_height_detector, coll_width=coll.max_coll_height_detector, channel_length=channel_length, wall_thickness=min_channel_wall_thickness)

    outputfile = os.path.join(samplepath, filename)


    supports=coll.support()

    truss=coll.support_design()

    coli = coll.gen_one_col(collimator_Nosupport=False)

    collimator=coll.gen_collimators_xml(multiple_collimator=False, scad_flag=scad_flag,detector_angles=[0], collimator_Nosupport=False, coll_file=outputfile)



both=operations.unite(coli,sample_assemblyCad)
# both= truss
# both=supports
truss=truss

with open (os.path.join(thisdir, '../figures/truss.xml'),'wt') as file_h:
    weave(truss,file_h, print_docs = False)
