from os import system
from os import path

def makeVivadoProject(projectName='myProject',fpgaPart="xc7z020clg484-1"):
    system("Vivado -mode tcl -source "+path.join(path.dirname(__file__),'db/vivadoScript.tcl')+" -tclargs "+fpgaPart)
    f=open("zynet.tcl","a")
    f.write("\nexit") #Vivado doesn't add exit command to the end of the script
    f.close()
    system("Vivado -mode tcl -source zynet.tcl -tclargs --project_name "+projectName)