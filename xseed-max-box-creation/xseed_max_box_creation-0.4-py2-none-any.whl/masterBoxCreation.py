import os
import subprocess as sp
import installCommonPackagesTools as installCommon
import prerequisiteChecks as checks
import packageCleanUp as cleanup
import configureMasterBox as configure
import dockerCompose as dc

#Code to accept sudo password from user
sudo_password  = input("Enter sudo password:\n")
miniCampus = "xaidjmd"


#1. Install common packages and common tools
installCommon.installCommonPackagesTools(sudo_password)

#2. Perform Prerequisite Checks
checks.checks()

# 3. Configure configureMasterBox
configure.configure(sudo_password)

#4. System cleanUp
cleanup.cleanup()

#5. Updating dockerCompose
username =  input("Enter docker login username:\n")
password =  input("Enter docker login password:\n")
dc.configureDocker(miniCampus, username, password)
