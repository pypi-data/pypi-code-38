


class CalC_BandStructure(object):

    """
    """



    def __init__(self, vasp, stdin=None, stdout=None, primary=True, 
                        *args, **kwargs):

        # calculate the band structure by using primary cell % 
        if primary is True:
            structure, isprimary = structure.get_primary_cell()
        self.isprimary = isprimary
        self.structure = structure     
        self.stdout = stdout 

    def band_workflow(self):

        self.nonscf_wave()
        self.nonscf_paths()
        self.extrct_band()


    def nonscsf_wave(self):
        
        if self.isprimary:
            vasp.icharg = 11
            vasp.compute(stdin, stdout)
        else:
            vasp.compute(stdin, stdout)
    

