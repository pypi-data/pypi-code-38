import numpy as np

class LR_Search:
    '''
    class which can check best learning rate for particular architecture 

    NEEDS TO BE REWRITED BC UNFORTUNATELY IT STRUGGLE TO FIND BEST LEARNING RATE
    '''
    
    def __init__(self, gym, check_interval, max_lr=2, min_lr=0.000001, max_lr_steps=0, min_lr_steps=0,valid_frac=1,diff_lr=None):
        self.gym = gym
        self.check_interval = check_interval
        self.valid_frac = valid_frac
        self.diff_lr = diff_lr
        if self.diff_lr:
            self.gym.optimizer_update = conf_update_with_diff(diff_lr)
        self.lr_bounds = self.fit_lr(max_lr, min_lr, max_lr_steps, min_lr_steps)

    def check_lr(self):
        i = 0
        lr_losses = []
        print("Searching learning rate...")
        last_loss = float('Inf')
        while True:
            lr = self.get_lr(self.min_lr, i)
            if lr > self.max_lr:
                break
            else:
                self.gym.optimizer.defaults['lr'] = lr
            print(lr)
            results = self.gym.workout(self.check_interval,stop_after_one=True,valid_frac=self.valid_frac,save_state=False)
            lr_loss = results['train_losses'][0]
            if np.isnan(lr_loss):
                break
            lr_losses.append([lr, lr_loss])
            i += 1
#             if last_loss * 1.1 < lr_loss:
#                 break
            last_loss = lr_loss
        return lr_losses

    def get_lr(self,min_lr,i):
        return min_lr * np.exp(i)

    def choose_min_lr(self, lr_losses):
        losses = np.array(lr_losses)[:, 1:2]
        ratios = []
        for i in range(len(losses) - 1):
            ratio = losses[i + 1] / losses[i]
            ratios.append(ratio[0])
        return ratios.index(min(ratios)) + 1

    def choose_max_lr(self, lr_losses, threshold=0.1):
        losses = np.array(lr_losses)[:, 1:2]
        rev_losses = losses[::-1]
        for i in range(len(rev_losses) - 1):
            ratio = rev_losses[i] / rev_losses[i + 1]
            if 1 - ratio > threshold:
                return losses.tolist().index(rev_losses[i])
        return len(lr_losses) - 1

    def fit_lr(self, max_lr, min_lr, max_lr_steps, min_lr_steps):
        self.max_lr = max_lr
        self.min_lr = min_lr
        self.max_lr_steps = max_lr_steps
        self.min_lr_steps = min_lr_steps

        lr_losses = self.check_lr()
        min_lr_idx = self.choose_min_lr(lr_losses) + self.min_lr_steps
        min_lr = lr_losses[min(max(0, min_lr_idx),len(lr_losses)-2)][0]
        max_lr_idx = self.choose_max_lr(lr_losses) - self.max_lr_steps
        max_lr_idx = min(max(min_lr_idx + 1, max_lr_idx),len(lr_losses)-1)
        max_lr = lr_losses[max_lr_idx][0]
        print("Chosen lr between " + min_lr.__str__() + ' and ' + max_lr.__str__())
        self.gym.optimizer.defaults['lr'] = min_lr
        return {'min_lr':min_lr,'max_lr':max_lr}

def conf_update_with_diff(diff_ratios):
    '''
    configuration of differential learning rate with ratios (optimizer needs to be created with parameters dict)
    diff_ratios - list of ratios per optimizers param_groups, ratio is ratio to deafault learning rate in optimizer
    '''
    def update_with_diff(obj):
        for p, lr_ratio in zip(obj.optimizer.param_groups,diff_ratios):
            p['lr'] = obj.optimizer.defaults['lr']*lr_ratio
    return update_with_diff

