# import statements
import subprocess
import os
import glob
import warnings
import time

# warnings
warnings.simplefilter('ignore')

# define options
cont = True
counter = 1
optionsList = []

while cont:
    option = input(f"Enter option {counter} > ")
    optionsList.append(option)

    print("Add more options?")
    query = input("Y/N ")
    if query.lower() == 'y':
        counter += 1
        continue
    elif query.lower() == 'n':
        cont = False
    else:
        print("Enter either 'Y' or 'N'")
optionsList.append("Misc")

# generate dictionary for options
optionsDict = {str(i): option for i, option in enumerate(optionsList)}

# create directories for each option
for option in optionsList:
    path = os.path.join("..", option)
    if os.path.exists(path) == False:
        os.mkdir(path)

# grab images
types = ('*.png', '*.jpg')  # the tuple of file types
files_grabbed = []
for files in types:
    files_grabbed.extend(glob.glob(f"../{files}"))
files_grabbed = [file[3:] for file in files_grabbed]
print(files_grabbed)

# display image and sort
for image in files_grabbed:
    currentDir = os.getcwd()
    parentPath = currentDir[:currentDir.rfind("/")]
    path = os.path.join(parentPath,image)
    processString = f"python imviewer.py \"{path}\""
    print(f"process string is {processString}")
    p = subprocess.Popen(processString, shell=True)

    time.sleep(1)
    print("Options:")
    for i, option in enumerate(optionsList):
        print(f"{i+1}. {option}")
    folder = str(int(input("Enter option > ")) - 1)
    rename = input("Type new name to rename file, else press enter > ")
    if rename == "":
        for key in optionsDict.keys():
            if folder == key:
                os.rename(os.path.join(parentPath,image), os.path.join(
                    parentPath, optionsDict[key], image))
    else:

        for key in optionsDict.keys():
            if folder == key:
                os.rename(os.path.join(parentPath,image), os.path.join(
                    parentPath, optionsDict[key], f"{rename}{image[image.rfind('.'):]}"))
    p.kill()
