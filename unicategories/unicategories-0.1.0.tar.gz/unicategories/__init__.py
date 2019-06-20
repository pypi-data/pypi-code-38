
import os
import unicodedata

import appdirs

from unicategories_tools import cache, merge, RangeGroup

__version__ = '0.1.0'
__all__ = [
    '__version__',
    'RangeGroup', 'categories', 'merge',
    'user_cache_path', 'user_cache_enabled',
    ]
user_cache_path = os.path.join(
    appdirs.user_cache_dir(__name__),
    'database-%s-%s.pickle' % (
        cache.cache_formats[-1],
        unicodedata.unidata_version,
        )
    )
user_cache_enabled = (
    os.getenv('UNICODE_CATEGORIES_CACHE', '').lower() in
    ('', '1', 'yes', 'true' 'on', 'enable', 'enabled')
    )
categories = (
    cache.load_from_package(__name__, 'database.pickle') or
    cache.load_from_cache(user_cache_path if user_cache_enabled else None) or
    cache.generate_and_cache(user_cache_path if user_cache_enabled else None)
    )
