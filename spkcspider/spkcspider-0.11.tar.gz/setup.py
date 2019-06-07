# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['spkcspider',
 'spkcspider.apps.spider',
 'spkcspider.apps.spider.forms',
 'spkcspider.apps.spider.migrations',
 'spkcspider.apps.spider.models',
 'spkcspider.apps.spider.templatetags',
 'spkcspider.apps.spider.views',
 'spkcspider.apps.spider.widgets',
 'spkcspider.apps.spider_accounts',
 'spkcspider.apps.spider_accounts.migrations',
 'spkcspider.apps.spider_filets',
 'spkcspider.apps.spider_filets.migrations',
 'spkcspider.apps.spider_keys',
 'spkcspider.apps.spider_keys.migrations',
 'spkcspider.apps.spider_tags',
 'spkcspider.apps.spider_tags.migrations',
 'spkcspider.apps.spider_webcfg',
 'spkcspider.apps.spider_webcfg.migrations',
 'spkcspider.apps.verifier',
 'spkcspider.apps.verifier.migrations',
 'spkcspider.settings']

package_data = \
{'': ['*'],
 'spkcspider.apps.spider': ['locale/de/LC_MESSAGES/*',
                            'management/commands/*',
                            'static/*',
                            'static/schemes/*',
                            'static/spider_base/*',
                            'static/spider_base/protections/*',
                            'templates/flatpages/*',
                            'templates/spider_base/*',
                            'templates/spider_base/forms/widgets/*',
                            'templates/spider_base/partials/*',
                            'templates/spider_base/protections/*'],
 'spkcspider.apps.spider_accounts': ['templates/registration/*'],
 'spkcspider.apps.spider_filets': ['locale/de/LC_MESSAGES/*',
                                   'static/spider_filets/*',
                                   'templates/spider_filets/*'],
 'spkcspider.apps.spider_keys': ['locale/de/LC_MESSAGES/*',
                                 'templates/spider_keys/*'],
 'spkcspider.apps.spider_tags': ['locale/de/LC_MESSAGES/*',
                                 'static/spider_tags/*',
                                 'templates/spider_tags/*'],
 'spkcspider.apps.verifier': ['locale/de/LC_MESSAGES/*',
                              'templates/spider_verifier/*']}

install_requires = \
['bleach',
 'certifi',
 'cryptography',
 'django-fast-ratelimit',
 'django-next-prev',
 'django-ranged-response',
 'django-simple-jsonfield>=0.3',
 'django-widget-tweaks',
 'django>=2.2',
 'html5lib',
 'lru-dict',
 'rdflib',
 'requests']

