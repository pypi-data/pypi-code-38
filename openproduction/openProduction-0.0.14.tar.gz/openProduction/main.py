import os
import argparse
import sys
import log
from openProduction.common import misc

logger = log.initLogger()


my_path = os.path.split(os.path.abspath(__file__))[0]
#sys.path.append(os.path.join(my_path, "common"))

parser = argparse.ArgumentParser(description='openProduction')
parser.add_argument('--verbose', '-v', action='store_true')
parser.add_argument('--headless', action='store_true', help='run without GUI')
parser.add_argument('--workspace', type=str, default=misc.getDefaultAppFolder(), help='workspace directory, defauts to %s'%misc.getDefaultAppFolder())
parser.add_argument('--stationCLI', action='store_true', default=False)

args = parser.parse_args()

if args.headless == False:
    from PyQt5 import QtWidgets, QtGui
    from openProduction.UI import mainUI
    sys.argv += ['--style', 'material']
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(":/icons/openProductionNurLogo-transparent.png"))
    ui = mainUI.UIRunner(args.workspace)
    app.exec_()
    
    

sys.exit(0)