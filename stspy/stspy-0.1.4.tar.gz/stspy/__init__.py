import numpy as np
import struct

class STM:
    def __init__(self, DAC_Voltage_Range = 20000.0):
        self.DAC_Voltage_Range = DAC_Voltage_Range #in mV
    def __str__(self):
        ret = 'DAC_Voltage_Range: %.1f mV' %self.DAC_Voltage_Range
        return ret

class spectra:
    def __init__(self, V, I, dIdV):
        self.label = None
        #data should include V, z, I, and dIdV in that order        
        #Assign values to spectra object (default values if you want to create a spectra object)
        self.ZPiezoconst = 1.0
        self.LockinRC = 0.0
        self.Speclength = 0
        self.VertSpecBack = 0
        self.LockinAmpl = 0
        self.Current = 1
        self.hyst = 0
        self.x = 0
        self.y = 0
        self.Length_x = 0
        self.Length_y = 0
        self.z = np.ones(len(V))
        self.V = V
        self.I = I
        self.dIdV = dIdV
        #Number of data points, needed for averaging and hysteresis correction
        self.N = len(V)

    #use command print(spectra_object) to print out a few relevant parameters
    def __str__(self):
        ret = 'label: ' + self.label +'\n'
        ret += 'data points: %d\n' %self.N
        ret += 'VertSpecBack: %d\n' %self.VertSpecBack
        ret += 'LockinAmpl: %.1f mV\n' %self.LockinAmpl
        ret += 'Setpoint: %.1e A\n' %self.Current
        ret += 'Hystersis Correction: %d\n' %self.hyst
        ret += 'x, y Coordinates: %.2f, %.2f Angstroms (relative to tip position)' %(self.x, self.y)
        return ret

    def average(self, hyst_cor = True):
    # this function averages the spectra together, and edits the values of sepctra_object.V, .z, .I, and .dIdV
    #not if you want to get the original values after this, just call e.g. epctra_object.I0
        
        N = self.N 
        if self.VertSpecBack + 1 <= 1:
            raise Exception('VertSpecBack is %d, which means no averaging or hystersis correction is possible.' %n)
        else:
            while self.N % (self.VertSpecBack + 1) != 0:
                self.V = delete(self.V, len(self.V))
                self.I = delete(self.I, len(self.I))
                self.dIdV = delete(self.dIdV, len(self.dIdV))
                self.z = delete(self.z, len(self.z))
                self.N = len(self.V)

        
        n = self.N/(self.VertSpecBack+1)
        V = self.V[0:n]
        dIdV = np.zeros(n)
        I = np.zeros(n)
        z = np.zeros(n)

        if hyst_cor == True:
            hyst = self.hyst
            if hyst % 2 != 0:
                hyst += 1
        else:
            hyst = 0


        foo = np.empty(n)
        for i in range(self.VertSpecBack+1):
            if i%2 == 0:

                j, k = hyst/2 + i*n, n * (i+1)
                foo[0:-hyst/2] = self.I[j:k]
                foo[-hyst/2:] = self.I[k-1]
                I += foo

                foo[0:-hyst/2] = self.dIdV[j:k]
                foo[-hyst/2:] = self.dIdV[k-1]
                dIdV += foo

                foo[0:-hyst/2] = self.z[j:k]
                foo[-hyst/2:] = self.z[k-1]
                z += foo
            else:
                j, k = i*n + hyst/2, (i + 1)*n
                
                foo[0:-hyst/2] = self.I[j:k]
                foo[-hyst/2:] = self.I[k-1]
                foo = foo[::-1]
                I += foo

                foo[0:-hyst/2] = self.dIdV[j:k]
                foo[-hyst/2:] = self.dIdV[k-1]
                foo = foo[::-1]
                dIdV += foo

                foo[0:-hyst/2] = self.z[j:k]
                foo[-hyst/2:] = self.z[k-1]
                foo = foo[::-1]
                z += foo

        self.V = V
        self.I = I/(self.VertSpecBack + 1)
        self.dIdV = dIdV/(self.VertSpecBack + 1)
        self.z = z/(self.VertSpecBack + 1)
        
    #normalize the spectra using an input value of kappa in Ang^-1
    def normalize(self, kappa):
        self.I = self.I * np.exp(-2 * kappa * self.z)
        self.dIdV = self.dIdV * np.exp(-2* kappa * self.z)

    
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def load_VERT_file(filename, stm = STM()):
     #find all the relevant parameters
    f = open(filename, 'r')
    for line in f:
        if "ParVERT32" in line:
            Version = '3.2' #STMAFM Software version
            LockinRC_factor = 7.989578/0.00251 #mutliplicative factor to get LockinRC param in Hz
            Current_index = 4 #column indexes for extracting current and dIdV
            dIdV_index = 5
        if "ParVERT30" in line:
            Version = '3.0'
            LockinRC_factor = 7960.
            Current_index = 3
            dIdV_index = 4
        if "ZPiezoconst" in line:
            ZPiezoconst = float(line[line.find('=')+1:-1])
        if "LockinRC" in line:
            LockinRC = float(line[line.find('=')+1:-1])
        if "Vertmandelay" in line:
            Vertmandelay = float(line[line.find('=')+1:-1])
        if "VertSpecBack" in line:
            VertSpecBack = int(line[line.find('=')+1:-1])
        if "LockinAmpl" in line:
            LockinAmpl = float(line[line.find('=')+1:-1]) #mV
        if "Current[A]" in line: #Old software version
            Current = float(line[line.find('=')+1:-1]) #Amps
        if "SetPoint" in line: #New software version
            Current = float(line[line.find('=')+1:-1]) #Amps
        if "DSP_Clock" in line:
            DSP_Clock = float(line[line.find('=')+1:-1]) #DSP Units to determine Speclength
        if "DAC-Type" in line:
            DAC_Type = float(line[line.find('=')+1:-4])
        if "Gainpreamp" in line:
            Gainpreamp = float(line[line.find('=')+1:-1])
        if "Length x[A]" in line:
            Length_x = float(line[line.find('=')+1:-1])
        if "Length y[A]" in line:
            Length_y = float(line[line.find('=')+1:-1])
    f.close()

    #data = np.loadtxt(filename, skiprows = stm.skiprows)
    EOF = file_len(filename)

    N = int(np.loadtxt(filename, skiprows = EOF - 1)[0]) + 1
    x = np.loadtxt(filename, skiprows = EOF - N - 1, max_rows = 1)[1]
    y = np.loadtxt(filename, skiprows = EOF - N - 1, max_rows = 1)[2]
    
    Speclength = Vertmandelay * N / DSP_Clock
    
    data = np.loadtxt(filename, skiprows = EOF-N)
                   
    z = data[:, 2] * ZPiezoconst/1000.0 # Angstroms
    V = data[:, 1] / 1000.0 #Volts
    I = data[:, Current_index] / 2**DAC_Type * stm.DAC_Voltage_Range / 10**Gainpreamp / 1e6#current in amps 
    dIdV = data[:, dIdV_index] / 2**DAC_Type * stm.DAC_Voltage_Range #conductance in meV

    ret = spectra(V, I, dIdV)
    
    label = filename[-19:-5]
    if 'L' in label or 'R' in label:
        label = filename[-25:-5]
    ret.label = label
    ret.z = z
    ret.ZPiezoconst = ZPiezoconst
    ret.LockinRC = LockinRC * LockinRC_factor #Hz
    ret.Speclength = Speclength
    ret.VertSpecBack = VertSpecBack
    ret.LockinAmpl = LockinAmpl
    ret.Current = Current
    ret.N = N
    ret.x = x * 10./2.**(20-1) * 40 * 10 #value in DAC units * Voltage range / 2^(bit count - 1 (account for positive vs negative)) * piezo constant * high voltage gain (hard coded for now)
    ret.y = y * 10./2**(20-1) * 40 * 10
    ret.Length_x = Length_x
    ret.Length_y = Length_y
    #hysteresis correction factor
    hyst = int(N/Speclength/LockinRC/LockinRC_factor/np.pi)
    ret.hyst = hyst
    return ret

