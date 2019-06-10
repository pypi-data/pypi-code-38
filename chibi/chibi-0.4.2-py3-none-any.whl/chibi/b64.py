import base64


def encode( s ):
    if isinstance( s, str ):
        s = s.encode( 'utf-8' )
    return base64.urlsafe_b64encode( s ).decode( 'utf-8' )


def decode( s ):
    return base64.urlsafe_b64decode( s ).decode( 'utf-8' )
