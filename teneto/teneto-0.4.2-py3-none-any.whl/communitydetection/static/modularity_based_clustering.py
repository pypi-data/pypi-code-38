from teneto.communitydetection.optimization.simulated_annealing import simulated_annealing
import numpy as np
def calc_modularityQ(netIn,clusters, param=None):

    """
    :out: is calc_Q being used as a modularity or cost funciton. If cost, return -calc_Q
    """
    if param == None:
        param={}
        param['out'] = 'cost'

    D = np.sum(netIn,axis=1)
    L = np.sum(np.triu(netIn,k=1))
    Q=np.zeros(1)
    for C in np.unique(clusters):
        Cind = np.where(clusters==C)
        if len(Cind[0])==1:
            l=0
        else:
            Cnet=netIn[Cind][:,Cind].squeeze()
            l=np.sum(np.triu(Cnet,k=1))
        d_s = np.sum(D[Cind])
        Q_s = (l/L)-np.power(d_s/(2*L),2)
        Q=np.sum([Q,Q_s])
    if param['out'] == 'cost':
        return -Q
    elif param['out'] == 'modularity':
        return Q


def calc_modularityQ_posneg(netIn ,clusters,param={}):

    """
    :netInput: 2D network
    :param: dictionary containing
        :'out': = 'modularity' or 'cost' (default).
        :'lambda': [0-1] Lower lambda = lower weight to positive edges. 0.5 (default) = equal to both
    """

    if 'out' not in param:
        param['out'] = 'cost'
    if 'lambda' not in param:
        param['lambda'] = 0.5

    netInP = np.array(netIn)
    netInP[netInP<0] = 0
    netInN = np.array(netIn)*-1
    netInN[netInN<0] = 0

    Qp = calc_modularityQ(netInP,clusters,param)
    Qn = calc_modularityQ(netInN,clusters,param)
    Q = (1-param['lambda'])*Qp-param['lambda']*(Qn)
    return Q

def girvan_newman(netIn,optimization='SA',Cnprior=1,repeat=1,cooldown = 0.995, f=0.5,Tstop=10e-100):

    """

    girvan_newman clustering is an optimization technique.

    **PARAMETERS**

    :netIn: 2 dimensional network (n x n).
    :optimization: 'SA' (only one avilable at present.)
    :Cnprior: Prior on number of clusters believes to exists.
    :repeat: how many times to repeat
    :cooldown: reduction in temeprature for each itteration. Decrase for quicker perfromance (and less exploration).
    :f: proportion of nodes shuffled each iteration (also how many merge/splitting attempts per round). Increase for more neighbours.
    :Tstop: terminate optimization. Increase number for quicker performance.

    """
    #No specified parameters needed here.
    Qparams={}
    Qparams['out']='cost'
    if optimization =='SA':
        C,cost=simulated_annealing(netIn,calc_modularityQ,Qparams,Cnprior=Cnprior,repeat=repeat,cooldown = cooldown, f=f,Tstop=Tstop)

    return C




def traag_bruggeman(netIn,optimization='SA',Qparams={},Cnprior=1,repeat=1,cooldown = 0.995, f=0.5,Tstop=10e-100):

    """
    Good for detecting modularity where negative clusters may be present

    READ MORE
    Traag, V. A., & Bruggeman, J. (2009). Community detection in networks with positive and negative links. Physical Review E - Statistical, Nonlinear, and Soft Matter Physics, 80(3), 1–6. http://doi.org/10.1103/PhysRevE.80.036115

    """

    if 'out' not in Qparams:
        Qparams['out']='cost'
    if 'lambda' not in Qparams:
        Qparams['lambda']=0.5

    if optimization =='SA':
        C,cost=simulated_annealing(netIn,calc_modularityQ_posneg,Qparams,Cnprior=Cnprior,repeat=repeat,cooldown = cooldown, f=f,Tstop=Tstop)

    return C
