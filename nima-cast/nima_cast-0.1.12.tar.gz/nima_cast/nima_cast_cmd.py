import cmd
import pychromecast

import os, sys
from minio import Minio
from minio.error import ResponseError
import logging
import select
import time

no_minio = False
if '--no-minio' in sys.argv:
    no_minio = True
    print('Skipping minio server...')
else:
    minio_server = os.environ['MINIO_SERVER']
    minio_access_key = os.environ['ACCESS_KEY']
    minio_secret_key = os.environ['SECRET_KEY']
    BUCKET_NAME = 'data'

if '--show-debug' in sys.argv:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

class HelloWorld(cmd.Cmd):
    """Simple command processor example."""

    prompt = '(nima.cast) '
    intro = "Welcome! Type ? to list commands. options: --no-minio and --show-debug"

    cast = None
    casts = None
    friendly_names = None
    fn = None

    if not no_minio:
        minioClient = Minio(minio_server,
                        access_key= minio_access_key,
                        secret_key= minio_secret_key,
                        secure=False)

    def do_search(self, line):
        """Search a list of available devices..."""
        casts = pychromecast.get_chromecasts()
        if len(casts) == 0:
            print("No Devices Found")
        self.friendly_names = [cc.device.friendly_name for cc in casts]
        self.casts = casts
        for i in range(len(self.friendly_names)):
            fn = self.friendly_names[i]
            print('[{}] - {}'.format(i, fn))

    def do_goto(self, line):
        """goto 0:00:25 seeks to the time specified as an argument"""
        return self.do_seek(get_sec(line))

    def do_sel(self, name):
        """sel [name] to select the chromecast with name "name" as the main chromecast device"""
        if not name:
            # return do_select(self, None)
            name = "Living Room TV"

        self.do_search(None)
        cast = next(cc for cc in self.casts if cc.device.friendly_name == name)
        if cast:
            self.cast = cast
            self.fn = cast.device.friendly_name
            self.cast.start()



    def do_select(self, num):
        """select [num] selects the number in the search results"""
        if not num:
            # print("Please choose an index")
            self.do_search(None)
            user_input = input ("Please choose an index: ")
            try:
                num = int(user_input)
            except:
                print("please choose a correct index!")
                return

        num = int(num)
        if num >= len(self.friendly_names):
            print("Index not in range, try again please")
            return

        self.fn = self.friendly_names[num]
        self.cast = self.casts[num]

        self.cast.connect()
        self.cast.wait()
        mc = self.cast.media_controller
        mc.block_until_active(10)

    def do_device(self, line):
        """Shows the name of the selected device"""
        print(self.fn)
    
    def do_list(self, line):
        """List files on the server"""
        self.objects = list(self.minioClient.list_objects(BUCKET_NAME, prefix='tv/', recursive=True))
        i = 0
        for obj in self.objects:
            print("[{:2d}]- \t{}".format(i, obj.object_name))
            i += 1

    def do_play(self, num):
        """play [num] starts playing the file specified by the number in results of list"""
        if not num:
            # print("Please choose an index, use <list> to list files")
            self.do_list(None)
            user_input = input ("Please choose an index: ")
            try:
                num = int(user_input)
            except:
                print("please choose a correct index!")
                return

        num = int(num)
        if num >= len(self.objects):
            print("Index not in range, try again please")
            return

        if not self.cast:
            print("please select cast device using <select>, use <search> for options")
            return

        obj = self.objects[num]
        url = self.minioClient.presigned_get_object(BUCKET_NAME, obj.object_name)
        print(url)

        self.cast.wait()
        mc = self.cast.media_controller
        mc.play_media(url, 'video/mp4')
        mc.block_until_active(10)

    def do_seek(self, time):
        """seek [time] starts playing the file on the specified time"""
        if not self.cast:
            print("please select cast device using <select>, use <search> for options")
            return

        time = int(time)
        self.cast.wait()
        mc = self.cast.media_controller
        mc.seek(time)


    def do_stream(self, url):
        """stream [url] starts playing the file specified by the url"""
        if not self.cast:
            print("please select cast device using <select>, use <search> for options")
            return

        self.cast.wait()
        mc = self.cast.media_controller
        mc.play_media(url, 'video/mp4')
        mc.block_until_active(10)

    def do_pause(self, line):
        if not self.cast:
            print("please select cast device using <select>, use <search> for options")
            return

        self.cast.wait()
        mc = self.cast.media_controller
        mc.pause()

    # def do_sub(self, line):
    #     if not self.cast:
    #         print("please select cast device using <select>, use <search> for options")
    #         return

    #     sub_url = r'http://cyb.nima-dev.com:9000/data/tv/The.Big.Bang.Theory.S08E01.HDTV.x264-LOL.HI.srt?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=Q34OR1AW4WU4YJCNIDC5%2F20190525%2F%2Fs3%2Faws4_request&X-Amz-Date=20190525T173612Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=6eef55bfb4b12f2cc1003a4e023ca46ca04140fc646c0663047198d719e5a03e'
    #     url = r'http://cyb.nima-dev.com:9000/data/tv/ThBgBngThry-S08E01-480p_iMovie-DL.mkv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=Q34OR1AW4WU4YJCNIDC5%2F20190525%2F%2Fs3%2Faws4_request&X-Amz-Date=20190525T173743Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=51ad8634645b62b54d74ba7c66af2645db21935c760f333c4163668fe647a7f9'
    #     self.cast.wait()
    #     mc = self.cast.media_controller
    #     mc.play_media(url, 'video/mp4', subtitles=sub_url)
    #     mc.block_until_active(10)
    #     mc.enable_subtitle(1)
    #     print('Line:' + line)
        
    def do_resume(self, line):
        if not self.cast:
            print("please select cast device using <select>, use <search> for options")
            return
        
        self.cast.wait()
        mc = self.cast.media_controller
        mc.play()

    def do_stop(self, line):
        """stop stops the currently playing file"""
        if not self.cast:
            print("please select cast device using <select>, use <search> for options")
            return

        self.cast.wait()
        mc = self.cast.media_controller
        mc.stop()

    def do_quit(self, line):
        """quit stops the current app on the chromecast"""
        self.cast.wait()
        self.cast.quit_app()
        return

    
    def do_EOF(self, line):
        """exits this environment, just press Ctrl+D"""
        return True

    def do_exit(self, line):
        """exits this environment"""
        return True

def main():
    if '--quit' in sys.argv:
        print('Quitting...')
        return
    else:
        HelloWorld().cmdloop()

if __name__ == '__main__':
    main()