class specgrid:
    def __init__(self, V, I, dIdV):
        self.label = None

        #data should include V, z, I, and dIdV in that order
        
        #Assign values to spectra object
        self.ZPiezoconst = 1.0
        self.LockinRC = 0.0
        self.Speclength = 0
        self.VertSpecBack = 0
        self.LockinAmpl = 0
        self.Current = 1

        self.hyst = 0

        self.z = np.ones(len(V))
        self.V = V
        
        self.I = I
        self.dIdV = dIdV
        
        #Number of data points, needed for averaging and hysteresis correction
        N = len(V)
        self.N = N

        self.nx, self.ny = I.shape[0], I.shape[1]

    def average(self, hyst_cor = True):

        N = self.N 
        if self.VertSpecBack + 1 <= 1:
            raise Exception('VertSpecBack is %d, which means no averaging or hystersis correction is possible.' %n)
        
        I = np.empty((self.nx, self.ny, self.N/(self.VertSpecBack + 1)))
        dIdV = np.empty((self.nx, self.ny, self.N/(self.VertSpecBack + 1)))
        for i in range(self.nx):
            for j in range(self.ny):
                spec = spectra(self.V, self.I[i, j, :], self.dIdV[i, j, :])
                spec.z = self.z
                spec.hyst = self.hyst
                spec.VertSpecBack = self.VertSpecBack
                spec.average(hyst_cor = hyst_cor)
                I[i, j, 0:len(spec.I)] = spec.I
                dIdV[i, j, 0:len(spec.dIdV)] = spec.dIdV
        self.z = spec.z
        self.V = spec.V
        self.I = I
        self.dIdV = dIdV

    def normalize(self, kappa):
        I = np.empty((self.nx, self.ny, self.N))
        dIdV = np.empty((self.nx, self.ny, self.N))
        for i in range(self.nx):
            for j in range(self.ny):
                spec = spectra(self.V, self.I[i, j, :], self.dIdV[i, j, :])
                spec.z = self.z
                spec.normalize(kappa)
                I[i, j, :] = spec.I
                dIdV[i, j, :] = spec.dIdV
        self.I = I
        self.dIdV = dIdV
        
    #use command print(spectra_object) to print out a few relevant parameters
    def __str__(self):
        ret = 'label: ' + self.label +'\n'
        ret += 'nx, ny: %d, %d\n' %(self.nx, self.ny)
        ret += 'data points: %d\n' %self.N
        ret += 'VertSpecBack: %d\n' %self.VertSpecBack
        ret += 'LockinAmpl: %.1f mV\n' %self.LockinAmpl
        ret += 'Setpoint: %.1e A\n' %self.Current
        ret += 'Hystersis Correction: %d' %self.hyst
        return ret

