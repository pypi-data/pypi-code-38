import functools
import logging
import os

from comring.lib import odoo
from . import utils

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

odoo.load_envs(os.path.expanduser('~/.config/odoopti.yaml'))

LOGGER = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        environment = request.form['environment']

        error = None
        client = None
        if username and password and environment:
            oenv = odoo.envs_info[environment]
            if not oenv:
                error = 'Invalid environment: {}'.format(environment)
                flash(error)
                return render_template('auth/login', environments=odoo.envs_info)
            osv = odoo.Odoo(oenv['url'])
            try:
                client = osv.login(
                        oenv['database'],
                        username,
                        password)
            except RuntimeError as e:
                error = str(e)

        if error is None:
            print('Login success')
            session.clear()
            session['o_username'] = client.get_session_data('username')
            session['o_uid'] = client.get_user_context('uid')
            session['o_partner_id'] = client.get_session_data('partner_id')
            session['o_env'] = environment
            session['o_session_id'] = client.get_session_data('session_id')
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html', environments=odoo.envs_info)

@bp.before_app_request
def load_logged_in_user():
    o_uid = session.get('o_uid')
    o_session_id = session.get('o_session_id')
    o_partner_id = session.get('o_partner_id')
    o_env = session.get('o_env')

    if o_session_id is None or o_env is None:
        g.user = None
    else:
        odoo_inst = odoo.get_instance(o_env)
        odoo_client = odoo_inst.connect()
        partner = odoo_client.read_one('res.partner', o_partner_id, ['id', 'name'])
        if partner:
            g.user = {'id': o_uid, 'name': partner['name']}
            if o_env:
                g.odoo_env_alias = o_env
                g.odoo_env = odoo.envs_info[o_env]
        else:
            g.user = None

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view
