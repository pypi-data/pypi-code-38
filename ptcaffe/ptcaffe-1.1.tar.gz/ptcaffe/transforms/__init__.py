from collections import OrderedDict

import torchvision.transforms as T

from .line_loader import *
from .group_transforms import *
from .imagenet_transforms import *
from .ssd_transforms import *
from .postprocess import *

from .tensor_transforms import *
from ptcaffe.utils.utils import parse_types, make_list

TRANSFORM_DICT = OrderedDict([
    # line reader
    ['line_split'                , [LineSplit              , [-1]]],
    ['line_loader'               , [LoadImageAndLabel      , [-1]]],

    ['pil_loader'                , [PIL_Loader             , [0]]],
    ['cv2_loader'                , [CV2_Loader             , [0]]],
    ['pil2numpy'                 , [PIL2Numpy              , [0]]],
    ['numpy2pil'                 , [Numpy2PIL              , [0]]],
    ['numpy2tensor'              , [Numpy2Tensor           , [0]]],
    ['cvimg2tensor'              , [CVImage2Tensor         , [0]]],
    ['save_pil'                  , [SavePIL                , [0]]],
    ['save_cv2'                  , [SaveCV2                , [0]]],

    # imagenet transforms
    ['lighting'                  , [Lighting               , [0]]],
    ['tf_resize'                 , [TFResizer              , [0]]],

    # pil transforms
    ['pil_centercrop'            , [T.CenterCrop           , [0]]],         
    ['pil_colorjitter'           , [T.ColorJitter          , [0]]],
    ['pil_fivecrop'              , [T.FiveCrop             , [0]]],
    ['pil_tencrop'               , [T.TenCrop              , [0]]],
    ['pil_grayscale'             , [T.Grayscale            , [0]]],
    ['pil_pad'                   , [T.Pad                  , [0]]],
    ['pil_resize'                , [T.Resize               , [0]]],
    ['pil_randomaffine'          , [T.RandomAffine         , [0]]],
    ['pil_randomcrop'            , [T.RandomCrop           , [0]]],
    ['pil_randomflip_h'          , [T.RandomHorizontalFlip , [0]]],
    ['pil_randomflip_v'          , [T.RandomVerticalFlip   , [0]]],
    ['pil_randomresizedcrop'     , [T.RandomResizedCrop    , [0]]],
    ['pil_randomrotation'        , [T.RandomRotation       , [0]]],


    # conversions
    ['pil2tensor'                , [T.ToTensor             , [0]]],
    ['tensor2pil'                , [T.ToPILImage           , [0]]],

    # tensor transforms
    ['tensor_normalize'          , [Tensor_Normalize       , [0]]],
    ['tensor_unsqueeze'          , [Tensor_Unsqueeze       , [0]]],

    # ssd transforms
    ['cv2_int2float'             , [CV2_Int2Float          , [0]]],
    ['cv2_subtractmeans'         , [CV2_SubtractMeans      , [0]]],
    ['cv2_resize'                , [CV2_Resize             , [0]]],
    ['cv2_randomsaturation'      , [CV2_RandomSaturation   , [0]]],
    ['cv2_randomhue'             , [CV2_RandomHue          , [0]]],
    ['cv2_randomlightingnoise'   , [CV2_RandomLightingNoise, [0]]],
    ['cv2_swapchannels'          , [CV2_SwapChannels       , [0]]],
    ['cv2_convertcolor'          , [CV2_ConvertColor       , [0]]],
    ['cv2_randomcontrast'        , [CV2_RandomContrast     , [0]]],
    ['cv2_randombrightness'      , [CV2_RandomBrightness   , [0]]],
    ['cv2_totensor'              , [CV2_ToTensor           , [0]]],
    ['tensor_tocv2'              , [Tensor_ToCV2           , [0]]],

    ['bbox_percent2absolute'     , [BBox_Percent2Absolute  , [0,1]]],
    ['bbox_absolute2percent'     , [BBox_Absolute2Percent  , [0,1]]],

    ['ssd_expand'                , [SSD_Expand             , [0,1]]],
    ['ssd_randommirror'          , [SSD_RandomMirror       , [0,1]]],
    ['ssd_tensorflowadjust'      , [SSD_TensorflowAdjust   , [0,1]]],
    ['ssd_lineloader'            , [SSD_LineLoader         , [-1]]],
    ['ssd_randomsamplecrop'      , [SSD_RandomSampleCrop   , [-1]]],
    ['ssd_mergetarget'           , [SSD_MergeTarget        , [-1]]],

    # post process
    ['print_result'              , [PrintResult            , [1]]],
    ['print_ssd_detection'       , [PrintSSDDetection      , [-1]]],
])

GROUP_DICT = dict()
GROUP_DICT['compose'] = Compose
GROUP_DICT['sequential'] = Compose
GROUP_DICT['sequential0'] = Compose
GROUP_DICT['sequential1'] = Compose
GROUP_DICT['sequential2'] = Compose
GROUP_DICT['oneof']   = OneOf
GROUP_DICT['random_choice'] = OneOf
GROUP_DICT['random_order'] = RandomOrder

def register_transform(name, override=False, ind=[0]):
    ind = make_list(ind)
    def register_func(transform_class):
        if not override:
            assert(not name in TRANSFORM_DICT)
        TRANSFORM_DICT[name] = [transform_class, ind]
        return transform_class
    return register_func

def create_transform(transform_param, out_type='compose'):
    transforms = []
    probs = []
    inds = []

    for name, param in transform_param.items():
        key = name.split('@')[0]
        if isinstance(param, list):
            raise ValueError("duplicated transform, please add @num in the end to distinguish them. E.g rename as %s@1, %s@2" % (key, key))
        if key in GROUP_DICT.keys():
            p = float(param.pop('p')) if 'p' in param else 1.0
            obj = create_transform(param, key)
            ind = [-1]
        else:
            kwargs = parse_types(param)
            p = kwargs.pop('p') if 'p' in kwargs else 1.0
            ind = kwargs.pop('ind') if 'ind' in kwargs else TRANSFORM_DICT[key][1]
            obj = TRANSFORM_DICT[key][0](**kwargs)
        transforms.append(obj)
        probs.append(p)
        inds.append(ind)

    return GROUP_DICT[out_type](transforms, probs, inds)
