"""
NOTE: Currently defunct as pytube is broken on windows
"""

from pytube import YouTube
import tkinter as tk
from tkinter import filedialog

def link_and_path():
    """Prompts user for the link to a youtube video, and path of where to download the video to"""
    video_url = input("What is the URL for the video you want to download?: ")
    root = tk.Tk()
    root.withdraw()
    file_path = str(filedialog.askdirectory(
        title="Select Video Output directory",
        mustexist=False))
    return video_url, file_path


def download(video_url, path):
    """Downloads specified video_url to path
    
    :type video_url: String
    :param video_url: The URL you want to download

    :type path: String
    :param path: Path to export donwload to
    """
    YouTube(video_url).streams.filter(subtype='mp4', progressive=True).download(path)
    video_title = str(YouTube(video_url).title)
    return("Downloaded {} to {} as {}.mp4".format(video_title, path, video_title))

if __name__ == "__main__":
    download("https://www.youtube.com/watch?v=rjlF4hvQv6o", ".")