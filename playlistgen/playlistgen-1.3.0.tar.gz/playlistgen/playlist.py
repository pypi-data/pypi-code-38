import os
import subprocess
import sys
from typing import List, Tuple
from urllib.request import pathname2url, url2pathname

import click
import lxml.etree as ET
from moviepy.video.io.VideoFileClip import VideoFileClip

SUPPORTED_VID = {".avi", ".mkv", ".mp4"}


@click.command()
@click.option(
    "-f",
    "--file-name",
    "fname",
    help="The filename for playlist (Default = dir name)",
    type=click.STRING,
)
@click.option(
    "--sort",
    "sort",
    help="Whether to sort (egghead)",
    default=False,
    type=click.BOOL,
    is_flag=True,
)
@click.argument("root_dir", required=True)
def generate(fname, sort, root_dir):
    if root_dir is None:
        root_dir = os.getcwd()

    click.echo("Getting files")
    file_paths, encoded_paths = get_files(root_dir, sort)

    fname = os.path.basename(root_dir)
    if fname is None:
        fname = os.path.basename(root_dir)
    fname = os.path.join(os.path.dirname(root_dir), fname)

    click.echo()
    xml_txt = get_xml(fname, file_paths, encoded_paths)
    with click.open_file(f"{fname}.xspf", "wb") as f:
        f.write(xml_txt)


def get_files(root_dir: str, sort: bool) -> Tuple[List[str], List[str]]:
    ret_list = [
        os.path.join(root, f)
        for root, dirs, files in os.walk(root_dir)
        for f in files
        if os.path.splitext(f)[-1] in SUPPORTED_VID
    ]
    if sort:
        click.echo("Sorting files")
        ret_list = list(
            sorted(
                ret_list, key=lambda x: int(os.path.basename(x).strip().split("-")[0])
            )
        )
    encoded_list = [f"file:{pathname2url(x)}" for x in ret_list]
    return ret_list, encoded_list


def get_xml(fname: str, file_list: list, encoded_list: list) -> bytes:
    NSMAP = {
        None: "http://xspf.org/ns/0/",
        "vlc": "http://www.videolan.org/vlc/playlist/ns/0/",
    }
    playlist = ET.Element("playlist", version="1", nsmap=NSMAP)
    ET.SubElement(playlist, "title").text = fname
    tracklist = ET.SubElement(playlist, "trackList")

    with click.progressbar(length=len(file_list), label="Generating playlist") as bar:
        for i, (normal_name, encoded_name) in enumerate(zip(file_list, encoded_list)):
            track = ET.SubElement(tracklist, "track")
            ET.SubElement(track, "location").text = encoded_name
            ET.SubElement(track, "duration").text = str(get_duration(normal_name))
            ext = ET.SubElement(
                track, "extension", application="http://www.videolan.org/vlc/playlist/0"
            )
            ET.SubElement(ext, "{%s}id" % NSMAP["vlc"]).text = str(i)
            bar.update(1)

    extension_outer = ET.SubElement(
        playlist, "extension", application="http://www.videolan.org/vlc/playlist/0"
    )
    for i, path in enumerate(file_list):
        ET.SubElement(extension_outer, "{%s}item" % NSMAP["vlc"], tid=str(i))
    tree = ET.ElementTree(playlist)
    return ET.tostring(
        tree, xml_declaration=True, encoding="UTF-8", method="xml", pretty_print=True
    )


def get_duration(file_path: str) -> int:
    result = subprocess.Popen(
        ["ffprobe", file_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    lines = result.stdout.readlines()
    clip = VideoFileClip(file_path)
    dur = int(clip.duration * 1000)
    clip.reader.close()
    clip.audio.reader.close_proc()
    return dur


if __name__ == "__main__":
    generate()
