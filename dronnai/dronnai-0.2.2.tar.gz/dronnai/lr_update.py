import numpy as np

def conf_lr_updater(min_lr,max_lr,cycles,diff_lr=False):
    '''
    configuration of lr_updater with lr_bounds and option for differential learning rate implementation
    min_lr - minimum learning rate value
    max_lr - maximum learning rate value
    cycles - how many times learning rate should bounce from boarders during one epoch
    diff_lr - False if there is only one learning rate level and list of learning rate ratios for every part of neural net
    '''
    def lr_updater(obj,diff_lr=diff_lr):
        step_size = obj.train_len / cycles
        cycle = np.floor(1 + obj.train_iters[0] / (2 * step_size))
        x = np.abs(obj.train_iters[0] / step_size - 2 * cycle + 1)
        lr = min_lr + (max_lr - min_lr) * np.maximum(0, (1 - x))
        if not diff_lr:
            diff_lr = [1] * len(obj.optimizer.param_groups)
        for p, lr_ratio in zip(obj.optimizer.param_groups,diff_lr):
            p['lr'] = lr*lr_ratio
    return lr_updater
