from ..actions import sync
from ..actions import upload
from ..actions import verify

actions = {
    'sync': [sync.run],
    'verify': [sync.run, verify.run],
    'upload': [sync.run, verify.run, upload.run],
}