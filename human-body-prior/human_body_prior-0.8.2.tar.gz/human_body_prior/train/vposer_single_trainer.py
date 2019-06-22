# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Max-Planck-Gesellschaft zur Förderung der Wissenschaften e.V. (MPG),
# acting on behalf of its Max Planck Institute for Intelligent Systems and the
# Max Planck Institute for Biological Cybernetics. All rights reserved.
#
# Max-Planck-Gesellschaft zur Förderung der Wissenschaften e.V. (MPG) is holder of all proprietary rights
# on this computer program. You can only use this computer program if you have closed a license agreement
# with MPG or you get the right to use the computer program from someone who is authorized to grant you that right.
# Any use of the computer program without a valid license is prohibited and liable to prosecution.
# Contact: ps-license@tuebingen.mpg.de
#
#
# If you use this code in a research publication please consider citing the following:
#
# Expressive Body Capture: 3D Hands, Face, and Body from a Single Image <https://arxiv.org/abs/1904.05866>
#
#
# Code Developed by:
# Nima Ghorbani <https://www.linkedin.com/in/nghorbani/>
#
# 2018.01.02

from human_body_prior.train.vposer_smpl import run_vposer_trainer
from configer import Configer

expr_code = '004_03_WO_accad'
args = {
    'expr_code' : expr_code,
    'base_lr': 0.005,
    'num_epochs': 100,

    'dataset_dir': '/ps/project/humanbodyprior/VPoser/data/005_00_WO_accad/smpl/pytorch/stage_III',
    'work_dir': '/ps/project/humanbodyprior/VPoser/smpl/pytorch/%s'%expr_code,
}
ps = Configer(default_ps_fname='./vposer_smpl_defaults.ini', **args)

expr_message = '\n[%s] %d H neurons, latentD=%d, batch_size=%d,  kl_coef = %.1e\n' \
               % (ps.expr_code, ps.num_neurons, ps.latentD, ps.batch_size, ps.kl_coef)
expr_message += 'Trained on all of amass excpet accad\n'
expr_message += 'Using SMPL to produce meshes of the bodies\n'
expr_message += 'Reconstruction loss is L1 on meshes\n'
expr_message += 'Using Batch Normalization\n'
expr_message += '\n'
ps.expr_message = expr_message

run_vposer_trainer(ps)