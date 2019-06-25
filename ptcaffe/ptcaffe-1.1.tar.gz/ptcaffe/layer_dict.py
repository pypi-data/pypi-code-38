# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang 2017.12.16
# --------------------------------------------------------
from .layers import *
from .models import *
from collections import OrderedDict

DATA_LAYERS = ['Data', 'ListData', 'FolderData', 'Input', 'RandomData', 'ImageData', 'InputData', 'MnistData', 'ImageNetData', 'TorchVisionData', 'PickleData', 'Hdf5BaseData']
LOSS_LAYERS = ['SoftmaxWithLoss', 'CtcLoss', 'MimicLoss', 'EuclideanLoss']

LAYER_DICT = OrderedDict([
              # Data Layers
              ['Data'              , CaffeLmdbData],
              ['ListData'          , ListData],
              ['FolderData'        , FolderData],
              ['RandomData'        , RandomData],
              ['ImageData'         , ImageData],
              ['ImageNetData'      , ImageNetData],
              ['Input'             , RandomData],
              ['InputData'         , InputData],
              ['MnistData'         , MnistData],
              ['TorchVisionData'   , TorchVisionData],
              ['PickleData'        , PickleData],

              ['SavePickleData'    , SavePickleData],    # not Data Layer
              ['ImageCroppingData' , ImageCroppingData], # don't add to DATA_LAYERS
              ['Hdf5BaseData'      , Hdf5BaseData],      # base data layer for hdf5

              # Container Layers
              ['TorchVisionModel'  , TorchVisionModel],
              ['CaffeNetLayer'     , CaffeNetLayer],
              ['TeacherLayer'      , TeacherLayer],

              # Convolution Layers
              ['Convolution'       , Convolution],
              ['Convolution3D'     , Convolution3D],
              ['Deconvolution'     , Deconvolution],
              ['SConvolution'      , SConvolution],

              # Linear Layers
              ['InnerProduct'      , InnerProduct],
              ['SInnerProduct'     , SInnerProduct],

              # Pooling Layers
              ['Pooling'           , Pooling],
              ['Pooling3D'         , Pooling3D],
              ['Embedding'         , Embedding],
              ['EmbeddingBag'      , EmbeddingBag],

              # Activation Layers
              ['ReLU'              , ReLU],
              ['ReLU6'             , ReLU6],
              ['Sigmoid'           , Sigmoid],
              ['Softmax'           , Softmax],

              # Normalization Layers
              ['BatchNorm'         , BatchNorm],
              ['SyncBatchNorm'     , SyncBatchNorm],
              ['Normalize'         , Normalize],
              ['LRN'               , LRN],

              # Dropout Layers
              ['Dropout'           , Dropout],
              ['Dropout3D'         , Dropout3D],
              ['DropBlock2D'       , DropBlock2D],

              # Recurrent Layers
              ['GRU'               , GRU],
              ['LSTM'              , LSTM],

              # Utility Layers
              ['Upsample'          , Upsample],
              ['Eltwise'           , Eltwise],
              ['Scale'             , Scale],
              ['Concat'            , Concat],
              ['Reshape'           , Reshape],
              ['Squeeze'           , Squeeze],
              ['Unsqueeze'         , Unsqueeze],
              ['SwapChannels'      , SwapChannels],
              ['ShuffleChannel'    , ShuffleChannel],
              ['Padding'           , Padding],


              # SSD Layers
              ['Crop'              , Crop],
              ['Slice'             , Slice],
              ['Permute'           , Permute],
              ['Flatten'           , Flatten],
              ['PriorBox'          , PriorBox],

              # Evaluation Layers
              ['Accuracy'          , Accuracy],
              ['AccuracyEvaluator' , AccuracyEvaluator],

              # Auxiliary Layers
              ['PrintValue'        , PrintValue],
              ['PrintMean'         , PrintMean],
              ['PrintShape'        , PrintShape],
              ['PrintMinMax'       , PrintMinMax],
              ['PrintGrad'         , PrintGrad],
              ['PrintWeight'       , PrintWeight],
              ['PrintWeightGrad'   , PrintWeightGrad],
              ['PrintBias'         , PrintBias],
              ['PrintBiasGrad'     , PrintBiasGrad],
              ['PrintWeightUpdate' , PrintWeightUpdate],
              ['PrintBiasUpdate'   , PrintBiasUpdate],
              ['PrintMsg'          , PrintMsg],
              ['Silence'           , Silence],
              ['Identity'          , Identity],
              ['CloneOutput'       , CloneOutput],
              ['MaxProb'           , MaxProb],

              # Quantization Layers
              ['QConvolution'      , QConvolution],
              ['QInnerProduct'     , QInnerProduct],
              ['QPooling'          , QPooling],
              ['QReLU'             , QReLU],


              # Communication Layers
              ['Broadcast'         , BroadcastLayer],
              ['Gather'            , GatherLayer],
              ['AllGather'         , AllGatherLayer],
              ['Scatter'           , ScatterLayer],
              ['ReduceAdd'         , ReduceAddLayer],
              ['AllReduceAdd'      , AllReduceAddLayer],

              # Loss Layers
              ['SoftmaxWithLoss'   , SoftmaxWithLoss],
              ['CtcLoss'           , CtcLoss],
              ['MimicLoss'         , MimicLoss],
              ['EuclideanLoss'     , EuclideanLoss],

              # Old Caffe
              ['CONVOLUTION'       , Convolution],
              ['DECONVOLUTION'     , Deconvolution],
              ['RELU'              , ReLU],
              ['POOLING'           , Pooling],
              ['CONCAT'            , Concat],
              ['CROP'              , Crop],
              ['DROPOUT'           , Dropout],
              ['SOFTMAX'           , Softmax],
              ['INNER_PRODUCT'     , InnerProduct],

              # Pytorch Layers
              ['AdaptiveAvgPool2d' , AdaptiveAvgPool2d],

              # Models
              ['AlexNet'           , AlexNet],
              ['Inception3'        , Inception3],
              ['VGG11'             , VGG11],
              ['VGG13'             , VGG13],
              ['VGG16'             , VGG16],
              ['VGG19'             , VGG19],
              ['VGG11BN'           , VGG11BN],
              ['VGG13BN'           , VGG13BN],
              ['VGG16BN'           , VGG16BN],
              ['VGG19BN'           , VGG19BN],
              ['ResNet18'          , ResNet18],
              ['ResNet34'          , ResNet34],
              ['ResNet50'          , ResNet50],
              ['ResNet101'         , ResNet101],
              ['ResNet152'         , ResNet152],
              ['DenseNet121'       , DenseNet121],
              ['DenseNet169'       , DenseNet169],
              ['DenseNet201'       , DenseNet201],
              ['DenseNet161'       , DenseNet161],
])

