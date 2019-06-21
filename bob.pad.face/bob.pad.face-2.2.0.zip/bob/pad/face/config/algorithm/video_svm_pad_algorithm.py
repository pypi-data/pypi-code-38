#!/usr/bin/env python

from bob.pad.base.algorithm import SVM

#=======================================================================================
# Define instances here:

machine_type = 'C_SVC'
kernel_type = 'RBF'
n_samples = 10000
# trainer_grid_search_params = {'cost': [2**p for p in range(-5, 16, 2)], 'gamma': [2**p for p in range(-15, 4, 2)]}
trainer_grid_search_params = {
    'cost': [2**p for p in range(-3, 14, 2)],
    'gamma': [2**p for p in range(-15, 0, 2)]
}
mean_std_norm_flag = True
frame_level_scores_flag = False  # one score per video(!) in this case

video_svm_pad_algorithm_10k_grid_mean_std = SVM(
    machine_type=machine_type,
    kernel_type=kernel_type,
    n_samples=n_samples,
    trainer_grid_search_params=trainer_grid_search_params,
    mean_std_norm_flag=mean_std_norm_flag,
    frame_level_scores_flag=frame_level_scores_flag)

frame_level_scores_flag = True  # one score per frame(!) in this case

video_svm_pad_algorithm_10k_grid_mean_std_frame_level = SVM(
    machine_type=machine_type,
    kernel_type=kernel_type,
    n_samples=n_samples,
    trainer_grid_search_params=trainer_grid_search_params,
    mean_std_norm_flag=mean_std_norm_flag,
    frame_level_scores_flag=frame_level_scores_flag)

trainer_grid_search_params = {
    'cost': [1],
    'gamma': [0]
}  # set the default LibSVM parameters

video_svm_pad_algorithm_default_svm_param_mean_std_frame_level = SVM(
    machine_type=machine_type,
    kernel_type=kernel_type,
    n_samples=n_samples,
    trainer_grid_search_params=trainer_grid_search_params,
    mean_std_norm_flag=mean_std_norm_flag,
    frame_level_scores_flag=frame_level_scores_flag)
