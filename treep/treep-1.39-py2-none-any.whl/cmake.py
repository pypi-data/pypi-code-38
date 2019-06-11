import multiprocessing,os
from .coloring import *


def get_cmake_command( workspace_path,
                       package_name,
                       package_path,
                       log=True,
                       clean=True,
                       multiprocess=True,
                       cmake_suffix="" ):

    if log:
        print("\tusing cmake for compiling: "+green(package_name))
    
    s = ["# calling cmake for "+str(package_name)+"\n"]

    s.append("cd "+package_path)

    build_folder = package_path+os.sep+"build"
    
    if clean:
        if os.path.isdir(build_folder):
            s.append("rm -rf build")
            s.append("mkdir build")

    if not os.path.isdir(build_folder):
        s.append("mkdir build")
        
    s.append("cd build")
    s.append("cmake .. "+cmake_suffix)

    j=""
    if multiprocess:
        cpus = multiprocessing.cpu_count()
        cpus = cpus-1
        if cpus<=0 : cpus = 1
        j = " -j"+str(cpus)

    s.append("make "+j)

    s.append("sudo make install")

    return "\n".join(s)
