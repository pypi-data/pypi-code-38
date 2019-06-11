import base64
import binascii
import os
import random
import string

from chibi import b64


def decode( s, code='utf-8' ):
    return s.decode( code )


def generate_string( length=10, letters=string.ascii_letters ):
    """
    Generate a random string

    Arguments
    ---------
    length: int (optional, default 10)
    letters: string (optional, default is all ascii letters)

    Returns
    -------
    string
        random string
    """
    return u''.join(
        random.choice(  letters ) for x in range( length ) )


def generate_email( domain=None, extention=None ):
    """
    Generate random email

    Arguments
    ---------
    domain: string, optional
        Name of domain of email, if no sen is generate randomly
    extention: string, optional
        extencion of the email, if no send is generate randomly

    Returns
    -------
    string
        random string formatted randomly
    """
    if not domain:
        domain = generate_string( 10 )
    if not extention:
        extention = generate_string( 10 )
    return "{name}@{domain}.{extention}".format( **{
        'name': generate_string( 10 ),
        'domain': domain,
        'extention': extention, } )


def generate_password(
        length=20,
        letters=(
            string.ascii_letters + string.digits + string.punctuation ) ):
    """
    Genera un password

    Arguments
    ---------
    length: int
        longitud del password a generar
    letters: string
        cadena con la lista de todas los caracteres que se pueden usar
    """
    return generate_string( length, letters )


def generate_token( length=20 ):
    """
    genera tokens

    Arguments
    ---------
    length: int
        numero de bites usados para generar el token
    """
    return binascii.hexlify( os.urandom( length ) ).decode()


def generate_token_b64( length=8 ):
    """
    genera tokens en base64

    TODO: remplazar los tokens hexadecimales por los de base64

    Arguments
    ---------
    length: int
        numero de bites usados para generar el token
        el default es 8 porque quiero 32 caracteres por default
    """
    return b64.encode( os.urandom( length ) )


def generate_b64_unsecure( length=24 ):
    """
    genera una cadena de base 64 aleatoria no segura

    Arguments
    ---------
    length: int
        numero de bites usados para generar la cadena
    """
    bites = bytearray( random.getrandbits(8) for _ in range( length ) )
    return base64.urlsafe_b64encode( bites ).decode( 'utf-8' )
