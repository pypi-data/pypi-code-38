from rest_framework import status
from test_runners import status_code as status_test


class Test_unauthorized( status_test.Test_status_code ):
    expected_status_code = status.HTTP_401_UNAUTHORIZED

    def setUp( self ):
        token = self.get_token()
        if token is not None:
            self.client.credentials( HTTP_AUTHORIZATION=str( token ) )

    def get_token( self ):
        pass


class Test_list( Test_unauthorized, status_test.Test_list ):
    pass


class Test_retrieve( Test_unauthorized, status_test.Test_retrieve ):
    pass


class Test_create( Test_unauthorized, status_test.Test_create ):
    pass
