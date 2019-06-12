# 31Mg radioactive decay function for fitting β-NMR SLR spectra, see:
# R. M. L. McFadden et al. JPS Conf. Proc. 21, 011047 (2018).
# https://doi.org/10.7566/JPSCP.21.011047
# 
# General solutions to the rate equations computed with:
# Maxima, a Computer Algebra System
# http://maxima.sourceforge.net/
# 
# Original Author: Ryan M. L. McFadden
# Transcribed to python by: Derek Fujimoto
# June 2019

import numpy as np

# GLOBAL CONSTANTS ===========================================================

# half-lives (s)
T_12_31Mg = 0.235
T_12_31Al = 0.644
T_12_31Si = 2.632*3600  # seconds
T_12_31P = np.inf
T_12_30Al = 3.62
T_12_30Si = np.inf

# nuclear lifetimes (s)
ln2 = np.log(2)
tau_31Mg = T_12_31Mg / ln2
tau_31Al = T_12_31Al / ln2
tau_31Si = T_12_31Si / ln2
tau_31P =  T_12_31P  / ln2
tau_30Al = T_12_30Al / ln2
tau_30Si = T_12_30Si / ln2

# decay constants (1/s)
lambda_31Mg = 1/tau_31Mg
lambda_31Al = 1/tau_31Al
lambda_31Si = 1/tau_31Si
lambda_31P  = 1/tau_31P
lambda_30Al = 1/tau_30Al
lambda_30Si = 1/tau_30Si

# branching ratios
b_31Mg = 0.938
b_31Al = 0.984

# Q values (keV)
Q_31Mg_b = 11829.0
Q_31Mg_bn = 4671.0
Q_31Al_b = 7998.3
Q_31Al_bn = 1410.9
Q_31Si_b = 1491.50
Q_30Al_b = 8568.1

# effective Q values
Q_31Mg = b_31Mg * Q_31Mg_b + (1-b_31Mg) * Q_31Mg_bn
Q_31Al = b_31Al * Q_31Al_b + (1-b_31Al) * Q_31Al_bn
Q_31Si = Q_31Si_b
Q_30Al = Q_30Al_b

# find the maximum effective Q value
Q_max = max((Q_31Mg, Q_31Al, Q_31Si, Q_30Al))

# naive detection efficiencies based on effective Q values
e_31Mg = Q_31Mg / Q_max
e_31Al = Q_31Al / Q_max
e_31Si = Q_31Si / Q_max
e_31P = 0.0
e_30Al = Q_30Al / Q_max
e_30Si = 0.0

# FUNCTIONS ==================================================================
def s_31Mg(time, beam_rate, n_31Mg_0):
  return    ((n_31Mg_0 * lambda_31Mg - beam_rate) * np.exp(-time * lambda_31Mg)\
            ) / lambda_31Mg + beam_rate / lambda_31Mg

# number 31Mg atoms
def n_31Mg(time, beam_pulse, beam_rate):
    
    # get indexes for pre beam-off
    out = np.zeros(time.shape[0])
    idx = time<=beam_pulse
    
    # beam on 
    out[idx] = s_31Mg(time[idx], beam_rate, 0)
    
    # beam off
    delta = time[~idx] - beam_pulse
    n_31Mg_0 = s_31Mg(beam_pulse, beam_rate, 0)
    out[~idx] = s_31Mg(delta, 0, n_31Mg_0)
    
    # negative times
    out[time<0] = 0
    return out

# activity of 31Mg atoms
def a_31Mg(time, beam_pulse, beam_rate):
    return e_31Mg * lambda_31Mg * n_31Mg(time, beam_pulse, beam_rate)

