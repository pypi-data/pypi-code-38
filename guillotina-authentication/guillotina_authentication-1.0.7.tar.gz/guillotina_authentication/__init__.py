from guillotina import configure


app_settings = {
    # provide custom application settings here...
    'auth_providers': {
        # 'github': {
        #   'configuration': {
        #     'client_id': 'b6281b6fe88fa4c313e6',
        #     'client_secret': '21ff23d9f1cad775daee6a38d230e1ee05b04f7c'
        #   },
        #   'scope': 'user:email'
        # }
    },
    'auth_callback_url': None,
    'auth_user_identifiers': [
        'guillotina_authentication.identifier.OAuthClientIdentifier'
    ]
}


def includeme(root):
    """
    custom application initialization here
    """
    configure.scan('guillotina_authentication.api')
