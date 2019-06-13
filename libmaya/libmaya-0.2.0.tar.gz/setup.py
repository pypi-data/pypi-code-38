from setuptools import setup, find_packages  
from maya.exp_runner import maya
  
setup(  
    name = "libmaya",  
    version = maya.__version__,  
    packages = find_packages(),  
  
    description = "maya system",  
    long_description = "Maya, the command running system.",  
    author = "hudson_huang",  
    author_email = "l_a@live.cn",  
  
    license = "MIT",  
    keywords = ("command", "maya"),  
    platforms = "Independant",  
    url = "https://github.com/HudsonHuang/Maya/",
    entry_points = {
        'console_scripts': [
            'maya = maya.exp_runner.maya:parse_args',
        ]
    }
)
