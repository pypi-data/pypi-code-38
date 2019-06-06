import json
from .get_required_images import get_required_images

def api_getimagelist(files_compose):
    print(json.dumps(list(get_required_images(files_compose))))