#!/usr/bin/env python
# Examples:
#
# ./scripts/plot_all.py results/I_d_ results/I_d  sim exp comparison
import numpy as np
import os, sys
thisdir = os.path.dirname(__file__)
parentpath = os.path.join(thisdir, '..')

libpath = os.path.join(thisdir, '../simlib')
if not libpath in sys.path:
    sys.path.insert(0, libpath)

from collimator_fun import collimator_geom
from scaling import scale

from matplotlib import pyplot as plt

# simFile=sys.argv[1]
# expFile=sys.argv[2]
# first_label=sys.argv[3]
# second_label=sys.argv[4]
# sample=sys.argv[5]
#
# sim=np.load(simFile)
# exp=np.load(expFile)
#
# plt.errorbar(sim[0,:], sim[1,:]/np.sum(sim[1,:]), label=first_label)
# plt.errorbar(exp[0,:], exp[1,:]/np.sum(exp[1,:]), label=second_label)
# plt.xlabel('d-spacing')
# plt.ylabel('I')
# plt.legend()
#
# plt.savefig(os.path.join(thisdir, '../figures/{sample}.png'.format(sample=sample)))
# sample='comparison_mantid_own_reduction'
sample='comparisons_simVsexp_masked_NotNormalized'

clampSi=np.load(os.path.join(thisdir, '../results/I_d_owned_reduction_1e9_ss_det-50_105.npy')) #I_d_coll_onlyclamp_small
clampSi_exp_Notmasked=np.load(os.path.join(thisdir, '../results/I_d_clampCell_Si_exp.npy')) #I_d_coll_onlyclamp_small
clampSi_mantid=np.load(os.path.join(thisdir, '../results/I_d_clampcellSi_1e9_det-50_105.npy')) #I_d_coll_onlyclamp_small
clampSi_masked=np.load(os.path.join(thisdir, '../results/I_d_clampcell_Si_1e11_mostCorrect_masked.npy'))
clampSi_test=np.load(os.path.join(thisdir, '../results/I_d_clampcellSi_1e9_det-50-105_test.npy'))

coll_SCAT=np.load(os.path.join(thisdir, '../results/I_d_coll_plastic_Scat_masked.npy'))
coll_NO_SCAT=np.load(os.path.join(thisdir, '../results/I_d_coll_plastic_NO_Scat_masked.npy'))
coll_High_SCAT=np.load(os.path.join(thisdir, '../results/I_d_coll_plas_High_Scat.npy'))
coll_boron=np.load(os.path.join(thisdir, '../results/I_d_coll_boron.npy'))

coll_NO_SCAT_ms=np.load(os.path.join(thisdir, '../results/I_d_coll_Plas_No_scat_ms.npy'))
coll_High_SCAT_ms=np.load(os.path.join(thisdir, '../results/I_d_coll_Plas_High_scat_ms.npy'))
coll_exp=np.load(os.path.join(thisdir, '../results/I_d_coll_exp_masked.npy'))
clampSi_exp_masked=np.load(os.path.join(thisdir, '../results/I_d_clampCell_Si_exp_masked.npy'))
coll_trial__1e4_ms3=np.load(os.path.join(thisdir, '../results/I_d_trial_1e4.npy'))
coll_HScat_MS=np.load(os.path.join(thisdir, '../results/I_d_Real_ms_Highscat_1e9.npy'))

# coll_Sz6_ch27=np.load(os.path.join(parentpath, 'I_d_coll_clampcell_only_small.npy')) #I_d_coll_onlyclamp_small
#
# # coll_clampSi=np.load(os.path.join(parentpath, 'I_d_coll_clampcell_Si_largeNcounts_ch4_dist30.npy')) #I_d_coll_onlyclamp_small
# coll_clampSi_smallCount=np.load(os.path.join(parentpath, 'I_d_coll_clampcell_Si_wall5_dist22_0.1_1e6.npy')) #I_d_coll_onlyclamp_small
# coll_clampSi_smallCount_45=np.load(os.path.join(parentpath, 'I_d_clampcell_Si_wall5_dist22_0.1_1e7_angle45.npy'))
# coll_clampSi_smallCount_135=np.load(os.path.join(parentpath, 'I_d_clampcell_Si_wall5_dist22_0.1_1e7_angle135.npy'))
#
# ##########################EXPERIMEANTAL DATA WITH COLLIMATOR###################################
# experiment_colli=np.loadtxt(os.path.join(parentpath, 'coli_experiment.dat'),delimiter=',' )
#
# experiment_without_colli=np.loadtxt(os.path.join(parentpath, 'without_coli_experiment.dat'),delimiter=',' )
#
# coll=np.load(os.path.join(parentpath, 'I_d_coll-ch27_chSZ6.8_curved.npy'))
# coll_flat=np.load(os.path.join(parentpath, 'I_d_coll-ch27_chSZ6.8_flat.npy'))
# clampSi=np.load(os.path.join(parentpath, 'I_d_clampcellSi.npy'))
# Si=np.load(os.path.join(parentpath, 'I_d_Si_noColl_noClamp.npy'))
# clamp=np.load(os.path.join(parentpath, 'I_d_clampcell_only.npy'))
# # coll_Sz6_ch27=np.load(os.path.join(parentpath, 'I_d_coll_chSz6_ch27.npy'))
#
#
# totalcounts_Si=np.sum(Si[1,:])
# totalcounts_gPt8=np.sum(coll[1,:])
# totalcounts_g1pt6=np.sum(coll_Sz6_ch27[1,:])
#
# reduc_gPt8=totalcounts_gPt8/totalcounts_Si
# reduc_g1pt6=totalcounts_g1pt6/totalcounts_Si
#
# print ('pt8',reduc_gPt8, '1pt6', reduc_g1pt6)
#
#
# print (max(clampSi[1,:])/max(coll_Sz6_ch27[1,:]))
# # scale_coll_pt8=scale(coll[1,:], min(clampSi[1,:]), max(clampSi[1,:]))
# # scale_coll_pt8_flat=scale(coll_flat[1,:], min(clampSi[1,:]), max(clampSi[1,:]))
# # scaleI_coll_clampSi=scale(coll_clampSi[1,:], min(clampSi[1,:]), max(clampSi[1,:]))
# # scaleE_coll_clampSi=scale(coll_clampSi[2,:], min(clampSi[1,:]), max(clampSi[1,:]))
#
# scaleI_coll_clampSi_smallCount_45=scale(coll_clampSi_smallCount_45[1,:], min(clampSi[1,:]), max(clampSi[1,:]))
# scaleI_coll_clampSi_smallCount_135=scale(coll_clampSi_smallCount_135[1,:], min(clampSi[1,:]), max(clampSi[1,:]))
# scaleI_experiment_colli=scale(experiment_colli[:,1]-200, 0, 10000)# plt.plot(clampSi_exp_masked[0,:], clampSi_exp_masked[1,:],'black', label='No collimator exp')
# scaleI_experiment_without_colli=scale(experiment_without_colli[:,1]-200, 0, 10000)
#



