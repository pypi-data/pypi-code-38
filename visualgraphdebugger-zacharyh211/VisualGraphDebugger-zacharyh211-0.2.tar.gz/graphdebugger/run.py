
from graphdebugger import DebuggerUI
import sys
import argparse
from PyQt5.QtWidgets import QApplication



def main():
	parser = argparse.ArgumentParser(description='Open the Graph Visual Debugger GUI.')
	parser.add_argument('-g','--graphfile',nargs='?',help='Graph JSON file.')
	parser.add_argument('-s','--scriptfile',nargs='?',help='Script py file.')

	args = parser.parse_args()
	app = QApplication(sys.argv)
	e = DebuggerUI.GraphApp(graph=args.graphfile, script=args.scriptfile)
	e.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()