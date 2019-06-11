from chibi.command import command


def rabbitmqctl( *args, stdin=None ):
    return command( "rabbitmqctl", *args )


def add_user( user, password ):
    return rabbitmqctl( 'add_user', user, password )


def delete_user( user ):
    return rabbitmqctl( 'delete_user', user )


def set_user_tags( user, tag ):
    return rabbitmqctl( 'set_user_tags', user, tag )


def set_permissions( vhost, user, conf='.*', write='.*', read='.*' ):
    return rabbitmqctl(
        'set_permissions', '-p', vhost, user, conf, write, read )


def add_vhost( vhost ):
    return rabbitmqctl( 'add_vhost', vhost )


def list_users():
    users_raw, e, return_code = rabbitmqctl( 'list_users', stdin='pipe' )
    return users_raw
