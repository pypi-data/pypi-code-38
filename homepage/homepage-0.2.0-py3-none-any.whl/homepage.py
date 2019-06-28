#!/usr/bin/env python3

# Import required modules
from __future__ import unicode_literals

from atexit import register
from datetime import datetime
from os import environ, makedirs, path, walk
from shutil import make_archive
from subprocess import call, check_output  # noqa: S404
from sys import argv, exit

import easyparse

from flask import Flask, render_template, request, safe_join, send_from_directory

from gevent.pywsgi import WSGIServer

import youtube_dl

version_string = " * HomePage, v0.1.0\n * Copyright (c) 2019 Sh3llcod3. (MIT License)"

# Get the environment paths
storage_folder = environ.get("HOMEPAGE_STORAGE")
downloads_folder = environ.get("HOMEPAGE_DOWNLOADS")

storage_folder = storage_folder if (storage_folder is not None) else "~/.homepage_storage"
downloads_folder = downloads_folder if (downloads_folder is not None) else "~/.homepage_downloads"

storage_folder = path.expanduser(storage_folder)
downloads_folder = path.expanduser(downloads_folder)


# Setup our youtube_dl logger class.
class YTDLLogger():
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def ytdl_hook(progress):
    if progress['status'] == 'finished':
        print(' * Downloaded video, now converting...')


# Setup our Video class, this will handle the youtube_dl side of things.
class Video():

    # Initialise the class.
    def __init__(self, post_request):
        self.post_request = post_request
        self.video_link = post_request["videoURL"]
        self.mime_type = post_request["format_preference"]
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': f'{self.mime_type}',
                'preferredquality': post_request["quality_preference"],
            }],
            'logger': YTDLLogger(),
            'progress_hooks': [ytdl_hook],
            'outtmpl': f'{downloads_folder}/%(title)s.%(ext)s'
        }
        if post_request["attach_thumb"].lower() == "yes":
            self.ydl_opts["writethumbnail"] = True
            self.ydl_opts["postprocessors"].append({'key': 'EmbedThumbnail', })
        if self.mime_type == "m4a":
            self.ydl_opts['postprocessor_args'] = [
                '-strict', '-2'
            ]

    # Add our download() method to download the video.
    def download(self):
        with youtube_dl.YoutubeDL(self.ydl_opts) as self.ydl:
            self.ydl.download([self.video_link])

    # Add our send_files() method to handle transfer.
    def send_files(self):
        path, dirs, files = next(walk(downloads_folder))
        file_count = len(files)
        self.final_file_name = str()
        self.final_file_location = str()

        # The link is invalid
        if file_count == 0:
            return render_template("error_template.html")

        # We have more than one file, so let's zip them up and send them back.
        if file_count > 1:
            self.final_file_name = "tracks_" + str(datetime.now().timestamp()).replace('.', '')
            self.final_file_location = "/tmp/" + self.final_file_name  # noqa: S108
            make_archive(self.final_file_location, 'zip', downloads_folder)
            self.final_file_name += ".zip"
            self.final_file_location += ".zip"
            self.mime_type = "application/zip"
            call(f"mv {self.final_file_location} {storage_folder}/", shell=True)  # noqa: S607, S602
            call(f"rm {downloads_folder}/*", shell=True)  # noqa: S607, S602

        # We only have one track, so let's send the file back.
        else:
            self.final_file_name = next(walk(downloads_folder))[2][0]
            call(f"mv {downloads_folder}/* {storage_folder}/", shell=True)  # noqa: S607, S602

        return safe_join("./transfer/", self.final_file_name)


list_item_template = """<li class="mdc-list-item">
    <span class="mdc-list-item__text">{file_full_name}</span>
    <span class="mdc-list-item__meta material-icons" aria-hidden="true" title="Download Track" onclick="getPreviousTrack('{previous_trackpath}')">cloud_download</span>
</li>"""  # noqa: E501


# Generate the html elements for the previous files.
def update_file_list():
    path, dirs, files = next(walk(storage_folder))
    prev_count = len(files)
    if prev_count == 0:
        return ["", ""]
    elif prev_count > 0:
        list_buffer = str()
        end_js = 'document.getElementById("Previous-Track-Table").style.display = "block";'
        for i in files:
            list_buffer += list_item_template.format(file_full_name=i, previous_trackpath=safe_join("./transfer/", i))
        return [list_buffer, end_js]


