from setuptools import setup, find_packages
import glob
import os

import torch
from torch.utils.cpp_extension import CUDA_HOME
from torch.utils.cpp_extension import CppExtension
from torch.utils.cpp_extension import CUDAExtension
from torch.utils.cpp_extension import BuildExtension

NAME = "ptcaffe"
PACKAGES = find_packages()

def get_extensions():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    extensions_dir = os.path.join(this_dir, "ptcaffe", "csrc")

    main_file = glob.glob(os.path.join(extensions_dir, "*.cpp"))
    source_cuda = glob.glob(os.path.join(extensions_dir, "cuda", "*.cu"))

    sources = main_file
    extension = CppExtension

    extra_compile_args = {"cxx": []}
    define_macros = []

    if torch.cuda.is_available() and CUDA_HOME is not None:
        extension = CUDAExtension
        sources += source_cuda
        define_macros += [("WITH_CUDA", None)]
        extra_compile_args["nvcc"] = [
            "-DCUDA_HAS_FP16=1",
        ]

    sources = [os.path.join(extensions_dir, s) for s in sources]

    include_dirs = [extensions_dir]

    ext_modules = [
        extension(
            "ptcaffe._C",
            sources
            #include_dirs=include_dirs,
            #define_macros=define_macros,
            #extra_compile_args=extra_compile_args,
        )
    ]

    return ext_modules

setup(
    name = NAME,
    version = "1.1",
    description = 'pytorch caffe',
    long_description = 'the caffe framework which works on pytorch',
    license = "MIT Licence",
    url = "http://github.com/orion/ptcaffe",
    author = "xiaohang",
    author_email = "xiaohang@ainirobot.com",
    packages = PACKAGES,
    #include_package_data = True,
    platforms = "any",

    install_requires=[
        'easydict',
        'nose',      # for test
        'packaging', # for version compare
        'torch>=0.4.0',
        'torchvision>=0.2.1',
        #'opencv-python',
	    'protobuf',
        'tqdm',
        'setuptools>=16.0',
    ],
    #ext_modules=get_extensions(),
    #cmdclass={"build_ext": BuildExtension},
    scripts = [],
    entry_points={'console_scripts': [
        'ptcaffe           = ptcaffe.tools.main:main',
        'ptcaffe-profile   = ptcaffe.tools.main_profile:main',

        'merge_bn          = ptcaffe.tools.merge_bn:main',
        'merge_scale       = ptcaffe.tools.merge_scale:main',
        'split_scale       = ptcaffe.tools.split_scale:main',
        'prototxt2graph    = ptcaffe.tools.prototxt2graph:main',
        'ptcmodel2prototxt = ptcaffe.tools.ptcmodel2prototxt:main',

        'darknet2ptcaffe   = ptcaffe.converter.darknet2ptcaffe:main',
        'ptcaffe2darknet   = ptcaffe.converter.ptcaffe2darknet:main',
        'caffe2ptcaffe     = ptcaffe.converter.caffe2ptcaffe:main',
        'ptcaffe2caffe     = ptcaffe.converter.ptcaffe2caffe:main',
        'pytorch2ptcaffe   = ptcaffe.converter.pytorch2ptcaffe:main',
        'onnx2ptcaffe      = ptcaffe.converter.onnx2ptcaffe:main',
        'ptcaffe2onnx      = ptcaffe.converter.ptcaffe2onnx:main',
        'tensorflow2ptcaffe   = ptcaffe.converter.tensorflow2ptcaffe:main',
    ]},
    test_suite='test'
)