def register_layer(name, override=False):
    def register_func(layer_class):
        if not override:
            assert(not name in LAYER_DICT)
        LAYER_DICT[name] = layer_class
        return layer_class
    return register_func

def register_data_layer(name, override=False):
    def register_func(layer_class):
        if not override:
            assert(not name in LAYER_DICT)
        LAYER_DICT[name] = layer_class
        DATA_LAYERS.append(name)
        return layer_class
    return register_func

def register_loss_layer(name, override=False):
    def register_func(layer_class):
        if not override:
            assert(not name in LAYER_DICT)
        LAYER_DICT[name] = layer_class
        LOSS_LAYERS.append(name)
        return layer_class
    return register_func

def add_layer(layer_name, layer_class, override=False):
    if not override:
        assert(not layer_name in LAYER_DICT)
    LAYER_DICT[layer_name] = layer_class

def add_data_layer(layer_name, layer_class, override=False):
    if not override:
        assert(not layer_name in LAYER_DICT)
    LAYER_DICT[layer_name] = layer_class
    DATA_LAYERS.append(layer_name)

def add_loss_layer(layer_name, layer_class, override=False):
    if not override:
        assert(not layer_name in LAYER_DICT)
    LAYER_DICT[layer_name] = layer_class
    LOSS_LAYERS.append(layer_name)
