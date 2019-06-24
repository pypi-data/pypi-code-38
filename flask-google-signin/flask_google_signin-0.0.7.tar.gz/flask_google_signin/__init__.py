__all__ = ['set_client_id', 'set_grant_rule', 'set_force_https', 'google_signin', 'login_required']

from flask import Flask, Blueprint, render_template_string, request, url_for, session, redirect
from functools import wraps
import json
import requests


_GOOGLE_CLIENT_ID = ''
_GRANT_RULE = None
_FORCE_HTTPS = True

def set_client_id(id):
    """Set GOOGLE_CLIENT_ID."""
    global _GOOGLE_CLIENT_ID
    _GOOGLE_CLIENT_ID = id


def set_grant_rule(func_rule):
    """Set a function(email) -> boolean to check email for login grant."""
    global _GRANT_RULE
    _GRANT_RULE = func_rule


def set_force_https(boo):
    global _FORCE_HTTPS
    _FORCE_HTTPS = boo


def _verified(id_token):
    r = requests.get("https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=" + id_token)
    if r.status_code == 200:
        user = json.loads(r.content)
        return True, user
    else:
        return False, None


def _has_right(user):
    if user['aud'] != _GOOGLE_CLIENT_ID:
        return False
    email = user['email']
    return _GRANT_RULE(email)


google_signin = Blueprint('google_signin', __name__, template_folder='templates')


@google_signin.route('/login_page', methods=['GET'])
def login_page():
    if _GOOGLE_CLIENT_ID == '':
        raise Exception('Forget to set_client_id!')
    if _GRANT_RULE is None:
        raise Exception('Forget to set_grant_rule!')
    return render_template_string(login_page_html, client_id=_GOOGLE_CLIENT_ID, success_redirect=request.args.get('from_url'))


@google_signin.route('/authorize', methods=['POST'])
def authorize():
    id_token = request.form.get('id_token')
    OK, user = _verified(id_token)
    if not OK:
        return 'login fail'
    if _has_right(user):
        session.permanent = True
        session['login'] = True
        session['login_email'] = user['email']
        return render_template_string(login_success_html, success_redirect=request.form.get('success_redirect'))
    else:
        return 'login fail'


@google_signin.route('/unprivileged', methods=['GET'])
def unprivileged():
    email = request.args.get('email')
    return f'Your google account({email}) has no privilege to access this page.'


@google_signin.route('/account', methods=['GET'])
def account():
    if session.get('login', False) == False:
        return 'You are not signed in.'
    else:
        email = session['login_email']
    return f'You are signed in. Account: {email}.'


@google_signin.route('/signout', methods=['GET'])
def signout():
    session['login'] = False
    session['login_email'] = None
    return 'Signed out.'


def login_required(email_checker=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            global _FORCE_HTTPS
            if request.url.startswith('http://localhost'):
                _FORCE_HTTPS = False
            if request.endpoint.startswith('google_signin.'):   #if requesting login page
                return f(*args, **kwargs)
            if session.get('login', False) == False:            #if not yet login
                if _FORCE_HTTPS:
                    return redirect(url_for('google_signin.login_page', from_url=request.url.replace('http:','https:'),  _external=True, _scheme='https'))
                else:
                    return redirect(url_for('google_signin.login_page', from_url=request.url))
            if session.get('login', False):                    #if already login
                if email_checker is None:
                    return f(*args, **kwargs)
                else:
                    email = session.get('login_email')
                    if email_checker(email):                   #if email pass check
                        return f(*args, **kwargs)
                    else:                                      #if email fail check
                        if _FORCE_HTTPS:
                            return redirect(url_for('google_signin.unprivileged', email=email, _external=True, _scheme='https'))
                        else:
                            return redirect(url_for('google_signin.unprivileged', email=email))
        return decorated_function
    return decorator



login_page_html = '''
<head>
    <meta name="google-signin-client_id" content="{{client_id}}">
</head>

<body>
    <div id="my-signin2"></div>

    <script>

        function onSuccess(googleUser) {
            document.getElementById('display').innerHTML = 'Logging in! Redirecting...';
            var id_token = googleUser.getAuthResponse().id_token;
            gapi.auth2.getAuthInstance().signOut()
            gapi.auth2.getAuthInstance().disconnect()

            document.getElementById('id_token').value = id_token;
            document.getElementById("myForm").submit();
        }

        function onFailure(error) {
            gapi.auth2.getAuthInstance().signOut()
            gapi.auth2.getAuthInstance().disconnect()
            document.getElementById('display').innerHTML = 'Login Fail! Try Again! Or:<br>1. Try another browser<br>2. Use incognito mode<br>3. Clear cookie first';
        }

        function renderButton() {
            gapi.signin2.render('my-signin2', {
                'scope': 'profile email',
                'width': 240,
                'height': 50,
                'longtitle': true,
                'theme': 'dark',
                'onsuccess': onSuccess,
                'onfailure': onFailure
            });
        }

    </script>

    <script src="https://apis.google.com/js/platform.js?onload=renderButton" async defer></script>
    <br>
    <p id="display"></p>

    <form id="myForm" action="{{url_for('google_signin.authorize')}}" method="post">
        <input id="id_token" type="hidden" name="id_token" value="">
        <input id="success_redirect" type="hidden" name="success_redirect" value="{{success_redirect}}">
    </form>
</body>
'''


login_success_html = '''
<head>
</head>

<body>
    <p>Login Success. Redirect now...</p>

    <script>
        window.setTimeout(function () {
            window.location.replace("{{success_redirect}}");
        }, 1000);

    </script>

</body>
'''
