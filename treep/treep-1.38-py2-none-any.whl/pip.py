from .coloring import *


def get_pip_command( workspace_path,
                     package_name,
                     package_path,
                     log=True,
                     pip_executable="pip",
                     user=True ):

    if log:
        print("\tusing pip to compile: "+green(package_name))
    
    s = ["# calling pip for "+str(package_name)+"\n"]

    s.append("cd "+package_path)

    user_ = ""
    if user:
        user_ = " --user"
    
    s.append(pip_executable+" . install "+user_)

    return "\n".join(s)
    
