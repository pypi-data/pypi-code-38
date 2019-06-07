import sys
from PyTrinamic.connections.ConnectionManager import ConnectionManager

connectionManager = ConnectionManager(sys.argv, debug=False)

myInterface = connectionManager.connect()
print(myInterface.getVersionString())


exit(0)