plt.figure(figsize=(10,6))
# plt.plot(coll_High_SCAT[0,:], coll_High_SCAT[1,:], 'red',label='collimator sim')
# plt.plot(coll_trial__1e4_ms3[0,:], coll_trial__1e4_ms3[1,:]*15000., 'blue',label='collimator MS_3 trial 1e4')
plt.plot(coll_HScat_MS[0,:], coll_HScat_MS[1,:], 'blue',label='collimator MS_R')

plt.plot(coll_NO_SCAT_ms[0,:], coll_NO_SCAT_ms[1,:],'green', label='H NO Scattering collimator')
# plt.plot(coll_NO_SCAT_ms[0,:], coll_NO_SCAT_ms[1,:],'green', label='H NO Scattering collimator')
# plt.plot(clampSi_masked[0,:], clampSi_masked[1,:],'green', label=' NO collimator sim')
# plt.plot(clampSi_mantid[0,:], clampSi_mantid[1,:],'orange', label='No collimator sim')
# plt.plot(clampSi_test[0,:], clampSi_test[1,:],'pink', label='No collimator test sim')
# plt.plot(clampSi_exp_masked[0,:], clampSi_exp_masked[1,:]*4,'pink', label='No collimator exp ')
# plt.plot(clampSi_exp_Notmasked[0,:], clampSi_exp_Notmasked[1,:]/5.,'magenta', label='No collimator exp Notmasked')
# plt.plot(coll_exp[0,:], coll_exp[1,:]*23*4,'blue', label='collimator exp')
plt.xlim(1.,4.)
# plt.ylim(20000,600000)
# plt.plot(clampSi[0,:], clampSi[1,:]/np.sum(clampSi[1,:]), 'blue',label='sim_own_script_reduction')
# plt.plot(clampSi_exp[0,:], clampSi_exp[1,:]/np.sum( clampSi_exp[1,:]),'black', label='exp')
# plt.plot(clampSi_mantid[0,:], clampSi_mantid[1,:]/np.sum( clampSi_mantid[1,:]), 'red',label='sim_mantid_reduction')
plt.legend()
plt.xlabel('d-spacing (Angstrom)')
plt.ylabel('Intensity (Arbitary Units)')
# plt.savefig(os.path.join(thisdir, '../figures/eps/{sample}.eps'.format(sample=sample)))
plt.show()
#
#
# # plt.plot(Si[0,:], Si[1,:]*50, label='Si')
# # plt.plot(clamp[0,:], clamp[1,:], label='clampcell_only')
# # plt.errorbar(coll_Sz6_ch27[0,:], coll_Sz6_ch27[1,:]*10000,coll_Sz6_ch27[2,:] *10000 ,label='clampcell+collimator_gap1.6')
# # plt.errorbar(coll_clampSi[0,:], coll_clampSi[1,:]*10000,coll_clampSi[2,:] *10000 ,label='clampcell+Si+collimator_gap1.6')
# # plt.errorbar(coll_clampSi[0,:], scaleI_coll_clampSi,coll_clampSi[2,:],  label='clampcell+Si+collimator_1e7')
# # plt.errorbar(coll_clampSi_smallCount_45[0,:], scaleI_coll_clampSi_smallCount_45, label='clampcell+Si+collimator_45_1e7')
# # plt.errorbar(coll_clampSi_smallCount_45[0,:], coll_clampSi_smallCount_45[1,:], label='clampcell+Si+collimator_45_1e7')
# # plt.errorbar(coll_clampSi_smallCount_45[0,:], coll_clampSi_smallCount_135[1,:]*100, label='clampcell+Si+collimator_135_1e7')
# plt.errorbar(experiment_colli[:,0], experiment_colli[:,1]*4, label='clampcell+Si+collimator_experiment')
# plt.errorbar(experiment_without_colli[:,0], experiment_without_colli[:,1], label='clampcell+Si+NOcollimator_experiment')
#
#
#
#
# # plt.plot(coll[0,:], scale_coll_pt8, label='clampcell+Si+collimator_gap.8')
# # plt.plot(coll[0,:], scale_coll_pt8_flat, label='clampcell+Si+collimator_gap.8_flat')
# plt.xlabel('d-spacing(A)')
# plt.xlim(1,5)
# plt.ylabel('Intensity(arb. units)')
#
# plt.legend()
# plt.show()

