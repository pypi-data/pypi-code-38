from scipy.io import readsav


class IDLout:
    def __init__(self, filename):
        idl = readsav(filename)
        idlout = idl['output']

        self.x = idlout['x'][0]
        self.y = idlout['y'][0]
        self.z = idlout['z'][0]
        self.vx = idlout['vx'][0]
        self.vy = idlout['vy'][0]
        self.vz = idlout['vz'][0]
        self.frac = idlout['frac'][0]
        self.time = idlout['time'][0]
        self.index = idlout['index'][0]

        index = sorted(list(set(idlout['index'][0])))
        x0 = [idlout['x0'][0][idlout['index'][0] == i][0] for i in index]
        y0 = [idlout['z0'][0][idlout['index'][0] == i][0] for i in index]
        z0 = [idlout['y0'][0][idlout['index'][0] == i][0] for i in index]
        vx0 = [idlout['vx0'][0][idlout['index'][0] == i][0] for i in index]
        vy0 = [idlout['vy0'][0][idlout['index'][0] == i][0] for i in index]
        vz0 = [idlout['vz0'][0][idlout['index'][0] == i][0] for i in index]

        self.x0 = np.array(x0)
        self.y0 = np.array(y0)
        self.z0 = np.array(z0)
        self.vx0 = np.array(vx0)
        self.vy0 = np.array(vy0)
        self.vz0 = np.array(vz0)
        del idlout
