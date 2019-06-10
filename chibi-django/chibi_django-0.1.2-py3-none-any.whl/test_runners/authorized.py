from test_runners import status_code as status_test


class Test_authorized( status_test.Test_status_code ):
    url_name = 'namespace:name'

    def setUp( self ):
        super().setUp()
        token = self.get_token()
        if token is not None:
            self.client.credentials( HTTP_AUTHORIZATION=str( token ) )

    def get_token( self ):
        pass


class Test_list( Test_authorized, status_test.Test_list ):
    pass


class Test_retrieve( Test_authorized, status_test.Test_retrieve ):
    pass


class Test_create( Test_authorized, status_test.Test_create ):
    pass
