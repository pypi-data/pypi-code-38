# -*- coding: utf-8 -*-


from django.core.management import BaseCommand
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

import subprocess
import magic
import string
import random
import json
import os
from pyPdf import PdfFileWriter, PdfFileReader

from aparnik.utils.utils import round
from aparnik.contrib.filefields.models import FileField
from aparnik.packages.educations.courses.models import CourseFile


def randomPasswordAndIV():
    """Generate a random password """
    password = ''
    iv = ''

    for i in range(64):
        password += random.choice(string.hexdigits)
    for i in range(32):
        iv += random.choice(string.hexdigits)
    return password.lower(), iv.lower()


class Command(BaseCommand):
    # Show this when the user types help
    help = "Encrypt File fields"

    # A command must define handle()
    def handle(self, *args, **options):

        start_time = now()

        queryset = FileField.objects.filter(is_lock=True)

        for file in queryset:
            # check file exist
            # ممکن ه که هنوز فرآیند آپلود به اتمام نرسیده باشد
            if not file.file_direct.storage.exists(file.file_direct.name):
                continue
            path = file.file_direct.path
            infile = path
            outfile = '%s.enc' % path

            if file.is_decrypt_needed:
                # decrypt
                # pdf
                # movies
                if file.type == FileField.FILE_PDF:
                    # with open(infile, "rb") as ifile, open(outfile, "wb") as ofile:
                    #     reader = PdfFileReader(ifile)
                    #     print(str(file.password))
                    #     if reader.isEncrypted:
                    #         reader.decrypt(unicode('1da72c67efb2ccdcf43fef8c6afacdd405659effaadcdae31cabb2ead8df43ab'))
                    #
                    #     writer = PdfFileWriter()
                    #     for i in range(reader.getNumPages()):
                    #         writer.addPage(reader.getPage(i))
                    #     writer.write(ofile)
                    # TODO: fix pdf decrypt
                    continue
                else:

                    subprocess.call(
                        'openssl enc -aes-256-cbc -d -nosalt -K %s -iv %s -in %s -out %s' % (
                        file.password, file.iv, infile, outfile),
                        shell=True, close_fds=True)

                os.remove(path)
                os.rename(outfile, infile)
                file.is_decrypt_needed = False
                file.password = None
                file.iv = None
            else:
               # find type
                f = magic.Magic(mime=True, uncompress=False)
                mime = f.from_file(path)
                file.type = file.detect_mime_type(mime)

                if not file.type:
                    f = magic.Magic()
                    mime = f.from_file(path)
                    file.type = file.detect_by_readable_description(mime)

                if not file.type:
                    continue

                if file.type == FileField.FILE_VOICE or file.type == FileField.FILE_MOVIE:
                    ffprobe_properties = "ffprobe -i '%s' -v quiet -print_format json -show_format -hide_banner" % path
                    metadata = subprocess.check_output(
                        ffprobe_properties,
                        shell=True, close_fds=True)
                    metadata = json.loads(metadata)

                    if 'duration' in metadata['format']:
                        duration = metadata['format']['duration']
                        file.seconds = int(round(duration))
                        for f in file.shop_file_obj.all():

                            if isinstance(f, CourseFile):
                                f.seconds = file.seconds
                                f.save()
                    else:
                        continue

                # Encrypt
                if file.is_encrypt_needed:
                    # Generate Key and IV
                    key, iv = randomPasswordAndIV()

                    if file.type == FileField.FILE_PDF:

                        iv = None
                        # Encrypt PDF

                        with open(infile, "rb") as ifile, open(outfile, "wb") as ofile:
                            reader = PdfFileReader(ifile)
                            writer = PdfFileWriter()
                            for i in range(reader.getNumPages()):
                                writer.addPage(reader.getPage(i))
                            writer.encrypt(str(key))
                            writer.write(ofile)

                    else:

                        # Encrypt Etc
                        subprocess.call('openssl enc -aes-256-cbc -nosalt -K %s -iv %s -in %s -out %s'%(key, iv, infile, outfile), shell=True, close_fds=True)

                    os.remove(path)
                    os.rename(outfile, infile)
                    file.password = key
                    file.iv = iv

            # Finish and release lock
            file.is_lock = False
            file.save()

        finished_time = now()

        print(('encrypt done %s - time long: %ss.' % (now(), relativedelta(finished_time, start_time).seconds)))
