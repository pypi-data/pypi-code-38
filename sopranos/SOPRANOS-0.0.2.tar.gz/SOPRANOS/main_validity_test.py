#from SOPRANO 
import SOPRANO_fun
import params_test as params
import time

import pylab


print('***** calculating the validity range for a given combination of parameters *****')

[t_best,R,vs,Mej,frho,Ebv]=[2.458350039588246960e+06,1.126680885134050186e+03,
													 2.163744281199419498e+08,8.040544097550345271e+00,
													 2.230561458966353605e+00,2.313776135439769566e-01]

SOPRANO_fun.info_model(params.ProgType,R,vs,Mej,frho,Ebv,params.redshift,params.dico)

