from chibi.file import Chibi_file
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
