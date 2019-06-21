#!/usr/bin/env python

from bob.pad.base.algorithm import OneClassGMM

#=======================================================================================
# Define instances here:

N_COMPONENTS = 2
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_2 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 3
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_3 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 4
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_4 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 5
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_5 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 6
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_6 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 7
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_7 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 8
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_8 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 9
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_9 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 10
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_10 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

#=======================================================================================
# above 10 Gaussians:

N_COMPONENTS = 12
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_12 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 14
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_14 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 16
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_16 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 18
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_18 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 20
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_20 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

#=======================================================================================
# above 20 Gaussians:

N_COMPONENTS = 25
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_25 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 30
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_30 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 35
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_35 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 40
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_40 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 45
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_45 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 50
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_50 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

#=======================================================================================
# above 50 Gaussians:

N_COMPONENTS = 60
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_60 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 70
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_70 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 80
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_80 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 90
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_90 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 100
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_100 = OneClassGMM(
    n_components=N_COMPONENTS, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

#=======================================================================================
# 50 Gaussians, different random seeds:

N_COMPONENTS = 50
RANDOM_STATE = 0
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_50_0 = OneClassGMM(
    n_components=N_COMPONENTS,
    random_state=RANDOM_STATE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 50
RANDOM_STATE = 1
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_50_1 = OneClassGMM(
    n_components=N_COMPONENTS,
    random_state=RANDOM_STATE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 50
RANDOM_STATE = 2
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_50_2 = OneClassGMM(
    n_components=N_COMPONENTS,
    random_state=RANDOM_STATE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 50
RANDOM_STATE = 3
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_50_3 = OneClassGMM(
    n_components=N_COMPONENTS,
    random_state=RANDOM_STATE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 50
RANDOM_STATE = 4
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_50_4 = OneClassGMM(
    n_components=N_COMPONENTS,
    random_state=RANDOM_STATE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 50
RANDOM_STATE = 5
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_50_5 = OneClassGMM(
    n_components=N_COMPONENTS,
    random_state=RANDOM_STATE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 50
RANDOM_STATE = 6
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_50_6 = OneClassGMM(
    n_components=N_COMPONENTS,
    random_state=RANDOM_STATE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 50
RANDOM_STATE = 7
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_50_7 = OneClassGMM(
    n_components=N_COMPONENTS,
    random_state=RANDOM_STATE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 50
RANDOM_STATE = 8
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_50_8 = OneClassGMM(
    n_components=N_COMPONENTS,
    random_state=RANDOM_STATE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

N_COMPONENTS = 50
RANDOM_STATE = 9
FRAME_LEVEL_SCORES_FLAG = True

algorithm_gmm_50_9 = OneClassGMM(
    n_components=N_COMPONENTS,
    random_state=RANDOM_STATE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)
