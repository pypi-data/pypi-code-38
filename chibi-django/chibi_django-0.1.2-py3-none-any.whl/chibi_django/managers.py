from django.db import models
from chibi import madness
import logging

logger = logging.getLogger( 'chibi_django.manager.base_64_pk' )


class Base_64_pk( models.Manager ):

    def create( self, *args, **kw ):
        kw.pop( 'pk', None )
        pk = self.get_new_pk()
        return super().create( *args, pk=pk, **kw )

    def _get_max_length_of_pk( self ):
        model_meta = self.model._meta
        return model_meta.get_field( 'id' ).max_length

    def get_new_pk( self ):
        max_field_pk = self._get_max_length_of_pk()
        start = 24
        max_retry = 5
        count_retry = 0
        while True:
            try_pk = madness.string.generate_token_b64( length=start )
            is_pk_exists = self.filter( pk=try_pk ).count()
            if is_pk_exists == 0:
                break
            logger.warinig(
                "colicion de pks",
                extra={
                    'number_pk_collide': 1, 'pk_collide': [ try_pk ],
                    'length_of_pk': start, 'count_of_retry': count_retry,
                    'max_length_pk': max_field_pk,
                    'current_length': len( try_pk )
                } )
            if count_retry >= max_retry:
                start += 1
                count_retry += 1
                start = min( start, max_field_pk )
        return try_pk
