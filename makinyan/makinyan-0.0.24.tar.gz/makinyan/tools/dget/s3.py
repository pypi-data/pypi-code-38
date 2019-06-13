#!-*-coding:utf-8-*-
__all__ = ["S3"]

import os
import sys
import boto
import boto3
from colorama import Fore, Back, Style
from progressbar import ProgressBar
from boto.s3.key import Key

class S3:
    """
    S3に接続し、各種機能を提供するクラス
    """

    def __init__( self , profile=None , BUCKET_NAME=None ):
        if profile:
            from boto3.session import Session
            session = Session(profile_name=profile)
            self.s3 = session.resource('s3')
        else:
            self.s3 = boto3.resource('s3')

        self.bucket = self.s3.Bucket( BUCKET_NAME )


    def ls( self ):
        """
        bucketリストを取得する
        return : list型
        """

        return self.s3.buckets.all()



    def dl( self , path ):
        """
        Download
        """
        file_list = self.bucket.objects.all()
        print( Fore.YELLOW + "downloading from S3..." )
        print(Style.RESET_ALL)
        p = ProgressBar( 0, len( list( file_list ) ) )
        for i , key in enumerate( file_list ):
            filename = path + "/" + str( key.key )
            filename = filename.replace(" ","")
            dirname = os.path.dirname( filename )
            if not os.path.exists( dirname ): os.mkdir( dirname )
            if os.path.exists( filename ): continue
            try:
                self.bucket.download_file( key.key , filename )
            except Exception as e:
                print( Fore.RED + "Bad Format→" , filename )

            p.update( i )
        print(Fore.YELLOW +"Done!")
        print(Style.RESET_ALL)
