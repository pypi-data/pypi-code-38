from pyroSAR.snap.auxil import Workflow

filename = '/home/truc_jh/Desktop/S1_ARD/data/SNAP/stack/S1A__IW___D_20180826T053453_VV_tnr_bnr_Orb_Cal_ML_TF_TC_dB_proc.xml'

with Workflow(filename) as wf:
    print(wf.ids)
    print(wf.operators)
    del wf['Multilook']
    # print(wf)