def read_item(content, loc, format_):
    size = struct.calcsize(format_)
    return struct.unpack(format_, content[loc:loc+size])[0]
        
def load_specgrid_file(filename, stm = STM()):
    #find all the relevant parameters
    f = open(filename + '.dat', 'r')
    for line in f:
        if "ParVERT32" in line:
            Version = '3.2' #STMAFM Software version
            LockinRC_factor = 7960. #mutliplicative factor to get LockinRC param in HzLockinRC_factor = 7960.
            Current_index = 5 #column indexes for extracting current and dIdV
            dIdV_index = 4
        if "ParVERT30" in line:
            Version = '3.0'
            LockinRC_factor = 7960.
            Current_index = 4
            dIdV_index = 3
        if "ZPiezoconst" in line:
            ZPiezoconst = float(line[line.find('=')+1:-1])
        if "LockinRC" in line:
            LockinRC = float(line[line.find('=')+1:-1])
        if "Vertmandelay" in line:
            Vertmandelay = float(line[line.find('=')+1:-1])
        if "VertSpecBack" in line:
            VertSpecBack = int(line[line.find('=')+1:-1])
        if "LockinAmpl" in line:
            LockinAmpl = float(line[line.find('=')+1:-1]) #mV
        if "Current[A]" in line:
            Current = float(line[line.find('=')+1:-1]) #Amps
        if "DSP_Clock" in line:
            DSP_Clock = float(line[line.find('=')+1:-1]) #DSP Units to determine Speclength
        if "DAC-Type" in line:
            DAC_Type = float(line[line.find('=')+1:-4])
        if "Gainpreamp" in line:
            Gainpreamp = float(line[line.find('=')+1:-1])
    f.close()

    with open(filename, mode='rb') as file: # b is important -> binary
        content = file.read()
    version = read_item(content, 0, 'i')    
    nx, ny = read_item(content, 4, 'i'), read_item(content, 8, 'i')
    dx, dy = read_item(content, 12, 'i'), read_item(content, 16, 'i')
    specxgrid, specygrid = read_item(content, 20, 'i'), read_item(content, 24, 'i')
    vertpoints = read_item(content, 28, 'i')
    vertmandelay = read_item(content, 32, 'i')
    vertmangain = read_item(content, 36, 'i')
    biasvoltage = read_item(content, 40, 'f')
    tunnelcurrent = read_item(content, 44, 'f')
    imagedatasize = read_item(content, 48, 'i')
    specgriddatasize = read_item(content, 52, 'i') 
    specgridchan = read_item(content, 56, 'i')
    specgridchannelselectval = read_item(content, 60, 'i')
    specgriddatasize64 = read_item(content, 64, 'q')
    if version >= 4:
        xstart, xend = read_item(content, 72, 'i'), read_item(content, 76, 'i')
        ystart, yend = read_item(content, 80, 'i'), read_item(content, 84, 'i')
    else:
        xstart, ystart = 1, 1
        xend = int(nx/specxgrid) + 1
        yend = int(ny/specygrid) + 1
    V = np.empty(vertpoints)
    z = np.empty(vertpoints)
    for i in range(vertpoints):
        V[i] = read_item(content, 1024 + (i*8), 'f')
        z[i] = read_item(content, 1028 + (i*8), 'f')
    
    current = np.empty((xend-xstart + 1, yend-ystart + 1, vertpoints))
    conductance = np.empty((xend-xstart + 1, yend-ystart + 1, vertpoints))
    n = 0
    for i in range(current.shape[0]):
        for j in range(current.shape[1]):
            I = np.empty(vertpoints)
            dIdV = np.empty(vertpoints)
            for k in range(vertpoints):
                I[k] = read_item(content, 1032 + n*vertpoints*8 + k*8, 'f')
                dIdV[k] = read_item(content, 1028 + n*vertpoints*8 + k*8, 'f')
            current[i, j, :] = I
            conductance[i, j, :] = dIdV
            n += 1

    current *= stm.DAC_Voltage_Range / 2**DAC_Type / 10**Gainpreamp /1e6 #current in amps
    conductance *= stm.DAC_Voltage_Range /2**DAC_Type #meV
    V /= 1000.0 #volts
    ret = specgrid(V, current, conductance)
    ret.z = z * ZPiezoconst/1000.0 #Angstroms

    Speclength = Vertmandelay * vertpoints / DSP_Clock
    
    ret.label = filename[-23:-9]
    ret.ZPiezoconst = ZPiezoconst
    ret.LockinRC = LockinRC * LockinRC_factor #Hz
    ret.Speclength = Speclength
    ret.VertSpecBack = VertSpecBack
    ret.LockinAmpl = LockinAmpl
    ret.Current = Current
    ret.N = vertpoints
    #hysteresis correction factor
    hyst = int(vertpoints/Speclength/LockinRC/LockinRC_factor/np.pi)
    ret.hyst = hyst

    return ret
