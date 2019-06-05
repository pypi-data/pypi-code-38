from __future__ import absolute_import, print_function

from mercurial import demandimport; demandimport.enable()
from mercurial import (
    error,
    pycompat,
    ui as uimod,
    url,
    util,
)
from mercurial.utils import (
    stringutil,
)

urlerr = util.urlerr
urlreq = util.urlreq

class myui(uimod.ui):
    def interactive(self):
        return False

origui = myui.load()

def writeauth(items):
    ui = origui.copy()
    for name, value in items.items():
        ui.setconfig(b'auth', name, value)
    return ui

def _stringifyauthinfo(ai):
    if ai is None:
        return ai
    realm, authuris, user, passwd = ai
    return (pycompat.strurl(realm),
            [pycompat.strurl(u) for u in authuris],
            pycompat.strurl(user),
            pycompat.strurl(passwd),
    )

def test(auth, urls=None):
    print('CFG:', pycompat.sysstr(stringutil.pprint(auth, bprefix=True)))
    prefixes = set()
    for k in auth:
        prefixes.add(k.split(b'.', 1)[0])
    for p in prefixes:
        for name in (b'.username', b'.password'):
            if (p + name) not in auth:
                auth[p + name] = p
    auth = dict((k, v) for k, v in auth.items() if v is not None)

    ui = writeauth(auth)

    def _test(uri):
        print('URI:', pycompat.strurl(uri))
        try:
            pm = url.passwordmgr(ui, urlreq.httppasswordmgrwithdefaultrealm())
            u, authinfo = util.url(uri).authinfo()
            if authinfo is not None:
                pm.add_password(*_stringifyauthinfo(authinfo))
            print('    ', tuple(pycompat.strurl(a) for a in
                                pm.find_user_password('test',
                                                      pycompat.strurl(u))))
        except error.Abort:
            print('    ','abort')

    if not urls:
        urls = [
            b'http://example.org/foo',
            b'http://example.org/foo/bar',
            b'http://example.org/bar',
            b'https://example.org/foo',
            b'https://example.org/foo/bar',
            b'https://example.org/bar',
            b'https://x@example.org/bar',
            b'https://y@example.org/bar',
            ]
    for u in urls:
        _test(u)


print('\n*** Test in-uri schemes\n')
test({b'x.prefix': b'http://example.org'})
test({b'x.prefix': b'https://example.org'})
test({b'x.prefix': b'http://example.org', b'x.schemes': b'https'})
test({b'x.prefix': b'https://example.org', b'x.schemes': b'http'})

print('\n*** Test separately configured schemes\n')
test({b'x.prefix': b'example.org', b'x.schemes': b'http'})
test({b'x.prefix': b'example.org', b'x.schemes': b'https'})
test({b'x.prefix': b'example.org', b'x.schemes': b'http https'})

print('\n*** Test prefix matching\n')
test({b'x.prefix': b'http://example.org/foo',
      b'y.prefix': b'http://example.org/bar'})
test({b'x.prefix': b'http://example.org/foo',
      b'y.prefix': b'http://example.org/foo/bar'})
test({b'x.prefix': b'*', b'y.prefix': b'https://example.org/bar'})

print('\n*** Test user matching\n')
test({b'x.prefix': b'http://example.org/foo',
      b'x.username': None,
      b'x.password': b'xpassword'},
     urls=[b'http://y@example.org/foo'])
test({b'x.prefix': b'http://example.org/foo',
      b'x.username': None,
      b'x.password': b'xpassword',
      b'y.prefix': b'http://example.org/foo',
      b'y.username': b'y',
      b'y.password': b'ypassword'},
     urls=[b'http://y@example.org/foo'])
test({b'x.prefix': b'http://example.org/foo/bar',
      b'x.username': None,
      b'x.password': b'xpassword',
      b'y.prefix': b'http://example.org/foo',
      b'y.username': b'y',
      b'y.password': b'ypassword'},
     urls=[b'http://y@example.org/foo/bar'])

print('\n*** Test user matching with name in prefix\n')

# prefix, username and URL have the same user
test({b'x.prefix': b'https://example.org/foo',
      b'x.username': None,
      b'x.password': b'xpassword',
      b'y.prefix': b'http://y@example.org/foo',
      b'y.username': b'y',
      b'y.password': b'ypassword'},
     urls=[b'http://y@example.org/foo'])
# Prefix has a different user from username and URL
test({b'y.prefix': b'http://z@example.org/foo',
      b'y.username': b'y',
      b'y.password': b'ypassword'},
     urls=[b'http://y@example.org/foo'])
# Prefix has a different user from URL; no username
test({b'y.prefix': b'http://z@example.org/foo',
      b'y.password': b'ypassword'},
     urls=[b'http://y@example.org/foo'])
# Prefix and URL have same user, but doesn't match username
test({b'y.prefix': b'http://y@example.org/foo',
      b'y.username': b'z',
      b'y.password': b'ypassword'},
     urls=[b'http://y@example.org/foo'])
# Prefix and URL have the same user; no username
test({b'y.prefix': b'http://y@example.org/foo',
      b'y.password': b'ypassword'},
     urls=[b'http://y@example.org/foo'])
# Prefix user, but no URL user or username
test({b'y.prefix': b'http://y@example.org/foo',
      b'y.password': b'ypassword'},
     urls=[b'http://example.org/foo'])

def testauthinfo(fullurl, authurl):
    print('URIs:', fullurl, authurl)
    pm = urlreq.httppasswordmgrwithdefaultrealm()
    ai = _stringifyauthinfo(util.url(pycompat.bytesurl(fullurl)).authinfo()[1])
    pm.add_password(*ai)
    print(pm.find_user_password('test', authurl))

print('\n*** Test urllib2 and util.url\n')
testauthinfo('http://user@example.com:8080/foo', 'http://example.com:8080/foo')
