"""Auth for testing.

$ pipenv shell
$ cd webreview
$ python test_auth.py
# Follow authentication prompts.
"""

import webreview

client = webreview.WebReview(
    project='jeremydw/test',
    name='test-staging-site',
    host='grow-prod.appspot.com',
    secure=True,)
client.login()
