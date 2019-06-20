#!/usr/bin/env python
if __name__ != '__main__': raise Exception("Do not import me!")
import sys

sys.path.append("..")
from inception import InceptionV3

import numpy as np
import chainer

from chainer.serializers import save_npz

pretrained_model = "/home/korsch/Data/MODELS/inception/ft_inat/model.ckpt.npz"
if len(sys.argv) >= 2:
	pretrained_model = sys.argv[1]

model = InceptionV3(pretrained_model, n_classes=1000)

save_npz("/home/korsch/Data/MODELS/inception/ft_inat/model.npz", model)

model.to_gpu(0)
var = model.xp.array(np.random.randn(8, 3, 299, 299).astype(np.float32))

with chainer.using_config("train", False):
	pred = model(var)

import pdb; pdb.set_trace()
