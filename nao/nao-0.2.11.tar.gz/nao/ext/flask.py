"""


"""

from functools import wraps

from flask import current_app, url_for

from flask_login import (
    LoginManager as OrigLoginManager, current_user, UserMixin,
    login_required, login_user, logout_user
    )

from collections import OrderedDict as odict

from ..types import naodict

class LoginManager(OrigLoginManager):
	"""
	FLASK-LOGIN enhancement
	"""

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.custom_auth_callback = None
        self.nopriv_callback = None


    def custom_auth_handler(self, callback):
        self.custom_auth_callback = callback
        return callback

    def nopriviledge_handler(self, callback):
        self.nopriv_callback = callback
        return callback

    def nopriviledge(self):
        return self.nopriv_callback()

    @property
    def auth_map(self):

        am = []

        for endpoint, args, kwds in _auth_map:

            ok = self.custom_auth_callback(endpoint, args, kwds)

            # add only kwds to be used separately
            am.append((endpoint, ok, kwds))

        return am


    def get_menu_base(self):

        def has_no_empty_params(rule):
            defaults = rule.defaults if rule.defaults is not None else ()
            arguments = rule.arguments if rule.arguments is not None else ()
            return len(defaults) >= len(arguments)

        links = {}

        for rule in current_app.url_map.iter_rules():

            # Filter out rules we can't navigate to in a browser
            # and rules that require parameters
            if "GET" in rule.methods and has_no_empty_params(rule):
                url = url_for(rule.endpoint, **(rule.defaults or {}))
                key = url.split('/')[1:] # more questions
                # no duplicates allowed by werkzeug
                links[rule.endpoint] = (key, url)

        mp = []

        for endpoint, ok, kwds in self.auth_map:

            if ok and endpoint in links:
                key, url = links[endpoint]

                item = naodict()
                item.url = url
                item.key = key
                item.endpoint = endpoint
                item.subs = []

                mp.append(item)

        return mp

    @property
    def menu(self):

        def treebuilder(data, key=None, max_level=None):
            """
            TODO implement tree flattening after a certain level
            """

            # collectiong the items in order for this level
            col = odict()

            level = 0 if key is None else len(key)
            start = '' if key is None else '.'.join(key)

            # print('treebuilder', key, level, start)

            # check all the items
            for item in data:

                # if they are not for this node then nothing happens
                if not '.'.join(item.key).startswith(start):
                    # print("not considered - different branch", item)
                    continue

                if len(item.key) == level:
                    # print("not considered - current node")
                    continue

                # print("consider", item)
                # node to consider
                key_piece = item.key[level]

                # add to collection if not already there
                if key_piece not in col:
                    # create a pseudo-node
                    x = naodict()
                    x.url = "#"
                    x.subs = []
                    # x.endpoint = ''
                    x.key = item.key[:level+1]
                    col[key_piece] = x

                # build tree if not yet exist - triggered on any node
                if len(item.key) > level and not item.subs:
                    col[key_piece].subs = treebuilder(data, item.key[:level+1])

                # a real subnode -> update
                if len(item.key) == level+1:
                    # save subs
                    item.subs = col[key_piece].subs
                    # update with the real item
                    col[key_piece] = item
                    # print("added", item)

            # return only the subs in order
            return list(col.values())

        mp = self.get_menu_base()

        menu = naodict()
        menu.items = treebuilder(mp)

        return menu


# context problem might need to set app current_menu context...
_auth_map = []


# add to utils near login_required
def custom_auth(*args, **kwds):

    # if callable(args[0]): pass

    def decorator(func):

        # log.info("FUNC DECORATED: {}".format(func.__name__))
        # False means needs authentication

        _auth_map.append((func.__name__, args, kwds))

        @wraps(func)
        def decorated_view(*f_args, **f_kwds):

            lm = current_app.login_manager

            # add standard checks from flask-login.utils login required
            if lm.custom_auth_callback and lm.custom_auth_callback(func.__name__, args, kwds):
                return func(*f_args, **f_kwds)
            elif current_user.is_authenticated:
                # no right to access - redirect back to previous page 
                return lm.nopriviledge()
            else:
                return lm.unauthorized()

        return decorated_view

    return decorator

auth = custom_auth

# could be a lm method
def check_auth(*args, **kwds):

    lm = current_app.login_manager

    # call `custom_auth_callback` with empty function name
    return lm.custom_auth_callback \
        and lm.custom_auth_callback('', args, kwds)

check = check_auth