from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.db import models
from .token import Token
from chibi_user.managers import User_manager


class User( AbstractBaseUser, PermissionsMixin ):
    """
    Modelo de usuarios para personalisar los campos
    """
    id = models.CharField( _( "Id of user" ), max_length=64, primary_key=True )
    username = models.CharField( unique=True, max_length=64, )
    email = models.CharField(
        unique=True, null=True, default=None, max_length=64, )

    first_name = models.CharField( max_length=64, )
    last_name = models.CharField( max_length=64, )

    is_active = models.BooleanField( default=True, null=False )
    is_staff = models.BooleanField( default=False, null=False )
    is_superuser = models.BooleanField( default=False, null=False )

    objects = User_manager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__( self ):
        return "pk: {} :: username: {}".format( self.pk, self.username )

    def refresh_token( self ):
        """
        TODO: make test
        Refresca el token el usuario o lo crea

        Returns
        -------

        Token
            token que se genero para el usuario
        """
        try:
            if self.token:
                self.token.delete()
        except Token.DoesNotExist:
            pass
        finally:
            return Token.objects.create( user=self )
