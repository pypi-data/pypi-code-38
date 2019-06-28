import json


def login_helper(conn, email, username, password, token):
    if email != "" and username != "":
        print("You cannot use both email and username, pass in one or the other.")
        return
    if password != "" and token != "":
        print("You cannot use both password and token, pass in one or the other.")
        return
    if email == "" and username == "":
        print("An email or username must be passed in.")
        return
    if password == "" and token == "":
        print("A password or token must be passed in.")
        return

    url = conn.URL + '/sessions'
    data = {
        'sessions': [
            {'device': 'cli'}
        ],
        'account': {}
    }
    if email:
        data['email'] = email
    if username:
        data['uid'] = username
    if password:
        data['password'] = password
    if token:
        data['accessToken'] = token

    r = conn.put(url, data=json.dumps(data))
    if r.status_code == 200:
        data = r.json()
        return data
    elif r.status_code == 401 or r.status_code == 422:
        print('Incorrect credentials.')
        print('It may help to log out and then try to login.')
        return None
    else:
        print('Error: {}'.format(r.status_code))
        return None

