import os

import fleep


class Chibi_path( str ):
    def __new__( cls, *args, **kw ):
        args_2 = []
        for a in args:
            if '~' in a:
                a = os.path.expanduser( a )
            args_2.append( a )
        return str.__new__( cls, *args_2, **kw )

    def __add__( self, other ):
        from chibi.file.snippets import join
        if isinstance( other, self.__class__ ):
            if self.is_a_file:
                return self.dir_name + other

            return self.__class__( join( str( self ), str( other ) ) )
        if isinstance( other, str ):
            return self + self.__class__( other )

    @property
    def is_a_folder( self ):
        from chibi.file.snippets import is_a_folder
        return is_a_folder( self )

    @property
    def is_a_file( self ):
        from chibi.file.snippets import is_a_file
        return is_a_file( self )

    @property
    def dir_name( self ):
        from chibi.file.snippets import file_dir
        return self.__class__( file_dir( self ) )

    def open( self ):
        if self.is_a_folder:
            raise NotImplementedError
        from . import Chibi_file
        return Chibi_file( self )

    def relative_to( self, root ):
        from .snippets import get_relative_path
        return type( self )( get_relative_path( self, root=root ) )

    def mkdir( self, **kw ):
        from .snippets import mkdir
        mkdir( self, **kw )

    def copy( self, dest, **kw ):
        from.snippets import copy, copy_folder
        if self.is_a_file:
            copy( self, dest, **kw )
            return Chibi_path( dest )
        elif self.is_a_folder:
            copy_folder( self, dest )
            return Chibi_path( dest )

    def delete( self ):
        from.snippets import delete
        delete( str( self ) )

    def chown(
            self, verbose=True, user_name=None, group_name=None,
            recursive=False ):
        from chibi.file.snippets import chown
        chown(
            self, user_name=user_name, group_name=group_name,
            recursive=recursive )

    def chmod( self, mod ):
        os.chmod( str( self ), mod )

    @property
    def properties( self ):
        from chibi.file.snippets import stat

        prop = stat( self )
        with open( self, 'rb' ) as f:
            info = fleep.get( f.read( 128 ) )

        prop.type = info.type[0] if info.type else None
        prop.extension = info.extension[0] if info.extension else None
        prop.mime = info.mime[0] if info.mime else None
        return prop
