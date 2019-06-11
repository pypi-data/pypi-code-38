import os
from .coloring import *

ROS_DIR = "/opt/ros/"


def get_ros_setup():

    global ROS_DIR
    
    if not os.path.isdir(ROS_DIR):
        return ROS_DIR,False

    dirs = [os.path.join(ROS_DIR, o) for o in os.listdir(ROS_DIR)
            if os.path.isdir(os.path.join(ROS_DIR,o))]

    for subdir in dirs:

        full_path = subdir+os.sep+"setup.bash"

        if os.path.isfile(full_path):
            return full_path,True

    return ROS_DIR,False


_CATKIN_ALREADY_ADDED = False

def get_catkin_make_command( workspace_path,
                             package_name,
                             package_path,
                             one_processor=False,
                             install=False,
                             log=True):

    if log:
        print("\tusing catkin for compiling: "+green(package_name))
    
    workspace_path = os.path.abspath(workspace_path+os.sep+"workspace"+os.sep)
    
    # catkin_cmake is required only once for
    # the whole workspace
    global _CATKIN_ALREADY_ADDED
    if _CATKIN_ALREADY_ADDED:
        return "\n# ("+package_name+": catkin_make)\n"
    _CATKIN_ALREADY_ADDED = True
    
    s = ["# calling catkin_make\n"]
    
    s.append("cd "+workspace_path)

    install_setup = workspace_path+"install"+os.sep+"setup.bash"
    install_setup_found = True
    if not os.path.isfile(install_setup):
        install_setup_found = False

            
    devel_setup = workspace_path+"devel"+os.sep+"setup.bash"
    devel_setup_found = True
    if not os.path.isfile(devel_setup):
        devel_setup_found = False
        
    ros_setup,ros_setup_found = get_ros_setup()

    if not any([setup for setup in [install_setup_found,devel_setup_found,ros_setup_found]]):
        global ROS_DIR
        error = ["failed to find ROS setup.bash. Searched in :"]
        error.append("\t"+install_setup)
        error.append("\t"+devel_setup)
        error.append("\t"+ros_setup)
        raise Exception("\n".join(error))
    
    for found,setup in zip([install_setup_found,devel_setup_found,ros_setup_found],
                           [install_setup,devel_setup,ros_setup]):

        if found :
            s.append(". "+setup)

            if log:
                print("\tcatkin make : sourcing "+green(setup))
            
            break

    j1_ = ""
    if one_processor: j1_ = " -j1"

    install_ = ""
    if install : install_ = " install"
    
    s.append("catkin_make"+j1_+install_)

    return "\n".join(s)
