import re

block_list = [
    '#',
    '/@',
    '/#',
    '/tag',
    '/api',
    '\.pdf',
    '/job',
    '/faq',
    '/.pdf',
    '/home',
    '/feed',
    '/devs',
    '/team',
    '[?]m=',
    'lang=',
    '/page',
    '/sign',
    '/terms',
    '/login',
    '/[?]m=',
    '/trend',
    '/about',
    '/stats',
    '/brand',
    '/logout',
    '/author',
    '/tagged',
    '/latest',
    '[?]cat=',
    '/people',
    '/upload',
    '/comment',
    '/careers',
    'careers[.]',
    '/welcome',
    '/support',
    '/privacy',
    '/keyword',
    '/sitemap',
    '/[?]cat=',
    '/contact',
    'irc:///',
    '/archive',
    '/tutorial',
    '/follower',
    '/support/',
    '/category',
    '/trending',
    '/register',
    '/download',
    '/newsfeed',
    '/wp-login',
    '/password',
    '/community',
    '/following',
    '/categories',
    '/docs/following',
    '/search',
    '/label',
    '{{',
    '/getting-started',
    '/profile',
    "/channel/",
    "/video/",
    "/videos/",
]


# c = Crawler(urls[120], "test", "currency", any_exclude_regexes=block,
#             notify=lambda a, c: print(a))
iso2_countries = r'/(af|ax|al|dz|as|ad|ao|aq|ag|ag|ar|am|aw|au|at|az|bs|bh|bd|bb|by|be|bz|bj|bm|bt|bo|ba|bw|bv|br|vg|bn|bg|bf|bi|ko|kh|cm|ca|cv|ky|cf|td|cl|cn|hk|mo|cx|cc|cc|co|km|ck|cr|ci|hr|cu|cy|cz|dk|dj|dm|do|ec|eg|sv|gq|er|ee|et|fk|fk|fo|fj|fi|fr|gf|pf|ga|gm|ge|de|gh|gi|gr|gl|gd|gp|gu|gt|gg|gn|gw|gy|ht|hm|va|va|hn|hu|is|in|id|ir|iq|ie|im|il|it|jm|jp|je|jo|kz|ke|ki|kr|kw|kg|la|lv|lb|ls|lr|ly|li|lt|lu|mk|mg|mw|my|mv|ml|mt|mh|mq|mr|mu|yt|mx|fm|md|mc|mn|me|ms|ma|mz|mm|nr|np|nl|an|nc|nz|ni|ne|ng|nu|nf|mp|no|om|pk|pw|ps|pa|pg|py|pe|ph|pn|pl|pt|pr|qa|ro|ru|rw|bl|sh|kn|lc|mf|pm|vc|ws|sm|st|sa|sn|rs|sc|sl|sg|sk|si|sb|so|za|gs|gs|ss|es|lk|sd|sr|sj|sj|sz|se|ch|sy|tw|tj|tz|th|tl|tg|tk|to|tt|tt|tn|tr|tm|tc|tv|tw|ug|ua|ae|uy|uz|vu|ve|vn|vn|vi|wf|wf|eh|xh|ye|zm|zw|zh)([/.?_-]|$)'
iso2_countries_re = re.compile(iso2_countries)


def should_be_blocked(url):
    for b in block_list:
        if re.search(b, url):
            return True
    # if re.search("/[0-9/]+$", url):
    #     print("blocking", url)
    #     return True
    if iso2_countries_re.search(url):
        return True
    return False
