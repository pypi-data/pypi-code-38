import pwd
import grp
from chibi.atlas import Chibi_atlas


def _parse_passwd( passwd ):
    return Chibi_atlas( dict(
        name=passwd.pw_name, passwd=passwd.pw_passwd, uid=passwd.pw_uid,
        gid=passwd.pw_gid, gecos=passwd.pw_gecos, dir=passwd.pw_dir,
        shell=passwd.pw_shell ) )


def _parse_group( group ):
    return Chibi_atlas( dict(
        name=group.gr_name, passwd=group.gr_passwd, gid=group.gr_gid,
        mem=group.gr_mem ) )


def get_passwd( uid=None, name=None ):
    if uid is not None:
        return _parse_passwd( pwd.getpwuid( uid ) )
    elif name is not None:
        return _parse_passwd( pwd.getpwnam( name ) )
    raise ValueError( "uid y name no pueden ser None" )


def get_group( gid=None, name=None ):
    if gid is not None:
        return _parse_group( grp.getgrgid( gid ) )
    elif name is not None:
        return _parse_group( grp.getgrnam( name ) )
    raise ValueError( "gid y name no pueden ser None" )


def user_exists( uid=None, name=None ):
    f = []
    if uid is not None and name is None:
        return any( filter( lambda x: x.pw_uid == uid, pwd.getpwall() ) )
    elif uid is None and name is not None:
        return any( filter( lambda x: x.pw_name == name, pwd.getpwall() ) )
    else:
        return any( filter(
            lambda x: x.pw_name == name and x.pw_uid == uid, pwd.getpwall() ) )


def group_exists( gid=None, name=None ):
    if gid is not None and name is None:
        return any( filter( lambda x: x.gr_gid == gid, grp.getgrall() ) )
    elif gid is None and name is not None:
        return any( filter( lambda x: x.gr_name == name, grp.getgrall() ) )
    else:
        return any( filter(
            lambda x: x.gr_name == name and x.gr_gid == gid, grp.getgrall() ) )
