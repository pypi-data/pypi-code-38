from pyroSAR import identify

filename = '/home/truc_jh/Desktop/S1_ARD/data/S1A_IW_GRDH_1SDV_20180829T170656_20180829T170721_023464_028DE0_F7BD.zip'

id = identify(filename)
print(id)
print(id.meta['incidence'])
print(id.meta['heading'])
