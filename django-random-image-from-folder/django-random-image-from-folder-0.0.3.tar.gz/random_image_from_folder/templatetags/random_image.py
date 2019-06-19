import os
import random
from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def random_image():
    try:
        valid_extensions = settings.RANDOM_IMAGE_EXTENSIONS
    except AttributeError:
        valid_extensions = ['.jpg','.jpeg','.png','.gif',]

    rel_dir = settings.RANDOM_IMAGE_DIR
    rand_dir = os.path.join(settings.STATICFILES_DIRS[0], rel_dir)

    files = [f for f in os.listdir(rand_dir) if os.path.splitext(f)[1] in valid_extensions]

    return "/static" + "/" + settings.RANDOM_IMAGE_DIR + "/" + random.choice(files)
