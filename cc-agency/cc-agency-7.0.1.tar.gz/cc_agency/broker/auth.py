from os import urandom
from time import time

from bson import ObjectId

from cc_agency.commons.helper import generate_secret, get_ip, create_kdf


class Auth:
    def __init__(self, conf, mongo):
        self._num_login_attempts = conf.d['broker']['auth']['num_login_attempts']
        self._block_for_seconds = conf.d['broker']['auth']['block_for_seconds']
        self._tokens_valid_for_seconds = conf.d['broker']['auth']['tokens_valid_for_seconds']

        self._mongo = mongo

    def create_user(self, username, password, is_admin):
        salt = urandom(16)
        kdf = create_kdf(salt)
        user = {
            'username': username,
            'password': kdf.derive(password.encode('utf-8')),
            'salt': salt,
            'is_admin': is_admin
        }
        self._mongo.db['users'].update_one({'username': username}, {'$set': user}, upsert=True)

    def verify_user(self, auth):
        if not auth:
            return None

        username = auth.username
        password = auth.password

        user = self._mongo.db['users'].find_one({'username': username})

        if not user:
            return None

        user['verified_by_credentials'] = False

        salt = user['salt']
        del user['salt']

        if not user:
            return None

        if self._is_blocked_temporarily(user):
            return None

        if self._verify_user_by_token(user, password):
            return user

        if self._verify_user_by_credentials(user, password, salt):
            user['verified_by_credentials'] = True
            return user

        self._add_block_entry(user)
        return None

    def _is_blocked_temporarily(self, user):
        self._mongo.db['block_entries'].delete_many({'timestamp': {'$lt': time() - self._block_for_seconds}})
        block_entries = list(self._mongo.db['block_entries'].find({'username': user['username']}))

        if len(block_entries) > self._num_login_attempts:
            return True

        return False

    def _add_block_entry(self, username):
        self._mongo.db['block_entries'].insert_one({
            'username': username,
            'timestamp': time()
        })
        print('Unverified login attempt: added block entry!')

    def issue_token(self, user):
        salt = urandom(16)
        kdf = create_kdf(salt)
        token = generate_secret()
        self._mongo.db['tokens'].insert_one({
            'username': user['username'],
            'ip': get_ip(),
            'salt': salt,
            'token': kdf.derive(token.encode('utf-8')),
            'timestamp': time()
        })
        return token

    def _verify_user_by_token(self, user, token):
        self._mongo.db['tokens'].delete_many({'timestamp': {'$lt': time() - self._tokens_valid_for_seconds}})
        cursor = self._mongo.db['tokens'].find(
            {'username': user['username'], 'ip': get_ip()},
            {'token': 1, 'salt': 1}
        )
        for c in cursor:
            try:
                kdf = create_kdf(c['salt'])
                kdf.verify(token.encode('utf-8'), c['token'])
                return True
            except:
                pass

        return False

    def verify_callback(self, batch_id, token):
        self._mongo.db['callback_tokens'].delete_many({'timestamp': {'$lt': time() - self._tokens_valid_for_seconds}})
        cursor = self._mongo.db['callback_tokens'].find(
            {'batch_id': batch_id},
            {'token': 1, 'salt': 1}
        )
        for c in cursor:
            try:
                kdf = create_kdf(c['salt'])
                kdf.verify(token.encode('utf-8'), c['token'])
                return True
            except:
                pass

        return False

    @staticmethod
    def _verify_user_by_credentials(user, password, salt):
        kdf = create_kdf(salt)
        try:
            kdf.verify(password.encode('utf-8'), user['password'])
        except:
            return False

        return True
