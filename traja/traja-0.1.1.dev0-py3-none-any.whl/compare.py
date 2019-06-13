import glob
import pickle

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sklearn import datasets
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis


import traja

files = sorted(glob.glob("/Users/justinshenk/neurodata/data/raw_centroids_rev2/*.csv"))
cages = ["E1", "E2", "E4", "F4", "F6"]

xlim = -0.058, 0.058
ylim = -0.119, 0.119

path_grids = {}

for cage in cages:
    path_grids[cage] = {}
    path_grids[cage]["day"] = []
    path_grids[cage]["night"] = []
    cagefiles = [file for file in files if cage in file]
    for idx, file in enumerate(cagefiles):
        if idx % 10 != 0:
            continue
        df = traja.read_file(file, xlim=xlim, ylim=ylim)
        day, _ = df.traja.day().traja.trip_grid(hist_only=True, log=True)
        night, _ = df.traja.night().traja.trip_grid(hist_only=True, log=True)
        path_grids[cage]["day"].append((idx, day))
        path_grids[cage]["night"].append((idx, night))
        print(f"Completed {cage}, index {idx}")
    print(f"Completed {cage}")

# path_grids_dest = "path_grids.pkl"
# pickle.dump(path_grids, open(path_grids_dest, "wb"))

X = []
target_names = []
path_grids = pickle.load(open("traja/path_grids.pkl", "rb"))
cages = path_grids.keys()
for cage in cages:
    for period in ("day", "night"):
        grids = path_grids[cage][period]
        for idx, grid in grids:
            X.append(grid.flatten())
            target_names.append(f"{cage}-{period}-{idx}")

days_from_surgery = set([int(x.split("-")[-1]) for x in target_names])

X = np.array(X)
pca = PCA(n_components=2)
X_r = pca.fit(X).transform(X)

# Group by period
plt.figure()
lw = 2
colors = ["navy", "darkorange"]

# for color, i, target_name in zip(colors, [0, 1], target_names):
day_idx = np.array(["day" in x for x in target_names])

plt.scatter(
    X_r[day_idx, 0], X_r[day_idx, 1], color=f"C0", alpha=0.8, lw=lw, label="Day"
)
plt.scatter(
    X_r[~day_idx, 0], X_r[~day_idx, 1], color=f"C1", alpha=0.8, lw=lw, label="Night"
)
plt.legend(loc="best", shadow=False, scatterpoints=1)
plt.title("PCA of Mouse trajectory dataset")
plt.show()
