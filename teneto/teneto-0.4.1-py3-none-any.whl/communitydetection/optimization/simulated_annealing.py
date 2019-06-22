import numpy as np

def acceptance_probabailities(T,costCurrent,costNew,costGlobal,cCurrent,cNew,cGlobal):
    if costCurrent >= costNew:
        costCurrent = np.array(costNew)
        cCurrent = np.array(cNew)
    else:
        p=np.exp(-(costNew-costCurrent)/T)
        if p>=np.random.rand():
            costCurrent = np.array(costNew)
            cCurrent=np.array(cNew)
    #This part is specified if the algorithem explores too far and goes away from already obtained optimal solution
    if costCurrent<costGlobal:
        costGlobal = np.array(costCurrent)
        cGlobal = np.array(cCurrent)
    return costCurrent,costGlobal,cCurrent,cGlobal


def simulated_annealing(netIn,costFun,costFunParams,Cnprior=1,repeat=1,cooldown = 0.995, f=0.5,Tstop=10e-100):

    """

    Simulated annelaing. Still in testing phase (see NOTE).

    **PARAMETERS**

    :netIn: 2D network input
    :costFun: cost function that takes input costFun(netIn,clusterAssignment,costFunParams)
    :costFunParams: dictionary of parameters for costFun
    :Cnprior: Prior on number of clusters believes to exists.
    :repeat: how many times to repeat
    :cooldown: reduction in temeprature for each itteration
    :f: proportion of nodes shuffled each iteration (also how many merge/splitting attempts per round)
    :Tstop: terminate optimization. Increase number for quicker performance.

    **OUTPUT**

    :cCurrent: Cluster assignment of network (glaobal minimum found)
    :cost: cost function output

    **NOTE**

    1. Currently a bit slow due to their being no stopping condition and low Tstop (I reasoned better safe than sorry)
    2. For merging/splitting new networks (found a bit ambigious at source), this was done at a seperate step than shuffling node clster membership (recaclulating Q). Nodes were only shuffled once per round of T (and the number of nodes shuffled is dictated by F). Cluster merging/splitting attempts are tried multiple times per T (if allowed by 0)
    For each attempt at merging/splitting, Q is recalculated.


    :REFERENCE:
    *Guimerà and Amaral (2005), Nature*.

    :HISTORY:

    Created, Jan17, WHT

    """

    n_i = int(np.round(f*netIn.shape[0]))
    n_c = int(np.round(f*netIn.shape[0]))

    costGlobal = 1000000
    cGlobal = []

    for r in range(0,repeat):

        #Initial state
        Cn = Cnprior
        cCurrent = np.random.randint(0,Cn,netIn.shape[0])
        costCurrent = costFun(netIn,cCurrent,costFunParams)
        T=1

        while T>Tstop:
            #
            #costNew = costFun(netIn,cNew)

            # Get Neighbours (Shuffle nodes across clusters)
            update = np.random.randint(0,netIn.shape[0],n_i)
            cNew = np.array(cCurrent)
            cNew[update] = np.random.randint(0,Cn,n_i)

            # Cost function of new cluster
            costNew = costFun(netIn,cNew,costFunParams)

            # Update
            costCurrent,costGlobal,cCurrent,cGlobal=acceptance_probabailities(T,costCurrent,costNew,costGlobal,cCurrent,cNew,cGlobal)


            # get neighbours part 2
            # Add or split clusters (slightly unclear in Guimerà and Amaral how they achieved this and I asusme equal probabalistic to split, merge)
            for splitmerge in range(0,n_c):
                cNew = np.array(cCurrent)
                if Cn > 1 and Cn < netIn.shape[0]:
                    r=np.random.rand()
                    if r>=.5:
                        merge = 1
                        split = 0
                    else:
                        merge = 0
                        split = 1
                elif Cn == netIn.shape[0]:
                    merge = 1
                    split = 0
                else:
                    merge = 0
                    split = 1
                # If f is high and too many merge and splittings occur so set to
                if split == 1:
                    if split > Cn:
                        split = Cn
                    coi_split= np.random.randint(0,Cn)
                    roi=np.where(cNew==coi_split)[0]
                    update = np.random.randint(0,2,len(roi))
                    if len(np.unique(update))>1:
                        cNew[roi[update==1]]=Cn
                        Cn += 1
                if merge == 1:
                    if merge > Cn:
                        merge = Cn
                    coi_merge=np.argsort(np.random.rand(Cn))
                    roi1=np.where(cNew==coi_merge[1])[0]
                    cNew[roi1]=coi_merge[0]
                    #Set max to empty cluster index
                    cNew[cNew==cNew.max()]=coi_merge[1]
                    Cn -= 1

                costNew = costFun(netIn,cNew,costFunParams)

                costCurrent,costGlobal,cCurrent,cGlobal=acceptance_probabailities(T,costCurrent,costNew,costGlobal,cCurrent,cNew,cGlobal)

            T=T*cooldown

    return cGlobal, costGlobal
