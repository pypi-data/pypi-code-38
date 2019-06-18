from flask_login import LoginManager, current_user, UserMixin, login_required
from flask import Flask, request, redirect, Response, session
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from urllib import parse
from requests import get, post, put
from functools import wraps
from string import ascii_letters, digits
from time import gmtime, strftime
from datetime import datetime, timedelta
from random import choice
from os import getenv
import base64
import json


class MLC_Auth(object):
	login_manager = None
	app = None

	def __init__(self, app, **kwargs):
		domain = '.mlc-services.com'
		# self.portal_URI = 'https://portal.mlc-services.com'
		self.portal_URI = 'http://local-portal.mlc-services.com:8050'
		app.config['REMEMBER_COOKIE_DOMAIN'] = domain
		app.config['SESSION_COOKIE_DOMAIN'] = domain
		self.api = MLC_API(portal_uri=self.portal_URI, secret=app.config['SECRET_KEY'])

		login_manager = LoginManager()
		login_manager.session_protection = "strong"
		login_manager.user_loader(self.load_user)
		login_manager.init_app(app)

		self.app = app
		self.login_manager = login_manager


	def load_user(self, user_id):
		"""Loads a User instance from the session cookie"""
		if 'auth' in session and \
		   'fresh' in session['auth'] and \
		   'user' in session['auth'] and \
		   session['auth']['fresh'] > datetime.now():
			return User(session['auth']['user'])

		user = self._fetch_user(user_id)
		if user:
			session['auth'] = {'fresh': datetime.now() + timedelta(minutes=5), 'user': vars(user)}
			return user



	def auth_required(self, accessable_by=['guest', 'user', 'manager', 'administrator']):
		"""Makes the route login required. Roles can be set so only those roles have access to the route.
		If no roles are given, all logged in users have access.

		Parameters:
		accessable_by (optional, List) -- A list of roles which have access to the route.
		"""

		def decorator(f):
			@wraps(f)
			def decorated_function(*args, **kwargs):
				self.login_manager.reload_user()
				if current_user.is_authenticated and current_user.role in accessable_by:
					return f(*args, **kwargs)
				return self._redirect_to_login(request)
			return decorated_function
		return decorator


	def _redirect_to_login(self, request):
		next_url = request.args.get('next') or ''
		new_next_url = request.url_root + next_url[1:]
		return redirect('{}/login?next={}'.format(self.portal_URI, parse.quote(string=new_next_url)))


	def _fetch_user(self, user_id):
		user_data = self.api._get_user(user_id)
		if user_data and 'id' in user_data:
			return User(user_data)



class MLC_API(object):
	def __init__(self, portal_uri, secret):
		self.portal_URI = portal_uri
		self.secret = secret


	def _generate_token(self, data=None):
		kdf = PBKDF2HMAC(
			algorithm=hashes.SHA256(),
			length=32,
			salt=strftime("%d%m%Y%H%M", gmtime()).encode(),
			iterations=100000,
			backend=default_backend()
		)
		key = base64.urlsafe_b64encode(kdf.derive(self.secret.encode()))
		f = Fernet(key)
		if not data:
			data = vars(current_user)
		return f.encrypt(str(data).encode())


	def _get_user(self, user_id):
		"""Fetches the user data from the portal API.

		Parameters:
		user_id (Integer) -- The user data id.
		"""
		token = self._generate_token({'id': user_id})
		response = get('{}/api/user/{}'.format(self.portal_URI, user_id), headers={'X-AUTH-TOKEN': token})
		try:
			return response.json()
		except Exception as e:
			print('An error had occured while trying to fetch data from the portal API: ', e)


	def get(self, endpoint, params={}):
		"""Sends a GET XMLHttpRequest to the portal API. returns the content as a dict.

		Parameters:
		endpoint (String) -- The endpoint url (ex: /api/user/1)
		params (optional, Dictionary) -- The URL params wich need to be send to the API.
		"""
		token = self._generate_token()
		headers = {'X-AUTH-TOKEN': token}
		url = self.portal_URI + endpoint
		response = get(url, params=params, headers=headers)
		try:
			return response.json()
		except Exception as e:
			print('An error had occured while trying to fetch data from the portal API: ', e)


	def post(self, endpoint, body={}, params={}):
		"""Sends a PUT XMLHttpRequest to the portal API.

		Parameters:
		endpoint (String) -- The endpoint url (ex: /api/user/1)
		body (optional, Dictionary) -- The data to be send in the requests body.
		params (optional, Dictionary) -- The URL params wich need to be send to the API.
		"""
		token = self._generate_token()
		headers = {'X-AUTH-TOKEN': token}
		url = self.portal_URI + endpoint
		response = post(url, json=json.dumps(body, default=str), params=params, headers=headers)
		try:
			return response.json()
		except Exception as e:
			print('An error had occured while trying to fetch data from the portal API: ', e)



class User(UserMixin):
	id = None
	email = None
	name = None
	role = None
	organisation_id = None
	organisation_name = None

	def __init__(self, data):
		self.id = data['id']
		self.email = data['email']
		self.name = data['name']
		self.role = data['role']
		self.organisation_id = data['organisation_id']
		self.organisation_name = data['organisation_name']

	def __repr__(self):
		return '<User: {}>'.format(self.name)
