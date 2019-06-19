#from SOPRANO 
import SOPRANO_fun
import params_test as params
import time

import pylab


print('***** plotting the model (for a given combination of parameters) versus the data *****')

[t_best,R,vs,Mej,frho,Ebv]=[2.458350039588246960e+06,1.126680885134050186e+03,
													 2.163744281199419498e+08,8.040544097550345271e+00,
													 2.230561458966353605e+00,2.313776135439769566e-01]

SOPRANO_fun.plot_model_versus_data(params.dict_all,path_to_data=params.path_to_data,path_to_filters=params.filters_directory,ProgType=params.ProgType,texp=t_best,R=R,vs=vs,Mej=Mej,frho=frho,Ebv=Ebv,redshift=params.redshift,dic_transmission=params.dico,output_flux_file='output_test_various/SW_model_flux.txt',kappa=None,output_file_path='output_test_various/model_versus_data.png')


