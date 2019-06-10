import json
import mmap

import fleep
import yaml

from chibi.file.path import Chibi_path
from chibi.file.snippets import (
    exists, stat, check_sum_md5, read_in_chunks, copy, base_name, file_dir
)


class Chibi_file:
    def __init__( self, file_name ):
        self._file_name = file_name
        self._current_dir = file_dir( file_name )
        if not self.exists:
            self.touch()
        self.reread()

    @property
    def file_name( self ):
        return base_name( self._file_name )

    @property
    def dir( self ):
        return self._current_dir

    @property
    def path( self ):
        return Chibi_path( self._file_name )

    @property
    def is_empty( self ):
        return self.properties.size == 0

    @property
    def properties( self ):
        prop = stat( self.path )
        with open( self.path, 'rb' ) as f:
            info = fleep.get( f.read( 128 ) )

        prop.type = info.type[0] if info.type else None
        prop.extension = info.extension[0] if info.extension else None
        prop.mime = info.mime[0] if info.mime else None
        return prop

    def __del__( self ):
        try:
            self.file.close()
        except AttributeError:
            pass

    def close( self ):
        self.file.close()

    def find( self, string_to_find ):
        if isinstance( string_to_find, str ):
            string_to_find = string_to_find.encode()
        return self.file.find( string_to_find )

    def reread( self ):
        try:
            with open( self.path, 'r' ) as f:
                self.file = mmap.mmap(
                    f.fileno(), 0, prot=mmap.PROT_READ )
        except ValueError as e:
            if not str( e ) == 'cannot mmap an empty file':
                raise

    def __contains__( self, string ):
        return self.find( string ) >= 0

    def append( self, string ):
        with open( self.path, 'a' ) as f:
            f.write( string )
        self.reread()

    def write( self, string ):
        with open( self.path, 'w' ) as f:
            f.write( string )
        self.reread()

    @property
    def file( self ):
        return self._file_content

    @file.setter
    def file( self, value ):
        self._file_content = value

    @property
    def exists( self ):
        return exists( self.path )

    def touch( self ):
        open( self.path, 'a' ).close()

    def copy( self, dest, verbose=True, **kw ):
        copy( self.path, dest, verbose=verbose, **kw )

    def chunk( self, chunk_size=4096 ):
        return read_in_chunks( self.path, 'r', chunk_size=chunk_size )

    def check_sum_md5( self, check_sum ):
        return check_sum_md5( self.path, check_sum )

    def read_json( self ):
        self.reread()
        return json.load( self.file )

    def write_json( self, data ):
        self.write( json.dumps( data ) )

    def read_yaml( self ):
        self.reread()
        return yaml.load( self.file )

    def write_yaml( self, data ):
        self.write( yaml.dump( data ) )
