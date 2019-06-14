"""Provides filesystem walkers"""
from .abstract_walker import AbstractWalker, FileInfo
from .pyfs_walker import PyFsWalker
from .s3_walker import S3Walker
from .factory import create_walker, create_archive_walker
