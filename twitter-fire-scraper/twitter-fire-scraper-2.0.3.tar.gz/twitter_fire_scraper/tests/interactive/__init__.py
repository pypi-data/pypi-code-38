"""
This module is a suite of tests that are not easily test, i.e. qualitative parts of this project.

They are meant to be run by humans and inspected to make sure they do what they say they do.
"""
import os
import sys

# Append parent directory to enhance portability.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))