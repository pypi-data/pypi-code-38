from math import ceil
from gwpy.timeseries import TimeSeries

#########################################################################################################

#########################################################################################################

#########################################################################################################


def BLWNB(f,df,dt,fs):
    #BLWNB - Generate a random signal of given duration with constant power
    #in a given band (and zero power out of band).

    #   x = blwnb(f,df,dt,fs)
    #
    #   f   Scalar. Minimum signal frequency [Hz].
    #   df  Scalar. Full signal bandwidth [Hz].
    #   dt  Scalar. Signal duration [s].
    #   fs  Scalar. Signal sample rate [Hz].

    # Power is restricted to the band (f,f+df). 
    # Note that fs must be greater than 2*(f+df).

    # original version: L. S. Finn, 2004.08.03

    # $Id: BLWNB.m 4992 2015-07-25 18:59:12Z patrick.sutton@LIGO.ORG $

    #% ---- Check that fs > 2*(f+df), otherwise sampling rate is not high enough to
    #       cover requested frequency range of the signal.
    if (fs <= abs(2*(f+df))):
        raise ValueError('Sampling rate fs is too small, fs = '+str(fs)+' must be greater than 2*(f+df) = '+str(np.abs(2*(f+df))))


    if f < 0 or df <= 0 or fs <= 0 or dt <= 0 :
        raise ValueError('All arguments must be greater than zero')

    #% ---- Generate white noise with duration dt at sample rate df. This will be
    #%      white over the band [-df/2,df/2].

    nSamp = ceil(dt*df)
    x_old = TimeSeries(np.random.randn(nSamp),sample_rate=1/dt)
    


    #% ---- Resample to desired sample rate fs.
    x=x_old.resample(fs/df)
    #frac = Fraction(Decimal(fs/df))
    #p, q = frac.numerator , frac.denominator


    #% ---- Note that the rat() function returns p,q values that give the desired
    #%      ratio to a default accuracy of 1e-6. This is a big enough error that
    #%      x may be a few samples too short or too long. If too long, then truncate
    #%      to duration dt. If too short, zero-pad to duration dt.
    #print((np.zeros(nSamp-len(x)).shape))
    nSamp = round(dt*fs)
    if len(x) > nSamp:
        x = x[0:nSamp]
    elif len(x) < nSamp:
        x=np.hstack((np.array(x),np.zeros(nSamp-len(x))))

    #% ---- Heterodyne up by f+df/2 (moves zero frequency to center of desired band).
    fup = f+df/2.
    x = x*np.exp(-2*np.pi*1j*fup/fs*np.arange(1,len(x)+1))

    #% ---- Take real part and adjust amplitude.
    x = np.array(np.real(x)/np.sqrt(2))
    #% ---- Done.
    return(x)


def envelope(t,q=0.5,t0='defult',sig=3):
    
    T=t[-1]-t[0]
    length=len(t)
    fs=int(length/T)
    
    if q>=1-1/fs: q=1-1/fs
    if q<=1/fs: q=1/fs

    sigma=T/sig
    sigma_m=q*sigma
    sigma_p=(1-q)*sigma
    

    
    if t0=='defult':
        t0=t[0]+sig*sigma_m
        
    
    tm=np.arange(0,t0,1/fs)
    tp=np.arange(t0,t[-1],1/fs)        
    
    env_m=np.exp(-((tm-t0)/(sigma_m))**2)
    env_p=np.exp(-((tp-t0)/(sigma_p))**2)
    envel=np.hstack((env_m,env_p))

    
    if (len(envel)>length):
        envel=np.delete(envel,-1)

    elif (len(envel)<length):
        envel=np.append(0,envel)


    return(envel)

def sig(t,T0,step):
    #T0: time of center of sigmoid
    #step: the duration of the step.
    y=-1/(1+np.exp((10/step)*(t-T0)))+1
    return(y)


#########################################################################################################
#########################################################################################################
#########################################################################################################






def ringdown(f0          # Central frequency
              ,h_pea=1   # RSS magnitude
              ,tau=Nne   # Duration of chirplet 
              ,T=None     # Duration of output signal
              ,t0=0       # Time of the peak
              ,delta=0    # Phase
              ,fs=2048):  # Frequency sample

    
    if tau==None: tau=1/f0    
    if T==None: T=16*tau

    t_m=np.arange(t0-2/f0,t0,1/fs)
    t_p=np.arange(t0,T+t0-2/f0-1/fs,1/fs)

    h_p = h_peak*np.cos(2*np.pi*(t_p-t0)*f0+delta)*np.exp(-(t_p-t0)/tau/0.1)     #t>=t0
    h_m = h_peak*np.cos(2*np.pi*(t_m-t0)*f0+delta)*sig(t_m,t0-1/f0/2,1/f0) #t<t0



    h=np.append(h_m,h_p)
    t=np.append(t_m,t_p)

    return(t,h)

def WNB(param,T,fs,q='gauss',seed=np.random.randint(0,1e3)):#param=[h_rss, fc, df]

    # ---- Turn off default interpolation.
    #      (Might actually be useful here, but don't want to alter
    #      frequency content of noise by low-pass filtering).
    #pregen = 0
    h_rss=param[0]
    fc=param[1]
    df=param[2]
    
    t=np.arange(0,T,1/fs)

    # ---- Gaussian-modulated noise burst, white over specified band.

    #% ---- If fifth parameter is specified, use it to set the seed for
    #%      the random number generator.
    #%      KLUDGE: injections will be coherent only if all the
    #%      detectors have the same sampling frequency.

    #if(length(parameters)>=5)
    #    randn('state',parameters(5));
    #end

    #% ---- Gaussian-like envelope
    if q=='gauss':
        env = envelope(t,0.5,t0='defult')
    elif (isinstance(q,float) or isinstance(q,int)) == True:
        env = envelope(t,q,t0='defult')
    #% ---- Band-limited noise (independent for each polarization)
    x = BLWNB(max(fc-df,0),2*df,T,fs)
    h = h_rss*env*x
    
    return(t,h)