def s_31Al(time, beam_rate, n_31Mg_0, n_31Al_0):
    
    nb_31Mg = n_31Mg_0 * b_31Mg
    rb_31Mg = beam_rate * b_31Mg
    
    term1 = -(nb_31Mg * lambda_31Mg - rb_31Mg) * np.exp(-time * lambda_31Mg) \
             / (lambda_31Mg - lambda_31Al)
               
    term2 = np.exp(-time * lambda_31Al) * \
            (((nb_31Mg + n_31Al_0) * lambda_31Al - rb_31Mg) * \
               lambda_31Mg - n_31Al_0 * lambda_31Al**2)
               
    return term1 + term2 / (lambda_31Al * lambda_31Mg - lambda_31Al**2) + \
           rb_31Mg / lambda_31Al

# number of 31Al atoms
def n_31Al(time, beam_pulse, beam_rate):
    
    # get indexes for pre beam-off
    out = np.zeros(time.shape[0])
    idx = time<=beam_pulse
    
    # beam on 
    out[idx] = s_31Al(time[idx], beam_rate, 0, 0)

    # beam off
    delta = time[~idx] - beam_pulse
    n_31Mg_0 = s_31Mg(beam_pulse, beam_rate, 0)
    n_31Al_0 = s_31Al(beam_pulse, beam_rate, 0, 0)
    out[~idx] = s_31Al(delta, 0, n_31Mg_0, n_31Al_0)

    # negative times
    out[time<0] = 0
    return out

# activity of 31Al atoms
def a_31Al(time, beam_pulse, beam_rate):
  return e_31Al * lambda_31Al * n_31Al(time, beam_pulse, beam_rate)

def s_31Si(time, beam_rate, n_31Mg_0, n_31Al_0, n_31Si_0):
    
    r_bAlbMg = beam_rate * b_31Al * b_31Mg
    lam_prod = lambda_31Al * lambda_31Mg
    delta_lam = lambda_31Mg - lambda_31Al
    
    prod1 = n_31Mg_0 * b_31Al * b_31Mg + n_31Al_0 * b_31Al
    prod2 = lam_prod * lambda_31Si
    
    
    
    return ((n_31Si_0 * lambda_31Si**3 +\
           ((-n_31Al_0 * b_31Al - n_31Si_0) * lambda_31Al -\
            n_31Si_0 * lambda_31Mg) * lambda_31Si**2 + (prod1 + n_31Si_0) * prod2-\
           r_bAlbMg * lam_prod) *\
          np.exp(-time * lambda_31Si)) /\
             (lambda_31Si**3 +\
              (-lambda_31Mg - lambda_31Al) * lambda_31Si**2 + prod2) -\
         ((n_31Mg_0 * b_31Al * b_31Mg * lam_prod -\
           r_bAlbMg * lambda_31Al) *\
          np.exp(-time * lambda_31Mg)) / (delta_lam * lambda_31Si -\
              lambda_31Mg**2 + lam_prod) +\
         (np.exp(-time * lambda_31Al) *\
          ((prod1 * lambda_31Al - r_bAlbMg) * lambda_31Mg -\
           n_31Al_0 * b_31Al * (lambda_31Al**2))) /\
             (delta_lam * lambda_31Si -\
              lam_prod + lambda_31Al**2) +r_bAlbMg / lambda_31Si

# number of 31Si atoms
def n_31Si(time, beam_pulse, beam_rate):
    
    # get indexes for pre beam-off
    out = np.zeros(time.shape[0])
    idx = time<=beam_pulse
    
    # beam on 
    out[idx] = s_31Si(time[idx], beam_rate, 0, 0, 0)

    # beam off
    delta = time[~idx] - beam_pulse
    n_31Mg_0 = s_31Mg(beam_pulse, beam_rate, 0)
    n_31Al_0 = s_31Al(beam_pulse, beam_rate, 0, 0)
    n_31Si_0 = s_31Si(beam_pulse, beam_rate, 0, 0, 0)
    out[~idx] = s_31Si(delta, 0, n_31Mg_0, n_31Al_0, n_31Si_0)
    
    # negative times
    out[time<0] = 0
    return out

# activity of 31Si atoms
def a_31Si(time, beam_pulse, beam_rate):
  return e_31Si * lambda_31Si * n_31Si(time, beam_pulse, beam_rate)

