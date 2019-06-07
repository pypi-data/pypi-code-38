from torch.nn.utils import clip_grad_norm_

def conf_gc(max_norm, norm_type=2):
    '''
    configurator of gradient clipping function which can easily be applied to gym
    '''
    def gc(obj):
        norm = clip_grad_norm_(obj.model.parameters(),max_norm,norm_type)
        return norm
    return gc

def conf_gradients_norm(norm_type=2):
    '''
    configurator which let you change norm_type which will be logged during training
    '''
    def gradients_norm(obj):
            total_norm = 0
            parameters = obj.model.parameters()
            parameters = list(filter(lambda p: p.grad is not None, parameters))
            for p in parameters:
                param_norm = p.grad.data.norm(norm_type)
                total_norm += param_norm.item() ** norm_type
            total_norm = total_norm ** (1. / norm_type)
            return total_norm
    return gradients_norm