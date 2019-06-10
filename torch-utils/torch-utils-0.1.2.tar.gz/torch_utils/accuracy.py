from typing import Sequence

import torch


def accuracy(output: torch.Tensor, target: torch.Tensor, top_k: Sequence[int] = (1,)) -> Sequence[torch.Tensor]:
    """
    Computes the accuracy over the k top predictions for the specified values of k
    refer to https://github.com/pytorch/examples/blob/master/imagenet/main.py#L399
    """
    with torch.no_grad():
        max_k = max(top_k)
        batch_size = target.size(0)

        _, predict = output.topk(max_k, 1, True, True)
        predict.t_()
        correct = predict.eq(target.view((1, -1)).expand_as(predict))

        res = []
        for k in top_k:
            correct_k = correct[:k].view(-1).float().sum(0, keepdim=True)
            res.append(correct_k.mul_(100.0 / batch_size))
        return res
