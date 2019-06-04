from __future__ import unicode_literals
from __future__ import absolute_import
from .get import Get
from .post import Post
from .patch import Patch
from .delete import Delete
from .settings import Settings

class EazySDK:
    """
    Creates a new instance of the EazySDK
    """
    def __init__(self):
        self.settings = Settings()
        self.get = Get()
        self.post = Post()
        self.patch = Patch()
        self.delete = Delete()
