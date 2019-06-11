import os
import subprocess
import shutil


def extractASM(text, filename):
    newText = ""
    lines = text.split("\n")
    assemblyStart = False
    for l in lines:
        if assemblyStart:
            if (filename not in l) and ("auxdata: 0x" not in l):
                newText += (l + "\n")
        elif l.find("EVM assembly:") == 0:
            assemblyStart = True
    return newText


def internalToPublic(filename):
    changedCode = []
    with open(filename, 'r') as inCodeFile:
        for line in inCodeFile:
            changedCode = line.replace(" internal ", " public ")
    with open(filename, 'w') as outCodeFile:
        for line in changedCode:
            outCodeFile.write(line)


def handler(tmpMutantName, mutant, sourceFile, uniqueMutants):
    outName = ".um.out." + str(os.getpid()) + ".asm"
    if len(uniqueMutants) == 0:
        shutil.copy(tmpMutantName, tmpMutantName + ".backup." + str(os.getpid()))
        shutil.copy(sourceFile, tmpMutantName)
        internalToPublic(tmpMutantName)
        with open(outName, 'w') as file:
            r = subprocess.call(
                ["solc", tmpMutantName, "--asm", "--optimize"], stdout=file, stderr=file)
        with open(outName, 'r') as file:
            uniqueMutants[extractASM(file.read(), tmpMutantName)] = 1
        shutil.copy(tmpMutantName + ".backup." + str(os.getpid()), tmpMutantName)
    shutil.copy(tmpMutantName, tmpMutantName + ".backup." + str(os.getpid()))
    internalToPublic(tmpMutantName)
    with open(outName, 'w') as file:
        r = subprocess.call(["solc", tmpMutantName, "--asm",
                             "--optimize"], stdout=file, stderr=file)
    shutil.copy(tmpMutantName + ".backup." + str(os.getpid()), tmpMutantName)
    if r == 0:
        with open(outName, 'r') as file:
            code = extractASM(file.read(), tmpMutantName)
        if code in uniqueMutants:
            uniqueMutants[code] += 1
            return "REDUNDANT"
        else:
            uniqueMutants[code] = 1
            return "VALID"
    else:
        return "INVALID"
