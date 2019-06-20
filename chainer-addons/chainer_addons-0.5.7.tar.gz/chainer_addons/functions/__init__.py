from .alpha_prod import alpha_prod
from .signed_square_root import signed_square_root
from .tf_avg_pooling import tf_average_pooling_2d

import chainer.functions as F

def smoothed_cross_entropy(pred, gt, N, eps=0.1):

	loss = F.softmax_cross_entropy(pred, gt)
	# -sum[ log( P(k) ) * U ]
	reg_loss = -F.mean(F.sum(F.log_softmax(pred) / N, axis=1))

	return (1-eps) * loss + eps * reg_loss

