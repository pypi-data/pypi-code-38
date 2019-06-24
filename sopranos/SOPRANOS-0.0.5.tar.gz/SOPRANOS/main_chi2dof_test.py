#from SOPRANO 
import SOPRANO_fun
import params_test as params
import time

import pylab


print('***** calculating chi2/dof for a given combination of parameters *****')

[t_best,R_best,vs_best,Mej_best,frho_best,Ebv_best]=[2.458350039588246960e+06,1.126680885134050186e+03,
													 2.163744281199419498e+08,8.040544097550345271e+00,
													 2.230561458966353605e+00,2.313776135439769566e-01]

[lnprob,chi2dof] = SOPRANO_fun.pdf_parallel_epochs(params.dict_all, data_band_dic=params.data_band_dic, to=t_best, rs=R_best, vs=vs_best,
							 ms=Mej_best, frho=frho_best, ebv=Ebv_best,
							 ProgType=params.ProgType, model=params.model, dic_transmissions=params.dico, redshift=params.redshift, verbose=True,
							 processes=params.proc, ndim=6,chi2show=True)


