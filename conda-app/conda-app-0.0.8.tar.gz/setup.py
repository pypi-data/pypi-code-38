from setuptools import setup
import sys

try:
    import conda
except ImportError:
    print(
        """Please install conda-app in the base conda environment:
conda activate base
pip install conda-app"""
    )
    sys.exit(1)

setup()
