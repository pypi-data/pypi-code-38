__all__ = ['set_client_id', 'set_grant_rule', 'bp_google_signin', 'login_required']

from flask import Flask, Blueprint, render_template_string, request, url_for, session, redirect
from functools import wraps
import datetime
import json
import requests
from .html_source import *


_GOOGLE_CLIENT_ID = ''
_GRANT_RULE_SET = False


def _GRANT_RULE(email): return False


def set_client_id(id):
    """Set GOOGLE_CLIENT_ID.
    
    Args:
        id (str): The GOOGLE_CLIENT_ID.
    """
    global _GOOGLE_CLIENT_ID
    _GOOGLE_CLIENT_ID = id


def set_grant_rule(func_rule):
    """Set the rule to check email for grant.
    
    Args:
        func_rule (str): Input the email to check. Should return boolean.
    """
    global _GRANT_RULE
    global _GRANT_RULE_SET
    _GRANT_RULE = func_rule
    _GRANT_RULE_SET = True


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


bp_google_signin = Blueprint('google_signin', __name__, template_folder='templates')


@bp_google_signin.route('/login_page', methods=['GET'])
def login_page():
    if _GOOGLE_CLIENT_ID == '':
        raise Exception('Forget to set_client_id!')
    if not _GRANT_RULE_SET:
        raise Exception('Forget to set_grant_rule!')
    return render_template_string(login_page_html, client_id=_GOOGLE_CLIENT_ID, success_redirect=request.args.get('next'))


@bp_google_signin.route('/authorize', methods=['POST'])
def authorize():
    id_token = request.form.get('id_token')
    OK, user = _verified(id_token)
    if not OK:
        return 'login fail'
    if _has_right(user):
        session.permanent = True
        session['login'] = True
        return render_template_string(login_success_html, success_redirect=request.form.get('success_redirect'))
    else:
        return 'login fail'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('login', False) != True:
            return redirect(url_for('google_signin.login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