def s_31P(time, beam_rate, n_31Mg_0, n_31Al_0, n_31Si_0, n_31P_0):
    
    bb = b_31Al * b_31Mg
    rbb = beam_rate * bb
    bblamAl = bb * lambda_31Al
    r_bblamAl = beam_rate * bblamAl
    lamlam = lambda_31Al * lambda_31Mg
    
    return -(\
            (n_31Si_0 * lambda_31Si**3 +\
                ((-n_31Al_0 * b_31Al - n_31Si_0) * lambda_31Al -n_31Si_0 * lambda_31Mg) *\
                lambda_31Si**2 +\
                (n_31Mg_0 * bb + n_31Al_0 * b_31Al + n_31Si_0) *\
                lamlam * lambda_31Si -\
                r_bblamAl * lambda_31Mg) *\
            np.exp(-time * lambda_31Si)) /\
            (lambda_31Si**3 + (-lambda_31Mg - lambda_31Al) * lambda_31Si**2 +\
                lamlam * lambda_31Si) +\
            ((n_31Mg_0 * bblamAl * lambda_31Mg - r_bblamAl) *\
                np.exp(-time * lambda_31Mg) * lambda_31Si) /\
            ((lambda_31Mg**2 - lamlam) *\
            lambda_31Si - lambda_31Mg**3 + lambda_31Al * lambda_31Mg**2) -\
            (np.exp(-time * lambda_31Al) *\
                (((n_31Mg_0 * bb + n_31Al_0 * b_31Al) * lambda_31Al -rbb) *\
                    lambda_31Mg -n_31Al_0 * b_31Al * lambda_31Al**2) *\
                lambda_31Si) /\
            ((lamlam - lambda_31Al**2) *\
                  lambda_31Si - lambda_31Al**2 * lambda_31Mg + lambda_31Al**3) +\
            ((((n_31Mg_0 * bb + n_31Al_0 * b_31Al + n_31Si_0 + n_31P_0) *\
                lambda_31Al - rbb) * \
                lambda_31Mg - r_bblamAl) *\
                lambda_31Si - r_bblamAl * lambda_31Mg) /\
            (lamlam * lambda_31Si) + rbb * time

# number of 31P atoms
def n_31P(time, beam_pulse, beam_rate): 
    
    # get indexes for pre beam-off
    out = np.zeros(time.shape[0])
    idx = time<=beam_pulse
    
    # beam on 
    out[idx] = s_31P(time[idx], beam_rate, 0, 0, 0, 0)

    # beam off
    delta = time[~idx] - beam_pulse    
    n_31Mg_0 = s_31Mg(beam_pulse, beam_rate, 0)
    n_31Al_0 = s_31Al(beam_pulse, beam_rate, 0, 0)
    n_31Si_0 = s_31Si(beam_pulse, beam_rate, 0, 0, 0)
    n_31P_0 = s_31P(time[~idx], beam_rate, 0, 0, 0, 0)
    out[~idx] = s_31P(delta, 0, n_31Mg_0, n_31Al_0, n_31Si_0, n_31P_0)
    
    # negative times
    out[time<0] = 0
    return out

def a_31P(time, beam_pulse, beam_rate): 
    return e_31P * lambda_31P * n_31P(time, beam_pulse, beam_rate)

def s_30Al( time,  beam_rate,  n_31Mg_0,  n_30Al_0): 
    return  (((n_31Mg_0 * b_31Mg - n_31Mg_0) * \
            lambda_31Mg - beam_rate * b_31Mg +beam_rate) *\
            np.exp(-time * lambda_31Mg)) /\
            (lambda_31Mg - lambda_30Al) -\
            (np.exp(-time * lambda_30Al) *\
            (((n_31Mg_0 * b_31Mg - n_31Mg_0 - n_30Al_0) * lambda_30Al -\
            beam_rate * b_31Mg + beam_rate) *\
            lambda_31Mg + n_30Al_0 * lambda_30Al**2)) /\
            (lambda_30Al * lambda_31Mg - lambda_30Al**2) -\
            (beam_rate * b_31Mg - beam_rate) / lambda_30Al

