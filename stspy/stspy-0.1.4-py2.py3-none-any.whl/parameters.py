#Setup specific parameters
LockinRC_factor = 7960.0 #multiplicative factor to get LockinRC param in Hz

#Parameters for reading VERT files, shouldn't change
spec_length_step = 0.2 # minimum step size in seconds i.e. spec_length_step*Spec*Vertmandelay = Speclenght[s]
skiprows = 576 # number of rows to skip to get to spectra data
current_conv = 5e13 # conversion factor to get current (and dIdV) in Amps

