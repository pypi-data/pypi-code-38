#!/usr/bin/env python

from bob.pad.base.algorithm import SVMCascadePCA

#=======================================================================================
# Define instances here:

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.2}
N = 2
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n2_gamma_02 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.1}
N = 2
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n2_gamma_01 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.05}
N = 2
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n2_gamma_005 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.01}
N = 2
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n2_gamma_001 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

#=======================================================================================

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.1}
N = 10
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n10_gamma_01 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.05}
N = 10
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n10_gamma_005 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.01}
N = 10
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n10_gamma_001 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.005}
N = 10
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n10_gamma_0005 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

#=======================================================================================

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.5}
N = 20
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n20_gamma_05 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.2}
N = 20
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n20_gamma_02 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.1}
N = 20
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n20_gamma_01 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.05}
N = 20
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n20_gamma_005 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.01}
N = 20
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n20_gamma_001 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.005}
N = 20
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n20_gamma_0005 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.001}
N = 20
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n20_gamma_0001 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

#=======================================================================================

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.1}
N = 2
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = False

algorithm_n2_gamma_01_video_level = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

#=======================================================================================

# Test the cascade of two-class SVMs.

MACHINE_TYPE = 'C_SVC'
KERNEL_TYPE = 'RBF'
TRAINER_GRID_SEARCH_PARAMS = {'cost': 1, 'gamma': 0.01}
N = 2
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm_n2_two_class_svm_c1_gamma_001 = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=TRAINER_GRID_SEARCH_PARAMS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)
