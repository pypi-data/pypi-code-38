import astrodash
import os


directory = '/Users/danmuth/PycharmProjects/DASH/templates/redesgeminireductions/'


names = ["des17x3rg", "des17x1kw", "des17x3b", "des17x3t", "des17c3e", "des17c3w", "des17c1azd", "des17x2blx",
        "des17s2bzl", "des17s1bqr", "des17c3bzw", "des17x1cu"]

redshifts = [0.280, 0.462, 0.67, 0.49, 0.260, 0.675, 0.341, 0.344, 0.651, 0.649, 0.768, 0.83]

filenames = os.listdir(directory)


fnames = []
z = []
for i, name in enumerate(names):
    for filename in filenames:
        if name in filename:
            fnames.append(directory + filename)
            z.append(redshifts[i])

classification = astrodash.Classify(fnames, z, classifyHost=False, smooth=5, knownZ=True)
bestFits, redshifts, bestTypes, rlapFlag, matchesFlag, redshiftErrs = classification.list_best_matches(n=5)

print(bestFits)
f = open('gemini_classifications.txt', 'w')
for i in range(len(fnames)):
    f.write("%s   z=%s     %s      %s     %s\n %s\n\n" % (fnames[i].replace(directory, ''), z[i], bestTypes[i], matchesFlag[i], rlapFlag[i], bestFits[i]))
f.close()
print("Finished classifying %d spectra!" % len(fnames))


print("{0:17} | {1:5} | {2:8} | {3:10} | {4:6} | {5:10}".format("Name", "  z  ", "DASH_Fit", "  Age ", "Prob.", "Flag"))
for i in range(len(fnames)):
    print("{0:17} | {1:5} | {2:8} | {3:10} | {4:6} | {5:10}".format(
        fnames[i].replace(directory, ''), z[i],
        bestTypes[i][0], bestTypes[i][1], bestTypes[i][2], matchesFlag[i].replace(' matches', '')))

# PLOT SPECTRUM ON GUI
classification.plot_with_gui(indexToPlot=0)
