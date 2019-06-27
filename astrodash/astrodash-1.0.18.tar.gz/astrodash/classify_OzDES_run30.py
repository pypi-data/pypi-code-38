import os
import subprocess
import astrodash

directoryPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates/run30/')

allFilePaths = []
for dirpath, dirnames, filenames in os.walk(directoryPath):
    for filename in [f for f in filenames if f.endswith(".dat")]:
        allFilePaths.append(os.path.join(dirpath, filename))

run30 = [('DES17E2cc', 0.149),
         ('DES17C3de', 0.107),
         ('DES17C3eg', 0.117),
         ('DES17X3az', 0.56),
         ('DES17X3bd', 0.141),
         ('DES17X3ca', 0.198),
         ('DES17X3cb', 0.317),
         ('DES17X3ct', 0.206),
         ('DES17E2a', 0.295),
         ('DES17E2b', 0.227),
         ('DES17E2aq', 0.352),
         ('DES17E2ar', 0.513),
         ('DES17E2bw', 0.147),
         ('DES17E2bx', 0.272),
         ('DES17E1by', 0.287),
         ('DES17E2ce', 0.269),
         ('DES17E2ci', 0.127),

         ('DES17E2f', 0.586),
         ('DES17E2ay', 0.186),
         ('DES17E1bp', 0.46),
         ('DES17E1ck', 0.221),
         ('DES17C3ef', 0.161),
         ('DES17E1by', 0.287),
         ('DES17C3ed', 0.354),
         ]

names = [i[0] for i in run30]
knownRedshifts = [i[1] for i in run30]

allFilePaths.reverse()
run30 = []

for i in range(len(names)):
    for filePath in allFilePaths:
        if names[i] == filePath.split('/')[-1].split('_')[0]:
            run30.append((filePath, knownRedshifts[i]))
            break

filenames = [i[0] for i in run30]
knownRedshifts = [i[1] for i in run30]

classification = astrodash.Classify(filenames, knownRedshifts, classifyHost=False, rlapScores=True, smooth=6)
bestFits, redshifts, bestTypes, rejectionLabels, reliableFlags, redshiftErrs = classification.list_best_matches(n=5, saveFilename='DASH_matches_run30_new.txt')
classification.plot_with_gui(indexToPlot=22)