# number of 30Al atoms
def n_30Al(time, beam_pulse, beam_rate):
    
    # get indexes for pre beam-off
    out = np.zeros(time.shape[0])
    idx = time<=beam_pulse
    
    # beam on 
    out[idx] = s_30Al(time[idx], beam_rate, 0, 0)
  
    # beam off
    delta = time[~idx] - beam_pulse    
    n_31Mg_0 = s_31Mg(beam_pulse, beam_rate, 0)
    n_30Al_0 = s_30Al(beam_pulse, beam_rate, 0, 0)
    out[~idx] = s_30Al(delta, 0, n_31Mg_0, n_30Al_0)
  
    # negative times
    out[time<0] = 0
    return out
    
def a_30Al(time, beam_pulse, beam_rate): 
  return e_30Al * lambda_30Al * n_30Al(time, beam_pulse, beam_rate)

def s_30Si(time, beam_rate, n_31Mg_0, n_31Al_0, n_30Al_0, n_30Si_0):
    return -((((n_31Mg_0 * b_31Al - n_31Mg_0) * b_31Mg * lambda_31Al +\
            (n_31Mg_0 * b_31Mg - n_31Mg_0) * lambda_30Al) *\
            lambda_31Mg**2 +\
            (((n_31Mg_0 - n_31Mg_0 * b_31Al * b_31Mg) * lambda_30Al +\
            (beam_rate - beam_rate * b_31Al) * b_31Mg) *\
            lambda_31Al +\
            (beam_rate - beam_rate * b_31Mg) * lambda_30Al) *\
            lambda_31Mg +\
            (beam_rate * b_31Al * b_31Mg - beam_rate) * lambda_30Al *\
            lambda_31Al) *\
            np.exp(-time * lambda_31Mg)) /\
            (lambda_31Mg**3 +\
            (-lambda_31Al - lambda_30Al) * lambda_31Mg**2 +\
            lambda_30Al * lambda_31Al * lambda_31Mg) -\
            ((((n_31Mg_0 * b_31Al * b_31Mg + n_31Al_0 * b_31Al - n_31Mg_0 -\
            n_31Al_0 - n_30Si_0 - n_30Al_0) *\
            lambda_30Al -\
            beam_rate * b_31Mg + beam_rate) *\
            lambda_31Al +\
            (beam_rate - beam_rate * b_31Al) * b_31Mg * lambda_30Al) *\
            lambda_31Mg +\
            (beam_rate - beam_rate * b_31Al * b_31Mg) * lambda_30Al *\
            lambda_31Al) /\
            (lambda_30Al * lambda_31Al * lambda_31Mg) +\
            (np.exp(-time * lambda_31Al) *\
            ((((n_31Mg_0 * b_31Al - n_31Mg_0) * b_31Mg + n_31Al_0 * b_31Al -\
            n_31Al_0) *\
            lambda_31Al +\
            (beam_rate - beam_rate * b_31Al) * b_31Mg) *\
            lambda_31Mg +\
            (n_31Al_0 - n_31Al_0 * b_31Al) * lambda_31Al**2)) /\
            (lambda_31Al * lambda_31Mg - lambda_31Al**2) +\
            (np.exp(-time * lambda_30Al) *\
            (((n_31Mg_0 * b_31Mg - n_31Mg_0 - n_30Al_0) * lambda_30Al -\
            beam_rate * b_31Mg + beam_rate) *\
            lambda_31Mg +\
            n_30Al_0 * lambda_30Al**2)) /\
            (lambda_30Al * lambda_31Mg - lambda_30Al**2) - \
            beam_rate * b_31Al * b_31Mg * time + beam_rate * time

