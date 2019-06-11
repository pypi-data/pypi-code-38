# -*- coding: utf-8 -*-


class MetricPhasePrefixes(object):
    VAL = 'ml_val_'
    TRAIN = 'ml_train_'
    TEST = 'ml_test_'


class MetricTypePrefixes(object):
    CUSTOM = 'custom_'


class AlgorithmTypes(object):
    VISUAL_BACKPROP = "visual_backprop"
    GRAD_CAM = "grad_cam"


class HyperParamTypes(object):
    RUN = 'run'
    OPTIMIZER = 'optimizer'
    MODEL = 'model'
    CUSTOM = 'custom'


class EventTypes(object):
    TRAIN_BEGIN = 'TRAIN_BEGIN'
    TRAIN_END = 'TRAIN_END'
    EPOCH_BEGIN = 'EPOCH_BEGIN'
    EPOCH_END = 'EPOCH_END'
    BATCH_BEGIN = 'BATCH_BEGIN'
    BATCH_END = 'BATCH_END'
    TEST_BEGIN = 'TEST_BEGIN'
    TEST_END = 'TEST_END'
    TEST_ITERATION_END = 'TEST_ITERATION_END'
