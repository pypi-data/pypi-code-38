"""
Command: genkey
===============



"""


from django.core.management.base import BaseCommand, CommandError
import os
import sys
import shutil

class Command(BaseCommand):
    help = 'Generate .apk for debug'
    can_import_settings = True


    #----------------------------------------------------------------------
    def add_arguments(self, parser):
        """"""

        # parser.add_argument(
            # '--upload',
            # action='store_true',
            # dest='upload_key',
            # default=True,
            # help='Generate new upload key',
        # )


    #----------------------------------------------------------------------
    def handle(self, *args, **options):
        """"""
        from django.conf import settings



        # if options['upload_key']:

        store = settings.ANDROID['KEY']['RELEASE_KEYSTORE'].replace('.keystore', '') + ".upload.jks"
        pem = settings.ANDROID['KEY']['RELEASE_KEYSTORE'].replace('.keystore', '') + ".pem"


        if os.path.exists(store) or os.path.exists(pem):
            print("For security reasons, overwrite keys is wrong!!!\nplease, MOVE your old keys.")
            sys.exit()


        alias = settings.ANDROID['KEY']['RELEASE_KEYALIAS']
        os.chdir(settings.BASE_DIR)
        os.system("keytool -genkey -v -keystore {} -alias {} -keyalg RSA -keysize 2048 -validity 10000".format(store, alias))
        os.system("keytool -export -rfc -keystore {} -alias {} -file {}".format(store, alias, pem))


        # else:
            # store = settings.ANDROID['KEY']['RELEASE_KEYSTORE']
            # alias = settings.ANDROID['KEY']['RELEASE_KEYALIAS']

            # if os.path.exists(store):
                # print("For security reasons, overwrite keys is wrong!!!\nplease, MOVE your old keys.")
                # sys.exit()

            # os.chdir(settings.BASE_DIR)
            # os.system("keytool -genkey -v -keystore {} -alias {} -keyalg RSA -keysize 2048 -validity 10000".format(store, alias))
