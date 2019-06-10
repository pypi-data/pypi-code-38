from chibi.pipeline import Pipeline
from chibi.snippet.dict import remove_xml_notatation


class Remove_xml_garage( Pipeline ):
    def run( self, obj, *args, **kw ):
        return remove_xml_notatation( obj )