setup_kwargs = {
    'name': 'spkcspider',
    'version': '0.11',
    'description': 'A secure, decentral platform for maintaining your online identity',
    'long_description': 'Simple protection-knocking (visiting) card Spider (short: spkcspider)\n--------------------------------------------------------\n\nspkcspider provides a digital visiting card which can e.g. be used for authentication, shopping and payment. For this a multifactor authentication is provided.\nIt keeps your online data safe while shopping by just providing a link to a potion of your data. Doing this, the user may can provide some knocking mechanism (e.g. has to provide some code, tan) to protect the content.\n\nFurther features and advantages of spkcspider are:\n\n* cross device configuration without saving user data on webshop/service.\n  This makes them easily DSGVO compatible without adjustments\n* Address Data have to changed only on one place if you move. This is especially useful if you move a lot\n  Also if you travel and want to buy something on the way.\n* Verification of data is possible.\n* Privacy: private servers are easily set up (only requirement: cgi), also compatible to tor\n* Travelling: some people don\'t respect common rules for privacy. This tool allows you to keep your digital life private.\n  * You don\'t have it on the device\n  * You can hide your data with the travel mode (against the worst kind of inspectors)\n    * Note: traces could be still existent (like "recently-used" feature, bookmarks)\n  * for governments: use psychology instead of breaking into systems! The only victims are law-abidding citizens.\n\n\n# Installation\n\nThis project can either be used as a standalone project (clone repo) or as a set of reusable apps (setup.py installation).\n\n\n## Build Requirements\n* npm\n* pip >=19 (and poetry)\n\n## Poetry (within virtual environment)\n~~~~ sh\npoetry install\n# for installing with extras specify -E extra1 -E extra2\n~~~~\n\n## Pip\n~~~~ sh\npip install .\n~~~~\n\n## Setup\n~~~~ sh\nnpm install --no-save\n./manager.py migrate\n./manager.py collectstatic\n# or simply use\n./tools/install_deps.sh\n~~~~\n\n## Caveats\n\nMysql works with some special settings:\nRequire mysql to use utf8 charset\nTo unbreak tests, use \'CHARSET\': \'utf8\':\n\n~~~~ python\nDATABASES = {\n    \'default\': {\n        \'ENGINE\': \'django.db.backends.mysql\',\n        ...\n        \'TEST\': {\n            \'CHARSET\': \'utf8\'\n        }\n    }\n}\n\n~~~~\n\n### Possibilities how to add utf8 charset to mysql:\n* use \'read_default_file\' and add "default-character-set = utf8" in config\n* create database with "CHARACTER SET utf8"\n* see: https://docs.djangoproject.com/en/dev/ref/databases/#mysql-notes\n\n\n### \\_\\_old crashes object creation:\ndowngrade sqlite3 to 3.25 or upgrade django to at least 2.1.5/2.0.10\n\nimporting data:\n\nset:\nUPDATE_DYNAMIC_AFTER_MIGRATION = False\nbefore importing data (with loaddata), update dynamic creates data\n\n### keep pathes if switching from cgi\n~~~~\nlocation /cgi-bin/cgihandler.fcgi {\n   rewrite /cgi-bin/cgihandler.fcgi/?(.*)$ https://new.spkcspider.net/$1 redirect ;\n}\n~~~~\n\n### logging\nIn this model tokens are transferred as GET parameters. Consider disabling the\nlogging of GET parameters (at least the sensible ones) or better:\ndisable logging of succeeding requests\n\n\nnginx filter tokens only (hard):\n~~~~\nlocation / {\n  set $filtered_request $request;\n  if ($filtered_request ~ (.*)token=[^&]*(.*)) {\n      set $filtered_request $1token=****$2;\n  }\n}\nlog_format filtered_combined \'$remote_addr - $remote_user [$time_local] \'\n                    \'"$filtered_request" $status $body_bytes_sent \'\n                    \'"$http_referer" "$http_user_agent"\';\n\naccess_log /var/logs/nginx-access.log filtered_combined;\n~~~~\n\nnginx filter GET parameters:\n~~~~\nlog_format filtered_combined \'$remote_addr - $remote_user [$time_local] \'\n                    \'"$uri" $status $body_bytes_sent \'\n                    \'"$http_referer" "$http_user_agent"\';\n\naccess_log /var/logs/nginx-access.log filtered_combined;\n~~~~\n\napache filter GET parameters:\n~~~~\nLogFormat "%h %l %u %t \\"%m %U %H\\" %>s %b \\"%{Referer}i\\" \\"%{User-agent}i\\"" combined\n\n~~~~\n\n# External usage\n\nThere are special GET parameters for controlling spkcspider:\n* page=<int>: page number\n* token=xy: token as GET parameter, if invalid: retrieve token as GET parameter\n* token=prefer: uses invalid mechanic, easier to see what it does\n* raw=true: optimize output for machines, use turtle format\n* raw=embed: embed content of components\n* id=id&id=id: limit content ids (Content lists only)\n* search=foo&search=!notfoo: search case insensitive a string\n* search=\\_unlisted: List "unlisted" content if owner, special user (doesn\'t work in public list).\n* protection=false: fail if protections are required\n* protection=xy&protection=yx...: protections to use\n* intention=auth: try to login with UserComponent authentication (falls back to login redirect)\n* referrer=<url>: activate referrer mode\n  * intention=domain: domain verify referrer mode\n  * intention=sl: server-less referrer mode\n  * payload=<foo>: passed on successfull requests (including post), e.g. for sessionid\n  * intention=login: referrer uses spkcspider for login (note: referrer should be the one where the user is logging in, check referrer field for that)\n  * intention=persist: referrer can persist data on webserver\n* embed_big=true: only for staff and superuser: Overrides maximal size of files which are embedded in graphs (only for default helper)\n\n## Referrer\n* normal referrer mode: send token to referrer, client verifies with hash that he sent the token.\n* server-less referrer mode (sl): token is transferred as GET parameter and no POST request is made (less secure as client sees token and client is not authenticated)\n* domain referrer mode (domain): referrer domain is add to token. Doesn\'t work with other intentions (but "live" mode is active as no filter will be created) and works only if domain_mode is for context active (e.g. feature or access context (content)). Can be automated, doesn\'t require user approval. Useful for tag updates (only active if feature requests domain mode).\n\n## search parameters\n\n* search also searches UserComponents name and description fields\n* can only be used with "list"-views\n* items can be negated with !foo\n* strict infofield search can be activated with \\_\n* !!foo escapes a !foo item\n* \\_\\_foo escapes a \\_foo item\n* !\\_ negates a strict infofield search\n* \\_unlisted is a special search: it lists with "unlisted" marked contents\n\nverified_by urls should return last verification date for a hash\n\n## raw mode\n\nraw mode can follow references even in other components because it is readonly.\nOtherwise security could be compromised.\n\n## Important Features\n\n* Persistence: Allow referrer to save data (used and activated by persistent features)\n* WebConfig: Allow remote websites and servers to save config data on your server (requires Persistence)\n* TmpConfig: Allow remote websites and servers to save config data on your server, attached to temporary tokens (means: they are gone after a while)\n\n\n# internal API\n\n\n## Structure\n\n### spider:\nFor spiders and contents\n\n* spkcspider.apps.spider: store User Components, common base, WARNING: has spider_base namespace to not break existing apps\n* spkcspider.apps.spider_accounts: user implementation suitable for the spiders. You can supply your own user model instead.\n* spkcspider.apps.spider_filets: File and Text Content types\n* spkcspider.apps.spider_keys: Public keys and anchors\n* spkcspider.apps.spider_tags: verified information tags\n* spkcspider.apps.spider_webcfg: WebConfig Feature\n* spkcspider: contains spkcspider url detection and wsgi handler\n\n### verifier:\nBase reference implementation of a verifier.\n\nspkcspider.apps.verifier: verifier base utils WARNING: has spider_verifier namespace to not break existing apps\n\n\n## info field syntax\n\nThe info field is a simple key value storage. The syntax is (strip the spaces):\n\nflag syntax: \\\\x1e key \\\\x1e\nkey value syntax: \\\\x1e key=value \\\\x1e\n\nNote: I use the semantic ascii seperators \\\\x1e. Why? Sperating with an non-printable character eases escaping and sanitizing.\nNote 2: I reverted from using \\\\x1f instead of = because the info field is used in searchs\n\nWhy not a json field? Django has no uniform json field for every db adapter yet.\n\n\n## authentication/privileges\n\n* request.is_staff: requesting user used staff rights to access view (not true in ComponentPublicIndex)\n* request.is_owner: requesting user owns the components\n* request.is_special_user: requesting user owns the components or is_staff\n* request.protections: int: enough protections were fullfilled, maximal measured strength, list: protections which failed, False: no access; access with protections not possible\n\n## Special Scopes\n\n* add: create content, with AssignedContent form\n* update: update content\n* raw_update: update Content, without AssignedContent form, adds second raw update mode (raw_add is not existent, can be archieved by returning HttpResponse in add scope)\n* export: export data (import not implemented yet)\n* view: present content to untrusted parties\n\n## strength (component)\n* 0: no protection. Complete content visible\n* 1-3: protection strength which can be provided by protections. Meta data (names, descriptions) visible, inclusion in sitemap, public components\n* 4: login only, user password. Still with inclusion of metadata\n* 5: public attribute not set. No inclusion in sitemap or public components index anymore\n* 6-8: protections + public attribute not set\n* 9: login only, user password + public attribute not set\n* 10: index, login only, special protected. Protections are used for login. Content here can be made unique per user by using unique per component attribute\n\n= extra["strength"] on token (if available elsewise treat as zero):\n\nthe strength of the usercomponent for which it was created at the creation point\n\n## strength (protection)\n* 0: no protection\n* 1-3: weak, medium, strong\n* 4: do component authentication\n\n= extra["prot_strength"] on token (if available elsewise treat as zero):\n\nthe strength of protections which was passed for creating the token\n\nNote: access tokens created by admin have strength 0\n\n## get usercomponent/content from url/urlpart for features\n\nUse UserComponent.from_url_part(url) / AssignedContent.from_url_part(url, [matchers]) for that\nor use a domain_mode or persistent token.\nNote: the difference between a domain_mode and a persistent token is, that the domain_mode token has a variable lifetime (user specific but defaults to 7 days)\n\n\n# API Breaks\n* >0.5: settings rename\\*\\_ TLD_PARAMS_MAPPING to \\*\\_REQUEST_KWARGS_MAP with new syntax (hosts are allowed, tlds start with .)\n  * Note: port arguments are stripped, localhost matches localhost:80, localhost:8000, ...\n\n# TODO\n* examples\n* documentation\n* test admin\n* tests for other dbs than sqlite3 (and postgresql)\n* Localisation\n  * harmonize punctation\n* good permission model for TravelProtection\n* MAYBE: remove dispatch_uid of signals or harmonize\n\n## Later\n* maybe: make quota type overridable (maybe add extra nonsaved quota: other or use 0)\n* create client side script for import (pushing to server, index token for auth?)\n  * use browerside javascript?\n* textfilet hot reloading\n* pw protection: add migration tool for changed SECRET_KEY\n* log changes\n* improve protections, add protections\n\n\n### Implement Web Comments\n* every internal page can be annotated (to keep contact to author)\n  * send as message?\n  * CommentBox?\n* Comment: url, subcommentlist, commenttext, reactionlist (reaction, counter)\n* view: load iframe with original content?\n* js for loading subcomments (only 1 level), sanitize!\n* you see only the comments of your friends\n* implement with messaging? Would keep comments private\n* Later/Maybe:\n  * way to register your comment url on webpage, so others can see all comments\n  * social media stuff: find content via comments and likes\n  * annotation of other pages\n\n\n\n# Thanks\n\n* Default theme uses Font Awesome by Dave Gandy - http://fontawesome.io\n* Some text fields use Trumbowyg by Alexander Demode\n* Django team for their excellent product\n',
    'author': 'Alexander Kaftan',
    'author_email': None,
    'url': 'https://spkcspider.net',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
