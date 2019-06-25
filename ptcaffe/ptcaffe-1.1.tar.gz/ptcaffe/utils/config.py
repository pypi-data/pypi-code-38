from __future__ import absolute_import, division, print_function

from easydict import EasyDict as edict

cfg = edict()

# ------------------------------------------------------------------------
# Prototxt default actions
cfg.DEFAULT_WEIGHT_FILLER_TYPE   = 'xavier'
cfg.DEFAULT_WEIGHT_FILLER_GAIN   = 1.0
cfg.DEFAULT_VARIANCE_NORM        = 'FAN_IN' #'FAN_IN', 'FAN_OUT', 'AVERAGE'
cfg.DEFAULT_NONLINEARITY         = 'relu' # 'tanh', 'relu', 'leaky_relu'
cfg.DEFAULT_BIAS_FILLER_TYPE     = 'constant'

cfg.DEFAULT_LR_MULT              = 1.0
cfg.DEFAULT_DECAY_MULT           = 1.0

cfg.DEFAULT_WEIGHT_LR_MULT       = 1.0
cfg.DEFAULT_WEIGHT_DECAY_MULT    = 1.0
cfg.DEFAULT_BIAS_LR_MULT         = 2.0
cfg.DEFAULT_BIAS_DECAY_MULT      = 0.0

cfg.DEFAULT_BN_WEIGHT_LR_MULT    = 1.0
cfg.DEFAULT_BN_WEIGHT_DECAY_MULT = 1.0
cfg.DEFAULT_BN_BIAS_LR_MULT      = 2.0
cfg.DEFAULT_BN_BIAS_DECAY_MULT   = 0.0

cfg.DEFAULT_BATCHNORM_AFFINE     = False
cfg.DEFAULT_SCALE_BIAS           = True

cfg.SYNCBN = False

# Loading Weight
cfg.ALLOW_MISMATCH_SIZE_WEIGHT_LOADING = False

# Quantization parameters
cfg.QUANTIZATION = False
cfg.QUANT_BITS   = 8

# Visdom Address
cfg.VISDOM_SERVER = None
cfg.VISDOM_ENV_NAME = None
cfg.VISDOM_SERVER_PORT = 8097
cfg.VISDOM_SERVER_USING_INCOMING_SOCKET = False
cfg.FORCE_VISDOM = False

# Global Variable
cfg.VERBOSE_LEVEL = 0
cfg.NUM_GPUS = None
cfg.SEED = None
cfg.CUDNN_DETERMINISTIC = False
# ------------------------------------------------------------------------


def parse_cfg_params_from_solver(solver):
    from .logger import logger
    for key in cfg.keys():
        if key in solver:
            value = cfg[key]
            if value is None:
                logger.print('ignore %s in solver' % key)
            elif isinstance(value, str):
                cfg[key] = solver[key]
                logger.print("set %s = %s" % (key, cfg[key]))
            elif isinstance(value, bool):
                cfg[key] = (solver[key].lower() == 'true')
                logger.print("set %s = %s" % (key, cfg[key]))
            elif isinstance(value, int):
                cfg[key] = int(solver[key])
                logger.print("set %s = %d" % (key, cfg[key]))
            elif isinstance(value, float):
                cfg[key] = float(solver[key])
                logger.print("set %s = %f" % (key, cfg[key]))
            else:
                logger.print('unknow value type for key %s in solver' % key)