# number of 30Si atoms
def n_30Si(time, beam_pulse, beam_rate):
    
    # get indexes for pre beam-off
    out = np.zeros(time.shape[0])
    idx = time<=beam_pulse
    
    # beam on 
    out[idx] = s_30Si(time[idx], beam_rate, 0, 0, 0, 0)

    # beam off
    delta = time[~idx] - beam_pulse    
    n_31Mg_0 = s_31Mg(beam_pulse, beam_rate, 0)
    n_31Al_0 = s_31Al(beam_pulse, beam_rate, 0, 0)
    n_30Al_0 = s_30Al(beam_pulse, beam_rate, 0, 0)
    n_30Si_0 = s_30Si(beam_pulse, beam_rate, 0, 0, 0, 0)
    out[~idx] = s_30Si(delta, 0, n_31Mg_0, n_31Al_0, n_30Al_0, n_30Si_0)

    # negative times
    out[time<0] = 0
    return out
    
def a_30Si(time, beam_pulse, beam_rate): 
    return e_30Si * lambda_30Si * n_30Si(time, beam_pulse, beam_rate)

# total atoms
def n_total(time, beam_pulse, beam_rate=1e6):
    return  n_31Mg(time, beam_pulse, beam_rate) + \
            n_31Al(time, beam_pulse, beam_rate) + \
            n_31Si(time, beam_pulse, beam_rate) + \
            n_31P (time, beam_pulse, beam_rate) + \
            n_30Al(time, beam_pulse, beam_rate) + \
            n_30Si(time, beam_pulse, beam_rate);

# fractions of total atoms
def fn_31Mg(time, beam_pulse, beam_rate=1e6): 
    return  n_31Mg(time, beam_pulse, beam_rate) / \
            n_total(time, beam_pulse, beam_rate)

def fn_31Al(time, beam_pulse, beam_rate=1e6):
    return n_31Al(time, beam_pulse, beam_rate) / \
            n_total(time, beam_pulse, beam_rate)

def fn_31Si(time, beam_pulse, beam_rate=1e6):
  return n_31Si(time, beam_pulse, beam_rate) / \
         n_total(time, beam_pulse, beam_rate)

def fn_31P(time, beam_pulse, beam_rate=1e6):
  return n_31P(time, beam_pulse, beam_rate) / \
         n_total(time, beam_pulse, beam_rate)

def fn_30Al(time, beam_pulse, beam_rate=1e6):
  return n_30Al(time, beam_pulse, beam_rate) / \
         n_total(time, beam_pulse, beam_rate)

def fn_30Si(time, beam_pulse, beam_rate=1e6):
  return n_30Si(time, beam_pulse, beam_rate) / \
         n_total(time, beam_pulse, beam_rate)

# total activity
def a_total(time, beam_pulse, beam_rate=1e6):
  return a_31Mg(time, beam_pulse, beam_rate) + \
         a_31Al(time, beam_pulse, beam_rate) + \
         a_31Si(time, beam_pulse, beam_rate) + \
         a_31P (time, beam_pulse, beam_rate) + \
         a_30Al(time, beam_pulse, beam_rate) + \
         a_30Si(time, beam_pulse, beam_rate)

# fractional activities
def fa_31Mg(time, beam_pulse, beam_rate=1e6):
  return a_31Mg(time, beam_pulse, beam_rate) / \
         a_total(time, beam_pulse, beam_rate)

def fa_31Al(time, beam_pulse, beam_rate=1e6):
  return a_31Al(time, beam_pulse, beam_rate) / \
         a_total(time, beam_pulse, beam_rate)

def fa_31Si(time, beam_pulse, beam_rate=1e6):
  return a_31Si(time, beam_pulse, beam_rate) / \
         a_total(time, beam_pulse, beam_rate)

def fa_31P(time, beam_pulse, beam_rate=1e6):
  return a_31P(time, beam_pulse, beam_rate) / \
         a_total(time, beam_pulse, beam_rate)

def fa_30Al(time, beam_pulse, beam_rate=1e6):
  return a_30Al(time, beam_pulse, beam_rate) / \
         a_total(time, beam_pulse, beam_rate)

def fa_30Si(time, beam_pulse, beam_rate=1e6):
  return a_30Si(time, beam_pulse, beam_rate) / \
         a_total(time, beam_pulse, beam_rate)
