
def plot_gvalues(sp, line=None):
    import matplotlib.pyplot as plt

    # Load the g-value table
    dd = (os.environ['ModelBasePath'] if 'ModelBasePath' in os.environ
            else '/Users/mburger/Work/Research/NeutralCloudModel/master/')
    gfile = open(dd + 'Data/AtomicData/g-values/gval_table.pkl', 'rb')
    gval_table = pickle.load(gfile)
    gfile.close()

    a = 1.*u.au
    gval_temp = gval_table[gval_table['species'] == sp]
    waves = list(set(gval_temp['wavelength']))
    gval = (gval_temp[gval_temp['wavelength'] == line] if line in waves
            else gval_temp)

    waves = list(set(gval['wavelength']))

    for w in waves:
        gg = gval[gval['wavelength'] == w]
        g = gg['g'] * gg['refpt']**2 / a**2
        plt.plot(gg['velocity'], g)

    plt.show()
