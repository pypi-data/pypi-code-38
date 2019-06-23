
def cosmo_pars(Partype=None):
    """Cosmological parameters as measured by various experiments.
    Input  :- Cosmological parameter source, options are:
            'wmap3'    : WMAPSNLS (Spergel et al. 2007).
            'wmap5'    : WMAPSNBO (Komatsu et al. 2008).NOT IMPLEMENTED YET
            'wmap9'    : WMAP9BAOH0 (Hinshaw et al. 2013).NOT IMPLEMENTED YET
            'planck'   : planck full mission (Ade et al. 2015).NOT IMPLEMENTED YET
    Output :- Disctionnary containing cosmological parameters.
          - Disctionnary containing cosmological parameters errors
            [1sigma lower error, 1sigma upper error].
     Tested : ?
         By : Maayane T. Soumagnac Feb 2019. Inspired by Eran's function of the same name
        URL :
     Example:[Par,ErrPar]=cosmo_pars('wmap3')
     Reliable:  """

    if Partype is None:
        Partype=='wmap3'
    
    Par=dict()
    ErrPar=dict()

    if Partype=='wmap3':
        Par['H0']= 70.4
        ErrPar['H0'] = [-1.6, 1.5]
        Par['OmegaM'] = 0.268
        ErrPar['OmegaM'] = [-0.018,  0.018]
        Par['OmegaB'] = 0.03105
        ErrPar['OmegaB'] = [0, 0] #NaN NaN in Eran s code
        Par['OmegaK']=0.986
        ErrPar['OmegaK']=[-0.017,  0.017]
        Par['OmegaL']=0.716
        ErrPar['OmegaL']=[-0.055,  0.055]
        Par['OmegaRad']=0.0
        ErrPar['OmegaRad']=[-0.0, 0.0]
        Par['W']=-1 # OmegaM_H2']=0.1324 #equation of state
        ErrPar['W']=[-0.0, 0.0]
        Par['OmegaM_H2']=0.1324
        ErrPar['OmegaM_H2']=[-0.0041, 0.0042]
        Par['OmegaB_H2']=0.02186
        ErrPar['OmegaB_H2']=[-0.00068,  0.00068]
        Par['Tau']=0.073
        ErrPar['Tau']=[-0.028,  0.027]
        Par['Ns']=0.947
        ErrPar['Ns']=[-0.015,  0.015]
        Par['Sigma8']=0.776
        ErrPar['Sigma8']=[-0.032,  0.031]
    return Par,ErrPar

