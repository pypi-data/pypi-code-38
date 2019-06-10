from chibi.file import Chibi_file
from chibi.file.snippets import add_extensions
from chibi.file.path import Chibi_path
from PIL import Image


class Chibi_image( Chibi_file ):
    @property
    def dimension( self ):
        return self._PIL.size

    @property
    def _PIL( self ):
        return Image.open( self.path )

    def __eq__( self, other ):
        if not isinstance( other, Chibi_image ):
            return False
        return (
            self.properties.mime == other.properties.mime and
            self.dimension == other.dimension and
            self.properties.size == other.properties.size
        )

    def thumbnail( self, path, size=( 64, 64 ) ):
        path = Chibi_path( path )
        if ( path.is_a_folder ):
            path = path + add_extensions( self.file_name, 'thumbnail' )
            thumbnail = self._PIL.copy()
            thumbnail.thumbnail( size )
            thumbnail.save( path )
            return type( self )( path )
        else:
            raise NotImplementedError