app = Flask(__name__, static_url_path='/static')


@app.route('/', methods=["GET", "POST"])
def index_page():
    if request.method == "GET":
        table_items, js_addition = update_file_list()
        return render_template("./site.html", previous_items=table_items, extra_js=js_addition)

    if request.method == "POST":
        dl_request = Video(request.form)
        dl_request.download()
        return dl_request.send_files()


@app.route('/transfer/<filepath>', methods=["GET"])
def download_file(filepath):
    return send_from_directory(storage_folder, filepath, as_attachment=True)


@app.route('/update_state', methods=["GET"])
def update_file_state():
    return update_file_list()[0]


def main():

    # Setup our argument parser
    parser = easyparse.opt_parser(argv)
    parser.add_comment("Deploy for the first time: homepage -fdip")
    parser.add_comment("Deploy the app normally: homepage -df")
    parser.add_comment("I am aware it complains about using a WSGI server.")
    parser.add_comment("This app isn't designed to scale at all, on purpose.")
    parser.add_comment("Please don't deploy this outside your internal network.")
    parser.add_arg(
        "-h",
        "--help",
        None,
        "Show this help screen and exit.",
        optional=True
    )
    parser.add_arg(
        "-v",
        "--version",
        None,
        "Print version information and exit.",
        optional=True
    )
    parser.add_arg(
        "-d",
        "--deploy-app",
        None,
        "Deploy the app and start the flask server.",
        optional=False
    )
    parser.add_arg(
        "-f",
        "--forward-to-all-hosts",
        None,
        "Add an iptables rule forwarding port 80 to 5000 for convenience.",
        optional=False
    )
    parser.add_arg(
        "-p",
        "--purge-cache",
        None,
        "If supplied, remove all past downloaded tracks.",
        optional=False
    )
    parser.add_arg(
        "-i",
        "--install-dependencies",
        None,
        "Install some apt dependencies, only need to run once.",
        optional=False
    )
    parser.parse_args()

    # View the help screen
    if parser.is_present("-h") or len(argv) == 1:
        parser.filename = "homepage"
        parser.show_help()
        exit()

    # Print the version.
    if parser.is_present("-v"):
        print(version_string)
        exit()

    # Add the iptables rule
    active_interface = check_output("route | grep '^default' | grep -o '[^ ]*$'",  # noqa: S607
                                     shell=True).decode('utf-8')  # noqa: S602
    active_interface = active_interface.rstrip()

    def remove_rule():
        print("\n * Reverting iptables rule.")
        call((f"sudo iptables -t nat -D PREROUTING -i {active_interface} "  # noqa: S607
              "-p tcp --dport 80 -j REDIRECT --to-port 5000"), shell=True)  # noqa: S602

    if parser.is_present("-f"):
        print(" * Adding iptables rule.")
        call((f"sudo iptables -t nat -A PREROUTING -i {active_interface} "  # noqa: S607
              "-p tcp --dport 80 -j REDIRECT --to-port 5000"), shell=True)  # noqa: S602
        register(remove_rule)

    # Delete the previous downloaded tracks
    if parser.is_present("-p"):
        print(" * Purging downloaded tracks.")
        call(f"rm {downloads_folder}/* {storage_folder}/* 2>/dev/null", shell=True)  # noqa: S602, S607

    # Install the apt dependencies.
    if parser.is_present("-i"):
        call("sudo apt update && sudo apt install ffmpeg lame atomicparsley faac libav-tools -y",  # noqa: S607
              shell=True)  # noqa: S602

    # Run the app
    if parser.is_present("-d"):

        # Create required directories if not present.
        if not path.isdir(storage_folder):
            makedirs(storage_folder)

        if not path.isdir(downloads_folder):
            makedirs(downloads_folder)

        local_ip = check_output(("ip a | grep \"inet \" | grep -v \"127.0.0.1\" "  # noqa: S607
                                 "| awk -F ' ' {'print $2'} | cut -d \"/\" -f1"), shell=True)  # noqa: S602
        print(f" * My local ip address is: {local_ip.decode('utf-8').rstrip()}")
        print(f" * My default interface is: {active_interface}")

        try:
            http_server = WSGIServer(('', 5000), app, log=None, error_log='default')
            http_server.serve_forever()
        except(KeyboardInterrupt):
            pass


if __name__ == "__main__":
    main()
