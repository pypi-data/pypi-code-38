import os
from setuptools import setup, find_packages, Extension
from pathlib import Path

LINE_TRACE = bool(os.environ.get('LINE_TRACE', 0))


# a good way to structure python package with Cython
# https://stackoverflow.com/questions/4505747/how-should-i-structure-a-python-package-that-contains-cython-code
try:
    from Cython.Build import cythonize

except ImportError:
    use_cython = False
else:
    use_cython = True

ext_modules = []

if use_cython:
    ext_modules += [
        Extension('uttut.elements', ['uttut/elements.pyx']),
        Extension('uttut.expand_by_entities', ['uttut/expand_by_entities.pyx']),
        Extension('uttut.toolkits.get_kth_combination', ['uttut/toolkits/get_kth_combination.pyx']),
        Extension('uttut.toolkits.partition_by_entities', [
                  'uttut/toolkits/partition_by_entities.pyx']),
        Extension('uttut.pipeline.edit.replacement', ['uttut/pipeline/edit/replacement.pyx']),
        Extension('uttut.pipeline.edit.span', ['uttut/pipeline/edit/span.pyx']),
        Extension('uttut.pipeline.edit.utils', ['uttut/pipeline/edit/utils.pyx']),
        Extension('uttut.pipeline.edit.validation', ['uttut/pipeline/edit/validation.pyx']),
        Extension('uttut.pipeline.edit.label_propagation',
                  ['uttut/pipeline/edit/label_propagation.pyx']),
        Extension(
            name='uttut.pipeline.ops.utils.consistent_hash',
            sources=[
                'uttut/pipeline/ops/utils/consistent_hash.pyx',
                'uttut/pipeline/ops/utils/MurmurHash3.cpp',
            ],
            extra_compile_args=['-O3'],
            language='c++',
        ),
    ]
    ext_modules = cythonize(
        ext_modules,
        compiler_directives={
            'language_level': 3,
            'linetrace': LINE_TRACE,
            'profile': True,
            'binding': LINE_TRACE,
        },
    )

else:
    ext_modules += [
        Extension('uttut.elements', ['uttut/elements.c']),
        Extension('uttut.expand_by_entities', ['uttut/expand_by_entities.c']),
        Extension('uttut.toolkits.get_kth_combination', ['uttut/toolkits/get_kth_combination.c']),
        Extension('uttut.toolkits.partition_by_entities',
                  ['uttut/toolkits/partition_by_entities.c']),
        Extension('uttut.pipeline.edit.replacement', ['uttut/pipeline/edit/replacement.c']),
        Extension('uttut.pipeline.edit.span', ['uttut/pipeline/edit/span.c']),
        Extension('uttut.pipeline.edit.utils', ['uttut/pipeline/edit/utils.c']),
        Extension('uttut.pipeline.edit.validation', ['uttut/pipeline/edit/validation.c']),
        Extension('uttut.pipeline.edit.label_propagation',
                  ['uttut/pipeline/edit/label_propagation.c']),
        Extension('uttut.pipeline.ops.utils.consistent_hash',
                  ['uttut/pipeline/ops/utils/consistent_hash.cpp',
                   'uttut/pipeline/ops/utils/MurmurHash3.cpp']),
    ]

here = Path(__file__).parent

readme = here.joinpath('README.md')
if readme.exists():
    with readme.open() as f:
        long_description = f.read()
else:
    long_description = '-'


about = {}
with open(here.joinpath('uttut', '__version__.py'), 'r') as filep:
    exec(filep.read(), about)

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    license=about["__license__"],
    author=about["__author__"],
    url=about["__url__"],
    packages=find_packages(),
    install_requires=[],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Development Status :: 3 - Alpha",
    ],
    include_package_data=True,
    ext_modules=ext_modules,
    python_requires='>=3.5',
)
