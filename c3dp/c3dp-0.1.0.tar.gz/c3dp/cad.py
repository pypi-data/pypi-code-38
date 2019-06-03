import numpy as np
import sys, os, glob

# path = os.path.expanduser('/home/fi0/dev/SNAP/SNAP_2018_package/xmlCad/SCADGen/')
path = os.path.expanduser('/home/fi0/dev/scadgen/SCADGen/')
print path
sys.path.append(path)
# sys.path.append(path1)

import SCADGen.Parser

# for file in glob.glob("*.xml"):
#     print(file)
#     p=SCADGen.Parser.Parser(file)
#     p.createSCAD()
#     test = p.rootelems[0]

p=SCADGen.Parser.Parser('collimator_support_ed2.xml')
p.createSCAD()
test = p.rootelems[0]
# print (test )
#
# p=SCADGen.Parser.Parser('Oripyramids.xml')
# p.createSCAD()
# test = p.rootelems[0]
# # print (test )
#
# p=SCADGen.Parser.Parser('collimator.xml')
# p.createSCAD()
# test = p.rootelems[0]
# #
# #
# # p=SCADGen.Parser.Parser('sphere.xml')
# # p.createSCAD()
# # test1 = p.rootelems[0]
# # print()
#
# p=SCADGen.Parser.Parser('sphere.xml')
# p.createSCAD()
# test1 = p.rootelems[0]
# # # print()
#
# p=SCADGen.Parser.Parser('coll_block.xml')
# p.createSCAD()
# test1 = p.rootelems[0]