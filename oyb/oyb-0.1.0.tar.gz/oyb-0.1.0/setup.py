"""Forwards call to setuptools.setup() after parsing:
   * name from package folder
   * long description from README.rst
   * packages from setuptools.find_packages()
   * dependencies from requirements.txt
   * remaining properties from package-level package.json
"""

import os
import json
from setuptools import setup, find_packages

def main():
    """
    """
    buildPath, _ = os.path.split(os.path.abspath(__file__))
    packPath, _ = os.path.split(buildPath)
    _, packName = os.path.split(packPath)
    currDir = os.getcwd()
    os.chdir(buildPath)
    try:
        settingsPath = packPath + "/package.json"
        readmePath = packPath + "/README.rst"
        reqsPath = packPath + "/requirements.txt"
        with open(settingsPath, 'r') as f:
            settings = json.load(f)
        with open(readmePath, 'r') as f:
            settings["long_description"] = f.read()
        with open(reqsPath, 'r') as f:
            settings["install_requires"] = f.readlines()
        settings["name"] = packName
        setup(**settings)
    except Exception as e:
        print("Error while building package:", e)
    os.chdir(currDir)

if __name__ == "__main__":
    main()
