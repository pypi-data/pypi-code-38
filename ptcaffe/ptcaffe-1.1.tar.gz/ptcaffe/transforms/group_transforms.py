import random

def get_valid_inputs(inputs, indices):
    if len(indices) == 1 and indices[0] == -1:
        return inputs

    valid_inputs = [inputs[idx] for idx in indices]
    return valid_inputs

def merge_result(inputs, valid_outputs, indices):
    outputs = list(inputs)
    if len(indices) == 1:
        ind = indices[0]
        if ind >= 0:
            outputs.pop(ind)
            outputs.insert(ind, valid_outputs)
        elif ind == -1:
            return valid_outputs
    else:
        for idx,ind in enumerate(indices):
            outputs.pop(ind)
            outputs.insert(ind, valid_outputs[idx])
    return tuple(outputs)

class Compose(object):
    def __init__(self, transforms, probs, inds):
        self.transforms = transforms
        self.probs = probs
        self.inds = inds
        assert len(transforms) == len(probs)
        assert len(transforms) == len(inds)

    def __call__(self, *inputs):
        output_dict = dict()
        output_dict[-1] = inputs
        prev_idx = -1
        for idx, (t,p,ind) in enumerate(zip(self.transforms, self.probs, self.inds)):
            if p == 1.0 or random.random() < p:
                valid_inputs = get_valid_inputs(output_dict[prev_idx], ind)
                output_dict[idx] = merge_result(output_dict[prev_idx], t(*valid_inputs), ind)
                del output_dict[prev_idx]
                prev_idx = idx
        outputs = output_dict[prev_idx]
        if outputs is None: return

        if len(outputs) == 1:
            return outputs[0]
        else:
            return outputs

class OneOf(object):
    def __init__(self, transforms, probs, inds):
        self.transforms = transforms
        self.probs = probs
        self.inds = inds
        assert len(transforms) == len(probs)

    def __call__(self, *inputs):
        choose_idx = random.randint(0, len(self.transforms)-1)
        t = self.transforms[choose_idx]
        p = self.probs[choose_idx]
        ind = self.inds[choose_idx]
        if p == 1.0 or random.random() < p:
            valid_inputs = get_valid_inputs(inputs, ind)
            outputs = merge_result(inputs, t(*valid_inputs), ind)
            return outputs
        else:
            return inputs 

class RandomOrder(object):
    def __init__(self, transforms, probs, inds):
        self.transforms = transforms
        self.probs = probs
        self.inds = inds
        assert len(transforms) == len(probs)
        assert len(transforms) == len(inds)

    def __call__(self, *inputs):
        output_dict = dict()
        order = list(np.random.permutation(len(self.probs)))
        output_dict[-1] = inputs
        prev_idx = -1
        for idx, o in enumerate(order):
            t = self.transforms[o]
            p = self.probs[o]
            ind = self.inds[o]
            if p == 1.0 or random.random() < p:
                valid_inputs = get_valid_inputs(output_dict[prev_idx], ind)
                output_dict[idx] = merge_result(output_dict[prev_idx], t(*valid_inputs), ind)
                del output_dict[prev_idx]
                prev_idx = idx
        return output_dict[prev_idx]
