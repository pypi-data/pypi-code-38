import periodictable as pt

"""

Blichert-Toft J. and Albarède F. (1997).
The Lu-Hf isotope geochemistry of chondrites
and the evolution of the mantle-crust system.
Earth and Planetary Science Letters 148, 243–258.

Jonathan Patchett P. (1983).
Hafnium isotope results from mid-ocean ridges and Kerguelen.
Lithos 16, 47–51.

Jonathan Patchett P., Kouvo O., Hedge C. E. and Tatsumoto M. (1982).
Evolution of continental crust and mantle heterogeneity:
Evidence from Hf isotopes.
Contr. Mineral. and Petrol. 78, 279–297.

Patchett P. J. and Tatsumoto M. (1981).
A routine high-precision method for Lu-Hf isotope geochemistry and chronology.
Contr. Mineral. and Petrol. 75, 263–267.

Patchett P. J. and Tatsumoto M. (1980).
Hafnium isotope variations in oceanic basalts.
Geophysical Research Letters 7, 1077–1080.

"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def delta(ratio, reference=1.0):
    return ((ratio / reference) - 1.0) * 1000

def epsilon(ratio, reference=1.0):
    return ((ratio / reference) - 1.0) * 10000

def delta2ratio(ratio, reference=1.):
    return ((ratio / 1000) + 1.) * reference

def epsilon2ratio(ratio, reference=1.):
    return ((ratio / 10000) + 1.) * reference

delta(18.0001, reference=18.01)

epsilon2ratio(epsilon(18.0001, reference=18.01), reference=18.01)


df = pd.read_hdf(Path("C:/Github/agu2018/agu2018/data/8class/8class_aggregation.h5"))

# 87Sr86Sr, 143Nd144Nd, 206Pb204Pb, 207Pb204Pb, 208Pb204Pb, 176Hf177Hf
# some of the hafnium data is too high - swapped out Nd values? here Tamura 143Nd144Nd is repeated twice
 # https://academic.oup.com/petrology/article/52/6/1143/1479418#81990700f
df.loc[df.loc[:, '176Hf177Hf'] > 0.5,  ['176Hf177Hf',  '143Nd144Nd']]
df = df.loc[(df.loc[:, '176Hf177Hf'] < 0.5) | (pd.isnull(df.loc[:, '176Hf177Hf'])),  :]

df.loc[df.loc[:, '143Nd144Nd'] > 0.515, :].index
oibdf =  pd.read_hdf(Path("C:/Github/agu2018/agu2018/data/8class/OI/_OI.h5"))
df.loc[(df.loc[:, '143Nd144Nd'] > 0.515) & (df.Srcidx == 'OI') , :]
oibdf.loc[df.loc[(df.loc[:, '143Nd144Nd'] > 0.515) & (df.Srcidx == 'OI') , :].index, :]
(~pd.isnull(oibdf.Uniqueid)).all()
(~pd.isnull(df.loc[:, ['Lu', 'Hf', '176Hf177Hf']]).any(axis=1)).sum()

df.loc[:, '176Hf177Hf'].apply(lambda x: epsilon(x, reference=0.28286)).max()
# %% --
df.columns.to_list()
fig, ax = plt.subplots(1)
#ax.set_xscale("log")
#ax.set_yscale("log")
cs = df.loc[:, '176Hf177Hf'].apply(lambda x: epsilon(x, reference=0.28286))
cs.min()
cs.max()

ax.scatter(df.loc[:, '143Nd144Nd'], df.loc[:, "176Hf177Hf"], c = cs, cmap='viridis')

# %% --

lmbdaSm147Nd143 = 6.54 * 10 ** -12  # y-1
lmbdaLu176Hf176 = 1.94 * 10 ** -11  # y-1


def epsilon_Hf(initialHf176Hf177=0.279, initialHf176Hf177CHUR=0.28286):

    return ((initialHf176Hf177 / initialHf176Hf177CHUR) - 1) * 10 ** 4


epsilon_Hf()
