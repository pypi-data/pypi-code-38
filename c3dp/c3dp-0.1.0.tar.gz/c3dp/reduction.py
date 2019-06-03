import os, glob, numpy as np
from mcni.utils import conversion

monitor2angle = {
    "monitor1":45 ,
    "monitor2":135
}


def event_processing(directory, detector, angle, l1=14.699, l2=0.3, l3=0.5):
    "angle: in degrees"
    eventsA=[]
    xA=[]
    yA=[]
    zA=[]
    tA=[]
    pA=[]
    pattern = "{directoryName}/*/{monitor}*.npy".format(directoryName=directory, monitor="detector")
    print pattern
    npyfiles =  glob.glob(pattern)
    assert len(npyfiles)
    import tqdm
    for npyf in tqdm.tqdm(npyfiles):
        narr = np.load(npyf)
        xA.append(narr[0])
        yA.append(narr[1])
        zA.append(narr[2])
        tA.append(narr[3])
        pA.append(narr[4])
        eventsA.append(narr)
    xA=np.hstack(xA)
    yA=np.hstack(yA)
    zA=np.hstack(zA)
    tA=np.hstack(tA)
    pA=np.hstack(pA)
    # L=[]
    # for i in range(len(xA)):
    #     L.append(l1+l2+np.sqrt(xA[i] ** 2 + yA[i] ** 2 + (zA[i] + l3) ** 2))
    L = l1 + l2 + np.sqrt(xA ** 2 + yA ** 2 + (zA + l3) ** 2)
    angle = np.deg2rad(angle*1.)
    m = np.array([
        [np.cos(angle), 0, np.sin(angle)],
        [0, 1, 0],
        [-np.sin(angle), 0, np.cos(angle)]
        ])
    labCoords = np.dot(m, np.array([xA, yA, zA])).T + [l3*np.sin(angle), 0, l3*np.cos(angle)]
    cos2theta = labCoords[:, 2]/np.linalg.norm(labCoords, axis=-1)
    # twotheta = np.arccos(cos2theta) * 180./np.pi
    lamda = 2 * np.pi / (conversion.V2K * (L / tA))
    sintheta = np.sqrt((1 - cos2theta) / 2)
    d = lamda / (2 * sintheta)
    return d, pA

# def reduce_monitor(path, conf, l1=14.699, l2=0.3, l3=0.5, bins=np.arange(0, 4, 0.01)):
#     d_1, p_1 = event_processing(path, 'monitor1', conf.mon1, l1=l1, l2=l2, l3=l3)
#     d_2, p_2 = event_processing(path, 'monitor2', conf.mon2, l1=l1, l2=l2, l3=l3)
#
#     import numpy as np
#
#     I_d1, dbb = np.histogram(d_1, bins=bins, weights=p_1)
#     I_d2, dbb = np.histogram(d_2, bins=bins, weights=p_2)
#
#     dcs = (dbb[1:] + dbb[:-1]) / 2
#
#     errorbar_sqr_I_d1, edgesS = np.histogram(d_1, bins=bins, weights=p_1 * p_1)
#     errorbar_sqr_I_d2, edgesS = np.histogram(d_2, bins=bins, weights=p_2 * p_2)
#
#     return (dcs, I_d1, np.sqrt(errorbar_sqr_I_d1), I_d2, np.sqrt(errorbar_sqr_I_d2))

def reduce_all(path, conf, l1=14.699, l2=0.3, l3=0.5, bins=np.arange(0, 4, 0.01)):
    d_1, p_1 = event_processing(path, 'monitor1', conf.mon1, l1=l1, l2=l2, l3=l3)
    d_2, p_2 = event_processing(path, 'monitor2', conf.mon2, l1=l1, l2=l2, l3=l3)

    import numpy as np

    I_d1, dbb = np.histogram(d_1, bins=bins, weights=p_1)
    I_d2, dbb = np.histogram(d_2, bins=bins, weights=p_2)

    errorbar_sqr_I_d1, edgesS = np.histogram(d_1, bins=bins, weights=p_1 * p_1)
    errorbar_sqr_I_d2, edgesS = np.histogram(d_2, bins=bins, weights=p_2 * p_2)

    error = np.sqrt(errorbar_sqr_I_d1 + errorbar_sqr_I_d2)

    I_d = I_d1 + I_d2
    dcs = (dbb[1:] + dbb[:-1]) / 2
    return(dcs, I_d, error)

