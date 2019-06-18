from functools import wraps
import hashlib
import json
import os

from build_utils import docker_utils

def create_source_archive(execution_context, source_path, include=None):
    full_path = os.path.join(execution_context.dir_path, source_path)
    return docker_utils.create_build_context_archive(full_path, include=include)
