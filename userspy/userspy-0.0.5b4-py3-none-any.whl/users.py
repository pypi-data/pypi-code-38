'''Manage users'''
import sqlite3
from passlib.hash import sha256_crypt
from userspy import sqlite

# connect to database
db = None
c = None
name = None


def create(n):
    global db, c, name
    db = sqlite3.connect(f'{n}.db')
    c = db.cursor()
    name = n
    sqlite.create_table(c, n, [('username', 'text'), ('password', 'text')])

# password hashing


def password_hash(password):
    return sha256_crypt.encrypt(password)


def check_password(password, hash_val):
    return sha256_crypt.verify(password, hash_val)

    # registering


def Register(username, password, confirm_password):
    if password == confirm_password:
        sqlite.insert(c, db, name, [
                      username.lower(), password_hash(password)])
    else:
        return False

# login


def Remove(username):
    sqlite.Remove(c, name, username)


def Login(username, password):
    username_verified = False
    password_verified = False

    # check username and password

    for e in sqlite.read(c, name):
        if not username_verified:
            if username in e[0]:
                username_verified = True
        if not password_verified:
            if check_password(password, e[1]):
                password_verified = True

    if password_verified and username_verified:
        return True
    else:
        return False


def Close():
    db.commit()
    c.close()
    db.close()
