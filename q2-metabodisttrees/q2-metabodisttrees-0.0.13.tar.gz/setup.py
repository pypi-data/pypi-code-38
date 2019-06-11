# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import setup, find_packages

setup(
    name="q2-metabodisttrees",
    version='0.0.13',
    packages=find_packages(),
    package_data={'q2_metabodisttrees': ['data/*.obo'],
    			  'q2_metabodisttrees': ['data/*.bib'],
                  '': ['*.bib']},
    author="Madeleine Ernst",
    author_email="ernst.made@gmail.com",
    description="Chemically-informed trees based on substructure or chemical class information.",
    license='BSD-3-Clause',
    url="https://github.com/madeleineernst/MetaboDistTrees",
    entry_points={
        'qiime2.plugins': ['q2-metabodisttrees=q2_metabodisttrees.plugin_setup:plugin']
    },
    include_package_data=True,
    zip_safe=False,
)
